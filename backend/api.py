"""
FastAPI application for M.A.R.S. Project
Provides HTTP endpoints for the game engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional, List
import random
import logging
import json
import os
from models import GlobalConfig, GameState, PlayerInputs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MARS] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mars")
from engine import (
    calculate_demand,
    calculate_demand_segmented,
    calculate_actual_sales,
    calculate_costs,
    calculate_revenue,
    check_mission_failure,
    calculate_failure_penalty,
    check_slot_constraint,
    update_state_after_turn
)
from financial_metrics import calculate_all_metrics, calculate_reputational_vulnerability
from projections import calculate_projected_stats
from scoring import calculate_game_results

app = FastAPI(title="M.A.R.S. API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state (in-memory storage)
# In production, this would be stored in a database
game_state: Optional[GameState] = None
profit_history: List[float] = []  # Track profit for each turn
starting_budget: float = 0.0
config = GlobalConfig()


from news_generator import NewsGenerator
from flavor_text import FlavorTextGenerator
from investor_system import calculate_investor_offer_chance, process_investor_offer, get_investor_offer_chance_preview
from event_engine import roll_event, apply_event_to_state, update_event_state

def generate_competitor_news(old_price: float, new_price: float, player_price: float) -> str:
    """Generate competitor news message based on price changes."""
    price_change_pct = ((new_price - old_price) / old_price) * 100
    
    if price_change_pct < -5:
        if new_price < player_price:
            return f"SpaceX announces major price cuts! Competitor price now €{new_price/1_000_000:.1f}M (down {abs(price_change_pct):.1f}%)"
        else:
            return f"Competitors lower prices by {abs(price_change_pct):.1f}% to €{new_price/1_000_000:.1f}M"
    elif price_change_pct > 5:
        return f"Competitors raise prices to €{new_price/1_000_000:.1f}M (up {price_change_pct:.1f}%)"
    elif new_price < player_price:
        return f"Competitor price at €{new_price/1_000_000:.1f}M - lower than yours!"
    else:
        return f"Market stable. Competitor price: €{new_price/1_000_000:.1f}M"


# Pydantic models for request/response
class StartGameResponse(BaseModel):
    message: str
    state: dict


class GameStateResponse(BaseModel):
    budget: float
    reputation: float
    year: int
    tech_level: int
    green_tech_level: int
    safety_tech_level: int
    co2_impact: float
    competitor_price: float
    tech_unlocks: dict
    hr_efficiency: float
    investor_interest: float
    investor_funded: bool
    vehicles_owned: int


class PlayerInputsRequest(BaseModel):
    mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"]
    ticket_price: float
    marketing_spend: float
    safety_invest: float
    green_invest: float
    rd_invest: float
    hr_invest: float = 0.0
    contingency_budget: float = 0.0
    buy_vehicle: bool = False
    investor_offer: float = 0.0
    market_scenario: str = "A"  # "A" = current market barriers, "B" = evolved elastic market
    regulatory_invest: float = 0.0
    buy_spaceport: bool = False


class FinancialsResponse(BaseModel):
    profit: float
    revenue: float
    costs: dict
    spaas_revenue: float = 0.0
    ancillary_revenue: float = 0.0


class ResultsResponse(BaseModel):
    pax_sold: int
    mission_success: bool
    message: str
    demand: float
    competitor_news: str
    failure_penalty: Optional[dict] = None
    investor_funding: Optional[dict] = None
    investor_offer_result: Optional[dict] = None
    slot_info: Optional[dict] = None
    persona_breakdown: Optional[dict] = None
    competitors: Optional[dict] = None


class NewStateResponse(BaseModel):
    budget: float
    reputation: float
    year: int
    tech_level: int
    green_tech_level: int
    safety_tech_level: int
    co2_impact: float
    competitor_price: float
    tech_unlocks: dict
    hr_efficiency: float
    investor_interest: float
    investor_funded: bool
    investor_roi_target: float
    vehicles_owned: int
    has_spaceport: bool = False
    spaceport_building: bool = False
    active_spaas_contracts: int = 0


class PlayTurnResponse(BaseModel):
    financials: FinancialsResponse
    results: ResultsResponse
    new_state: NewStateResponse
    game_over: bool
    game_over_reason: Optional[str]
    event: Optional[dict] = None
    scenario_comparison: Optional[dict] = None


class StartGameRequest(BaseModel):
    seed: Optional[int] = None


@app.post("/start_game", response_model=StartGameResponse)
async def start_game(request: StartGameRequest = None):
    """
    Reset the game state to default values.
    """
    global game_state, profit_history, starting_budget

    if request and request.seed is not None:
        random.seed(request.seed)
        logger.info("RNG seeded with %d", request.seed)

    game_state = GameState(
        budget=config.STARTING_BUDGET,
        reputation=config.STARTING_REPUTATION,
        competitor_price=config.COMPETITOR_PRICE
    )
    profit_history = []
    starting_budget = config.STARTING_BUDGET
    logger.info("=" * 60)
    logger.info("NEW GAME  Budget: €%.0fM | Reputation: %.0f",
                config.STARTING_BUDGET / 1e6, config.STARTING_REPUTATION)

    return {
        "message": "Game started successfully",
        "state": {
            "budget": game_state.budget,
            "reputation": game_state.reputation,
            "year": game_state.turn_number,
            "tech_level": game_state.tech_level,
            "green_tech_level": game_state.green_tech_level,
            "safety_tech_level": game_state.safety_tech_level,
            "co2_impact": game_state.co2_impact,
            "competitor_price": game_state.competitor_price,
            "tech_unlocks": game_state.tech_unlocks,
            "hr_efficiency": game_state.hr_efficiency,
            "investor_interest": game_state.investor_interest,
            "investor_funded": game_state.investor_funded,
            "investor_roi_target": game_state.investor_roi_target,
            "vehicles_owned": game_state.vehicles_owned,
            "has_spaceport": game_state.has_spaceport,
            "spaceport_building": game_state.spaceport_building,
            "active_investor_offers": game_state.active_investor_offers or []
        }
    }


@app.post("/projected_stats")
async def get_projected_stats(player_inputs: PlayerInputsRequest):
    """
    Get projected statistics based on player inputs (before executing turn).
    Provides live feedback on investment impacts.
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    # Convert request to PlayerInputs
    inputs = PlayerInputs(
        mission_type=player_inputs.mission_type,
        ticket_price=player_inputs.ticket_price,
        marketing_spend=player_inputs.marketing_spend,
        safety_invest=player_inputs.safety_invest,
        green_invest=player_inputs.green_invest,
        rd_invest=player_inputs.rd_invest,
        hr_invest=player_inputs.hr_invest,
        contingency_budget=player_inputs.contingency_budget,
        buy_vehicle=player_inputs.buy_vehicle,
        regulatory_invest=player_inputs.regulatory_invest,
        buy_spaceport=player_inputs.buy_spaceport,
    )

    projected = calculate_projected_stats(inputs, game_state, config)
    return projected


