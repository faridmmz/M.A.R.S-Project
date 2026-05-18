"""
Core game engine logic for M.A.R.S. Project
"""

import random
import math
import logging
from models import GlobalConfig, GameState, PlayerInputs

logger = logging.getLogger("mars")


def calculate_demand_segmented(
    ticket_price: float,
    safety_invest: float,
    marketing_spend: float,
    reputation: float,
    market_scenario: str,
    config: GlobalConfig,
    mission_type: str = "Short_Suborbital",
    has_spaceport: bool = True,
    event_demand_multiplier: float = 1.0,
    event_safety_share_bonus: float = 0.0,
    marketing_multiplier: float = 1.0,
    tech_unlocks: dict = None,
    consecutive_safe_missions: int = 0,
) -> dict:
    """
    Calculate demand split across three customer personas, under either market scenario.

    Scenario A (Current Market): structural accessibility barriers cap demand hard —
      price or marketing improvements barely move the needle.
    Scenario B (Evolved Market): demand scales elastically with price drops, mimicking
      early aviation mass-market dynamics.

    Competitor reference set is mission-type-specific:
      Short_Suborbital → Virgin Galactic & Blue Origin New Shepard (~€450–500k)
      Long_Orbital     → SpaceX Dragon, Blue Origin, Axiom Space (~€8–15M)

    Returns a dict with keys:
        uhnw_tourists, government, research_industrial, total, potential,
        available_share, competitor_avg_price, competitor_avg_safety, competitors
    """
    # ── Select competitor set by mission type ────────────────────────────────
    if mission_type == "Long_Orbital":
        competitors_raw = {
            "SpaceX Dragon": {
                "price": config.SPACEX_PRICE,
                "safety": config.SPACEX_SAFETY,
                "market_share": config.SPACEX_MARKET_SHARE,
            },
            "Blue Origin": {
                "price": config.BLUE_ORIGIN_PRICE,
                "safety": config.BLUE_ORIGIN_SAFETY,
                "market_share": config.BLUE_ORIGIN_MARKET_SHARE,
            },
            "Axiom Space": {
                "price": config.AXIOM_PRICE,
                "safety": config.AXIOM_SAFETY,
                "market_share": config.AXIOM_MARKET_SHARE,
            },
        }
    else:  # Short_Suborbital (Scientific has no direct tourist competitors)
        competitors_raw = {
            "Virgin Galactic": {
                "price": config.VIRGIN_GALACTIC_PRICE,
                "safety": config.VIRGIN_GALACTIC_SAFETY,
                "market_share": config.VIRGIN_GALACTIC_MARKET_SHARE,
            },
            "Blue Origin (New Shepard)": {
                "price": config.BLUE_ORIGIN_NEW_SHEPARD_PRICE,
                "safety": config.BLUE_ORIGIN_NEW_SHEPARD_SAFETY,
                "market_share": config.BLUE_ORIGIN_NEW_SHEPARD_MARKET_SHARE,
            },
        }

    # ── Competitor weighted averages ─────────────────────────────────────────
    total_comp_share = sum(c["market_share"] for c in competitors_raw.values())
    comp_price_avg = sum(
        c["price"] * c["market_share"] for c in competitors_raw.values()
    ) / total_comp_share
    comp_safety_avg = sum(
        c["safety"] * c["market_share"] for c in competitors_raw.values()
    ) / total_comp_share

    # ── Player's addressable market share ────────────────────────────────────
    # Base: whatever competitors don't own.  Player improves share by under-cutting
    # on price or out-performing on safety.
    available_share = max(0.02, 1.0 - total_comp_share)  # minimum 2 %

    if ticket_price < comp_price_avg:
        price_steal = min(0.15, (1.0 - ticket_price / comp_price_avg) * 0.30)
        available_share += price_steal

    # Safety score derived from investment (base 50 %, capped at 100 %)
    safety_score = min(100.0, 50.0 + safety_invest / 2_000_000)
    if safety_score > comp_safety_avg:
        safety_steal = min(0.10, (safety_score - comp_safety_avg) / 100.0 * 0.20)
        available_share += safety_steal

    # Event: safety share bonus (competitor accident shifts share to safe players)
    if event_safety_share_bonus > 0 and safety_score > comp_safety_avg:
        available_share += event_safety_share_bonus

    safety_norm = safety_score / 100.0
    rep_factor = reputation / 100.0
    marketing_millions = marketing_spend / 1_000_000
    effective_marketing = marketing_millions * marketing_multiplier  # event can double this
    # Helia: in Scenario A, marketing cannot overcome the accessibility barrier
    # (medical screening, training timeline, remote site logistics kill conversion)
    if market_scenario == "A":
        effective_marketing *= config.SCENARIO_A_MARKETING_EFFICIENCY
    marketing_factor = 1.0 + min(effective_marketing * 0.02, 1.0)  # up to +100 % at €50 M

    personas = {
        "uhnw_tourists": {
            "price_sensitivity": config.PERSONA_UHNW_PRICE_SENSITIVITY,
            "safety_sensitivity": config.PERSONA_UHNW_SAFETY_SENSITIVITY,
            "base_pool": config.PERSONA_UHNW_BASE_POOL,
        },
        "government": {
            "price_sensitivity": config.PERSONA_GOV_PRICE_SENSITIVITY,
            "safety_sensitivity": config.PERSONA_GOV_SAFETY_SENSITIVITY,
            "base_pool": config.PERSONA_GOV_BASE_POOL,
        },
        "research_industrial": {
            "price_sensitivity": config.PERSONA_RESEARCH_PRICE_SENSITIVITY,
            "safety_sensitivity": config.PERSONA_RESEARCH_SAFETY_SENSITIVITY,
            "base_pool": config.PERSONA_RESEARCH_BASE_POOL,
        },
    }

    # Autonomous Systems: AI navigation removes training/medical bottleneck → TAM expands
    # (Antonio: shift from 2–3 year to 2–6 week training, "Select-In" medical policy)
    autonomous_systems = (tech_unlocks or {}).get("autonomous_systems", False)

    result: dict = {}
    total_demand = 0.0
    total_potential = 0.0

    for name, w in personas.items():
        price_ratio = comp_price_avg / max(ticket_price, 1_000_000)
        price_factor = price_ratio ** w["price_sensitivity"]
        safety_factor = safety_norm ** w["safety_sensitivity"]

        effective_pool = w["base_pool"] * (config.AUTONOMOUS_TAM_MULTIPLIER if autonomous_systems else 1.0)
        raw = effective_pool * price_factor * safety_factor * marketing_factor * rep_factor
        total_potential += raw

        if market_scenario == "A":
            # Hard barrier: cap per-persona then apply structural multiplier
            raw = min(raw, config.SCENARIO_A_DEMAND_CAP_PER_PERSONA)
            raw *= config.SCENARIO_A_BARRIER_MULTIPLIER
        else:
            # Evolved market: elasticity depends on spaceport infrastructure
            elastic_multiplier = (
                config.SCENARIO_B_ELASTIC_MULTIPLIER if has_spaceport
                else config.SCENARIO_B_NO_SPACEPORT_MULTIPLIER
            )
            # Reusability Dividend: Reusable Stage 1 adds to elasticity (Salvatore: the
            # "Jet Age turning point" — repeated reuse enables the mass-market demand shift)
            if tech_unlocks and tech_unlocks.get("reusable_stage1", False):
                elastic_multiplier += config.REUSABLE_STAGE1_ELASTICITY_BOOST
            if ticket_price < comp_price_avg:
                drop_ratio = (comp_price_avg - ticket_price) / comp_price_avg
                raw *= 1.0 + drop_ratio * elastic_multiplier

        # Apply event demand multiplier (e.g. competitor accident shrinks market)
        raw *= event_demand_multiplier

        demand = max(0.0, raw * available_share)
        result[name] = demand
        total_demand += demand

    # Safety Track Record: consecutive safe missions build public trust → demand boost
    # (Salvatore: "sustained safety record transforms spaceflight from risky novelty to routine")
    if consecutive_safe_missions > 0:
        streak_bonus = min(
            config.SAFETY_STREAK_MAX_BONUS,
            consecutive_safe_missions * config.SAFETY_STREAK_DEMAND_BOOST,
        )
        for name in personas:
            result[name] *= (1.0 + streak_bonus)
        total_demand *= (1.0 + streak_bonus)

    result["total"] = total_demand
    result["potential"] = total_potential
    result["available_share"] = available_share
    result["competitor_avg_price"] = comp_price_avg
    result["competitor_avg_safety"] = comp_safety_avg
    result["competitors"] = competitors_raw
    return result


