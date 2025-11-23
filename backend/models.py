"""
Data models for M.A.R.S. (Market Analysis & Risk Simulation) Project
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class GlobalConfig:
    """Constants for the game"""
    MAX_PAX: int = 7  # Maximum passenger capacity
    STARTING_BUDGET: float = 500_000_000  # €500M in euros
    COMPETITOR_PRICE: float = 10_000_000  # €10M default competitor price
    BASE_DEMAND: float = 10.0  # Base demand multiplier
    PRICE_ELASTICITY: float = 1.5  # Price elasticity factor
    BASE_RISK: float = 0.10  # 10% base failure probability
    SAFETY_EFFICIENCY: float = 0.001  # How much each € reduces risk (per million)
    FIXED_COSTS: float = 5_000_000  # Fixed costs per turn (maintenance, salaries)
    FUEL_COST_PER_LAUNCH: float = 15_000_000  # Base fuel cost
    LAUNCH_COST_BASE: float = 20_000_000  # Base launch cost
    GREEN_TECH_REDUCTION: float = 0.01  # Each green tech point reduces costs by 1%
    CO2_BASE_IMPACT: float = 100.0  # Base CO2 impact per launch
    GREEN_TECH_CO2_REDUCTION: float = 0.02  # Each green tech point reduces CO2 by 2%
    STARTING_REPUTATION: float = 50.0  # Starting reputation (0-100)
    REPUTATION_SUCCESS_BONUS: float = 2.0  # Reputation gain on success
    REPUTATION_FAILURE_PENALTY: float = 20.0  # Reputation loss on failure
    MARKETING_REPUTATION_BOOST: float = 0.1  # Reputation boost per €1M marketing
    MAX_YEARS: int = 10  # Game ends after this many years
    BANKRUPTCY_THRESHOLD: float = 0.0  # Game over if budget goes below this
    
    # Mission Type Configurations
    SHORT_SUBORBITAL_RISK: float = 0.05  # Low risk (5%)
    SHORT_SUBORBITAL_REVENUE_MIN: float = 200_000  # €200k per pax
    SHORT_SUBORBITAL_REVENUE_MAX: float = 400_000  # €400k per pax
    
    LONG_ORBITAL_RISK: float = 0.15  # Medium risk (15%)
    LONG_ORBITAL_REVENUE_MIN: float = 5_000_000  # €5M per pax
    LONG_ORBITAL_REVENUE_MAX: float = 10_000_000  # €10M per pax
    LONG_ORBITAL_SAFETY_REQ: int = 5  # Requires Safety tech level 5
    
    SCIENTIFIC_RISK: float = 0.25  # High risk (25%)
    SCIENTIFIC_REVENUE_PER_KG: float = 50_000  # €50k per kg payload
    SCIENTIFIC_RD_BONUS: float = 2.0  # Bonus R&D points on success
    
    # HR System
    HR_EFFICIENCY_BASE: float = 1.0
    HR_COST_REDUCTION_FACTOR: float = 0.01  # Each €1M HR = 1% cost reduction
    HR_SAVING_THROW_CHANCE: float = 0.3  # 30% chance to save mission with high HR
    
    # Fleet Management
    STARTING_VEHICLES: int = 1
    VEHICLE_COST: float = 150_000_000  # €150M per vehicle
    VEHICLE_BUILD_TIME: int = 1  # 1 turn to build
    
    # Market Saturation
    BASE_AVAILABLE_SLOTS: int = 3
    SLOT_PREMIUM_COST: float = 10_000_000  # €10M to rush launch
    CANCELLATION_FEE: float = 5_000_000  # €5M cancellation fee
    
    # Investor System
    INVESTOR_INTEREST_THRESHOLD: float = 100.0  # 100% interest bar
    INVESTOR_FUNDING_AMOUNT: float = 200_000_000  # €200M injection
    INVESTOR_REPUTATION_REQ: float = 70.0  # Requires 70 reputation
    INVESTOR_ROI_TARGET_MULTIPLIER: float = 1.2  # 20% higher profit target
    
    # Investor Offer System
    INVESTOR_OFFER_BASE_CHANCE: float = 0.1  # 10% base chance
    INVESTOR_OFFER_AMOUNT_PENALTY: float = 0.0001  # Penalty per €1M (higher offer = lower chance)
    INVESTOR_OFFER_REPUTATION_BONUS: float = 0.01  # Bonus per reputation point
    INVESTOR_OFFER_MIN_AMOUNT: float = 10_000_000  # Minimum offer (€10M)
    INVESTOR_OFFER_MAX_AMOUNT: float = 500_000_000  # Maximum offer (€500M)
    
    # Contingency System
    FAILURE_PENALTY_BASE: float = 50_000_000  # Base penalty for failures (€50M)
    FAILURE_PENALTY_MULTIPLIER: float = 1.5  # Multiplier based on mission type risk


@dataclass
class GameState:
    """Mutable game state"""
    budget: float
    reputation: float
    tech_level: int = 0
    green_tech_level: int = 0
    safety_tech_level: int = 0  # Safety tech level (from safety investments)
    turn_number: int = 1
    co2_impact: float = 0.0
    competitor_price: float = 10_000_000  # Dynamic competitor price
    tech_unlocks: dict = None  # Track unlocked technologies
    hr_efficiency: float = 1.0  # Staff efficiency (1.0 = 100%)
    total_hr_invest: float = 0.0  # Cumulative HR investment
    investor_interest: float = 0.0  # Investor interest bar (0-100%)
    investor_funded: bool = False  # Whether investor funding was received
    investor_roi_target: float = 0.0  # Target profit per year after investor funding
    active_investor_offers: list = None  # List of active investor offers made
    vehicles_owned: int = 1  # Number of vehicles in fleet
    vehicles_building: int = 0  # Vehicles currently being built
    vehicles_ready_next_turn: int = 0  # Vehicles ready next turn
    available_slots: int = 3  # Available launch slots this turn
    cash_flow_history: list = None  # History for NPV calculation
    total_investment: float = 0.0  # Total investments for ROI
    last_mission_type: str = "Short_Suborbital"  # Last mission type for news feed
    
    def __post_init__(self):
        if self.tech_unlocks is None:
            self.tech_unlocks = {
                "reusable_stage1": False,  # Unlocked at 10 tech points
                "green_hydrogen": False    # Unlocked at 20 tech points
            }
        # Initialize unlocks based on current tech level
        if self.tech_level >= 10:
            self.tech_unlocks["reusable_stage1"] = True
        if self.tech_level >= 20:
            self.tech_unlocks["green_hydrogen"] = True
        if self.cash_flow_history is None:
            self.cash_flow_history = []


@dataclass
class PlayerInputs:
    """Player choices for each turn"""
    mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"]
    ticket_price: float  # For Short/Long tourist missions, or contract value for Scientific
    marketing_spend: float
    safety_invest: float
    green_invest: float
    rd_invest: float
    hr_invest: float = 0.0  # HR & Training investment
    contingency_budget: float = 0.0  # Contingency reserve for this turn
    buy_vehicle: bool = False  # Whether to purchase a new vehicle this turn
    investor_offer: float = 0.0  # Amount to offer investors (€0 = no offer)

