"""
Financial metrics calculations for M.A.R.S. Project
"""

import math
from models import GameState, GlobalConfig


def calculate_npv(cash_flows: list[float], discount_rate: float = 0.05) -> float:
    """
    Calculate Net Present Value (NPV) of cash flows.
    
    Formula: NPV = Sum( CashFlow / (1 + r)^t )
    
    Args:
        cash_flows: List of cash flows (profits) over time
        discount_rate: Discount rate (default 5% = 0.05)
        
    Returns:
        NPV value
    """
    if not cash_flows:
        return 0.0
    
    npv = 0.0
    for t, cash_flow in enumerate(cash_flows, start=1):
        npv += cash_flow / ((1 + discount_rate) ** t)
    
    return npv


def calculate_roi(total_profit: float, total_investment: float) -> float:
    """
    Calculate Return on Investment (ROI).
    
    Formula: ROI = (Total Profit / Total Investment) * 100
    
    Args:
        total_profit: Cumulative profit
        total_investment: Total investment made
        
    Returns:
        ROI as a percentage
    """
    if total_investment == 0:
        return 0.0
    
    roi = (total_profit / total_investment) * 100
    return roi


def calculate_irr(cash_flows: list[float], initial_investment: float = 0.0, max_iterations: int = 100) -> float:
    """
    Calculate Internal Rate of Return (IRR) using Newton-Raphson method.
    
    IRR is the discount rate that makes NPV = 0.
    
    Args:
        cash_flows: List of cash flows (profits) over time
        initial_investment: Initial investment (negative cash flow at t=0)
        max_iterations: Maximum iterations for convergence
        
    Returns:
        IRR as a percentage (e.g., 0.15 = 15%)
    """
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
        
        # Prevent negative or extremely high rates
        rate = max(0.0, min(rate, 10.0))
    
    return rate * 100  # Return as percentage


def calculate_all_metrics(game_state: GameState, config: GlobalConfig) -> dict:
    """
    Calculate all financial metrics for the current game state.
    
    Args:
        game_state: Current game state
        config: Global configuration
        
    Returns:
        Dictionary with NPV, ROI, IRR, and other metrics
    """
    # Calculate NPV
    npv = calculate_npv(game_state.cash_flow_history, discount_rate=0.05)
    
    # Calculate ROI
    total_profit = sum(game_state.cash_flow_history) if game_state.cash_flow_history else 0.0
    roi = calculate_roi(total_profit, game_state.total_investment)
    
    # Calculate IRR
    initial_investment = config.STARTING_BUDGET  # Could be adjusted
    irr = calculate_irr(game_state.cash_flow_history, initial_investment)
    
    # Additional metrics
    total_revenue = sum([cf for cf in game_state.cash_flow_history if cf > 0])
    total_costs = abs(sum([cf for cf in game_state.cash_flow_history if cf < 0]))
    
    return {
        "npv": npv,
        "roi": roi,
        "irr": irr,
        "total_profit": total_profit,
        "total_investment": game_state.total_investment,
        "total_revenue": total_revenue,
        "total_costs": total_costs,
        "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0,
        "turns": len(game_state.cash_flow_history)
    }