def calculate_demand(
    ticket_price: float,
    competitor_price: float,
    reputation: float,
    config: GlobalConfig,
) -> float:
    """Backward-compatible wrapper — returns only the total demand float."""
    result = calculate_demand_segmented(
        ticket_price=ticket_price,
        safety_invest=0.0,
        marketing_spend=0.0,
        reputation=reputation,
        market_scenario="A",
        config=config,
    )
    return result["total"]


def calculate_actual_sales(demand: float, capacity: int) -> int:
    """
    Calculate actual sales (capped by vehicle capacity).
    
    Args:
        demand: Calculated demand
        capacity: Maximum passenger capacity
        
    Returns:
        Actual number of tickets sold (integer)
    """
    return min(round(demand), capacity)


def calculate_costs(
    player_inputs: PlayerInputs,
    game_state: GameState,
    config: GlobalConfig,
    event_extra_regulatory: float = 0.0,
) -> dict:
    """
    Calculate all costs for a turn.
    
    Includes tech tree unlocks:
    - Reusable Stage 1 (10 tech points): Reduces launch cost by 20%
    - Green Hydrogen (20 tech points): Reduces CO2 by 50% (already handled in CO2 calc)
    
    Returns:
        Dictionary with fixed_costs, variable_costs, investments, total_costs
    """
    # Fixed costs
    fixed_costs = config.FIXED_COSTS
    
    # Variable costs (fuel and launch, reduced by green tech)
    green_reduction = 1.0 - (game_state.green_tech_level * config.GREEN_TECH_REDUCTION)
    base_variable = (config.FUEL_COST_PER_LAUNCH + config.LAUNCH_COST_BASE) * green_reduction
    
    # Apply tech tree unlocks
    tech_reduction = 1.0
    if game_state.tech_unlocks.get("reusable_stage1", False):
        tech_reduction *= 0.8  # 20% reduction from Reusable Stage 1
    if game_state.tech_unlocks.get("rapid_reusability", False):
        tech_reduction *= config.RAPID_REUSABILITY_COST_REDUCTION  # additional -50% (Antonio: LCC model)
    
    # Apply HR efficiency (better ops = lower costs)
    hr_reduction = 1.0 / game_state.hr_efficiency  # Higher efficiency = lower costs
    
    variable_costs = base_variable * tech_reduction * hr_reduction
    
    # Investments (including HR and regulatory, but NOT contingency)
    investments = (
        player_inputs.marketing_spend +
        player_inputs.safety_invest +
        player_inputs.green_invest +
        player_inputs.rd_invest +
        player_inputs.hr_invest +
        player_inputs.regulatory_invest +
        event_extra_regulatory
    )

    # Regulatory compliance check
    regulatory_penalty_rep = 0.0
    regulatory_vuln_penalty = 0.0
    if player_inputs.regulatory_invest == 0:
        regulatory_penalty_rep = config.REGULATORY_REP_PENALTY
        regulatory_vuln_penalty = config.REGULATORY_VULN_PENALTY
    elif player_inputs.regulatory_invest < config.REGULATORY_MIN_SPEND:
        regulatory_vuln_penalty = config.REGULATORY_VULN_PENALTY

    total_costs = fixed_costs + variable_costs + investments

    return {
        "fixed_costs": fixed_costs,
        "variable_costs": variable_costs,
        "investments": investments,
        "total_costs": total_costs,
        "regulatory_invest": player_inputs.regulatory_invest,
        "regulatory_penalty_rep": regulatory_penalty_rep,
        "regulatory_vuln_penalty": regulatory_vuln_penalty,
    }


