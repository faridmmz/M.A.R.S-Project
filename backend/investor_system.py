"""
Investor Attraction System with Randomized Investors
Each investor has a name, profession, and preferences that affect acceptance chance
"""

import random
from typing import Dict, List, Literal
from models import GlobalConfig, GameState


# Investor pool with names, professions, and preferences
INVESTOR_POOL = [
    # Safety-focused investors
    {"name": "Dr. Sarah Chen", "profession": "Emergency Medicine Physician", "preference": "safety", "icon": "👩‍⚕️"},
    {"name": "Dr. James Mitchell", "profession": "Aerospace Safety Engineer", "preference": "safety", "icon": "👨‍🔬"},
    {"name": "Dr. Maria Rodriguez", "profession": "Aviation Safety Inspector", "preference": "safety", "icon": "👩‍⚕️"},
    
    # Environmental investors
    {"name": "Elena Green", "profession": "Environmental Activist", "preference": "co2", "icon": "🌱"},
    {"name": "David Forest", "profession": "Climate Scientist", "preference": "co2", "icon": "🌍"},
    {"name": "Sophie Earth", "profession": "Sustainability Consultant", "preference": "co2", "icon": "🌿"},
    
    # Technology investors
    {"name": "Alex Tech", "profession": "Tech Entrepreneur", "preference": "tech", "icon": "💻"},
    {"name": "Jordan Innovation", "profession": "R&D Director", "preference": "tech", "icon": "🚀"},
    {"name": "Sam Code", "profession": "Software Billionaire", "preference": "tech", "icon": "💡"},
    
    # Reputation/Financial investors
    {"name": "Robert Wealth", "profession": "Investment Banker", "preference": "reputation", "icon": "💰"},
    {"name": "Victoria Capital", "profession": "Venture Capitalist", "preference": "reputation", "icon": "💼"},
    {"name": "Michael Finance", "profession": "Hedge Fund Manager", "preference": "reputation", "icon": "📊"},
    
    # Balanced investors (care about multiple things)
    {"name": "Lisa Balanced", "profession": "Impact Investor", "preference": "balanced", "icon": "⚖️"},
    {"name": "Chris Future", "profession": "Futurist", "preference": "balanced", "icon": "🔮"},
]


def select_random_investor() -> Dict:
    """Select a random investor from the pool."""
    return random.choice(INVESTOR_POOL)


