"""
Randomized macro-systemic event engine for M.A.R.S.
Events fire each turn with weighted probability, injecting real-world shocks.
"""

import random
from models import GameState, GlobalConfig

# Each event defines what it affects and for how many turns.
# Probabilities must sum to 1.0.
EVENTS = [
    {
        "id": "no_event",
        "title": None,
        "description": None,
        "icon": None,
        "color": None,
        "duration": 0,
        "probability": 0.48,
    },
    {
        "id": "competitor_accident",
        "title": "Competitor Catastrophe",
        "description": (
            "A rival operator suffers a high-profile vehicle loss. "
            "Overall market demand drops 40% this turn as public confidence plummets — "
            "but operators with strong safety scores gain extra market share."
        ),
        "icon": "💥",
        "color": "red",
        "demand_multiplier": 0.60,        # 40% demand reduction
        "safety_share_bonus": 0.10,        # +10% share steal if safety > avg
        "duration": 1,
        "probability": 0.10,
    },
    {
        "id": "insurance_spike",
        "title": "Global Insurance Spike",
        "description": (
            "A cluster of industry incidents forces insurers to triple premiums. "
            "Failure penalties are increased by 50% for the next 2 turns. "
            "Contingency reserves become critical."
        ),
        "icon": "📈",
        "color": "orange",
        "failure_penalty_multiplier": 1.5,
        "duration": 2,
        "probability": 0.12,
    },
    {
        "id": "government_subsidy",
        "title": "Government Subsidy Programme",
        "description": (
            "A national space agency launches a commercial operator grant programme. "
            "High-reputation companies receive R&D funding and a direct cash injection."
        ),
        "icon": "🏛️",
        "color": "green",
        "rd_bonus_points": 3,
        "cash_grant": 30_000_000,          # €30M
        "reputation_requirement": 75,
        "duration": 1,
        "probability": 0.12,
    },
    {
        "id": "media_spotlight",
        "title": "Media Spotlight",
        "description": (
            "A viral documentary about space tourism airs globally. "
            "Public interest surges — your marketing spend is twice as effective this turn."
        ),
        "icon": "🎥",
        "color": "blue",
        "marketing_multiplier": 2.0,
        "duration": 1,
        "probability": 0.10,
    },
    {
        "id": "regulatory_review",
        "title": "Industry-Wide Regulatory Review",
        "description": (
            "Authorities launch an emergency safety audit across all operators. "
            "An unplanned €10M compliance cost applies this turn regardless of your "
            "regulatory budget."
        ),
        "icon": "⚖️",
        "color": "yellow",
        "extra_regulatory_cost": 10_000_000,
        "duration": 1,
        "probability": 0.08,
    },
]


def roll_event(game_state: GameState) -> dict:
    """
    Roll for a random event this turn.
    Returns an event dict (may be the no_event stub).
    Multi-turn events are not re-rolled while active.
    """
    # If a multi-turn event is still running, return the continuing event
    if game_state.event_turns_remaining > 0 and game_state.active_event:
        return game_state.active_event

    roll = random.random()
    cumulative = 0.0
    for event in EVENTS:
        cumulative += event["probability"]
        if roll < cumulative:
            return event

    return EVENTS[0]  # fallback: no_event


def apply_event_to_state(
    event: dict,
    game_state: GameState,
    config: GlobalConfig,
    is_new_event: bool,
) -> dict:
    """
    Apply persistent state mutations for the event (cash grants, R&D bonuses).
    Demand/cost modifiers are handled inline in the turn pipeline.
    Returns a summary dict for the response payload.
    """
    if not event.get("id") or event["id"] == "no_event":
        return {}

    summary = {
        "id": event["id"],
        "title": event["title"],
        "description": event["description"],
        "icon": event["icon"],
        "color": event["color"],
        "is_new": is_new_event,
        "turns_remaining": game_state.event_turns_remaining,
        "effects": [],
    }

    if is_new_event:
        # Government subsidy: one-time grant + R&D on first turn only
        if event["id"] == "government_subsidy":
            if game_state.reputation >= event.get("reputation_requirement", 75):
                game_state.budget += event.get("cash_grant", 0)
                game_state.tech_level += event.get("rd_bonus_points", 0)
                # Check unlocks
                if game_state.tech_level >= 10:
                    game_state.tech_unlocks["reusable_stage1"] = True
                if game_state.tech_level >= 20:
                    game_state.tech_unlocks["green_hydrogen"] = True
                summary["effects"].append(
                    f"+€{event['cash_grant']/1_000_000:.0f}M grant + "
                    f"+{event['rd_bonus_points']} R&D points"
                )
            else:
                summary["effects"].append(
                    f"Reputation too low ({game_state.reputation:.0f}/100 < "
                    f"{event['reputation_requirement']} required) — subsidy bypassed."
                )

    return summary


def update_event_state(event: dict, game_state: GameState, is_new_event: bool) -> None:
    """Tick the event counter and update active_event on game_state."""
    if not event.get("id") or event["id"] == "no_event":
        game_state.active_event = {}
        game_state.event_turns_remaining = 0
        return

    if is_new_event:
        game_state.active_event = event
        game_state.event_turns_remaining = event.get("duration", 1)
    else:
        game_state.event_turns_remaining = max(0, game_state.event_turns_remaining - 1)
        if game_state.event_turns_remaining == 0:
            game_state.active_event = {}