def calculate_revenue(
    mission_type: str,
    actual_sales: int,
    ticket_price: float,
    config: GlobalConfig
) -> float:
    """
    Calculate revenue based on mission type.
    
    Args:
        mission_type: Type of mission (Short_Suborbital, Long_Orbital, Scientific)
        actual_sales: Number of passengers (or kg for Scientific)
        ticket_price: Price per ticket (or contract value for Scientific)
        config: Global configuration
        
    Returns:
        Total revenue
    """
    if mission_type in ["Short_Suborbital", "Long_Orbital"]:
        return actual_sales * ticket_price

    elif mission_type == "Scientific":
        return ticket_price  # Contract value is the revenue

    else:
        return actual_sales * ticket_price


def calculate_hr_efficiency(total_hr_invest: float, config: GlobalConfig) -> float:
    """
    Calculate staff efficiency based on HR investment.
    
    Formula: Staff_Efficiency = log(Total_HR_Invest)
    
    Args:
        total_hr_invest: Cumulative HR investment
        config: Global configuration
        
    Returns:
        Efficiency multiplier (1.0 = 100%)
    """
    if total_hr_invest <= 0:
        return config.HR_EFFICIENCY_BASE
    
    # Logarithmic scaling: log base 10, scaled appropriately
    # €1M = 1.0, €10M = 1.3, €100M = 1.6, etc.
    hr_millions = total_hr_invest / 1_000_000
    efficiency = 1.0 + (math.log10(max(1, hr_millions)) * 0.3)
    
    # Cap at 200% efficiency
    return min(2.0, efficiency)