def calculate_investor_offer_chance(
    offer_amount: float,
    game_state: GameState,
    config: GlobalConfig,
    investor: Dict
) -> tuple[float, str]:
    """
    Calculate the chance of an investor accepting an offer based on their preferences.
    
    Args:
        offer_amount: Amount being offered (€)
        game_state: Current game state
        config: Global configuration
        investor: Investor dictionary with name, profession, preference
        
    Returns:
        Tuple of (acceptance chance 0.0-1.0, explanation string)
    """
    if offer_amount < config.INVESTOR_OFFER_MIN_AMOUNT:
        return (0.0, "Offer too low")
    
    if offer_amount > config.INVESTOR_OFFER_MAX_AMOUNT:
        return (0.0, "Offer too high")
    
    # Base chance: 20% (increased from 10%)
    base_chance = 0.20
    
    # Penalty: Higher offer = lower chance (0.005% per €1M, reduced penalty)
    offer_millions = offer_amount / 1_000_000
    penalty = offer_millions * 0.00005  # Much smaller penalty
    base_chance -= penalty
    
    # Investor preference bonuses
    preference_bonus = 0.0
    preference_explanation = ""
    
    preference = investor.get("preference", "balanced")
    
    if preference == "safety":
        # Safety-focused: bonus based on safety tech level (up to +30%)
        safety_bonus = min(0.30, game_state.safety_tech_level * 0.03)
        preference_bonus = safety_bonus
        preference_explanation = f"Safety Tech Lvl {game_state.safety_tech_level}: +{safety_bonus*100:.1f}%"
        
    elif preference == "co2":
        # Environmental: bonus based on CO2 reduction (lower CO2 = higher bonus, up to +30%)
        # CO2 impact is typically 50-100, so we invert it
        co2_reduction = max(0, 100 - game_state.co2_impact)  # 0-50 range
        co2_bonus = min(0.30, (co2_reduction / 100) * 0.60)  # Up to 30% bonus
        preference_bonus = co2_bonus
        preference_explanation = f"CO2 Impact {game_state.co2_impact:.1f}%: +{co2_bonus*100:.1f}%"
        
    elif preference == "tech":
        # Tech-focused: bonus based on tech level (up to +30%)
        tech_bonus = min(0.30, game_state.tech_level * 0.015)
        preference_bonus = tech_bonus
        preference_explanation = f"Tech Lvl {game_state.tech_level}: +{tech_bonus*100:.1f}%"
        
    elif preference == "reputation":
        # Reputation-focused: bonus based on reputation (up to +40%)
        rep_bonus = min(0.40, game_state.reputation * 0.004)
        preference_bonus = rep_bonus
        preference_explanation = f"Reputation {game_state.reputation:.1f}: +{rep_bonus*100:.1f}%"
        
    else:  # balanced
        # Balanced: small bonuses from multiple factors (up to +25%)
        safety_bonus = min(0.10, game_state.safety_tech_level * 0.01)
        co2_reduction = max(0, 100 - game_state.co2_impact)
        co2_bonus = min(0.10, (co2_reduction / 100) * 0.20)
        tech_bonus = min(0.05, game_state.tech_level * 0.005)
        rep_bonus = min(0.10, game_state.reputation * 0.001)
        preference_bonus = safety_bonus + co2_bonus + tech_bonus + rep_bonus
        preference_explanation = f"Balanced: +{preference_bonus*100:.1f}%"
    
    # Reputation always helps (but less than preference-specific bonuses)
    reputation_bonus = game_state.reputation * 0.002  # 0.2% per reputation point
    
    # Calculate final chance
    final_chance = base_chance + preference_bonus + reputation_bonus
    
    # Clamp between 5% and 95% (never 0% or 100% guaranteed)
    final_chance = max(0.05, min(0.95, final_chance))
    
    explanation = f"Base {base_chance*100:.1f}% - Offer penalty {penalty*100:.1f}% + {preference_explanation} + Reputation {reputation_bonus*100:.1f}%"
    
    return (final_chance, explanation)


