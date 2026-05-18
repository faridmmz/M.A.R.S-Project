"""
Data models for M.A.R.S. (Market Analysis & Risk Simulation) Project
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class GlobalConfig:
    """Constants for the game"""
    MAX_PAX: int = 7  # Maximum passenger capacity
    STARTING_BUDGET: float = 1_500_000_000  # €1.5B in euros
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

    # ── Market Scenario System ────────────────────────────────────────────────
    # Scenario A (Current Market): high structural barriers cap demand hard
    SCENARIO_A_DEMAND_CAP_PER_PERSONA: float = 2.0   # raised cap lets rep/streak growth matter
    SCENARIO_A_BARRIER_MULTIPLIER: float = 0.30       # 70 % structural suppression
    # Scenario B (Evolved Market): price drops drive super-proportional growth
    SCENARIO_B_ELASTIC_MULTIPLIER: float = 5.5        # spaceport unlocks strong elasticity
    # Without a Dedicated Spaceport, Scenario B elasticity is capped
    SCENARIO_B_NO_SPACEPORT_MULTIPLIER: float = 1.2  # partial boost only

    # ── Helia's Market Stagnation Baseline: Scenario A Supply-Side Constraints ─
    # Three-pillar stagnation: extreme pricing, low cadence, high complexity
    # (Helia: "the issue is the structure of the offer, not the lack of demand")
    SCENARIO_A_SUBORBITAL_PRICE_FLOOR: float = 450_000   # Real market min €450k (Virgin/BO baseline)
    SCENARIO_A_ORBITAL_PRICE_FLOOR: float = 5_000_000    # Real market min €5M (ISS module pricing)
    SCENARIO_A_AVAILABLE_SLOTS: int = 2                  # Low cadence: max 1–2 launches/turn
    # Accessibility barrier: medical checks + weeks of training → marketing cannot overcome it
    # In Scenario A, marketing spend is only 50% as effective (interest ≠ conversion)
    SCENARIO_A_MARKETING_EFFICIENCY: float = 0.50

    # ── Regulatory Compliance ─────────────────────────────────────────────────
    REGULATORY_MIN_SPEND: float = 5_000_000          # €5M recommended minimum
    REGULATORY_VULN_PENALTY: float = 15.0             # vulnerability +15 if underspend
    REGULATORY_REP_PENALTY: float = 3.0               # reputation -3 if zero spend

    # ── Spaceport Infrastructure ──────────────────────────────────────────────
    SPACEPORT_COST: float = 300_000_000               # €300M one-time investment

    # ── Aviation Blueprint: Supply-Side Democratization (Salvatore's research) ─
    # Reusable Stage 1 in Scenario B adds to elasticity — the "Jet Age turning point"
    # where repeated reuse transforms market economics (airfare −50% → pax ×3 in 1960s−70s)
    REUSABLE_STAGE1_ELASTICITY_BOOST: float = 0.7    # 2.5 → 3.2 with Spaceport + Reusable

    # Consecutive safe missions build public trust, incrementally boosting demand
    # (models Salvatore's "standardised safety record → routine activity" progression)
    SAFETY_STREAK_DEMAND_BOOST: float = 0.05          # +5% demand per consecutive safe mission
    SAFETY_STREAK_MAX_BONUS: float = 0.15             # cap at 3 consecutive missions (+15%)

    # Long Orbital destination stay: in Scenario B, an Axiom-style station experience
    # raises perceived value beyond the flight itself → extra reputation on success
    LONG_ORBITAL_DESTINATION_REP_BONUS: float = 3.0

    # Spaceport infrastructure enhances research-mission capabilities → extra R&D point
    # (Salvatore: aviation addressed "practical transportation needs" through functional use)
    SPACEPORT_SCIENTIFIC_RD_BONUS: int = 1

    # ── Antonio's LCC Space Model: Three-Pillar Strategic Redesign ─────────────
    # 1. Rapid Reusability (unlock at 30 R&D pts) — LCC model: standardised fleet,
    #    65–90% marginal cost reduction, ancillary unbundled revenue stream
    RAPID_REUSABILITY_THRESHOLD: int = 30
    RAPID_REUSABILITY_COST_REDUCTION: float = 0.50   # additional -50% variable costs (on top of Stage 1 -20%)
    ANCILLARY_REVENUE_MULTIPLIER: float = 1.15        # +15% per-pax tourist revenue from add-on services

    # 2. Autonomous Systems (unlock at 25 R&D pts) — AI navigation removes the
    #    physiological/temporal training bottleneck; expands TAM to older and corporate demographics
    AUTONOMOUS_SYSTEMS_THRESHOLD: int = 25
    AUTONOMOUS_TAM_MULTIPLIER: float = 1.50           # +50% to all persona base pools
    INTERMODAL_FAILURE_REDUCTION: float = 0.50        # -50% Scientific failure penalty (plug-and-play modularity)

    # 3. SPaaS / Fractional Ownership — research institutions buy a share of a module
    #    rather than the full mission; generates stable Annual Recurring Revenue
    SPAAS_ARR_PER_CONTRACT: float = 5_000_000         # €5M ARR per active contract per turn
    SPAAS_MAX_CONTRACTS: int = 5                       # cap at 5 simultaneous fractional contracts

    # ── Customer Persona Weights ──────────────────────────────────────────────
    PERSONA_UHNW_PRICE_SENSITIVITY: float = 0.4   # wealthy tourists: price-insensitive
    PERSONA_UHNW_SAFETY_SENSITIVITY: float = 0.9
    PERSONA_UHNW_BASE_POOL: float = 5.0

    PERSONA_GOV_PRICE_SENSITIVITY: float = 0.2    # government: almost price-blind
    PERSONA_GOV_SAFETY_SENSITIVITY: float = 1.5   # but extremely safety-conscious
    PERSONA_GOV_BASE_POOL: float = 3.0

    PERSONA_RESEARCH_PRICE_SENSITIVITY: float = 0.8   # research/industrial: price-driven
    PERSONA_RESEARCH_SAFETY_SENSITIVITY: float = 0.6
    PERSONA_RESEARCH_BASE_POOL: float = 4.0

    # ── Orbital Competitors (Long Orbital missions) ───────────────────────────
    SPACEX_PRICE: float = 8_000_000
    SPACEX_SAFETY: float = 90.0
    SPACEX_MARKET_SHARE: float = 0.45

    BLUE_ORIGIN_PRICE: float = 12_000_000
    BLUE_ORIGIN_SAFETY: float = 75.0
    BLUE_ORIGIN_MARKET_SHARE: float = 0.25

    AXIOM_PRICE: float = 15_000_000
    AXIOM_SAFETY: float = 80.0
    AXIOM_MARKET_SHARE: float = 0.20

    # ── Suborbital Competitors (Short Suborbital missions) ────────────────────
    # Virgin Galactic SpaceShipTwo/III baseline — suspended commercial ops 2023
    VIRGIN_GALACTIC_PRICE: float = 450_000
    VIRGIN_GALACTIC_SAFETY: float = 65.0        # 2014 VSS Enterprise accident
    VIRGIN_GALACTIC_MARKET_SHARE: float = 0.25

    # Blue Origin New Shepard — 2022 anomaly, returned to flight 2024
    BLUE_ORIGIN_NEW_SHEPARD_PRICE: float = 500_000
    BLUE_ORIGIN_NEW_SHEPARD_SAFETY: float = 82.0
    BLUE_ORIGIN_NEW_SHEPARD_MARKET_SHARE: float = 0.35


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

    # ── Market-pivot additions ────────────────────────────────────────────────
    market_scenario: str = "A"                  # "A" = current barriers, "B" = evolved
    total_passengers: int = 0                   # Cumulative passengers carried (all turns)
    total_marketing_spend: float = 0.0          # Cumulative marketing spend (for CAC)
    safety_incidents: int = 0                   # Cumulative mission failures
    cumulative_potential_demand: float = 0.0    # Sum of uncapped potential demand (for penetration %)
    shadow_cash_flow_history: list = None       # What profits would have been in the other scenario

    # ── Spaceport & Regulatory ────────────────────────────────────────────────
    has_spaceport: bool = False                 # Dedicated commercial spaceport built
    spaceport_building: bool = False            # Spaceport ordered, under construction
    consecutive_zero_regulatory: int = 0        # Turns with zero regulatory spend

    # ── Aviation Blueprint: Safety Streak ────────────────────────────────────
    consecutive_safe_missions: int = 0          # Resets on failure; drives trust streak bonus

    # ── Antonio: LCC Space Model State ────────────────────────────────────────
    active_spaas_contracts: int = 0             # Fractional research contracts generating ARR each turn

    # ── Financial tracking ────────────────────────────────────────────────────
    total_revenue_earned: float = 0.0           # Cumulative gross revenue (mission + SPaaS + ancillary)

    # ── Event System ─────────────────────────────────────────────────────────
    active_event: dict = None                   # Currently active multi-turn event
    event_turns_remaining: int = 0              # Countdown for multi-turn events

    def __post_init__(self):
        if self.tech_unlocks is None:
            self.tech_unlocks = {}
        # Ensure all keys exist (setdefault is backward-compatible with old saved states)
        self.tech_unlocks.setdefault("reusable_stage1", False)    # 10 pts
        self.tech_unlocks.setdefault("green_hydrogen", False)     # 20 pts
        self.tech_unlocks.setdefault("autonomous_systems", False) # 25 pts (Antonio)
        self.tech_unlocks.setdefault("rapid_reusability", False)  # 30 pts (Antonio)
        # Initialize unlocks based on current tech level
        if self.tech_level >= 10:
            self.tech_unlocks["reusable_stage1"] = True
        if self.tech_level >= 20:
            self.tech_unlocks["green_hydrogen"] = True
        if self.tech_level >= 25:
            self.tech_unlocks["autonomous_systems"] = True
        if self.tech_level >= 30:
            self.tech_unlocks["rapid_reusability"] = True
        if self.cash_flow_history is None:
            self.cash_flow_history = []
        if self.shadow_cash_flow_history is None:
            self.shadow_cash_flow_history = []
        if self.active_investor_offers is None:
            self.active_investor_offers = []
        if self.active_event is None:
            self.active_event = {}


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
    regulatory_invest: float = 0.0  # Legal & Licensing compliance spend
    buy_spaceport: bool = False  # Order a Dedicated Commercial Spaceport (€300M)