@app.get("/news_feed")
async def get_news_feed():
    """
    Get a feed of news items including competitor prices and jokes.
    Updates frequently like real-world TV news.
    """
    if game_state is None:
        return {"news_items": [
            "Welcome to M.A.R.S. — Market Analysis & Risk Simulation",
            "SpaceX Falcon 9 completes routine resupply mission to ISS",
            "Blue Origin announces new crew capsule safety upgrades",
            "Axiom Space signs multi-year government research contract",
            "LEO tourism market projected to grow 40% by 2030",
        ]}
    
    # Reference prices from actual competitor constants (with small market variation)
    suborbital_comp_avg = (
        config.VIRGIN_GALACTIC_PRICE * config.VIRGIN_GALACTIC_MARKET_SHARE +
        config.BLUE_ORIGIN_NEW_SHEPARD_PRICE * config.BLUE_ORIGIN_NEW_SHEPARD_MARKET_SHARE
    ) / (config.VIRGIN_GALACTIC_MARKET_SHARE + config.BLUE_ORIGIN_NEW_SHEPARD_MARKET_SHARE)

    orbital_comp_avg = (
        config.SPACEX_PRICE * config.SPACEX_MARKET_SHARE +
        config.BLUE_ORIGIN_PRICE * config.BLUE_ORIGIN_MARKET_SHARE +
        config.AXIOM_PRICE * config.AXIOM_MARKET_SHARE
    ) / (config.SPACEX_MARKET_SHARE + config.BLUE_ORIGIN_MARKET_SHARE + config.AXIOM_MARKET_SHARE)

    short_suborbital_price = suborbital_comp_avg
    long_orbital_price = orbital_comp_avg
    scientific_price = orbital_comp_avg
    
    # Get current mission type
    current_mission = game_state.last_mission_type if hasattr(game_state, 'last_mission_type') else 'Short_Suborbital'
    
    news_feed = NewsGenerator.generate_news_feed(
        current_mission,
        game_state.turn_number,
        short_suborbital_price,
        long_orbital_price,
        scientific_price,
        num_items=5
    )
    
    return {"news_items": news_feed}