def process_investor_offer(
    offer_amount: float,
    game_state: GameState,
    config: GlobalConfig
) -> dict:
    """
    Process an investor offer and determine if it's accepted.
    Randomly selects an investor and calculates chance based on their preferences.
    
    Args:
        offer_amount: Amount being offered
        game_state: Current game state
        config: Global configuration
        
    Returns:
        Dictionary with accepted (bool), amount (float), message (str), investor info
    """
    if offer_amount < config.INVESTOR_OFFER_MIN_AMOUNT:
        return {
            "accepted": False,
            "amount": 0.0,
            "message": f"Offer too low. Minimum: €{config.INVESTOR_OFFER_MIN_AMOUNT/1_000_000:.0f}M",
            "investor": None
        }
    
    if offer_amount > config.INVESTOR_OFFER_MAX_AMOUNT:
        return {
            "accepted": False,
            "amount": 0.0,
            "message": f"Offer too high. Maximum: €{config.INVESTOR_OFFER_MAX_AMOUNT/1_000_000:.0f}M",
            "investor": None
        }
    
    # Select a random investor
    investor = select_random_investor()
    
    # Calculate acceptance chance based on investor preferences
    chance, explanation = calculate_investor_offer_chance(offer_amount, game_state, config, investor)
    
    # Roll the dice
    roll = random.random()
    accepted = roll < chance
    
    if accepted:
        # Investor accepts! Add funding to budget
        game_state.budget += offer_amount
        
        # Increase reputation for successful investment (positive signal to market)
        reputation_bonus = min(5.0, offer_amount / 10_000_000)  # Up to +5 rep, scales with offer amount
        game_state.reputation += reputation_bonus
        game_state.reputation = min(100.0, game_state.reputation)  # Clamp to 100
        
        # Track the offer
        if not hasattr(game_state, 'active_investor_offers') or game_state.active_investor_offers is None:
            game_state.active_investor_offers = []
        
        game_state.active_investor_offers.append({
            "amount": offer_amount,
            "turn": game_state.turn_number,
            "accepted": True,
            "investor_name": investor["name"],
            "investor_profession": investor["profession"]
        })
        
        # Set ROI target (investors expect returns)
        if len(game_state.cash_flow_history) > 0:
            avg_profit = sum(game_state.cash_flow_history) / len(game_state.cash_flow_history)
            game_state.investor_roi_target = max(game_state.investor_roi_target, avg_profit * 1.15)
        else:
            game_state.investor_roi_target = max(game_state.investor_roi_target, offer_amount * 0.1)
        
        return {
            "accepted": True,
            "amount": offer_amount,
            "chance": chance,
            "reputation_change": reputation_bonus,
            "message": f"{investor['icon']} {investor['name']} ({investor['profession']}) accepted! +€{offer_amount/1_000_000:.1f}M funding received. Reputation +{reputation_bonus:.1f}.",
            "investor": investor,
            "explanation": explanation
        }
    else:
        # Decrease reputation for rejected investment (negative signal)
        reputation_penalty = min(3.0, offer_amount / 20_000_000)  # Up to -3 rep, scales with offer amount
        game_state.reputation -= reputation_penalty
        game_state.reputation = max(0.0, game_state.reputation)  # Clamp to 0
        
        # Track the rejected offer
        if not hasattr(game_state, 'active_investor_offers') or game_state.active_investor_offers is None:
            game_state.active_investor_offers = []
        
        game_state.active_investor_offers.append({
            "amount": offer_amount,
            "turn": game_state.turn_number,
            "accepted": False,
            "investor_name": investor["name"],
            "investor_profession": investor["profession"]
        })
        
        return {
            "accepted": False,
            "amount": 0.0,
            "chance": chance,
            "reputation_change": -reputation_penalty,
            "message": f"{investor['icon']} {investor['name']} ({investor['profession']}) declined. Chance was {chance*100:.1f}%. Reputation -{reputation_penalty:.1f}.",
            "investor": investor,
            "explanation": explanation
        }


def get_investor_offer_chance_preview(
    offer_amount: float,
    game_state: GameState,
    config: GlobalConfig
) -> dict:
    """
    Get a preview of investor offer chances for different investor types.
    Used to show what chance different investors would have.
    
    Returns average chance and best/worst case scenarios.
    """
    if offer_amount < config.INVESTOR_OFFER_MIN_AMOUNT or offer_amount > config.INVESTOR_OFFER_MAX_AMOUNT:
        return {
            "average_chance": 0.0,
            "best_chance": 0.0,
            "worst_chance": 0.0,
            "best_investor": None,
            "worst_investor": None
        }
    
    chances = []
    for investor in INVESTOR_POOL:
        chance, _ = calculate_investor_offer_chance(offer_amount, game_state, config, investor)
        chances.append((chance, investor))
    
    chances.sort(key=lambda x: x[0], reverse=True)
    
    avg_chance = sum(c[0] for c in chances) / len(chances)
    best_chance, best_investor = chances[0]
    worst_chance, worst_investor = chances[-1]
    
    return {
        "average_chance": avg_chance,
        "best_chance": best_chance,
        "worst_chance": worst_chance,
        "best_investor": best_investor,
        "worst_investor": worst_investor
    }