def calculate_available_slots(config: GlobalConfig, market_scenario: str = "A") -> int:
    """
    Calculate available launch slots this turn (competitor saturation + cadence).

    Helia: Scenario A has low operational cadence — regulatory bottlenecks and long
    turnaround times restrict launch windows to 1–2 per turn. Scenario B unlocks higher
    cadence as infrastructure and reusability mature.

    Returns:
        Number of available launch slots (0 to cap)
    """
    max_slots = (
        config.SCENARIO_A_AVAILABLE_SLOTS if market_scenario == "A"
        else config.BASE_AVAILABLE_SLOTS
    )
    return random.randint(0, max_slots)


def check_slot_constraint(
    vehicles_owned: int,
    available_slots: int,
    missions_planned: int,
    config: GlobalConfig
) -> dict:
    """
    Check if slot constraint affects mission execution.
    
    Args:
        vehicles_owned: Number of vehicles available
        available_slots: Available launch slots this turn
        missions_planned: Number of missions planned (default 1)
        
    Returns:
        Dictionary with slot_available, needs_rush, needs_cancellation
    """
    # Can only launch as many missions as vehicles owned
    max_missions = vehicles_owned
    
    # Check slot availability
    if available_slots >= missions_planned and missions_planned <= max_missions:
        return {
            "slot_available": True,
            "needs_rush": False,
            "needs_cancellation": False,
            "rush_cost": 0.0,
            "cancellation_cost": 0.0
        }
    
    # Need to rush or cancel
    if available_slots < missions_planned:
        if missions_planned <= max_missions:
            # Can rush the launch
            return {
                "slot_available": False,
                "needs_rush": True,
                "needs_cancellation": False,
                "rush_cost": config.SLOT_PREMIUM_COST,
                "cancellation_cost": 0.0
            }
        else:
            # Must cancel excess missions
            excess = missions_planned - max_missions
            return {
                "slot_available": False,
                "needs_rush": False,
                "needs_cancellation": True,
                "rush_cost": 0.0,
                "cancellation_cost": config.CANCELLATION_FEE * excess
            }
    
    # Vehicle constraint
    if missions_planned > max_missions:
        excess = missions_planned - max_missions
        return {
            "slot_available": False,
            "needs_rush": False,
            "needs_cancellation": True,
            "rush_cost": 0.0,
            "cancellation_cost": config.CANCELLATION_FEE * excess
        }
    
    return {
        "slot_available": True,
        "needs_rush": False,
        "needs_cancellation": False,
        "rush_cost": 0.0,
        "cancellation_cost": 0.0
    }


