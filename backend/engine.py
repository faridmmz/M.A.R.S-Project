"""
Core game engine logic for M.A.R.S. Project
"""

import random
import math
from models import GlobalConfig, GameState, PlayerInputs


def calculate_demand(
    ticket_price: float,
    competitor_price: float,
    reputation: float,
    config: GlobalConfig
) -> float:
    """
    Calculate demand based on price, competitor price, and reputation.
    
    Formula: Demand = Base_Demand * (Competitor_Price / Your_Price)^Elasticity * (Reputation / 100)
    
    Enhanced: If competitor price is lower, demand drops significantly.
    
    Args:
        ticket_price: Player's ticket price
        competitor_price: Competitor's ticket price
        reputation: Current reputation (0-100)
        config: Global configuration
        
    Returns:
        Calculated demand (number of potential customers)
    """
    if ticket_price <= 0:
        return 0.0
    
    price_ratio = competitor_price / ticket_price
    price_factor = price_ratio ** config.PRICE_ELASTICITY
    reputation_factor = reputation / 100.0
    
    # Enhanced competitor logic: If competitor is cheaper, demand drops more
    if competitor_price < ticket_price:
        # Additional penalty when competitor is cheaper
        price_penalty = (ticket_price / competitor_price - 1) * 0.5  # Up to 50% reduction
        price_factor *= (1.0 - min(price_penalty, 0.5))
    
    demand = config.BASE_DEMAND * price_factor * reputation_factor
    
    return max(0.0, demand)


def calculate_actual_sales(demand: float, capacity: int) -> int:
    """
    Calculate actual sales (capped by vehicle capacity).
    
    Args:
        demand: Calculated demand
        capacity: Maximum passenger capacity
        
    Returns:
        Actual number of tickets sold (integer)
    """
    return min(int(demand), capacity)


def calculate_costs(
    player_inputs: PlayerInputs,
    game_state: GameState,
    config: GlobalConfig
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
    
    # Apply HR efficiency (better ops = lower costs)
    hr_reduction = 1.0 / game_state.hr_efficiency  # Higher efficiency = lower costs
    
    variable_costs = base_variable * tech_reduction * hr_reduction
    
    # Investments (including HR, but NOT contingency - that's reserved cash)
    investments = (
        player_inputs.marketing_spend +
        player_inputs.safety_invest +
        player_inputs.green_invest +
        player_inputs.rd_invest +
        player_inputs.hr_invest
    )
    
    total_costs = fixed_costs + variable_costs + investments
    
    return {
        "fixed_costs": fixed_costs,
        "variable_costs": variable_costs,
        "investments": investments,
        "total_costs": total_costs
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
    if mission_type == "Short_Suborbital":
        # Revenue per passenger: €200k-400k
        revenue_per_pax = random.uniform(
            config.SHORT_SUBORBITAL_REVENUE_MIN,
            config.SHORT_SUBORBITAL_REVENUE_MAX
        )
        return actual_sales * revenue_per_pax
    
    elif mission_type == "Long_Orbital":
        # Revenue per passenger: €5M-10M
        revenue_per_pax = random.uniform(
            config.LONG_ORBITAL_REVENUE_MIN,
            config.LONG_ORBITAL_REVENUE_MAX
        )
        return actual_sales * revenue_per_pax
    
    elif mission_type == "Scientific":
        # Fixed contract: €50k per kg payload
        # ticket_price represents contract value, actual_sales represents kg
        return ticket_price  # Contract value is the revenue
    
    else:
        # Fallback to old system
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


def calculate_available_slots(config: GlobalConfig) -> int:
    """
    Calculate available launch slots this turn (competitor saturation).
    
    Args:
        config: Global configuration
        
    Returns:
        Number of available launch slots (0 to BASE_AVAILABLE_SLOTS)
    """
    # Random variation: 0 to BASE_AVAILABLE_SLOTS
    # Lower slots = more competitor activity
    slots = random.randint(0, config.BASE_AVAILABLE_SLOTS)
    return slots


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
    config: GlobalConfig
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
    
    # HR "Saving Throw" - high HR can save a failed mission
    if mission_failed and hr_efficiency > 1.5:
        saving_throw_roll = random.random()
        if saving_throw_roll < config.HR_SAVING_THROW_CHANCE:
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
    failure_penalty: dict = None
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
        # Marketing boost
        marketing_millions = player_inputs.marketing_spend / 1_000_000
        game_state.reputation += marketing_millions * config.MARKETING_REPUTATION_BOOST
    else:
        game_state.reputation -= config.REPUTATION_FAILURE_PENALTY
    
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
    
    old_tech_level = game_state.tech_level
    game_state.tech_level += rd_points
    
    # Check for tech unlocks
    if old_tech_level < 10 <= game_state.tech_level:
        game_state.tech_unlocks["reusable_stage1"] = True
    if old_tech_level < 20 <= game_state.tech_level:
        game_state.tech_unlocks["green_hydrogen"] = True
    
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
    
    # Market Saturation: Calculate available slots for next turn
    game_state.available_slots = calculate_available_slots(config)
    
    # Update turn number
    game_state.turn_number += 1
    
    # Update competitor price (random variation with trend)
    # Competitors may lower prices to compete
    variation = random.uniform(0.85, 1.05)  # Can drop up to 15% or rise 5%
    game_state.competitor_price *= variation
    # Ensure competitor price stays within reasonable bounds
    game_state.competitor_price = max(5_000_000, min(20_000_000, game_state.competitor_price))
    
    return game_state
