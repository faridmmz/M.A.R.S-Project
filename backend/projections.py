"""
Projected statistics calculator for live feedback
Shows players the impact of their investments before launching
"""

from models import GlobalConfig, GameState, PlayerInputs
from engine import (
    calculate_demand,
    calculate_demand_segmented,
    calculate_actual_sales,
    calculate_revenue,
    check_mission_failure,
    calculate_hr_efficiency
)


def calculate_projected_stats(
    player_inputs: PlayerInputs,
    current_state: GameState,
    config: GlobalConfig
) -> dict:
    """Non-mutating pre-turn forecast shown to the player as sliders move."""
    # R&D Points: Every €10M = +1 tech point
    rd_points = player_inputs.rd_invest / 10_000_000
    # Scientific missions grant bonus R&D points on success
    if player_inputs.mission_type == "Scientific":
        rd_points += config.SCIENTIFIC_RD_BONUS
    
    # Green Tech Points: Every €10M = +1 green tech point
    green_points = player_inputs.green_invest / 10_000_000
    
    # Safety Tech Points: Every €10M = +1 safety tech point
    safety_points = player_inputs.safety_invest / 10_000_000
    projected_safety_level = current_state.safety_tech_level + int(safety_points)
    
    # Projected Failure Risk
    # Get base risk for mission type
    projected_failure_risk = 0.0  # Initialize
    
    if player_inputs.mission_type == "Short_Suborbital":
        base_risk = config.SHORT_SUBORBITAL_RISK
        safety_millions = player_inputs.safety_invest / 1_000_000
        failure_prob = base_risk - (safety_millions * config.SAFETY_EFFICIENCY)
        projected_failure_risk = max(0.0, min(1.0, failure_prob))
    elif player_inputs.mission_type == "Long_Orbital":
        base_risk = config.LONG_ORBITAL_RISK
        # Check if safety requirement will be met
        if projected_safety_level < config.LONG_ORBITAL_SAFETY_REQ:
            projected_failure_risk = 1.0  # 100% failure if requirement not met
        else:
            # Calculate failure probability
            safety_millions = player_inputs.safety_invest / 1_000_000
            failure_prob = base_risk - (safety_millions * config.SAFETY_EFFICIENCY)
            projected_failure_risk = max(0.0, min(1.0, failure_prob))
    elif player_inputs.mission_type == "Scientific":
        base_risk = config.SCIENTIFIC_RISK
        safety_millions = player_inputs.safety_invest / 1_000_000
        failure_prob = base_risk - (safety_millions * config.SAFETY_EFFICIENCY)
        projected_failure_risk = max(0.0, min(1.0, failure_prob))
    else:
        base_risk = config.BASE_RISK
        safety_millions = player_inputs.safety_invest / 1_000_000
        failure_prob = base_risk - (safety_millions * config.SAFETY_EFFICIENCY)
        projected_failure_risk = max(0.0, min(1.0, failure_prob))
    
    # HR Efficiency after investment
    projected_total_hr = current_state.total_hr_invest + player_inputs.hr_invest
    hr_efficiency_after = calculate_hr_efficiency(projected_total_hr, config)
    
    # Projected CO2 Impact (if mission succeeds)
    projected_green_level = current_state.green_tech_level + int(green_points)
    green_reduction = 1.0 - (projected_green_level * config.GREEN_TECH_CO2_REDUCTION)
    # Apply Green Hydrogen unlock if applicable
    if current_state.tech_level + int(rd_points) >= 20:
        green_reduction *= 0.5  # 50% reduction from Green Hydrogen
    projected_co2_impact = config.CO2_BASE_IMPACT * green_reduction
    
    # Projected Revenue (for tourist missions)
    projected_revenue_min = 0.0
    projected_revenue_max = 0.0
    projected_demand = 0.0
    projected_sales = 0
    competitor_avg_safety: float | None = None
    # Safety score for demand competitiveness: base 50, +1 per €2M invested, capped at 100
    safety_score = min(100.0, 50.0 + player_inputs.safety_invest / 2_000_000)

    if player_inputs.mission_type in ["Short_Suborbital", "Long_Orbital"]:
        # Calculate demand using the same segmented model as the turn engine
        demand_result = calculate_demand_segmented(
            ticket_price=player_inputs.ticket_price,
            safety_invest=player_inputs.safety_invest,
            marketing_spend=player_inputs.marketing_spend,
            reputation=current_state.reputation,
            market_scenario=current_state.market_scenario,
            config=config,
            mission_type=player_inputs.mission_type,
            has_spaceport=current_state.has_spaceport,
            tech_unlocks=current_state.tech_unlocks,
            consecutive_safe_missions=current_state.consecutive_safe_missions,
        )
        projected_demand = demand_result["total"]
        projected_sales = calculate_actual_sales(projected_demand, config.MAX_PAX)
        competitor_avg_safety = demand_result["competitor_avg_safety"]

        # Revenue = sales × ticket_price (same formula as engine.py)
        projected_revenue_min = projected_sales * player_inputs.ticket_price
        projected_revenue_max = projected_sales * player_inputs.ticket_price
    elif player_inputs.mission_type == "Scientific":
        # Scientific missions: ticket_price is contract value
        projected_revenue_min = player_inputs.ticket_price
        projected_revenue_max = player_inputs.ticket_price
    
    # Marketing Reputation Boost (assumes success for projection purposes)
    marketing_millions = player_inputs.marketing_spend / 1_000_000
    marketing_reputation_boost = marketing_millions * config.MARKETING_REPUTATION_BOOST
    projected_reputation = current_state.reputation + marketing_reputation_boost + config.REPUTATION_SUCCESS_BONUS
    projected_reputation = max(0.0, min(100.0, projected_reputation))
    
    # Investor Interest Gain
    investor_interest_gain = marketing_millions * 2.0  # 2% per €1M
    projected_investor_interest = min(100.0, current_state.investor_interest + investor_interest_gain)
    
    # Contingency Coverage
    # Calculate potential failure penalty
    if player_inputs.mission_type == "Short_Suborbital":
        penalty_multiplier = 0.5
    elif player_inputs.mission_type == "Long_Orbital":
        penalty_multiplier = 1.0
    elif player_inputs.mission_type == "Scientific":
        penalty_multiplier = config.FAILURE_PENALTY_MULTIPLIER
    else:
        penalty_multiplier = 1.0
    
    potential_penalty = config.FAILURE_PENALTY_BASE * penalty_multiplier
    contingency_coverage = min(potential_penalty, player_inputs.contingency_budget)
    contingency_mitigation_pct = (contingency_coverage / potential_penalty * 100) if potential_penalty > 0 else 0.0
    estimated_penalty_after_contingency = max(0.0, potential_penalty - player_inputs.contingency_budget)
    
    return {
        "rd_points": rd_points,
        "green_points": green_points,
        "safety_points": safety_points,
        "projected_failure_risk": projected_failure_risk,
        "projected_failure_risk_pct": projected_failure_risk * 100,
        "projected_co2_impact": projected_co2_impact,
        "projected_revenue_min": projected_revenue_min,
        "projected_revenue_max": projected_revenue_max,
        "projected_demand": projected_demand,
        "projected_sales": projected_sales,
        "marketing_reputation_boost": marketing_reputation_boost,
        "hr_efficiency_after": hr_efficiency_after,
        "hr_efficiency_gain": hr_efficiency_after - current_state.hr_efficiency,
        "contingency_coverage": contingency_coverage,
        "contingency_mitigation_pct": contingency_mitigation_pct,
        "estimated_failure_penalty": potential_penalty,
        "estimated_penalty_after_contingency": estimated_penalty_after_contingency,
        "investor_interest_gain": investor_interest_gain,
        "projected_investor_interest": projected_investor_interest,
        "projected_reputation": projected_reputation,
        "projected_safety_level": projected_safety_level,
        "meets_safety_requirement": (
            player_inputs.mission_type != "Long_Orbital" or
            projected_safety_level >= config.LONG_ORBITAL_SAFETY_REQ
        ),
        "safety_score": safety_score,
        "competitor_avg_safety": competitor_avg_safety,
    }