def calculate_failure_penalty(
    mission_type: str,
    contingency_budget: float,
    config: GlobalConfig,
    event_penalty_multiplier: float = 1.0,
) -> dict:
    """
    Calculate financial penalty for mission failure with contingency mitigation.
    
    Formula: Actual_Loss = max(0, Penalty_Cost - Contingency_Budget)
    
    Args:
        mission_type: Type of mission that failed
        contingency_budget: Contingency reserve for this turn
        config: Global configuration
        
    Returns:
        Dictionary with penalty_cost, contingency_used, actual_loss
    """
    # Base penalty
    penalty_cost = config.FAILURE_PENALTY_BASE
    
    # Adjust based on mission type risk (higher risk = higher penalty)
    if mission_type == "Short_Suborbital":
        risk_multiplier = 0.5  # Lower risk = lower penalty
    elif mission_type == "Long_Orbital":
        risk_multiplier = 1.0
    elif mission_type == "Scientific":
        risk_multiplier = config.FAILURE_PENALTY_MULTIPLIER  # Higher risk = higher penalty
    else:
        risk_multiplier = 1.0
    
    penalty_cost *= risk_multiplier
    penalty_cost *= event_penalty_multiplier  # insurance spike, etc.

    # Contingency mitigation
    contingency_used = min(penalty_cost, contingency_budget)
    actual_loss = max(0.0, penalty_cost - contingency_budget)
    
    return {
        "penalty_cost": penalty_cost,
        "contingency_used": contingency_used,
        "actual_loss": actual_loss
    }


def check_mission_failure(
    mission_type: str,
    safety_invest: float,
    safety_tech_level: int,
    hr_efficiency: float,
    config: GlobalConfig
) -> tuple[bool, str]:
    """
    Determine if mission fails based on mission type, safety, and HR.
    
    Args:
        mission_type: Type of mission
        safety_invest: Amount invested in safety this turn
        safety_tech_level: Current safety tech level
        hr_efficiency: Staff efficiency multiplier
        config: Global configuration
        
    Returns:
        Tuple of (mission_failed: bool, failure_reason: str)
    """
    # Get base risk for mission type
    if mission_type == "Short_Suborbital":
        base_risk = config.SHORT_SUBORBITAL_RISK
    elif mission_type == "Long_Orbital":
        base_risk = config.LONG_ORBITAL_RISK
        # Check if safety tech requirement is met
        if safety_tech_level < config.LONG_ORBITAL_SAFETY_REQ:
            return True, "Insufficient safety technology for Long Orbital missions"
    elif mission_type == "Scientific":
        base_risk = config.SCIENTIFIC_RISK
    else:
        base_risk = config.BASE_RISK
    
    # Calculate failure probability
    safety_millions = safety_invest / 1_000_000
    failure_prob = base_risk - (safety_millions * config.SAFETY_EFFICIENCY)
    failure_prob = max(0.0, min(1.0, failure_prob))
    
    # Roll the dice
    roll = random.random()
    mission_failed = roll < failure_prob
    logger.info(
        "  FAILURE ROLL — base_risk=%.3f | safety=€%.1fM | prob=%.3f | roll=%.3f → %s",
        base_risk,
        safety_invest / 1e6,
        failure_prob,
        roll,
        "FAILED" if mission_failed else "SAFE",
    )

    # HR "Saving Throw" - high HR can save a failed mission
    if mission_failed and hr_efficiency > 1.5:
        saving_throw_roll = random.random()
        if saving_throw_roll < config.HR_SAVING_THROW_CHANCE:
            logger.info("  HR SAVING THROW — roll=%.3f < %.3f → mission saved!",
                        saving_throw_roll, config.HR_SAVING_THROW_CHANCE)
            return False, "Crew solved the issue manually"

    if mission_failed:
        return True, "Mission failure"

    return False, "Mission successful"