@app.get("/investor_offer_chance")
async def get_investor_offer_chance(offer_amount: float):
    """
    Calculate the chance of an investor accepting an offer.
    
    Args:
        offer_amount: Amount being offered (€)
        
    Returns:
        Dictionary with chance (float 0-1), chance_pct (float 0-100), and message
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    if offer_amount < config.INVESTOR_OFFER_MIN_AMOUNT:
        return {
            "chance": 0.0,
            "chance_pct": 0.0,
            "message": f"Minimum offer: €{config.INVESTOR_OFFER_MIN_AMOUNT/1_000_000:.0f}M"
        }
    
    if offer_amount > config.INVESTOR_OFFER_MAX_AMOUNT:
        return {
            "chance": 0.0,
            "chance_pct": 0.0,
            "message": f"Maximum offer: €{config.INVESTOR_OFFER_MAX_AMOUNT/1_000_000:.0f}M"
        }
    
    preview = get_investor_offer_chance_preview(offer_amount, game_state, config)
    
    return {
        "chance": preview["average_chance"],
        "chance_pct": preview["average_chance"] * 100,
        "best_chance_pct": preview["best_chance"] * 100,
        "worst_chance_pct": preview["worst_chance"] * 100,
        "best_investor": preview["best_investor"],
        "worst_investor": preview["worst_investor"],
        "message": f"Average chance: {preview['average_chance']*100:.1f}% (Best: {preview['best_chance']*100:.1f}%, Worst: {preview['worst_chance']*100:.1f}%)",
        "offer_amount": offer_amount,
        "reputation": game_state.reputation
    }


@app.post("/make_investor_offer")
async def make_investor_offer(offer_amount: float):
    """
    Process an investor offer immediately (real-time).
    
    Args:
        offer_amount: Amount being offered (€)
        
    Returns:
        Dictionary with result, updated game state, and message
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    # Process the offer
    result = process_investor_offer(offer_amount, game_state, config)
    
    # Return updated state (using GameStateResponse format for consistency)
    return {
        "result": result,
        "new_state": {
            "budget": game_state.budget,
            "reputation": game_state.reputation,
            "year": game_state.turn_number,
            "tech_level": game_state.tech_level,
            "green_tech_level": game_state.green_tech_level,
            "safety_tech_level": game_state.safety_tech_level,
            "co2_impact": game_state.co2_impact,
            "competitor_price": game_state.competitor_price,
            "tech_unlocks": game_state.tech_unlocks,
            "hr_efficiency": game_state.hr_efficiency,
            "investor_interest": game_state.investor_interest,
            "investor_funded": game_state.investor_funded,
            "investor_roi_target": game_state.investor_roi_target,
            "vehicles_owned": game_state.vehicles_owned,
            "active_investor_offers": game_state.active_investor_offers or []
        }
    }


@app.get("/financial_metrics")
async def get_financial_metrics():
    """
    Get financial metrics (NPV, ROI, IRR) for the current game state.
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    metrics = calculate_all_metrics(game_state, config)
    return metrics


@app.get("/state", response_model=GameStateResponse)
async def get_state():
    """
    Get the current game state.
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    return {
        "budget": game_state.budget,
        "reputation": game_state.reputation,
        "year": game_state.turn_number,
        "tech_level": game_state.tech_level,
        "green_tech_level": game_state.green_tech_level,
        "safety_tech_level": game_state.safety_tech_level,
        "co2_impact": game_state.co2_impact,
        "competitor_price": game_state.competitor_price,
        "tech_unlocks": game_state.tech_unlocks,
        "hr_efficiency": game_state.hr_efficiency,
        "investor_interest": game_state.investor_interest,
        "investor_funded": game_state.investor_funded,
        "vehicles_owned": game_state.vehicles_owned
    }


