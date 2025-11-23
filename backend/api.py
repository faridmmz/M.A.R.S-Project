"""
FastAPI application for M.A.R.S. Project
Provides HTTP endpoints for the game engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional, List
import random
from models import GlobalConfig, GameState, PlayerInputs
from engine import (
    calculate_demand,
    calculate_actual_sales,
    calculate_costs,
    calculate_revenue,
    check_mission_failure,
    calculate_failure_penalty,
    check_slot_constraint,
    update_state_after_turn
)
from financial_metrics import calculate_all_metrics
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
    investor_offer: float = 0.0  # Amount to offer investors


class FinancialsResponse(BaseModel):
    profit: float
    revenue: float
    costs: dict


class ResultsResponse(BaseModel):
    pax_sold: int
    mission_success: bool
    message: str
    demand: float
    competitor_news: str
    failure_penalty: Optional[dict] = None
    investor_funding: Optional[dict] = None
    investor_offer_result: Optional[dict] = None


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


class PlayTurnResponse(BaseModel):
    financials: FinancialsResponse
    results: ResultsResponse
    new_state: NewStateResponse
    game_over: bool
    game_over_reason: Optional[str]


@app.post("/start_game", response_model=StartGameResponse)
async def start_game():
    """
    Reset the game state to default values.
    """
    global game_state, profit_history, starting_budget
    
    game_state = GameState(
        budget=config.STARTING_BUDGET,
        reputation=config.STARTING_REPUTATION,
        competitor_price=config.COMPETITOR_PRICE
    )
    profit_history = []
    starting_budget = config.STARTING_BUDGET
    
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
            "active_investor_offers": game_state.active_investor_offers if hasattr(game_state, 'active_investor_offers') else []
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
        buy_vehicle=player_inputs.buy_vehicle
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
        raise HTTPException(status_code=400, detail="Game not started. Call /start_game first.")
    
    # Generate competitor prices (use current competitor_price as base, vary for different mission types)
    short_suborbital_price = game_state.competitor_price * 0.03  # ~€300k
    long_orbital_price = game_state.competitor_price * 0.75  # ~€7.5M
    scientific_price = game_state.competitor_price * 1.0  # ~€10M
    
    # Add some variation
    import random
    short_suborbital_price *= random.uniform(0.9, 1.1)
    long_orbital_price *= random.uniform(0.9, 1.1)
    scientific_price *= random.uniform(0.9, 1.1)
    
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
            "active_investor_offers": game_state.active_investor_offers if hasattr(game_state, 'active_investor_offers') else []
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
        buy_vehicle=player_inputs.buy_vehicle
    )
    
    # Step 0: Check slot constraints and fleet capacity
    slot_check = check_slot_constraint(
        game_state.vehicles_owned,
        game_state.available_slots,
        1,  # missions_planned
        config
    )
    
    # Handle slot constraints
    slot_costs = 0.0
    slot_message = ""
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
    
    # Step 1: Calculate demand (only for tourist missions, and if not cancelled)
    if mission_cancelled:
        demand = 0.0
        actual_sales = 0
        mission_failed = True
        failure_reason = "Mission cancelled due to slot constraints"
        revenue = 0.0
    else:
        if inputs.mission_type in ["Short_Suborbital", "Long_Orbital"]:
            demand = calculate_demand(
                inputs.ticket_price,
                game_state.competitor_price,
                game_state.reputation,
                config
            )
            actual_sales = calculate_actual_sales(demand, config.MAX_PAX)
        else:
            # Scientific missions: ticket_price is contract value, actual_sales is payload kg
            demand = 0.0
            actual_sales = int(inputs.ticket_price / config.SCIENTIFIC_REVENUE_PER_KG)  # Convert contract to kg
        
        # Step 2: Check for mission failure (with new parameters)
        mission_failed, failure_reason = check_mission_failure(
            inputs.mission_type,
            inputs.safety_invest,
            game_state.safety_tech_level,
            game_state.hr_efficiency,
            config
        )
        
        # Step 3: Calculate revenue (0 if mission failed)
        revenue = calculate_revenue(
            inputs.mission_type,
            actual_sales,
            inputs.ticket_price,
            config
        ) if not mission_failed else 0.0
    
    # Step 4: Calculate failure penalty (if mission failed)
    failure_penalty = None
    if mission_failed:
        failure_penalty = calculate_failure_penalty(
            inputs.mission_type,
            inputs.contingency_budget,
            config
        )
    
    # Step 5: Calculate costs
    costs = calculate_costs(inputs, game_state, config)
    
    # Add slot costs and vehicle costs
    costs["slot_costs"] = slot_costs
    costs["vehicle_costs"] = vehicle_cost
    costs["total_costs"] += slot_costs + vehicle_cost
    
    # Step 6: Calculate profit (will be adjusted in update_state for failures)
    profit = revenue - costs["total_costs"]
    
    # Track profit history
    global profit_history
    profit_history.append(profit)
    
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
    
    update_state_after_turn(
        game_state,
        inputs,
        actual_sales,
        revenue,
        costs,
        not mission_failed,
        config,
        failure_penalty
    )
    
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
        new_unlocks.append("Reusable Stage 1 unlocked! Launch costs reduced by 20%.")
    if old_state.tech_level < 20 <= game_state.tech_level:
        new_unlocks.append("Green Hydrogen unlocked! CO2 emissions reduced by 50%.")
    
    if new_unlocks:
        message += " " + " ".join(new_unlocks)
    
    # Check for game over conditions
    game_over = False
    game_over_reason = None
    
    if game_state.budget < config.BANKRUPTCY_THRESHOLD:
        game_over = True
        game_over_reason = "bankruptcy"
    elif game_state.turn_number > config.MAX_YEARS:
        game_over = True
        game_over_reason = "max_years"
    
    # Return response
    return {
        "financials": {
            "profit": profit,
            "revenue": revenue,
            "costs": costs
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
            }
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
            "active_investor_offers": game_state.active_investor_offers if hasattr(game_state, 'active_investor_offers') else []
        },
        "game_over": game_over,
        "game_over_reason": game_over_reason
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