def update_state_after_turn(
    game_state: GameState,
    player_inputs: PlayerInputs,
    actual_sales: int,
    revenue: float,
    costs: dict,
    mission_success: bool,
    config: GlobalConfig,
    failure_penalty: dict = None,
    potential_demand: float = 0.0,
    shadow_profit: float = None,
    regulatory_vuln_delta: float = 0.0,
) -> GameState:
    """
    Update game state after a turn is resolved.
    
    Args:
        game_state: Current game state
        player_inputs: Player's inputs for the turn
        actual_sales: Number of tickets sold
        revenue: Total revenue
        costs: Cost breakdown dictionary
        mission_success: Whether mission succeeded
        config: Global configuration
        failure_penalty: Failure penalty dict (if mission failed)
        
    Returns:
        Updated game state
    """
    # Calculate profit
    if mission_success:
        profit = revenue - costs["total_costs"]
    else:
        # On failure: no revenue, but still pay costs
        # Plus failure penalty (mitigated by contingency)
        penalty_loss = failure_penalty["actual_loss"] if failure_penalty else 0.0
        profit = -costs["total_costs"] - penalty_loss
    
    # Update budget (contingency is already reserved, so it's not spent unless used)
    game_state.budget += profit
    # Contingency budget is returned if not used, or deducted if used
    if failure_penalty:
        game_state.budget -= failure_penalty["contingency_used"]
    else:
        # Contingency not used, return it to budget
        game_state.budget += player_inputs.contingency_budget
    
    # Update reputation
    if mission_success:
        game_state.reputation += config.REPUTATION_SUCCESS_BONUS
        marketing_millions = player_inputs.marketing_spend / 1_000_000
        game_state.reputation += marketing_millions * config.MARKETING_REPUTATION_BOOST
        # Long Orbital destination stay: Scenario B adds extra reputation (Salvatore: Axiom-style
        # destination travel increases perceived value beyond the flight itself)
        if player_inputs.mission_type == "Long_Orbital" and game_state.market_scenario == "B":
            game_state.reputation += config.LONG_ORBITAL_DESTINATION_REP_BONUS
    else:
        game_state.reputation -= config.REPUTATION_FAILURE_PENALTY

    # Regulatory compliance reputation hit
    if costs.get("regulatory_penalty_rep", 0) > 0:
        game_state.reputation -= costs["regulatory_penalty_rep"]

    # Track consecutive zero-regulatory turns
    if player_inputs.regulatory_invest == 0:
        game_state.consecutive_zero_regulatory += 1
    else:
        game_state.consecutive_zero_regulatory = 0

    # Clamp reputation between 0 and 100
    game_state.reputation = max(0.0, min(100.0, game_state.reputation))
    
    # Update HR investment and efficiency
    game_state.total_hr_invest += player_inputs.hr_invest
    game_state.hr_efficiency = calculate_hr_efficiency(game_state.total_hr_invest, config)
    
    # Update Safety Tech Level: Every €10M = +1 safety tech point
    safety_points = int(player_inputs.safety_invest / 10_000_000)
    game_state.safety_tech_level += safety_points
    
    # Update tech levels
    # R&D: Every €10M = +1 tech point
    rd_points = int(player_inputs.rd_invest / 10_000_000)
    
    # Scientific missions grant bonus R&D points on success
    if mission_success and player_inputs.mission_type == "Scientific":
        rd_points += int(config.SCIENTIFIC_RD_BONUS)
        # Spaceport infrastructure enhances research capabilities (Salvatore: functional
        # use of space — aviation analogue of addressing "practical transportation needs")
        if game_state.has_spaceport:
            rd_points += config.SPACEPORT_SCIENTIFIC_RD_BONUS
            # SPaaS: each successful Scientific mission with Spaceport adds a fractional
            # research contract generating stable ARR (Antonio: Fractional Ownership model)
            game_state.active_spaas_contracts = min(
                config.SPAAS_MAX_CONTRACTS,
                game_state.active_spaas_contracts + 1,
            )
    
    old_tech_level = game_state.tech_level
    game_state.tech_level += rd_points
    
    # Check for tech unlocks
    if old_tech_level < 10 <= game_state.tech_level:
        game_state.tech_unlocks["reusable_stage1"] = True
    if old_tech_level < 20 <= game_state.tech_level:
        game_state.tech_unlocks["green_hydrogen"] = True
    if old_tech_level < 25 <= game_state.tech_level:
        game_state.tech_unlocks["autonomous_systems"] = True
    if old_tech_level < 30 <= game_state.tech_level:
        game_state.tech_unlocks["rapid_reusability"] = True
    
    # Green investment: Every €10M = +1 green tech point
    green_points = int(player_inputs.green_invest / 10_000_000)
    game_state.green_tech_level += green_points
    
    # Update investor interest (from marketing)
    marketing_millions = player_inputs.marketing_spend / 1_000_000
    game_state.investor_interest += marketing_millions * 2.0  # 2% per €1M
    game_state.investor_interest = min(100.0, game_state.investor_interest)
    
    # Check for investor funding
    if (not game_state.investor_funded and 
        game_state.investor_interest >= config.INVESTOR_INTEREST_THRESHOLD and
        game_state.reputation >= config.INVESTOR_REPUTATION_REQ):
        game_state.budget += config.INVESTOR_FUNDING_AMOUNT
        game_state.investor_funded = True
        # Set ROI target: 20% higher profit expectations
        # Calculate based on average profit per year so far
        if len(game_state.cash_flow_history) > 0:
            avg_profit = sum(game_state.cash_flow_history) / len(game_state.cash_flow_history)
            game_state.investor_roi_target = avg_profit * config.INVESTOR_ROI_TARGET_MULTIPLIER
        else:
            game_state.investor_roi_target = 50_000_000  # Default target
    
    # Track cash flow for NPV calculation
    game_state.cash_flow_history.append(profit)

    # ── New strategic KPI tracking ────────────────────────────────────────────
    if mission_success:
        game_state.total_passengers += actual_sales
        game_state.consecutive_safe_missions += 1
    else:
        game_state.safety_incidents += 1
        game_state.consecutive_safe_missions = 0
    game_state.total_marketing_spend += player_inputs.marketing_spend
    game_state.cumulative_potential_demand += potential_demand

    # Shadow history: profit under the other scenario (for comparison overlay)
    if shadow_profit is not None:
        game_state.shadow_cash_flow_history.append(shadow_profit)
    else:
        game_state.shadow_cash_flow_history.append(profit)  # fallback: mirror real
    
    # Track total investment for ROI
    game_state.total_investment += (
        player_inputs.marketing_spend +
        player_inputs.safety_invest +
        player_inputs.green_invest +
        player_inputs.rd_invest +
        player_inputs.hr_invest
    )
    
    # Update CO2 impact
    if mission_success:
        green_reduction = 1.0 - (game_state.green_tech_level * config.GREEN_TECH_CO2_REDUCTION)
        # Apply Green Hydrogen unlock (50% additional reduction)
        if game_state.tech_unlocks.get("green_hydrogen", False):
            green_reduction *= 0.5  # 50% reduction from Green Hydrogen
        co2_this_turn = config.CO2_BASE_IMPACT * green_reduction
        game_state.co2_impact += co2_this_turn
    
    # Fleet Management: Vehicles ready this turn become available (process first)
    if game_state.vehicles_ready_next_turn > 0:
        game_state.vehicles_owned += game_state.vehicles_ready_next_turn
        game_state.vehicles_ready_next_turn = 0
    
    # Fleet Management: Move building vehicles to ready for next turn
    if game_state.vehicles_building > 0:
        game_state.vehicles_ready_next_turn = game_state.vehicles_building
        game_state.vehicles_building = 0
    
    # Fleet Management: Handle new vehicle purchases (will be ready in 1 turn)
    if player_inputs.buy_vehicle:
        if game_state.budget >= config.VEHICLE_COST:
            game_state.budget -= config.VEHICLE_COST
            game_state.vehicles_building += 1

    # Spaceport: complete construction (ordered last turn → ready this turn)
    if game_state.spaceport_building:
        game_state.has_spaceport = True
        game_state.spaceport_building = False

    # Spaceport: handle new purchase order
    if player_inputs.buy_spaceport and not game_state.has_spaceport and not game_state.spaceport_building:
        if game_state.budget >= config.SPACEPORT_COST:
            game_state.budget -= config.SPACEPORT_COST
            game_state.spaceport_building = True

    # Market Saturation: Calculate available slots for next turn
    # Helia: Scenario A cadence capped at SCENARIO_A_AVAILABLE_SLOTS (low operational frequency)
    game_state.available_slots = calculate_available_slots(config, game_state.market_scenario)
    
    # Update turn number
    game_state.turn_number += 1
    
    # Update competitor price (random variation with trend)
    # Competitors may lower prices to compete
    variation = random.uniform(0.85, 1.05)  # Can drop up to 15% or rise 5%
    game_state.competitor_price *= variation
    # Ensure competitor price stays within reasonable bounds
    game_state.competitor_price = max(5_000_000, min(20_000_000, game_state.competitor_price))
    
    return game_state