@app.post("/play_turn", response_model=PlayTurnResponse)
async def play_turn(player_inputs: PlayerInputsRequest):
    """
    Execute one turn of the game with player's decisions.
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    # Convert request to PlayerInputs
    inputs = PlayerInputs(
        mission_type=player_inputs.mission_type,
        ticket_price=player_inputs.ticket_price,
        marketing_spend=player_inputs.marketing_spend,
        safety_invest=player_inputs.safety_invest,
        green_invest=player_inputs.green_invest,
        rd_invest=player_inputs.rd_invest,
        hr_invest=player_inputs.hr_invest,
        contingency_budget=player_inputs.contingency_budget,
        buy_vehicle=player_inputs.buy_vehicle,
        regulatory_invest=player_inputs.regulatory_invest,
        buy_spaceport=player_inputs.buy_spaceport,
    )

    logger.info("─" * 60)
    logger.info(
        "TURN %d | %s | Price: €%.1fM | Budget: €%.0fM | Rep: %.0f",
        game_state.turn_number,
        inputs.mission_type,
        inputs.ticket_price / 1e6,
        game_state.budget / 1e6,
        game_state.reputation,
    )
    logger.info(
        "  Investments — Mktg: €%.1fM | Safety: €%.1fM | R&D: €%.1fM"
        " | HR: €%.1fM | Green: €%.1fM | Reg: €%.1fM | Contingency: €%.1fM",
        inputs.marketing_spend / 1e6,
        inputs.safety_invest / 1e6,
        inputs.rd_invest / 1e6,
        inputs.hr_invest / 1e6,
        inputs.green_invest / 1e6,
        inputs.regulatory_invest / 1e6,
        inputs.contingency_budget / 1e6,
    )

    # Step 0a: Roll for random event (before turn resolves)
    is_new_event = game_state.event_turns_remaining == 0
    event = roll_event(game_state)
    event_demand_multiplier = event.get("demand_multiplier", 1.0) if event else 1.0
    event_safety_share_bonus = event.get("safety_share_bonus", 0.0) if event else 0.0
    event_marketing_multiplier = event.get("marketing_multiplier", 1.0) if event else 1.0
    event_failure_penalty_multiplier = event.get("failure_penalty_multiplier", 1.0) if event else 1.0
    event_extra_regulatory = event.get("extra_regulatory_cost", 0.0) if event else 0.0

    # Apply persistent event effects (grants, R&D) and update state counters
    event_summary = {}
    if event and event.get("id") and event["id"] != "no_event":
        logger.info("  EVENT: %s (demand×%.2f | fail_penalty×%.2f)",
                    event.get("title", event.get("id")),
                    event_demand_multiplier,
                    event_failure_penalty_multiplier)
        event_summary = apply_event_to_state(event, game_state, config, is_new_event)
        update_event_state(event, game_state, is_new_event)
    else:
        update_event_state({}, game_state, False)

    # Step 0b: Check slot constraints and fleet capacity
    slot_check = check_slot_constraint(
        game_state.vehicles_owned,
        game_state.available_slots,
        1,  # missions_planned
        config
    )
    
    # Handle slot constraints
    slot_costs = 0.0
    slot_message = ""
    mission_cancelled = False
    if slot_check["needs_rush"]:
        slot_costs = slot_check["rush_cost"]
        slot_message = f"Launch slot premium paid: €{slot_costs:,.0f}"
    elif slot_check["needs_cancellation"]:
        slot_costs = slot_check["cancellation_cost"]
        slot_message = f"Mission cancelled due to slot constraints. Cancellation fee: €{slot_costs:,.0f}"
        # If cancelled, no mission happens
        mission_cancelled = True
    else:
        mission_cancelled = False
    
    # Check vehicle purchase
    vehicle_cost = 0.0
    if inputs.buy_vehicle:
        if game_state.budget >= config.VEHICLE_COST:
            vehicle_cost = config.VEHICLE_COST
        else:
            inputs.buy_vehicle = False  # Can't afford it
    
    # Step 1: Update market scenario on game state (player can switch per turn)
    game_state.market_scenario = player_inputs.market_scenario

    # Step 1b: Calculate demand (only for tourist missions, and if not cancelled)
    demand_result: dict = {}
    shadow_demand_result: dict = {}
    if mission_cancelled:
        demand = 0.0
        actual_sales = 0
        mission_failed = True
        failure_reason = "Mission cancelled due to slot constraints"
        revenue = 0.0
    else:
        if inputs.mission_type in ["Short_Suborbital", "Long_Orbital"]:
            demand_result = calculate_demand_segmented(
                ticket_price=inputs.ticket_price,
                safety_invest=inputs.safety_invest,
                marketing_spend=inputs.marketing_spend,
                reputation=game_state.reputation,
                market_scenario=game_state.market_scenario,
                config=config,
                mission_type=inputs.mission_type,
                has_spaceport=game_state.has_spaceport,
                event_demand_multiplier=event_demand_multiplier,
                event_safety_share_bonus=event_safety_share_bonus,
                marketing_multiplier=event_marketing_multiplier,
                tech_unlocks=game_state.tech_unlocks,
                consecutive_safe_missions=game_state.consecutive_safe_missions,
            )
            demand = demand_result["total"]
            actual_sales = calculate_actual_sales(demand, config.MAX_PAX)

            # Shadow demand: what the other scenario would have produced
            other_scenario = "B" if game_state.market_scenario == "A" else "A"
            shadow_demand_result = calculate_demand_segmented(
                ticket_price=inputs.ticket_price,
                safety_invest=inputs.safety_invest,
                marketing_spend=inputs.marketing_spend,
                reputation=game_state.reputation,
                market_scenario=other_scenario,
                config=config,
                mission_type=inputs.mission_type,
                has_spaceport=game_state.has_spaceport,
                event_demand_multiplier=event_demand_multiplier,
                event_safety_share_bonus=event_safety_share_bonus,
                marketing_multiplier=event_marketing_multiplier,
                tech_unlocks=game_state.tech_unlocks,
                consecutive_safe_missions=game_state.consecutive_safe_missions,
            )
        else:
            # Scientific missions: ticket_price is contract value, actual_sales is payload kg
            demand = 0.0
            actual_sales = int(inputs.ticket_price / config.SCIENTIFIC_REVENUE_PER_KG)
        
        if inputs.mission_type in ["Short_Suborbital", "Long_Orbital"]:
            logger.info(
                "  DEMAND: total=%.2f (UHNW=%.2f | Gov=%.2f | Research=%.2f)"
                " | sold=%d/%d | share=%.1f%%",
                demand,
                demand_result.get("uhnw_tourists", 0.0),
                demand_result.get("government", 0.0),
                demand_result.get("research_industrial", 0.0),
                actual_sales,
                config.MAX_PAX,
                demand_result.get("available_share", 0.0) * 100,
            )

        # Step 2: Check for mission failure (with new parameters)
        mission_failed, failure_reason = check_mission_failure(
            inputs.mission_type,
            inputs.safety_invest,
            game_state.safety_tech_level,
            game_state.hr_efficiency,
            config
        )
        
        logger.info("  MISSION: %s%s",
                    "FAILED" if mission_failed else "SUCCESS",
                    f" — {failure_reason}" if mission_failed else "")

        # Step 3: Calculate revenue (0 if mission failed)
        revenue = calculate_revenue(
            inputs.mission_type,
            actual_sales,
            inputs.ticket_price,
            config
        ) if not mission_failed else 0.0

    # Ancillary Revenue: Rapid Reusability enables unbundled add-on services on tourist missions
    # (Antonio: base ticket = flight only; luxury amenities and payload integration sold separately)
    ancillary_revenue = 0.0
    if not mission_failed and not mission_cancelled and inputs.mission_type in ["Short_Suborbital", "Long_Orbital"]:
        if game_state.tech_unlocks.get("rapid_reusability", False):
            ancillary_revenue = revenue * (config.ANCILLARY_REVENUE_MULTIPLIER - 1.0)
            revenue += ancillary_revenue

    # SPaaS Annual Recurring Revenue: active fractional research contracts pay out every turn
    # (Antonio: Fractional Ownership — €5M/turn per contract, regardless of mission outcome)
    spaas_revenue = game_state.active_spaas_contracts * config.SPAAS_ARR_PER_CONTRACT
    
    # Step 4: Calculate failure penalty (if mission failed)
    # Intermodal Modularity: Autonomous Systems halves integration risk for Scientific missions
    # (Antonio: plug-and-play payload interfaces eliminate custom engineering delays)
    intermodal_reduction = (
        config.INTERMODAL_FAILURE_REDUCTION
        if inputs.mission_type == "Scientific" and game_state.tech_unlocks.get("autonomous_systems", False)
        else 1.0
    )
    failure_penalty = None
    if mission_failed:
        failure_penalty = calculate_failure_penalty(
            inputs.mission_type,
            inputs.contingency_budget,
            config,
            event_penalty_multiplier=event_failure_penalty_multiplier * intermodal_reduction,
        )

    # Step 5: Calculate costs (includes regulatory + event extra costs)
    costs = calculate_costs(inputs, game_state, config, event_extra_regulatory=event_extra_regulatory)
    
    # Add slot costs and vehicle costs
    costs["slot_costs"] = slot_costs
    costs["vehicle_costs"] = vehicle_cost
    costs["total_costs"] += slot_costs + vehicle_cost
    
    # Step 6: Calculate profit (will be adjusted in update_state for failures)
    profit = revenue - costs["total_costs"]

    # Shadow profit: estimate using shadow demand (same costs, different revenue)
    shadow_profit: float = profit  # default — overwritten for tourist missions
    if not mission_cancelled and inputs.mission_type in ["Short_Suborbital", "Long_Orbital"] and shadow_demand_result:
        shadow_sales = calculate_actual_sales(shadow_demand_result["total"], config.MAX_PAX)
        shadow_revenue = calculate_revenue(inputs.mission_type, shadow_sales, inputs.ticket_price, config)
        shadow_profit = (shadow_revenue if not mission_failed else 0.0) - costs["total_costs"]

    # SPaaS ARR is scenario-independent — add to both profit and shadow_profit
    profit += spaas_revenue
    shadow_profit += spaas_revenue

    # Track profit history
    global profit_history
    profit_history.append(profit)

    # Capture spaceport state before the engine mutates it
    old_spaceport_building = game_state.spaceport_building
    old_has_spaceport = game_state.has_spaceport

    # Step 7: Update state
    old_state = GameState(
        budget=game_state.budget,
        reputation=game_state.reputation,
        tech_level=game_state.tech_level,
        green_tech_level=game_state.green_tech_level,
        safety_tech_level=game_state.safety_tech_level,
        turn_number=game_state.turn_number,
        co2_impact=game_state.co2_impact,
        competitor_price=game_state.competitor_price,
        hr_efficiency=game_state.hr_efficiency,
        investor_interest=game_state.investor_interest,
        investor_funded=game_state.investor_funded,
        vehicles_owned=game_state.vehicles_owned
    )

    # Pass revenue including ancillary to state update; SPaaS added directly to budget after
    update_state_after_turn(
        game_state,
        inputs,
        actual_sales,
        revenue,
        costs,
        not mission_failed,
        config,
        failure_penalty,
        potential_demand=demand_result.get("potential", 0.0),
        shadow_profit=shadow_profit,
        regulatory_vuln_delta=costs.get("regulatory_vuln_penalty", 0.0),
    )

    # SPaaS ARR applied directly to budget (recurring, independent of mission outcome)
    game_state.budget += spaas_revenue

    # Track gross revenue for accurate financial metrics (mission revenue + SPaaS; failed missions = 0 mission revenue)
    game_state.total_revenue_earned += revenue + spaas_revenue

    # If spaceport was just ordered this turn, surface the capex in reported financials
    # (the €300M deduction already happened inside update_state_after_turn)
    if game_state.spaceport_building and not old_spaceport_building:
        costs["spaceport_cost"] = config.SPACEPORT_COST
        costs["total_costs"] += config.SPACEPORT_COST
        profit -= config.SPACEPORT_COST
        profit_history[-1] = profit
        logger.info("  SPACEPORT ordered — €%.0fM capex | Budget now €%.0fM",
                    config.SPACEPORT_COST / 1e6, game_state.budget / 1e6)

    # Generate message with contextual flavor text
    investor_funding_info = None
    flavor_text = ""
    
    if mission_cancelled:
        message = f"Mission cancelled! {slot_message}"
    elif mission_failed:
        # Add flavor text for failures
        flavor_text = FlavorTextGenerator.generate_flavor_text(inputs.mission_type, False)
        penalty_info = failure_penalty
        if penalty_info["contingency_used"] > 0:
            message = f"Mission failed! {failure_reason}. {flavor_text} Penalty: €{penalty_info['penalty_cost']:,.0f}, mitigated by €{penalty_info['contingency_used']:,.0f} contingency. Actual loss: €{penalty_info['actual_loss']:,.0f}"
        else:
            message = f"Mission failed! {failure_reason}. {flavor_text} Penalty: €{penalty_info['penalty_cost']:,.0f} (no contingency). No revenue generated. Reputation decreased."
    else:
        # Add flavor text for successes
        flavor_text = FlavorTextGenerator.generate_flavor_text(inputs.mission_type, True)
        if inputs.mission_type == "Scientific":
            message = f"Scientific mission successful! {flavor_text} Contract value: €{revenue:,.0f}"
        else:
            message = f"Mission successful! {flavor_text} Sold {actual_sales}/{config.MAX_PAX} tickets."
            if actual_sales < config.MAX_PAX and demand > 0:
                message += f" Demand was {demand:.2f} but capacity limited sales."
    
    # Process investor offer (if any)
    investor_offer_result = None
    if inputs.investor_offer > 0:
        investor_offer_result = process_investor_offer(
            inputs.investor_offer,
            game_state,
            config
        )
        if investor_offer_result["accepted"]:
            message += f" {investor_offer_result['message']}"
        else:
            message += f" {investor_offer_result['message']}"
    
    # Check for investor funding (old system - marketing-based)
    if game_state.investor_funded and not old_state.investor_funded:
        investor_funding_info = {
            "triggered": True,
            "amount": config.INVESTOR_FUNDING_AMOUNT,
            "roi_target": game_state.investor_roi_target
        }
        message += f" Series A Funding Round! +€{config.INVESTOR_FUNDING_AMOUNT/1_000_000:.0f}M injection. ROI target: €{game_state.investor_roi_target/1_000_000:.0f}M/year."
    
    # Track last mission type for news feed
    game_state.last_mission_type = inputs.mission_type
    
    # Generate news using NewsGenerator
    mission_news = NewsGenerator.generate_news(
        inputs.mission_type,
        game_state.turn_number,
        include_crisis=True
    )
    
    # Also generate competitor price news
    competitor_price_news = generate_competitor_news(
        old_state.competitor_price,
        game_state.competitor_price,
        inputs.ticket_price
    )
    
    # Combine news items
    competitor_news = f"{mission_news} | {competitor_price_news}"
    
    # Check for new tech unlocks
    new_unlocks = []
    if old_state.tech_level < 10 <= game_state.tech_level:
        new_unlocks.append("Reusable Stage 1 unlocked! Launch costs −20% and Scenario B elasticity boosted to ×3.2 — the Jet Age turning point.")
    if old_state.tech_level < 20 <= game_state.tech_level:
        new_unlocks.append("Green Hydrogen unlocked! CO2 emissions reduced by 50%.")
    if old_state.tech_level < 25 <= game_state.tech_level:
        new_unlocks.append("Autonomous Systems unlocked! AI navigation reduces passenger training from years to weeks — TAM expanded +50% across all customer segments.")
    if old_state.tech_level < 30 <= game_state.tech_level:
        new_unlocks.append("Rapid Reusability unlocked! Variable costs −50% further + ancillary unbundled revenue active — the Low-Cost Carrier space model is online.")

    if new_unlocks:
        message += " " + " ".join(new_unlocks)

    # SPaaS revenue notice
    if spaas_revenue > 0:
        message += f" SPaaS ARR: +€{spaas_revenue/1_000_000:.1f}M from {game_state.active_spaas_contracts} fractional research contract(s)."
    if ancillary_revenue > 0:
        message += f" Ancillary add-ons: +€{ancillary_revenue/1_000_000:.1f}M."

    # Regulatory compliance alerts
    if inputs.regulatory_invest == 0:
        message += " ⚠️ REGULATORY ALERT: Zero compliance spend — reputation penalised and vulnerability increased."
    elif inputs.regulatory_invest < config.REGULATORY_MIN_SPEND:
        message += f" ⚠️ Regulatory spend below recommended €{config.REGULATORY_MIN_SPEND/1_000_000:.0f}M minimum — vulnerability increased."

    # Helia: price-floor advisory in Scenario A (training barrier makes sub-floor pricing irrational)
    if game_state.market_scenario == "A" and not mission_cancelled:
        if inputs.mission_type == "Short_Suborbital" and inputs.ticket_price < config.SCENARIO_A_SUBORBITAL_PRICE_FLOOR:
            message += f" ⚠️ PRICING NOTE: Ticket price below real-market floor (€{config.SCENARIO_A_SUBORBITAL_PRICE_FLOOR/1_000:,.0f}k). In Scenario A the accessibility barrier — not price — limits demand; under-cutting may sacrifice margin without gaining passengers."
        elif inputs.mission_type == "Long_Orbital" and inputs.ticket_price < config.SCENARIO_A_ORBITAL_PRICE_FLOOR:
            message += f" ⚠️ PRICING NOTE: Ticket price below real-market floor (€{config.SCENARIO_A_ORBITAL_PRICE_FLOOR/1_000_000:.0f}M). In Scenario A the training/medical qualification barrier constrains demand regardless of price."

    # Spaceport status messages — detect transitions via pre-captured state
    if game_state.spaceport_building and not old_spaceport_building:
        message += f" 🏗️ Dedicated Commercial Spaceport ordered — €{config.SPACEPORT_COST/1_000_000:.0f}M invested, operational next turn."
    if game_state.has_spaceport and not old_has_spaceport:
        message += " 🚀 Dedicated Commercial Spaceport is now operational! Scenario B full elasticity ×2.5 unlocked."

    # Check for game over conditions
    game_over = False
    game_over_reason = None

    if game_state.budget < config.BANKRUPTCY_THRESHOLD:
        game_over = True
        game_over_reason = "bankruptcy"
    elif game_state.turn_number > config.MAX_YEARS:
        game_over = True
        game_over_reason = "max_years"

    logger.info(
        "  FINANCIALS — Revenue: €%.1fM | Costs: €%.1fM | Profit: €%.1fM",
        revenue / 1e6,
        costs["total_costs"] / 1e6,
        profit / 1e6,
    )
    if failure_penalty:
        logger.info(
            "  PENALTY — Base: €%.1fM | Contingency used: €%.1fM | Actual loss: €%.1fM",
            failure_penalty["penalty_cost"] / 1e6,
            failure_penalty["contingency_used"] / 1e6,
            failure_penalty["actual_loss"] / 1e6,
        )
    logger.info(
        "  NEW STATE — Budget: €%.0fM | Rep: %.0f | Tech: %d | SafeTech: %d | Green: %d",
        game_state.budget / 1e6,
        game_state.reputation,
        game_state.tech_level,
        game_state.safety_tech_level,
        game_state.green_tech_level,
    )
    if game_over:
        logger.info("  *** GAME OVER: %s ***", game_over_reason.upper())

    # Return response
    return {
        "financials": {
            "profit": profit,
            "revenue": revenue,
            "costs": costs,
            "spaas_revenue": spaas_revenue,
            "ancillary_revenue": ancillary_revenue,
        },
        "results": {
            "pax_sold": actual_sales,
            "mission_success": not mission_failed and not mission_cancelled,
            "message": message,
            "demand": demand,
            "competitor_news": competitor_news,
            "failure_penalty": failure_penalty,
            "investor_funding": investor_funding_info,
            "investor_offer_result": investor_offer_result,
            "slot_info": {
                "available_slots": game_state.available_slots,
                "vehicles_owned": game_state.vehicles_owned,
                "slot_costs": slot_costs,
                "vehicle_purchased": inputs.buy_vehicle and vehicle_cost > 0
            },
            "persona_breakdown": {
                "uhnw_tourists": demand_result.get("uhnw_tourists", 0.0),
                "government": demand_result.get("government", 0.0),
                "research_industrial": demand_result.get("research_industrial", 0.0),
            },
            "competitors": demand_result.get("competitors", {}),
        },
        "scenario_comparison": {
            "current_scenario": game_state.market_scenario,
            "shadow_scenario": "B" if game_state.market_scenario == "A" else "A",
            "shadow_demand": shadow_demand_result.get("total", demand),
            "shadow_profit": shadow_profit,
            "shadow_persona_breakdown": {
                "uhnw_tourists": shadow_demand_result.get("uhnw_tourists", 0.0),
                "government": shadow_demand_result.get("government", 0.0),
                "research_industrial": shadow_demand_result.get("research_industrial", 0.0),
            },
            "market_penetration_pct": (
                (game_state.total_passengers / game_state.cumulative_potential_demand * 100)
                if game_state.cumulative_potential_demand > 0 else 0.0
            ),
            "cac": (
                game_state.total_marketing_spend / game_state.total_passengers
                if game_state.total_passengers > 0 else 0.0
            ),
            "reputational_vulnerability": calculate_reputational_vulnerability(
                game_state.reputation,
                game_state.safety_incidents,
                game_state.consecutive_zero_regulatory,
            ),
        },
        "new_state": {
            "budget": game_state.budget,
            "reputation": game_state.reputation,
            "year": game_state.turn_number,
            "tech_level": game_state.tech_level,
            "green_tech_level": game_state.green_tech_level,
            "safety_tech_level": game_state.safety_tech_level,
            "co2_impact": game_state.co2_impact,
            "competitor_price": game_state.competitor_price,
            "tech_unlocks": game_state.tech_unlocks,
            "hr_efficiency": game_state.hr_efficiency,
            "investor_interest": game_state.investor_interest,
            "investor_funded": game_state.investor_funded,
            "investor_roi_target": game_state.investor_roi_target,
            "vehicles_owned": game_state.vehicles_owned,
            "has_spaceport": game_state.has_spaceport,
            "spaceport_building": game_state.spaceport_building,
            "active_spaas_contracts": game_state.active_spaas_contracts,
            "active_investor_offers": game_state.active_investor_offers or []
        },
        "game_over": game_over,
        "game_over_reason": game_over_reason,
        "event": event_summary if event_summary else None,
    }


@app.get("/final_score")
async def get_final_score():
    """
    Calculate and return final game score.
    """
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    if len(profit_history) == 0:
        raise HTTPException(status_code=400, detail="No turns played yet.")
    
    results = calculate_game_results(
        game_state,
        starting_budget,
        profit_history,
        config
    )
    
    return results


@app.get("/load_run/{run_key}")
async def load_run(run_key: str):
    """
    Load a saved playthrough run from playthrough_results.json for frontend display.
    run_key: one of run_A_status_quo | run_B_premature_evolved | run_C_lcc_revolution
    """
    json_path = os.path.join(os.path.dirname(__file__), "playthrough_results.json")
    if not os.path.exists(json_path):
        raise HTTPException(
            status_code=404,
            detail="playthrough_results.json not found. Run the playthrough script first."
        )

    with open(json_path) as f:
        data = json.load(f)

    run_data = data.get(run_key)
    if not run_data:
        valid = [k for k in data if k.startswith("run_")]
        raise HTTPException(
            status_code=400,
            detail=f"Unknown run key '{run_key}'. Available: {valid}"
        )

    turns       = run_data["turns"]
    final_score = run_data["final_score"]
    final_metrics = run_data["financial_metrics"]
    cfg         = data.get("config", {})
    last_turn   = turns[-1]

    # Determine market scenario from run key
    market_scenario = "A" if run_key == "run_A_status_quo" else "B"

    # Build frontend HistoryData array (initial entry + one per turn)
    history = [{
        "year": 1,
        "profit": 0,
        "reputation": 50.0,
        "budget": 1_500_000_000,
        "revenue": 0,
        "costs": 0,
        "marketPenetration": 0,
        "cac": 0,
        "repVulnerability": 0,
        "scenario": market_scenario,
    }]
    for t in turns:
        costs_approx = max(0.0, t["revenue"] - t["profit"])
        history.append({
            "year": t["year"] + 1,
            "profit": t["profit"],
            "reputation": t["reputation"],
            "budget": t["budget"],
            "revenue": t["revenue"],
            "costs": costs_approx,
            "paxSold": t.get("pax_sold", 0),
            "missionSuccess": t.get("mission_success", True),
            "spaceportActive": t.get("spaceport_active", False),
            "marketPenetration": t.get("market_penetration", 0),
            "cac": t.get("cac", 0),
            "repVulnerability": 0,
            "scenario": market_scenario,
        })

    # Reconstruct a GameState-compatible dict for the frontend TopBar
    game_state = {
        "budget":            last_turn["budget"],
        "reputation":        last_turn["reputation"],
        "year":              11,
        "tech_level":        final_score.get("tech_level", 0),
        "green_tech_level":  final_score.get("green_tech_level", 0),
        "safety_tech_level": 50,   # 10 turns × 5 pts/turn
        "co2_impact":        final_score.get("total_co2", 0),
        "competitor_price":  10_000_000,
        "tech_unlocks":      final_score.get("tech_unlocks", {}),
        "hr_efficiency":     1.0,
        "investor_interest": 0,
        "investor_funded":   False,
        "investor_roi_target": 0,
        "vehicles_owned":    1,
        "has_spaceport":     last_turn.get("spaceport_active", False),
        "spaceport_building": False,
        "active_spaas_contracts": 0,
        "active_investor_offers": [],
    }

    run_labels = {
        "run_A_status_quo":        ("Run A — Status Quo",        "Scenario A · Price floors · No spaceport"),
        "run_B_premature_evolved":  ("Run B — Premature Evolved",  "Scenario B · −30% pricing · No spaceport"),
        "run_C_lcc_revolution":     ("Run C — LCC Revolution",     "Scenario B · −30% pricing · Spaceport Y3"),
    }
    label, description = run_labels.get(run_key, (run_key, ""))

    return {
        "run_key":     run_key,
        "label":       label,
        "description": description,
        "market_scenario": market_scenario,
        "game_state":  game_state,
        "history":     history,
        "final_score": final_score,
        "financial_metrics": final_metrics,
        "config":      cfg,
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "M.A.R.S. API",
        "version": "1.0.0",
        "endpoints": {
            "POST /start_game": "Start a new game",
            "GET /state": "Get current game state",
            "POST /play_turn": "Play one turn",
            "GET /final_score": "Get final game score"
        }
    }

