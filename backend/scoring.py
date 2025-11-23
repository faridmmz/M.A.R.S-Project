"""
Scoring system for M.A.R.S. Project
Calculates final scores based on economic and environmental performance.
"""

from models import GameState, GlobalConfig
from typing import List, Dict, Tuple


def calculate_economic_score(
    final_budget: float,
    starting_budget: float,
    final_reputation: float,
    total_profit: float,
    years_played: int
) -> Tuple[float, str]:
    """
    Calculate economic score based on financial performance.
    
    Returns:
        Tuple of (score 0-100, letter grade)
    """
    # Budget growth (40% weight)
    budget_growth = ((final_budget - starting_budget) / starting_budget) * 100
    budget_score = min(100, max(0, 50 + budget_growth * 2))  # 0% growth = 50, 25% growth = 100
    
    # Reputation (30% weight)
    reputation_score = final_reputation
    
    # Profit per year (30% weight)
    avg_profit_per_year = total_profit / max(years_played, 1)
    profit_score = min(100, max(0, 50 + (avg_profit_per_year / 1_000_000) * 2))  # €50M/year = 100
    
    # Weighted average
    economic_score = (budget_score * 0.4) + (reputation_score * 0.3) + (profit_score * 0.3)
    
    # Convert to letter grade
    if economic_score >= 90:
        grade = "A+"
    elif economic_score >= 85:
        grade = "A"
    elif economic_score >= 80:
        grade = "A-"
    elif economic_score >= 75:
        grade = "B+"
    elif economic_score >= 70:
        grade = "B"
    elif economic_score >= 65:
        grade = "B-"
    elif economic_score >= 60:
        grade = "C+"
    elif economic_score >= 55:
        grade = "C"
    elif economic_score >= 50:
        grade = "C-"
    elif economic_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return round(economic_score, 1), grade


def calculate_green_score(
    total_co2: float,
    years_played: int,
    green_tech_level: int,
    green_hydrogen_unlocked: bool
) -> Tuple[float, str]:
    """
    Calculate green/environmental score.
    
    Returns:
        Tuple of (score 0-100, letter grade)
    """
    # CO2 per year (50% weight) - Lower is better
    co2_per_year = total_co2 / max(years_played, 1)
    # Target: 50 CO2/year = 100 points, 200 CO2/year = 0 points
    co2_score = max(0, min(100, 100 - ((co2_per_year - 50) / 1.5)))
    
    # Green tech level (30% weight)
    green_tech_score = min(100, green_tech_level * 10)  # 10 levels = 100
    
    # Tech unlocks (20% weight)
    unlock_score = 0
    if green_hydrogen_unlocked:
        unlock_score = 100
    elif green_tech_level >= 5:
        unlock_score = 50
    
    # Weighted average
    green_score = (co2_score * 0.5) + (green_tech_score * 0.3) + (unlock_score * 0.2)
    
    # Convert to letter grade
    if green_score >= 90:
        grade = "A+"
    elif green_score >= 85:
        grade = "A"
    elif green_score >= 80:
        grade = "A-"
    elif green_score >= 75:
        grade = "B+"
    elif green_score >= 70:
        grade = "B"
    elif green_score >= 65:
        grade = "B-"
    elif green_score >= 60:
        grade = "C+"
    elif green_score >= 55:
        grade = "C"
    elif green_score >= 50:
        grade = "C-"
    elif green_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return round(green_score, 1), grade


def calculate_final_score(
    economic_score: float,
    green_score: float,
    economic_weight: float = 0.6,
    green_weight: float = 0.4
) -> Tuple[float, str]:
    """
    Calculate overall final score.
    
    Args:
        economic_score: Economic performance score (0-100)
        green_score: Environmental performance score (0-100)
        economic_weight: Weight for economic score (default 60%)
        green_weight: Weight for green score (default 40%)
    
    Returns:
        Tuple of (final score 0-100, letter grade)
    """
    final_score = (economic_score * economic_weight) + (green_score * green_weight)
    
    # Convert to letter grade
    if final_score >= 90:
        grade = "A+"
    elif final_score >= 85:
        grade = "A"
    elif final_score >= 80:
        grade = "A-"
    elif final_score >= 75:
        grade = "B+"
    elif final_score >= 70:
        grade = "B"
    elif final_score >= 65:
        grade = "B-"
    elif final_score >= 60:
        grade = "C+"
    elif final_score >= 55:
        grade = "C"
    elif final_score >= 50:
        grade = "C-"
    elif final_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return round(final_score, 1), grade


def calculate_game_results(
    game_state: GameState,
    starting_budget: float,
    profit_history: List[float],
    config: GlobalConfig
) -> Dict:
    """
    Calculate comprehensive game results and scores.
    
    Args:
        game_state: Final game state
        starting_budget: Starting budget
        profit_history: List of profits for each turn
        config: Global configuration
    
    Returns:
        Dictionary with all scores and breakdowns
    """
    years_played = game_state.turn_number - 1
    total_profit = sum(profit_history)
    
    # Calculate scores
    economic_score, economic_grade = calculate_economic_score(
        game_state.budget,
        starting_budget,
        game_state.reputation,
        total_profit,
        years_played
    )
    
    green_score, green_grade = calculate_green_score(
        game_state.co2_impact,
        years_played,
        game_state.green_tech_level,
        game_state.tech_unlocks.get("green_hydrogen", False)
    )
    
    final_score, final_grade = calculate_final_score(economic_score, green_score)
    
    return {
        "years_played": years_played,
        "final_budget": game_state.budget,
        "starting_budget": starting_budget,
        "budget_change": game_state.budget - starting_budget,
        "budget_change_pct": ((game_state.budget - starting_budget) / starting_budget) * 100,
        "final_reputation": game_state.reputation,
        "total_profit": total_profit,
        "avg_profit_per_year": total_profit / max(years_played, 1),
        "total_co2": game_state.co2_impact,
        "co2_per_year": game_state.co2_impact / max(years_played, 1),
        "tech_level": game_state.tech_level,
        "green_tech_level": game_state.green_tech_level,
        "tech_unlocks": game_state.tech_unlocks,
        "economic_score": economic_score,
        "economic_grade": economic_grade,
        "green_score": green_score,
        "green_grade": green_grade,
        "final_score": final_score,
        "final_grade": final_grade
    }

