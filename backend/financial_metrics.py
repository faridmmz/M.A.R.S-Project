"""
Financial metrics calculations for M.A.R.S. Project
"""

import math
from models import GameState, GlobalConfig


def calculate_npv(cash_flows: list[float], discount_rate: float = 0.05) -> float:
    """NPV = Sum( CashFlow / (1 + r)^t )"""
    if not cash_flows:
        return 0.0
    
    npv = 0.0
    for t, cash_flow in enumerate(cash_flows, start=1):
        npv += cash_flow / ((1 + discount_rate) ** t)
    
    return npv


def calculate_roi(total_profit: float, total_investment: float) -> float:
    """ROI = (Total Profit / Total Investment) * 100"""
    if total_investment == 0:
        return 0.0
    
    roi = (total_profit / total_investment) * 100
    return roi


def calculate_irr(cash_flows: list[float], initial_investment: float = 0.0, max_iterations: int = 100) -> float:
    """Discount rate that makes NPV = 0, solved via Newton-Raphson."""
    if not cash_flows:
        return 0.0
    
    # Include initial investment as first cash flow (negative)
    all_cash_flows = [-initial_investment] + cash_flows
    
    # Initial guess
    rate = 0.1  # 10%
    
    for _ in range(max_iterations):
        npv = 0.0
        npv_derivative = 0.0
        
        for t, cash_flow in enumerate(all_cash_flows):
            if t == 0:
                npv += cash_flow
                npv_derivative += 0
            else:
                discount_factor = (1 + rate) ** t
                npv += cash_flow / discount_factor
                npv_derivative -= (t * cash_flow) / (discount_factor * (1 + rate))
        
        # Newton-Raphson: x_new = x_old - f(x) / f'(x)
        if abs(npv_derivative) < 1e-10:
            break
        
        new_rate = rate - npv / npv_derivative
        
        # Check for convergence
        if abs(new_rate - rate) < 1e-6:
            rate = new_rate
            break
        
        rate = new_rate
        
        # Allow negative IRR (losing investment) down to -99%; cap upside at 1000%
        rate = max(-0.99, min(rate, 10.0))
    
    return rate * 100  # Return as percentage


def calculate_market_penetration(total_passengers: int, cumulative_potential_demand: float) -> float:
    """
    Market Penetration %: passengers captured vs. total uncapped potential demand.
    Low in Scenario A (barriers kill conversion); high in Scenario B.
    """
    if cumulative_potential_demand <= 0:
        return 0.0
    return (total_passengers / cumulative_potential_demand) * 100.0


def calculate_cac(total_marketing_spend: float, total_passengers: int) -> float:
    """Customer Acquisition Cost: marketing spend per passenger carried."""
    if total_passengers <= 0:
        return 0.0
    return total_marketing_spend / total_passengers


def calculate_reputational_vulnerability(
    reputation: float,
    safety_incidents: int,
    consecutive_zero_regulatory: int = 0,
) -> float:
    """
    Reputational Vulnerability score (0-100).
    Combines low reputation, accumulated incident history, and regulatory neglect.
    High score means future demand is at structural risk.
    """
    base = (100.0 - reputation) / 100.0
    incident_impact = min(safety_incidents * 0.05, 0.50)
    regulatory_impact = min(consecutive_zero_regulatory * 0.05, 0.25)
    return round(min(100.0, (base + incident_impact + regulatory_impact) * 100.0), 1)


def calculate_all_metrics(game_state: GameState, config: GlobalConfig) -> dict:
    # Calculate NPV (discounted value of all operating cash flows at 5%)
    npv = calculate_npv(game_state.cash_flow_history, discount_rate=0.05)

    # Calculate ROI: return on strategic investment (marketing, safety, R&D, green, HR)
    total_profit = sum(game_state.cash_flow_history) if game_state.cash_flow_history else 0.0
    roi = calculate_roi(total_profit, game_state.total_investment)

    # Calculate IRR: discount rate that makes NPV of starting budget + operating CFs = 0
    irr = calculate_irr(game_state.cash_flow_history, config.STARTING_BUDGET)

    # Gross revenue and costs from tracked actuals (not approximated from profit signs)
    total_revenue = game_state.total_revenue_earned
    total_costs = max(0.0, total_revenue - total_profit)  # all money spent = revenue minus net profit
    
    # ── New strategic KPIs ────────────────────────────────────────────────────
    market_penetration = calculate_market_penetration(
        game_state.total_passengers,
        game_state.cumulative_potential_demand,
    )
    cac = calculate_cac(game_state.total_marketing_spend, game_state.total_passengers)
    rep_vulnerability = calculate_reputational_vulnerability(
        game_state.reputation,
        game_state.safety_incidents,
        game_state.consecutive_zero_regulatory,
    )

    return {
        "npv": npv,
        "roi": roi,
        "irr": irr,
        "total_profit": total_profit,
        "total_investment": game_state.total_investment,
        "total_revenue": total_revenue,
        "total_costs": total_costs,
        "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0,
        "turns": len(game_state.cash_flow_history),
        # Strategic KPIs
        "market_penetration_pct": market_penetration,
        "customer_acquisition_cost": cac,
        "reputational_vulnerability": rep_vulnerability,
        "total_passengers": game_state.total_passengers,
        "market_scenario": game_state.market_scenario,
    }

