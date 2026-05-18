# M.A.R.S. — Features & Technical Reference

**Market Analysis & Risk Simulation**
PoliTOrbital · Student Aerospace Challenge

---

## Table of Contents

1. [Project Purpose](#1-project-purpose)
2. [How to Run](#2-how-to-run)
3. [Architecture Overview](#3-architecture-overview)
4. [Game Loop](#4-game-loop)
5. [Market Scenario System](#5-market-scenario-system)
6. [Customer Demand Engine](#6-customer-demand-engine)
7. [Fixed Competitor Environment](#7-fixed-competitor-environment)
8. [Mission Types](#8-mission-types)
9. [Investment Sliders](#9-investment-sliders)
10. [Technology Tree](#10-technology-tree)
11. [Investor System](#11-investor-system)
12. [Fleet Management](#12-fleet-management)
13. [Strategic KPIs](#13-strategic-kpis)
14. [News Ticker & Market Intelligence Panel](#14-news-ticker--market-intelligence-panel)
15. [Analytics Dashboard](#15-analytics-dashboard)
16. [Financial Director Tab](#16-financial-director-tab)
17. [Scoring System](#17-scoring-system)
18. [API Reference](#18-api-reference)
19. [Configuration Constants](#19-configuration-constants)
20. [Randomized Event Engine](#20-randomized-event-engine)
21. [Regulatory & Compliance System](#21-regulatory--compliance-system)
22. [Spaceport Infrastructure Gate](#22-spaceport-infrastructure-gate)
23. [Aviation Blueprint Integration (Salvatore's Research)](#23-aviation-blueprint-integration-salvatores-research)
24. [LCC Space Model Integration (Antonio's Research)](#24-lcc-space-model-integration-antonios-research)
25. [Market Stagnation Baseline (Helia's Research)](#25-market-stagnation-baseline-helias-research)

---

## 1. Project Purpose

M.A.R.S. is a **turn-based strategic business simulation** built for the PoliTOrbital Student Aerospace Challenge. Players manage an aerospace startup operating Type 2 LEO vehicles over 10 in-game years.

The simulation has two layers of purpose:

**Layer 1 — Business simulation.** Players balance budget, reputation, technology investment, and risk while trying to grow a profitable commercial spaceflight company.

**Layer 2 — Market research tool.** The game is the quantitative validation layer for PoliTOrbital's WP4 Market Analysis research, designed to answer a central strategic question:

> *Why isn't the LEO tourism market taking off — and what would it take to change that?*

The answer encoded in the simulation: **supply-side failure, not demand-side failure.** Global survey data indicates strong latent willingness-to-pay (56% of respondents willing to pay $415,000 for a suborbital flight), but actual market pricing sits 2× to 100× above this threshold — combined with near-zero launch frequency and physical/temporal training barriers that prevent most willing buyers from converting. The bottleneck is not appetite; it is the structure of the offer.

This thesis is tested through a **dual-scenario engine**:
- **Scenario A** models the current market: hard-capped demand, 70% structural suppression, and a 50% marketing efficiency penalty reflecting the accessibility barrier
- **Scenario B** models an evolved market with elastic, aviation-like demand growth gated behind supply-side infrastructure and technology investments

Players can switch between scenarios at any time and compare outcomes side-by-side in the Analytics Dashboard.

### Research Layer Breakdown

Three distinct research threads from the WP4 report are embedded as simulation mechanics. Each researcher's findings govern a specific set of game parameters.

#### Helia — Market Stagnation Baseline ([§25](#25-market-stagnation-baseline-helias-research))

Helia's analysis establishes the factual foundation for Scenario A — the three structural bottlenecks that explain why the LEO market stagnates despite demonstrable demand. Her finding: *"The issue is the structure of the offer, not the lack of demand."*

| Helia's Finding | Simulation Parameter |
|---|---|
| 70% structural demand suppression from regulatory, infrastructure, and pricing barriers | `SCENARIO_A_BARRIER_MULTIPLIER = 0.30` applied to all persona demand |
| 50% marketing conversion efficiency loss — advertising cannot overcome pre-qualification barriers (medical screening, weeks of training, remote logistics) | `SCENARIO_A_MARKETING_EFFICIENCY = 0.50` applied before computing demand factor |
| Rigid real-market price floors below which price cuts have no demand effect | `SCENARIO_A_SUBORBITAL_PRICE_FLOOR = €450k`, `SCENARIO_A_ORBITAL_PRICE_FLOOR = €5M` — trigger `⚠️ PRICING NOTE` warnings |
| Low operational cadence from regulatory friction and turnaround constraints | `SCENARIO_A_AVAILABLE_SLOTS = 2` max launch windows per turn |

#### Salvatore — Aviation Blueprint Integration ([§23](#23-aviation-blueprint-integration-salvatores-research))

Salvatore's analysis of the 1950s–1970s aviation democratisation establishes the supply-driven transition model: demand did not create cheap flights — cheap flights created demand. The Jet Age only happened when repeated vehicle reuse *and* logistics infrastructure converged simultaneously.

| Salvatore's Finding | Simulation Parameter |
|---|---|
| Repeated vehicle reuse collapses marginal cost and activates super-linear demand elasticity | Reusable Stage 1 (10 R&D pts): −20% costs + `REUSABLE_STAGE1_ELASTICITY_BOOST = 0.7` in Scenario B |
| Infrastructure deployment (airfields → airports) gates the full elasticity dividend | Spaceport (€300M): required to unlock full `SCENARIO_B_ELASTIC_MULTIPLIER = 2.5`; without it, elasticity is capped at ×1.2 |
| Both supply improvements must converge — neither alone crosses the threshold | Full ×3.2 elasticity only when Spaceport + Reusable Stage 1 are simultaneously active |
| Sustained safety record converts a "risky novelty" into a routine activity, unlocking risk-averse buyers | `SAFETY_STREAK_DEMAND_BOOST = 5%` per consecutive safe mission, capped at `SAFETY_STREAK_MAX_BONUS = 15%` |
| 1960s–70s airfare −50% → passengers ×3 (conservative baseline vs. historical ~6×) | `SCENARIO_B_ELASTIC_MULTIPLIER = 2.5` |

#### Antonio — LCC Space Model Integration ([§24](#24-lcc-space-model-integration-antonios-research))

Antonio's proposal for a Low-Cost Carrier Space architecture argues that partial reusability is insufficient. Full market transformation requires a three-pillar structural redesign: Rapid Reusability (standardised turnaround economics), Radical Accessibility (autonomous navigation eliminating the training bottleneck), and Space-as-a-Service (fractional ownership replacing bespoke mission procurement).

| Antonio's Pillar | Simulation Parameter |
|---|---|
| Rapid Reusability: LCC-style standardised fleet driving 65–90% marginal cost reduction + unbundled ancillary revenue | Rapid Reusability (30 R&D pts): `RAPID_REUSABILITY_COST_REDUCTION = 0.50` additional variable cost reduction + `ANCILLARY_REVENUE_MULTIPLIER = 1.15` per-pax tourist revenue |
| Radical Accessibility: autonomous AI navigation removes the 2–3 year astronaut training pipeline; "Select-In" medical policy expands TAM to older and corporate demographics | Autonomous Systems (25 R&D pts): `AUTONOMOUS_TAM_MULTIPLIER = 1.50` across all personas; Scientific mission failure penalty −50% via `INTERMODAL_FAILURE_REDUCTION` |
| Space-as-a-Service: fractional ownership + intermodal modularity generates stable Annual Recurring Revenue independent of individual mission outcomes | SPaaS contracts: each successful Scientific mission (with Spaceport) adds one contract at `SPAAS_ARR_PER_CONTRACT = €5M/turn`, up to `SPAAS_MAX_CONTRACTS = 5` |

---

## 2. How to Run

### Docker (recommended — zero local dependencies)

```bash
docker-compose up
```

| Service | URL |
|---------|-----|
| Frontend (React) | http://localhost:3000 |
| Backend (FastAPI) | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

### Local development

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# Vite proxies /api/* → http://localhost:8000
```

### Environment

The frontend reads `VITE_API_BASE_URL` (defaults to `http://localhost:8000`). A `.env` file is pre-configured in `frontend/`.

---

## 3. Architecture Overview

```
frontend/src/
├── App.tsx                   # Root: state, turn execution, tab routing
├── components/
│   ├── ControlPanel.tsx      # Mission type + 6 investment sliders
│   ├── MissionForecast.tsx   # Live pre-turn outcome preview
│   ├── AnalyticsCharts.tsx   # KPI charts + scenario overlay
│   ├── FinancialDirectorTab.tsx  # NPV / ROI / IRR + strategic KPIs
│   ├── InvestorTab.tsx       # Investor offer interface
│   ├── ResearchTab.tsx       # Technology tree
│   ├── Advisor.tsx           # Advisor logic (tips rendered in NewsTicker hover panel, not on Dashboard)
│   ├── ReportCardModal.tsx   # Per-turn result summary (with persona breakdown)
│   ├── TopBar.tsx            # Budget / reputation / year at a glance; scenario toggle with rich hover tooltips
│   ├── NewsTicker.tsx        # Live news feed with market intelligence hover panel (portal-rendered)
│   └── WinScreen.tsx         # End-game score display

backend/
├── api.py                    # FastAPI app + all REST endpoints
├── engine.py                 # Core turn logic, demand engine, state mutation
├── models.py                 # Pydantic/dataclass models + GlobalConfig constants
├── financial_metrics.py      # NPV, ROI, IRR, Market Penetration, CAC, Rep Vulnerability
├── projections.py            # Live pre-turn forecast (non-mutating)
├── scoring.py                # Final score calculation
├── investor_system.py        # Randomised investor pool + offer acceptance
├── news_generator.py         # Dynamic per-turn news feed
└── flavor_text.py            # Narrative strings keyed to game state
```

**Data flow per turn:**

```
[ControlPanel sliders] → POST /play_turn
  → engine.calculate_demand_segmented()   ← Scenario A or B
  → engine.check_mission_failure()
  → engine.calculate_costs()
  → engine.calculate_revenue()
  → engine.update_state_after_turn()      ← mutates in-memory GameState
  ← PlayTurnResponse {financials, results, scenario_comparison, new_state}
[App.tsx] appends to history[] → AnalyticsCharts re-renders
```

**State storage:** All game state is in-memory on the backend (single `GameState` object). No database. The session ends when the process stops.

---

## 4. Game Loop

| Parameter | Value |
|-----------|-------|
| Starting budget | €500M |
| Starting reputation | 50 / 100 |
| Max years | 10 turns |
| Bankruptcy threshold | €0 |
| Max passengers per mission | 7 |

Each **turn = 1 in-game year**. The player sets:

1. Mission type
2. Ticket price (or contract value)
3. Six investment sliders
4. Optionally: buy a new vehicle, make an investor offer

The backend resolves demand, mission success/failure, revenue, costs, and all state updates, then returns a full result object. A `ReportCardModal` summarises the turn before the next one begins.

The game ends when:
- Year 11 is reached (max years)
- Budget drops below €0 (bankruptcy)

**Game-over flow:** When a game-ending turn is processed, the `ReportCardModal` is always shown first so the player can see that turn's results (mission outcome, financials, persona breakdown). Only after the player closes the modal does the `WinScreen` (final score display) appear. The final score is fetched from `/final_score` as part of the same turn response, so there is no second network request on modal close.

---

## 5. Market Scenario System

This is the core research feature of M.A.R.S.

### Scenario A — Current Market (Barriers)

Models the real-world LEO market as it exists today.

- **Demand is hard-capped** per customer persona regardless of price or marketing
- A **structural barrier multiplier (×0.30)** suppresses ~70% of organic demand
- Even aggressive price cuts generate minimal new customers
- Represents: extreme capital intensity, regulatory rigidity, no mass-market infrastructure

**Effect in-game:** Total demand rarely exceeds 1–2 passengers per turn. Profitability is nearly impossible without external funding.

#### Why ×0.30 (70% suppression)?

The 30% barrier multiplier is grounded in what actually blocks the LEO market today:

- **Regulatory friction** — FAA launch licensing takes 1–3 years per vehicle type; no expedited pathway exists for commercial passenger flights
- **No mass-market infrastructure** — no dedicated passenger terminals, no standardised insurance products, no medical screening pipelines
- **Physical price floor** — achieving orbit costs ~€5–10M/seat with current non-reusable or semi-reusable vehicles; there is no route to dramatically lower prices without new technology

In practice, the total addressable market for orbital tourism in 2024 is estimated at fewer than 20 people/year globally — consistent with a ~70% structural suppression applied to an already small base pool.

### Scenario B — Evolved Market (Elastic)

Models a hypothetical future market analogous to early commercial aviation.

- **No hard demand cap**; demand scales elastically with price reductions
- Price drops below the competitor average trigger a **super-linear boost** (elasticity multiplier ×2.5 with Spaceport, ×1.2 without)
- A 50% price reduction can grow demand by 100–200% — but only after building the required infrastructure
- Represents: reusable vehicles at scale, regulatory modernisation, mass-market accessibility

**Effect in-game:** Price-competitive players can unlock dramatically higher passenger volumes, making profitability achievable through volume rather than premium margins. The Dedicated Commercial Spaceport (€300M) is required to unlock full elasticity — without it, Scenario B provides only a partial ×1.2 boost, demonstrating the capital intensity bottleneck.

#### Why ×2.5 elasticity?

The 2.5× multiplier is modelled on the **commercial aviation transition (1960s–1970s)** — the only comparable mass-market accessibility shift in transport history. When transatlantic airfares dropped ~50% during that decade, annual passenger volume grew roughly 300%. A 2.5× boost per price-halving is actually *conservative* relative to that historical rate. The multiplier only activates when the player prices below the weighted competitor average, reflecting that demand elasticity requires a genuine accessibility threshold to be crossed, not just marginal discounting.

#### Reusability Dividend (×3.2 ceiling)

Unlocking **Reusable Stage 1** in Scenario B adds a further **+0.7** to the elasticity multiplier (2.5 → 3.2 with Spaceport, or 1.2 → 1.9 without). This models Salvatore's "Jet Age turning point" finding: aviation only democratised when aircraft could be operated *repeatedly and efficiently* — it was reusability that collapsed marginal costs and enabled high-cadence scheduling. In the simulation, reaching 3.2 elasticity requires the player to combine both supply-side breakthroughs simultaneously (infrastructure + technology), consistent with the historical precedent that neither alone was sufficient.

### Switching Scenarios

The scenario toggle is in the **top bar**, next to the M.A.R.S. Project title — always visible regardless of active tab.

**Hover tooltips:** Hovering either scenario button opens a rich card panel that summarises:
- The scenario's strategic premise and market mechanics (4 bullet points with icons)
- A framing question to orient the player's thinking
- Color-coded theme — red for Scenario A (barriers), green for Scenario B (elastic)

Players are encouraged to:

1. Run 3–5 turns in Scenario A to experience the structural barrier
2. Switch to Scenario B and observe the demand difference
3. Use the **Analytics → Scenario Overlay** to compare the profit trajectories side-by-side

The backend also computes **shadow data** every turn: what revenue and profit *would have been* under the other scenario. This is stored and plotted as the dashed line in the comparison chart.

---

## 6. Customer Demand Engine

`backend/engine.py → calculate_demand_segmented()`

Demand is no longer a single number. It is computed separately for **three customer personas**, each with distinct price and safety sensitivity weights.

### Customer Personas

| Persona | Price Sensitivity | Safety Sensitivity | Base Pool (pax/yr) |
|---------|-------------------|--------------------|--------------------|
| **UHNW Tourists** | Low (0.4) | High (0.9) | 5.0 |
| **Government Agencies** | Very low (0.2) | Very high (1.5) | 3.0 |
| **Research / Industrial** | High (0.8) | Moderate (0.6) | 4.0 |

**Total global market pool: 12 pax/year** across all players.

#### Why these sensitivity weights?

The weights are qualitative judgements grounded in how each customer type actually procures spaceflight today — not arbitrary numbers:

**UHNW Tourists (price 0.4 · safety 0.9)**
Billionaires buying a once-in-a-lifetime experience are largely indifferent to price up to a very high threshold — Jared Isaacman paid ~$200M for Inspiration4 without haggling. What they *do* care about is safety anxiety: the reputational and personal risk of something going wrong. A low price sensitivity (0.4) and high safety sensitivity (0.9) captures this. The pool of 5 pax/yr reflects the small but real pipeline of ultra-HNW individuals who have publicly expressed interest in orbital flight.

**Government Agencies (price 0.2 · safety 1.5)**
Government space budgets are pre-allocated years in advance by contract and political process — a 20% price drop does not unlock more missions. What governments care about most is mission success rate: a failure is a political and programmatic catastrophe. Safety sensitivity of 1.5 (the highest) reflects this. The pool of 3 pax/yr represents the realistic annual throughput of government-sponsored research astronauts and payload specialists outside of national programs.

**Research / Industrial (price 0.8 · safety 0.6)**
Universities, pharmaceutical companies, and materials science firms choosing between LEO experiments, ISS time, sounding rockets, and balloon platforms are highly price-sensitive — they have alternatives. A high price sensitivity (0.8) captures this competitive substitution pressure. Safety matters less than for tourists (the payload, not the researcher, is usually at risk). The pool of 4 pax/yr reflects growing interest in microgravity manufacturing and life-sciences research.

The exact numerical values were tuned so that in Scenario A the game is genuinely hard to win, and in Scenario B aggressive pricing creates a real demand reward — making the research contrast visible through gameplay rather than just in a spreadsheet.

### Mission-Type-Specific Competitor Reference

The demand formula uses `competitor_avg_price` as the benchmark — but this average is now **mission-type-specific**. Short Suborbital and Long Orbital (and Scientific) compete in entirely different markets:

| Mission Type | Competitors | Weighted Avg Price | Weighted Avg Safety |
|---|---|---|---|
| **Short Suborbital** | Virgin Galactic + Blue Origin New Shepard | ~€479k | ~75 / 100 |
| **Long Orbital / Scientific** | SpaceX + Blue Origin + Axiom Space | ~€10.67M | ~85 / 100 |

This matters significantly for demand: at a €1M suborbital ticket, the player is priced above the ~€479k competitor average — a modest premium. At a €1M orbital ticket, the price_ratio would be ~10.67, generating a massive (and unrealistic) demand boost. Using the correct per-market benchmark keeps demand numbers grounded in reality for each mission category.

### Per-Persona Demand Formula

```
raw_demand = base_pool
           × (competitor_avg_price / ticket_price) ^ price_sensitivity
           × (safety_score / 100) ^ safety_sensitivity
           × marketing_factor
           × (reputation / 100)
```

Where `competitor_avg_price` is the weighted average for the **active mission type** (see table above).

**Scenario modifier applied after:**
- Scenario A: `demand = min(raw, 1.0 pax) × 0.30`
- Scenario B: if `ticket_price < competitor_avg`, `demand *= 1 + drop_ratio × 2.5`

**Player's addressable share:**
```
available_share = (1 - total_competitor_share)          # base ~10% orbital, ~40% suborbital
                + price_steal  (if cheaper than avg)    # up to +15%
                + safety_steal (if safer than avg)      # up to +10%
```

### Safety Score

Safety is derived from investment each turn:
```
safety_score = min(100, 50 + safety_invest / 2,000,000)
```
Base is 50/100; maximum is 100/100 at €100M investment.

### Marketing Factor

```
marketing_factor = 1.0 + min(effective_marketing × 0.02, 1.0)
```

Where `effective_marketing = marketing_millions × marketing_multiplier × scenario_efficiency`.

**Scenario A efficiency penalty (Helia):** In Scenario A, `effective_marketing` is multiplied by `SCENARIO_A_MARKETING_EFFICIENCY = 0.50`. Marketing spend is only 50% as effective because the accessibility barrier — medical screening, weeks of training, remote site logistics — kills the conversion step that advertising cannot influence. The result: a player needs €100M of marketing spend to achieve the same demand boost that €50M would produce in Scenario B. This drives up the **CAC** metric, exactly as Helia predicts.

*A Media Spotlight event (2× marketing multiplier) does partially offset this — but even at 2× the effective marketing in Scenario A still equals only the standard base in Scenario B.*

### Safety Track Record Multiplier

```
streak_bonus = min(0.15, consecutive_safe_missions × 0.05)
demand      *= (1.0 + streak_bonus)
```

After each consecutive successful mission (no failure in between), all persona demand receives a cumulative +5% multiplier, capped at +15% after three consecutive successes. A single mission failure resets the streak to zero.

This directly models Salvatore's finding that aviation safety standardisation was a *process*, not a single event: repeated successful operations progressively transform a "risky novelty" into a routine activity, unlocking a broader pool of risk-averse customers who would not have considered the product at launch. In Scenario A the raw demand is so suppressed that the streak bonus has minimal visible effect. In Scenario B, a well-managed operator can stack this bonus on top of the elasticity multiplier, creating a compounding growth curve that mirrors the historical aviation takeoff.

---

## 7. Fixed Competitor Environment

Real-world companies are injected as **environmental constants** that shape each market segment. Their prices and safety ratings do not change; they set the reference points that all demand formulas use. Competitors are split by mission type — suborbital and orbital are distinct markets.

### Suborbital Competitors (Short Suborbital missions)

| Competitor | Ticket Price | Safety Rating | Market Share |
|------------|-------------|---------------|--------------|
| **Virgin Galactic** | €450k | 65 / 100 | 25% |
| **Blue Origin (New Shepard)** | €500k | 82 / 100 | 35% |

**Combined suborbital competitor share: 60%.** The player starts with ~40% of the addressable suborbital market — a much larger opening than orbital.

**Weighted averages (suborbital):**
```
competitor_avg_price  ≈ €479k
competitor_avg_safety ≈ 75 / 100
```

### Orbital Competitors (Long Orbital and Scientific missions)

| Competitor | Ticket Price | Safety Rating | Market Share |
|------------|-------------|---------------|--------------|
| **SpaceX** | €8M | 90 / 100 | 45% |
| **Blue Origin** | €12M | 75 / 100 | 25% |
| **Axiom Space** | €15M | 80 / 100 | 20% |

**Combined orbital competitor share: 90%.** The player starts with access to ~10% of the orbital market.

**Weighted averages (orbital):**
```
competitor_avg_price  ≈ €10.67M
competitor_avg_safety ≈ 85 / 100
```

### Why these companies?

SpaceX, Blue Origin, and Axiom Space are the only companies that had **actually flown paying passengers to LEO or near-LEO** as of 2024–2025. Virgin Galactic and Blue Origin New Shepard are the only companies with a **commercial suborbital passenger record**. They are not hypothetical rivals — they are the real market the player is entering.

### Why these specific numbers?

**Virgin Galactic** — *Price €450k:* SpaceShipTwo commercial tickets sold at $450k before the program suspension in 2023. *Safety 65/100:* 2014 VSS Enterprise fatal accident during test flight; commercial program history is limited. *Market share 25%:* Had the most developed suborbital tourism marketing pipeline before suspension.

**Blue Origin (New Shepard)** — *Price €500k:* NS commercial seat pricing; premium above VG reflecting post-2014 brand trust advantage. *Safety 82/100:* 2022 vehicle anomaly grounded the program; returned to flight 2024. *Market share 35%:* Dominant in the suborbital market post-VG suspension.

**SpaceX** — *Price €8M:* Per-seat estimate on a shared Crew Dragon commercial manifest. *Safety 90/100:* Highest operational cadence of any crewed orbital vehicle, zero passenger fatalities. *Market share 45%:* Dominates the commercial orbital launch manifest.

**Blue Origin (orbital)** — *Price €12M:* Projected New Glenn / orbital tourism pricing. *Safety 75/100:* Less proven than SpaceX at the orbital level. *Market share 25%:* Significant capital but operationally behind SpaceX in crewed orbital missions.

**Axiom Space** — *Price €15M:* ISS private astronaut missions publicly listed at ~$55M/seat; Axiom charges a premium for mission management and training. *Safety 80/100:* Flies on SpaceX hardware but adds mission complexity as a newer operator. *Market share 20%:* Limited to ISS-docking missions constrained by docking port availability.

### How competitors affect gameplay

Players can steal additional share by:
- Undercutting the **mission-type-specific** weighted average competitor price (up to +15% share)
- Out-performing the **mission-type-specific** weighted average competitor safety rating (up to +10% share)

Both averages appear in the ControlPanel **Market Intel** tooltip (hover the ℹ button next to the ticket price slider) and in the Analytics → Competitor Landscape panel.

---

## 8. Mission Types

| Type | Risk | Revenue | Notes |
|------|------|---------|-------|
| **Short Suborbital** | 5% | €200k–€400k / pax | Default. Lowest risk. Price range: €200k–€1M |
| **Long Orbital** | 15% | €5M–€10M / pax | Requires Safety Tech Level ≥ 5. Price range: €5M–€25M. In Scenario B: +3 reputation on success (destination stay bonus) |
| **Scientific / Industrial** | 25% | Fixed contract | Ticket price = contract value. Grants +2 R&D points on success (+3 if Spaceport is built) |

### Long Orbital — Destination Stay Bonus (Scenario B)

In Scenario B, a successful Long Orbital mission grants an extra **+3 reputation** on top of the standard +2. This represents the Axiom Space / private space-station model described in Salvatore's research: when orbital access evolves from a "trophy experience" to a destination-based stay, the perceived value of each mission to the public and media is substantially higher. The bonus only applies in Scenario B because in Scenario A the public frame remains "risky novelty" regardless of the mission's success.

### Scientific / Industrial — Spaceport R&D Bonus

A successful Scientific mission normally grants +2 R&D points. With a Dedicated Commercial Spaceport operational, it grants +3. The spaceport provides dedicated lab integration, dedicated payload bays, and faster turnaround — directly improving the research yield of each mission. This operationalises Salvatore's finding that aviation succeeded partly by addressing *practical transportation needs*, making the "functional" use of space infrastructure a visible competitive advantage.

### Mission Failure

Failure probability:
```
failure_prob = base_risk − (safety_invest_millions × safety_efficiency)
```

If mission fails:
- Zero revenue
- Reputation −20
- Failure penalty: €25M (Suborbital), €50M (Orbital), €75M (Scientific)
- Contingency budget mitigates penalty up to the full amount reserved

**HR Saving Throw:** If `hr_efficiency > 1.5`, there is a 30% chance the crew solves the failure in-flight (no penalty, reputation impact reduced).

---

## 9. Investment Sliders

Six investment categories are available each turn. All are optional (minimum €0).

| Slider | Effect |
|--------|--------|
| **Marketing** | Boosts demand (all personas) + reputation + investor interest |
| **Safety** | Reduces failure probability + improves safety score for demand |
| **Green / Sustainability** | Reduces CO2 per launch + unlocks Green Hydrogen tech |
| **R&D** | Adds tech points; unlocks Reusable Stage 1 and Green Hydrogen |
| **HR & Training** | Improves staff efficiency (logarithmic), enables HR saving throw |
| **Contingency Reserve** | Mitigates failure penalties up to the reserved amount |
| **Legal & Licensing** | Regulatory compliance spend; minimum €5M/turn recommended |

### Market Intel Tooltip (ControlPanel)

The ticket price slider has an **ℹ Market Intel** button (hover to open). It renders via a React Portal into `document.body` at `position: fixed` — completely outside the sidebar's `overflow-y-auto` container so it is never clipped. The tooltip shows competitor data for the **currently selected mission type**:

- **Short Suborbital:** Virgin Galactic and Blue Origin New Shepard with prices, safety ratings, and market shares
- **Long Orbital / Scientific:** SpaceX, Blue Origin, and Axiom Space

Each entry shows the weighted average price and safety for that market segment, with a note on how price and safety position relative to the average translates to market share.

Additionally:
- **Buy Vehicle** checkbox: orders a new vehicle (€150M, ready next turn)
- **Build Spaceport** checkbox: orders a Dedicated Commercial Spaceport (€300M, ready next turn) — see [Section 22](#22-spaceport-infrastructure-gate)
- **Investor Offer** (Investor tab): real-time offer to the investor pool

### Total Spend Warning

Investments + variable costs + fixed costs are deducted each turn regardless of mission outcome. Players who over-invest without revenue will rapidly deplete their budget.

---

## 10. Technology Tree

Tech points accumulate from R&D investment (€10M = +1 point) and from successful Scientific missions (+2, or +3 with Spaceport).

| Unlock | Threshold | Effect |
|--------|-----------|--------|
| **Reusable Stage 1** | 10 tech points | Launch cost −20% + Scenario B elasticity +0.7 (permanent) |
| **Green Hydrogen** | 20 tech points | CO2 per launch −50% (permanent) |
| **Autonomous Systems** | 25 tech points | TAM +50% across all personas + Scientific failure penalty −50% |
| **Rapid Reusability** | 30 tech points | Variable costs −50% additional + ancillary revenue +15% on tourist missions |

Green tech level (from Green Investment) separately reduces variable launch costs by 1% per level.

### Full Cost Reduction Stack

With all reusability unlocks active (Reusable Stage 1 + Rapid Reusability + Green Hydrogen + HR efficiency):

```
Variable cost multiplier = 0.80 (Stage 1) × 0.50 (Rapid) × 0.80 (Green, 10 lvls) ≈ 0.32
Total variable cost reduction ≈ 68% from base
```

This lands within Antonio's projected 65–90% marginal cost reduction for the full LCC Space Model, and makes per-mission costs economically comparable to early commercial aviation.

### Reusability Dividend (Scenario B elasticity)

Unlocking Reusable Stage 1 produces **two simultaneous effects**: −20% costs and Scenario B elasticity +0.7 (2.5 → 3.2 with Spaceport). Without reusability, even a price-competitive player in Scenario B cannot reach historical aviation-level elasticity.

### Autonomous Systems — TAM Expansion

Unlocking Autonomous Systems (25 pts) applies a **×1.5 multiplier to every persona's base pool** — effectively expanding the total addressable market from 12 to 18 pax/year. This models Antonio's key finding: the current physiological and temporal barriers (2–3 year astronaut training, strict medical screening) are the primary human bottleneck. AI navigation and a "Select-In" medical policy open the market to older wealthy individuals, corporate researchers, and scientific institutions that currently cannot qualify.

### SPaaS via Scientific Missions

Each successful Scientific mission with the Spaceport operational adds one **fractional research contract** (up to 5 total). Each contract pays **€5M ARR per turn**, permanently from that turn onwards, regardless of future mission outcomes. This cash flow stabiliser models Antonio's Fractional Ownership proposal — research institutions pre-buying guaranteed access rather than full-mission commitments.

---

## 11. Investor System

### Real-Time Offers (Investor Tab)

Players can make funding offers at any time outside of a turn. A random investor is selected from a pool of 14 named characters, each with a different preference:

| Type | Values weighted | Acceptance bonus |
|------|-----------------|-----------------|
| Safety-focused (3) | Safety tech level | Up to +30% |
| Environmental (3) | Low CO2 impact | Up to +30% |
| Tech-focused (3) | R&D / tech level | Up to +30% |
| Financial / Reputation (3) | Reputation score | Up to +40% |
| Balanced (2) | All factors equally | Up to +25% |

**Base acceptance chance:** 20%  
**Offer size penalty:** −0.005% per €1M offered (higher asks face more scrutiny)  
**Reputation bonus:** +0.2% per reputation point (applies to all investor types)  
**Chance clamped:** 5%–95% — no outcome is ever certain  

If accepted: full offer amount added to budget immediately, reputation +2–5 (scales with offer size).  
If declined: reputation −1–3 (scales with offer size).  
**ROI target after accepted offer:** avg profit × 1.15, or offer × 10% if no profit history yet — whichever is higher.


---

## 12. Fleet Management

- **Starting vehicles:** 1
- **Vehicle cost:** €150M
- **Build time:** 1 turn (ordered this turn → available next turn)
- **Capacity:** Each vehicle carries up to 7 passengers

**Launch slot system:** Each turn has a random number of available slots, drawn from:
- **Scenario A:** `randint(0, 2)` — rare launches, regulatory bottlenecks, long turnaround (Helia)
- **Scenario B:** `randint(0, 3)` — higher cadence with mature infrastructure

If the player needs to rush (not enough slots), a €10M premium applies. If missions must be cancelled, a €5M cancellation fee applies per excess mission.

---

## 13. Strategic KPIs

Three new KPIs were introduced in the market-pivot update. They are calculated every turn and displayed in the Analytics tab, Financial Director tab, and the per-turn Report Card modal.

### Market Penetration %

```
market_penetration = (total_passengers_carried / cumulative_potential_demand) × 100
```

Measures how much of the addressable market the player has actually converted. In Scenario A this stays near 0–2% because barriers suppress conversion. In Scenario B a well-priced strategy can reach 10–30%.

### Customer Acquisition Cost (CAC)

```
CAC = total_marketing_spend / total_passengers_carried
```

The cost of winning each customer through marketing. High CAC relative to ticket price indicates marketing spend is not converting to sales — a direct signal that barriers (Scenario A) prevent marketing from working.

### Reputational Vulnerability

```
rep_vulnerability = (
    (100 - reputation) / 100
    + min(incidents × 0.05, 0.50)
    + min(consecutive_zero_regulatory × 0.05, 0.25)
) × 100
```

A compound score (0–100) with three components:
- **Reputation deficit** — low reputation directly raises vulnerability
- **Safety incidents** — each mission failure permanently adds 5 points (capped at +50)
- **Regulatory neglect** — each turn with zero regulatory spend adds 5 points (capped at +25)

High vulnerability means future demand is structurally at risk. Color-coded green (<30), amber (30–60), red (>60). The regulatory term ensures that companies cutting compliance costs as a survival strategy accumulate hidden brand risk even if they have no direct failures.

---

## 14. News Ticker & Market Intelligence Panel

`frontend/src/components/NewsTicker.tsx`

The news bar runs below the TopBar at all times and cycles through dynamic market news generated by the backend each turn. News items are colour-coded by type:

| Style | Prefix | Meaning |
|-------|--------|---------|
| Yellow / 📰 NEWS | Standard | Narrative flavour and market events |
| Blue / 📊 MARKET | `Market Update:` | Current price benchmarks per mission type |
| Purple / 😄 JOKE | `💡` | Lighthearted space-industry quips |

### Market Intelligence Hover Panel

Hovering the news bar opens a **three-column overlay panel** rendered via a React Portal into `document.body` — completely outside the app's DOM tree so it is never clipped by `overflow-hidden` containers and never interferes with tab navigation.

The panel updates live with the current game state:

**Column 1 — Competitor Landscape**
- Two segments displayed with a divider: **Suborbital** (Virgin Galactic €450k 25%, Blue Origin New Shepard €500k 35%) and **Orbital** (SpaceX €8M 45%, Blue Origin €12M 25%, Axiom Space €15M 20%)
- Suborbital weighted average: ~€479k price, ~75 safety — displayed as the benchmark for Short Suborbital missions
- Orbital weighted average: ~€10.67M price, ~85 safety — displayed as the benchmark for Long Orbital and Scientific missions
- Plain-language reminders: price below the relevant average steals share and (in Scenario B) unlocks elasticity; safety above the average steals up to +10% share
- Notes on each competitor's specific record (e.g., "2022 anomaly, returned 2024" for New Shepard)

**Column 2 — Advisor**
- Context-aware tips derived from the current game state, identical logic to the `Advisor` component (which was removed from the Dashboard to avoid duplication)
- Tips cover: budget danger, reputation crisis, Safety Tech unlock progress toward Long Orbital, R&D progress toward Reusable Stage 1 and Green Hydrogen, CO₂ excess warnings
- Shows a positive confirmation message when no issues are detected

**Column 3 — Tech & Unlock Status**
- Live progress on all three unlock gates: Reusable Stage 1 (10 R&D pts), Green Hydrogen (20 R&D pts), Long Orbital (Safety Tech ≥ 5)
- Quick-reference investment-to-points rates (€10M R&D = +1 Tech Point, etc.)

---

## 15. Analytics Dashboard

`frontend/src/components/AnalyticsCharts.tsx`

The Analytics tab contains seven charts and one KPI card row. The active scenario badge in the top-right of this tab reflects the **currently selected scenario**, not the last-played turn.

### KPI Card Row

Three cards at the top of the page showing the **latest-turn values** of Market Penetration, CAC, and Reputational Vulnerability with contextual colour coding.

### Scenario Comparison Chart (AreaChart)

The flagship chart. Shows profit over time as a filled area. An **Overlay ON/OFF toggle** shows both scenario trajectories simultaneously.

- **Red line** = Scenario A profit (barriers) — always red regardless of which scenario was active that turn
- **Green dashed line** = Scenario B profit (elastic) — always green

Each turn records both `scenarioAProfit` and `scenarioBProfit` based on which scenario was *actually played* that turn. The backend computes **shadow profit** every turn (what the other scenario would have produced given identical inputs), so both lines are always populated across the full game history even when the player switches scenarios mid-game.

**Important:** the two lines will be identical when the player earns zero passengers (e.g. playing Scientific missions, or when demand rounds below 1 in both scenarios). Divergence requires Short Suborbital or Long Orbital missions with a ticket price below the €10M competitor average to activate Scenario B's elastic boost.

This chart makes the research finding immediately visual: Scenario A produces flat or negative profit regardless of player decisions, while Scenario B unlocks a growth trajectory once prices drop below the competitor average.

### Customer Persona Demand Breakdown (BarChart)

Stacked bar chart showing demand from each of the three personas per turn. In Scenario A, all bars remain near-zero. In Scenario B, Research/Industrial demand responds fastest to price cuts, then UHNW Tourists, with Government demand growing last but most sustainably.

### Market Penetration % (LineChart)

Tracks the cumulative conversion rate over all turns. Useful for demonstrating that in Scenario A, even sustained play never breaks 5% penetration — the market cannot be cracked by price or marketing alone.

### Reputational Vulnerability (LineChart)

Tracks the vulnerability score over time. Every mission failure spikes the line permanently. Used to demonstrate that high-risk strategies in Scenario A compound both financial losses and brand risk simultaneously.

### Profit, Reputation, Budget (LineCharts)

Standard financial history charts retained from the original game.

---

## 16. Financial Director Tab

`frontend/src/components/FinancialDirectorTab.tsx`

Fetches live data from `/financial_metrics` after each turn.

### Classic Metrics

| Metric | Formula |
|--------|---------|
| **NPV** | `Σ (cash_flow_t / (1.05)^t)` at 5% discount rate |
| **ROI** | `(total_profit / total_investment) × 100` where investment = all non-fixed spending |
| **IRR** | Newton-Raphson to find rate where NPV = 0; can be negative if cumulative cash flows don't recover the starting budget |
| **Profit Margin** | `(total_profit / total_revenue) × 100` |
| **Total Revenue** | Tracked directly as cumulative gross revenue (`total_revenue_earned` in `GameState`), includes mission revenue + SPaaS ARR + ancillary revenue |
| **Total Costs** | `total_revenue − total_profit` — derived from actual tracked revenue, not estimated from profit sign |

### Strategic KPI Row (new)

Four additional cards: Market Penetration %, Customer Acquisition Cost, Reputational Vulnerability, Total Passengers Carried.

### CSV Export

The Export Report button downloads a `.csv` containing:
- Summary metrics (NPV, ROI, IRR, profit margin, CO2)
- Year-by-year ledger (revenue, costs, profit, cumulative profit)

---

## 17. Scoring System

Final score is calculated at game end (turn 11 or bankruptcy).

### Economic Score (60% weight)

| Sub-component | Weight | Formula |
|---------------|--------|---------|
| Budget growth | 40% | `50 + budget_growth_pct × 2` |
| Final reputation | 30% | `reputation / 1` |
| Avg profit/year | 30% | `50 + (avg_profit_M × 2)` |

### Green Score (40% weight)

| Sub-component | Weight | Metric |
|---------------|--------|--------|
| CO2 per year | 50% | Lower is better; 50 CO2/yr = 100 pts |
| Green tech level | 30% | 10 per level |
| Tech unlocks | 20% | Green Hydrogen = 100 pts |

### Letter Grades

`A+` ≥ 90 · `A` ≥ 85 · `A-` ≥ 80 · `B+` ≥ 75 · `B` ≥ 70 · `B-` ≥ 65 · `C+` ≥ 60 · `C` ≥ 55 · `C-` ≥ 50 · `D` ≥ 40 · `F` < 40

---

## 18. API Reference

All endpoints are documented interactively at `http://localhost:8000/docs`.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/start_game` | Reset all state, return initial GameState |
| `GET` | `/state` | Current GameState |
| `POST` | `/play_turn` | Execute one turn; returns full PlayTurnResponse |
| `POST` | `/projected_stats` | Non-mutating pre-turn forecast |
| `GET` | `/news_feed` | Dynamic news items (auto-refreshes every 8s in UI) |
| `GET` | `/investor_offer_chance` | Preview acceptance probability for a given offer amount |
| `POST` | `/make_investor_offer` | Submit a funding offer (real-time, not tied to a turn) |
| `GET` | `/financial_metrics` | NPV, ROI, IRR, and all strategic KPIs |
| `GET` | `/final_score` | Full scoring breakdown (economic + green + final) |

### PlayTurnResponse — key fields

```json
{
  "financials": { "profit", "revenue", "costs" },
  "results": {
    "pax_sold", "mission_success", "message", "demand",
    "persona_breakdown": { "uhnw_tourists", "government", "research_industrial" },
    "competitors": { "SpaceX": {...}, "Blue Origin": {...}, "Axiom Space": {...} }
  },
  "scenario_comparison": {
    "current_scenario",
    "shadow_scenario",
    "shadow_demand",
    "shadow_profit",
    "shadow_persona_breakdown",
    "market_penetration_pct",
    "cac",
    "reputational_vulnerability"
  },
  "event": {
    "id", "title", "description", "icon", "color",
    "is_new", "turns_remaining", "effects"
  },
  "new_state": { ... full GameState ... },
  "game_over", "game_over_reason"
}
```

### PlayerInputsRequest fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mission_type` | enum | required | `Short_Suborbital` / `Long_Orbital` / `Scientific` |
| `ticket_price` | float | required | €/pax or contract value |
| `marketing_spend` | float | required | €0–50M |
| `safety_invest` | float | required | €0–50M |
| `green_invest` | float | required | €0–50M |
| `rd_invest` | float | required | €0–50M |
| `hr_invest` | float | 0 | €0–50M |
| `contingency_budget` | float | 0 | Reserved for failure mitigation |
| `regulatory_invest` | float | 0 | Legal & licensing compliance (min €5M recommended) |
| `buy_vehicle` | bool | false | Order a new vehicle (€150M) |
| `buy_spaceport` | bool | false | Order a Dedicated Commercial Spaceport (€300M) |
| `investor_offer` | float | 0 | Offer amount for turn-embedded investor pitch |
| `market_scenario` | str | `"A"` | `"A"` = barriers, `"B"` = elastic |

---

## 19. Configuration Constants

All constants live in `backend/models.py → GlobalConfig`. Key values:

### Core Economy

| Constant | Value |
|----------|-------|
| `STARTING_BUDGET` | €500M |
| `STARTING_REPUTATION` | 50 |
| `MAX_YEARS` | 10 |
| `FIXED_COSTS` | €5M/turn |
| `FUEL_COST_PER_LAUNCH` | €15M |
| `LAUNCH_COST_BASE` | €20M |

### Scenario System

| Constant | Value | Meaning |
|----------|-------|---------|
| `SCENARIO_A_DEMAND_CAP_PER_PERSONA` | 1.0 | Hard cap per persona per turn |
| `SCENARIO_A_BARRIER_MULTIPLIER` | 0.30 | 70% structural suppression |
| `SCENARIO_B_ELASTIC_MULTIPLIER` | 2.5 | Full price drop amplification (with Spaceport) |
| `SCENARIO_B_NO_SPACEPORT_MULTIPLIER` | 1.2 | Partial elasticity without Spaceport |

### Regulatory & Spaceport

| Constant | Value | Meaning |
|----------|-------|---------|
| `REGULATORY_MIN_SPEND` | €5M | Recommended minimum legal spend per turn |
| `REGULATORY_VULN_PENALTY` | 15 pts | Vulnerability increase if underspend |
| `REGULATORY_REP_PENALTY` | 3 pts | Reputation loss for zero compliance spend |
| `SPACEPORT_COST` | €300M | One-time Dedicated Commercial Spaceport cost |

### Customer Personas

| Constant | UHNW | Government | Research |
|----------|------|------------|----------|
| Price sensitivity | 0.4 | 0.2 | 0.8 |
| Safety sensitivity | 0.9 | 1.5 | 0.6 |
| Base pool (pax) | 5.0 | 3.0 | 4.0 |

### Competitors

| Constant | SpaceX | Blue Origin | Axiom Space |
|----------|--------|-------------|-------------|
| Price | €8M | €12M | €15M |
| Safety | 90 | 75 | 80 |
| Market share | 45% | 25% | 20% |

### Reputation

| Event | Change |
|-------|--------|
| Mission success | +2 |
| Mission failure | −20 |
| Marketing (per €1M) | +0.1 |
| Investor accepted | +2 to +5 |
| Investor rejected | −1 to −3 |

### Tech Tree

| Unlock | R&D Points Required | Effect |
|--------|---------------------|--------|
| Reusable Stage 1 | 10 | −20% launch costs + Scenario B elasticity +0.7 |
| Green Hydrogen | 20 | −50% CO2 per launch |

### Aviation Blueprint Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `REUSABLE_STAGE1_ELASTICITY_BOOST` | 0.7 | Elasticity boost when Reusable Stage 1 unlocked in Scenario B |
| `SAFETY_STREAK_DEMAND_BOOST` | 5% | Per-consecutive-safe-mission demand boost |
| `SAFETY_STREAK_MAX_BONUS` | 15% | Cap after 3 consecutive safe missions |
| `LONG_ORBITAL_DESTINATION_REP_BONUS` | +3 | Extra reputation for Long Orbital success in Scenario B |
| `SPACEPORT_SCIENTIFIC_RD_BONUS` | +1 pt | Extra R&D for Scientific missions when Spaceport is operational |

### Market Stagnation Baseline Constants (Helia)

| Constant | Value | Meaning |
|----------|-------|---------|
| `SCENARIO_A_SUBORBITAL_PRICE_FLOOR` | €450k | Real market minimum — Virgin Galactic / Blue Origin suborbital baseline |
| `SCENARIO_A_ORBITAL_PRICE_FLOOR` | €5M | Real market minimum — ISS module / orbital mission pricing |
| `SCENARIO_A_AVAILABLE_SLOTS` | 2 | Max launch slots per turn in Scenario A (low cadence) |
| `SCENARIO_A_MARKETING_EFFICIENCY` | 0.50 | Marketing is half as effective in Scenario A (accessibility barrier) |

---

---

## 20. Randomized Event Engine

`backend/event_engine.py`

A macro-systemic shock system that fires each turn with weighted probability. Events inject real-world disruptions that force reactive strategy — demonstrating that the LEO market is not just structurally limited by demand, but also by systemic fragility.

### How It Works

At the start of each turn (before demand and costs are calculated), the engine rolls for an event. The combined probability of *something* firing is ~52%. Multi-turn events persist across turns and are tracked in `GameState.active_event` and `event_turns_remaining`.

Events are displayed prominently in the per-turn **Report Card modal** with a color-coded card, icon, and description of active effects. Ongoing multi-turn events show a "turns remaining" counter.

### Event Catalogue

| Event | Icon | Duration | Probability | Effect |
|-------|------|----------|-------------|--------|
| **Competitor Catastrophe** | 💥 | 1 turn | 10% | Market demand ×0.60 this turn; operators above avg safety gain +10% share |
| **Global Insurance Spike** | 📈 | 2 turns | 12% | Failure penalties ×1.5 while active — contingency reserves become critical |
| **Government Subsidy Programme** | 🏛️ | 1 turn | 12% | If reputation ≥ 75: +€30M grant + 3 R&D points (one-time, new event only) |
| **Media Spotlight** | 🎥 | 1 turn | 10% | Marketing spend 2× effective this turn |
| **Industry-Wide Regulatory Review** | ⚖️ | 1 turn | 8% | Mandatory extra €10M compliance cost regardless of regulatory budget |
| *(no event)* | — | — | 48% | Normal turn |

### Research Value

**Competitor Catastrophe** directly models the systemic interdependence of the LEO market: one high-profile failure depresses the entire market for all operators, which is exactly the dynamic that slows market development in Scenario A. **Insurance Spike** quantifies the risk-premium bottleneck. **Government Subsidy** demonstrates that public-sector intervention is the most plausible accelerator for early-phase commercial spaceflight.

---

## 21. Regulatory & Compliance System

`backend/engine.py → calculate_costs()` · `frontend/src/components/ControlPanel.tsx`

### Mechanic

A dedicated **Legal & Licensing** investment slider (€0–€30M) represents the ongoing cost of regulatory compliance — FAA licensing, safety certifications, insurance underwriting, and international coordination frameworks.

**Minimum recommended spend: €5M/turn.**

| Spend level | Consequence |
|-------------|-------------|
| ≥ €5M | Compliant — no penalty |
| €1–€4.9M | Reputational Vulnerability +15 this turn |
| €0 | Reputational Vulnerability +15 **and** Reputation −3 |
| Zero spend (cumulative) | `consecutive_zero_regulatory` counter increases Vulnerability by an additional 5% per turn (max +25 pts) |

### UI

The slider displays a red **⚠️ Low** or **⚠️ None!** badge when spend falls below the minimum. A green "Compliant ✓" confirmation appears when the threshold is met. The turn message and Report Card flag any regulatory penalty explicitly.

### Research Value

This mechanic makes the "cost of doing business" in a rigid regulatory environment **financially visible**. Players discover that even when revenue is zero (Scenario A), compliance costs are mandatory and non-negotiable — directly demonstrating the structural overhead identified in the market analysis. The cumulative vulnerability penalty represents the compounding reputational risk of a company seen as operating outside regulatory norms.

---

## 22. Spaceport Infrastructure Gate

`backend/engine.py → calculate_demand_segmented()` · `frontend/src/components/ControlPanel.tsx`

### Mechanic

A **Dedicated Commercial Spaceport** is a one-time capital investment (€300M) that takes one turn to build. It represents the ground infrastructure prerequisite for mass-market LEO access: dedicated terminals, standardised passenger processing, crew training facilities, and launch pad exclusivity.

**Without a Spaceport**, Scenario B elasticity is capped at ×1.2 (partial boost).  
**With a Spaceport**, Scenario B reaches its full ×2.5 elasticity multiplier.

```
Scenario B demand boost:
  Without Spaceport: raw *= 1 + drop_ratio × 1.2
  With Spaceport:    raw *= 1 + drop_ratio × 2.5
```

### UI

- **ControlPanel**: A "Build Dedicated Spaceport" checkbox appears if the spaceport is not yet built or ordered. Includes cost, build time, and elasticity impact.
- **ControlPanel** (building state): A blue "🏗️ Spaceport Under Construction" badge replaces the checkbox.
- **ControlPanel** (complete): A green "🚀 Spaceport Operational" badge confirms full elasticity is active.
- **TopBar**: A persistent status pill ("🏗️ Building…" or "🚀 Active") is visible at all times.

### Research Value

This is the most strategically significant single mechanic for the research question. The capital intensity of infrastructure investment is the key bottleneck the team identified in WP4. The Spaceport gate forces players to:

1. **Experience the capital intensity** — €300M is more than half the starting budget, requiring careful timing.
2. **Observe the before/after contrast** — switching to Scenario B without the Spaceport produces only modest demand growth, making the infrastructure gap viscerally clear.
3. **Choose between short-term survival and long-term scalability** — exactly the strategic trade-off facing real LEO market entrants today.

The ×1.2 vs ×2.5 split is calibrated so the gap is large enough to be unmistakable in the Analytics → Scenario Comparison chart, but the partial Scenario B boost still provides a meaningful advantage over Scenario A — representing the partial benefits of incremental infrastructure improvements even before full dedicated facilities exist.

---

---

## 23. Aviation Blueprint Integration (Salvatore's Research)

This section documents how the team's theoretical research on commercial aviation's democratisation is directly encoded in the simulation constants and mechanics. The goal is to show that every parameter is grounded in historical precedent, not arbitrary game design.

### Core Thesis

Salvatore's analysis identifies aviation's mass-market transition as **supply-driven**, not demand-driven. Demand did not create cheap flights — cheap flights created demand. The same logic governs M.A.R.S.: Scenario B is not a "more optimistic" demand model, it is a model of what happens when supply-side improvements (reusability, infrastructure, safety standardisation) cross a threshold that makes mass access structurally possible.

### Mapping from Research to Code

| Salvatore's Finding | Game Mechanic | Variables |
|---------------------|---------------|-----------|
| Shift from disposable to reusable vehicles | Reusable Stage 1 Tech: −20% costs + Scenario B elasticity +0.7 | `REUSABLE_STAGE1_ELASTICITY_BOOST = 0.7` |
| Transition from airfields to complex logistical hubs | Spaceport Infrastructure Gate (€300M) unlocks full ×2.5 elasticity | `SPACEPORT_COST`, `SCENARIO_B_ELASTIC_MULTIPLIER` |
| Combined reusability + infrastructure = Jet Age elasticity | Full ×3.2 elasticity only when Spaceport + Reusable Stage 1 are both active | `2.5 + 0.7 = 3.2` |
| Repeated safe operations → public trust → routine activity | Safety Streak: +5% demand per consecutive safe mission, capped +15% | `SAFETY_STREAK_DEMAND_BOOST`, `SAFETY_STREAK_MAX_BONUS` |
| 1960s–70s aviation price elasticity (−50% fare → ×3 passengers) | Scenario B elasticity multiplier = 2.5× (conservative vs. historical ~6×) | `SCENARIO_B_ELASTIC_MULTIPLIER = 2.5` |
| Destination-based travel increases perceived value | Long Orbital success in Scenario B gives +3 reputation | `LONG_ORBITAL_DESTINATION_REP_BONUS = 3.0` |
| Aviation addressed practical transportation needs | Scientific missions represent functional space use; Spaceport adds +1 R&D bonus | `SPACEPORT_SCIENTIFIC_RD_BONUS = 1` |
| 70% structural suppression in today's market | Scenario A barrier multiplier (×0.30) | `SCENARIO_A_BARRIER_MULTIPLIER = 0.30` |

### The Three-Level Unlock Path

Salvatore's research implies that democratisation requires convergence of three supply-side improvements. The simulation encodes these as three distinct unlockable states, each providing a measurable gameplay step:

1. **Reusability alone** (Reusable Stage 1, no Spaceport): Costs drop 20%, Scenario B elasticity rises from 1.2 → 1.9. The market is more responsive but still constrained by infrastructure.
2. **Infrastructure alone** (Spaceport, no Reusable): Scenario B elasticity reaches 2.5. Flight cadence can increase, but costs remain high.
3. **Both together** (Spaceport + Reusable Stage 1): Full ×3.2 elasticity. This is the simulation's "Jet Age" state — the combination that historically enabled mass aviation and the only state where aggressive pricing can create genuine passenger volume growth.

### Research Validation for Chapter 5

The simulation constants listed above are not calibrated for fun — they are calibrated for research validity. A player who achieves the Jet Age state in Scenario B and compares the Analytics → Scenario Comparison chart against a Scenario A run is observing the same structural dynamic that Salvatore's research describes: identical inputs, dramatically different outcomes, driven entirely by supply-side conditions.

---

---

## 24. LCC Space Model Integration (Antonio's Research)

This section documents how Antonio's Chapter 4 strategic redesign — the "Low-Cost Carrier Space Model" — is encoded in the simulation. His three pillars (Rapid Reusability, Radical Accessibility, Space-as-a-Service) each map to distinct mechanics that only unlock at sustained R&D investment levels.

### Core Thesis

Antonio argues that partial reusability is insufficient. The LEO market requires a **full structural redesign** analogous to the LCC revolution in aviation: standardised fleets, unbundled revenue, autonomous operation, and subscription-based access models. The simulation encodes this as a four-stage R&D progression where each unlock layer adds a different economic dimension.

### Mapping from Research to Code

| Antonio's Concept | Game Mechanic | Variables |
|-------------------|---------------|-----------|
| Rapid Reusability: LCC standardised fleet | Rapid Reusability unlock (30 pts): variable costs −50% additional | `RAPID_REUSABILITY_COST_REDUCTION = 0.50` |
| Unbundled revenue (base ticket + add-ons) | Ancillary Revenue: +15% per-pax tourist revenue when Rapid Reusability active | `ANCILLARY_REVENUE_MULTIPLIER = 1.15` |
| Autonomous AI navigation | Autonomous Systems unlock (25 pts): TAM ×1.5 across all personas | `AUTONOMOUS_TAM_MULTIPLIER = 1.50` |
| "Select-In" medical policy (older demographics) | Same TAM multiplier — expands UHNW pool to include older wealthy travellers | included in ×1.5 |
| Intermodal modularity (plug-and-play payloads) | Autonomous Systems halves Scientific mission failure penalty | `INTERMODAL_FAILURE_REDUCTION = 0.50` |
| Fractional Ownership / SPaaS | Successful Scientific missions (with Spaceport) add ARR contracts: €5M/turn each | `SPAAS_ARR_PER_CONTRACT = 5M`, `SPAAS_MAX_CONTRACTS = 5` |
| Subscription cash flow stability | SPaaS ARR paid every turn regardless of mission outcome | applied before game-over check |

### The Four-Stage R&D Progression

| Stage | Unlock | Key Effect | Antonio's Pillar |
|-------|--------|------------|-----------------|
| 10 pts | Reusable Stage 1 | −20% costs, Scenario B elasticity +0.7 | Partial reusability (necessary but insufficient) |
| 20 pts | Green Hydrogen | −50% CO₂ | Sustainability baseline |
| 25 pts | Autonomous Systems | TAM ×1.5, Scientific penalty −50% | Radical Accessibility + Intermodal Modularity |
| 30 pts | Rapid Reusability | −50% more costs, +15% ancillary revenue | Full LCC model activation |

To reach Rapid Reusability purely from R&D spend: 30 × €10M = **€300M over 10 turns** (€30M/turn average). Scientific missions with the Spaceport accelerate this via the +3 R&D bonus. The progression rewards players who commit to the full LCC roadmap rather than spreading investment thinly.

### Revenue Architecture at Full Deployment

When all unlocks are active and the player has 5 SPaaS contracts:

```
Per-turn revenue sources:
  Tourist missions:  base revenue × 1.15 (ancillary add-ons)
  Scientific:        contract value + accumulated SPaaS ARR (up to €25M/turn)
  SPaaS ARR floor:   €25M guaranteed regardless of mission outcome

Per-turn variable costs:
  Base ×0.80 (Stage 1) ×0.50 (Rapid) × green reduction ≈ 0.32× base
  Effective variable cost: ~€11–13M vs €35M baseline
```

This is Antonio's target architecture: a business that generates recurring subscription revenue while simultaneously driving down marginal mission costs — the LEO equivalent of Ryanair's operating model.

### Research Value for Chapter 4

The simulation makes Antonio's strategic argument testable. A player who runs two parallel games — one investing heavily in R&D to reach Rapid Reusability, one playing conservative — will see the financial divergence in the Analytics → Scenario Comparison chart. The SPaaS ARR floor is particularly visible: it prevents bankruptcy during mission failures that would otherwise be fatal in a pure per-mission revenue model.

---

---

## 25. Market Stagnation Baseline (Helia's Research)

This section documents how Helia's empirical analysis of today's LEO market supply-side constraints is encoded in the simulation. Her work establishes the **factual foundation for Scenario A** — the three structural bottlenecks that explain why the market has not grown despite demonstrable demand.

### Core Thesis

Helia's finding: *"The issue is the structure of the offer, not the lack of demand."*

The current market stagnation is not caused by a lack of interested buyers. UHNW individuals, government agencies, and research institutions all express real interest in LEO access. What prevents conversion is the **structure of the product itself**: extreme prices, minimal launch cadence, and a complexity barrier that makes participation logistically impossible for most qualified buyers.

This thesis is the logical counterpart to Salvatore's and Antonio's research. Salvatore explains how aviation democratised (supply-driven). Antonio proposes the specific LCC strategy. Helia explains *why* the starting point is so constrained — which is what players experience in Scenario A for the first 3–5 turns.

### The Triad of Stagnation

| Constraint | Helia's Real-World Data | M.A.R.S. Scenario A Implementation |
|---|---|---|
| **Extreme Pricing** | $450k (suborbital) → $50M+ (orbital); ultra-wealthy elite only | Price floor warnings below €450k (suborbital) / €5M (orbital); `SCENARIO_A_BARRIER_MULTIPLIER = 0.30` suppresses 70% of demand |
| **Low Operational Cadence** | 4–6 pax per flight; rare, irregular launches | `SCENARIO_A_AVAILABLE_SLOTS = 2`: max 1–2 launch windows per turn |
| **High Complexity / Low Accessibility** | Weeks of medical screening + simulation training; remote launch sites | `SCENARIO_A_MARKETING_EFFICIENCY = 0.50`: marketing is 50% as effective because advertising cannot overcome the pre-qualification bottleneck |

### Price Floor Calibration

Helia's data provides the real market price reference points that the game uses for advisory warnings:

| Mission Type | Price Floor | Source |
|---|---|---|
| **Short Suborbital** | €450,000 | Virgin Galactic / Blue Origin New Shepard seat pricing |
| **Long Orbital** | €5,000,000 | ISS private astronaut module pricing (Axiom Space range) |

In Scenario A, if a player sets their ticket price below these floors, the backend generates a `⚠️ PRICING NOTE` warning explaining that **price is not the binding constraint**. Dropping below the market floor sacrifices margin without gaining passengers — because the accessibility barrier (not price) is what filters out potential buyers at the commitment stage.

This makes the contrast with Scenario B visceral: in Scenario B, cutting prices below the competitor average *does* generate proportional demand growth (elasticity = 2.5×) because the training/medical barrier has been eliminated. The same price cut that is ineffective in Scenario A becomes the primary growth lever in Scenario B.

### Marketing Efficiency Penalty

**Formula:**
```
effective_marketing = marketing_spend × event_multiplier × SCENARIO_A_MARKETING_EFFICIENCY
marketing_factor = 1.0 + min(effective_marketing × 0.02, 1.0)
```

In Scenario A only, marketing spend is multiplied by `0.50` before computing the demand factor. Helia's finding: advertising creates awareness but cannot overcome the conversion barrier imposed by:
- Medical screening that eliminates many interested buyers
- 2–3 week simulation training commitments
- Travel to remote launch facilities (e.g., Mojave, Van Horn, Boca Chica)
- Insurance and liability paperwork

**Mechanical consequence:** To reach the maximum marketing factor (+100% demand) in Scenario A, a player must spend **€100M** on marketing — twice what it would take in Scenario B. This directly inflates the **Customer Acquisition Cost (CAC)** KPI, matching Helia's prediction that high CAC is a structural symptom of the accessibility problem, not a marketing execution failure.

### Launch Cadence Penalty

In Scenario A, available launch slots per turn are drawn from `randint(0, 2)` — a maximum of 2 slots vs. 3 in Scenario B. This reflects Helia's observation that:
- Regulatory approval timelines constrain launch windows
- Turnaround time without mature reusability is measured in months
- Shared infrastructure (launch pads, range safety, airspace) creates queuing constraints

Practically, players in Scenario A face more frequent slot shortages, forcing either a €10M rush premium or mission cancellation. This adds friction to revenue generation — consistent with Helia's "low cadence" constraint — and rewards investment in infrastructure (Spaceport) and reusability (which together unlock Scenario B cadence).

### Mapping to the Existing KPIs

Helia's research validates the interpretation of all three Strategic KPIs:

| KPI | Scenario A Reading | Helia's Explanation |
|---|---|---|
| **Market Penetration %** | Stays near 0–2% across all turns | The barrier multiplier (×0.30) prevents most potential demand from converting — the market is supply-constrained, not demand-constrained |
| **Customer Acquisition Cost (CAC)** | Very high (€1M+ per passenger) | Accessibility barrier kills the marketing → commitment conversion step; each passenger requires disproportionate outreach |
| **Reputational Vulnerability** | Rises quickly with any failure | Small markets cannot absorb setbacks; a single incident is visible to the entire TAM |

### Research Value for Helia's Chapter

Every Scenario A gameplay session is a direct test of Helia's supply-side stagnation thesis. The three effects are independently measurable:

1. **Price floor effect**: Run a suborbital campaign at €300k — watch demand not improve despite being cheaper than the floor. Switch the same inputs to Scenario B — demand responds immediately. The `⚠️ PRICING NOTE` message appears in Scenario A only, making the structural difference explicit.
2. **Marketing efficiency**: Compare CAC in 10 turns of Scenario A vs. 10 turns of Scenario B with identical marketing spend. Scenario A CAC will be roughly 2× higher.
3. **Cadence penalty**: Count slot shortages across a Scenario A game vs. Scenario B — the higher disruption rate in Scenario A directly quantifies the operational frequency gap Helia identifies.

---

*Last updated: April 2026 — Mission-type-specific competitor markets (suborbital: Virgin Galactic €450k + Blue Origin New Shepard €500k; orbital: SpaceX €8M + Blue Origin €12M + Axiom €15M) · ControlPanel Market Intel tooltip (portal-rendered, mission-type-aware) · News Ticker competitor prices aligned to weighted averages · Reputational Vulnerability formula updated with regulatory neglect term · Financial metrics: total_revenue tracked from actual gross revenue; IRR allows negative values · Game-over flow: ReportCardModal always shown before WinScreen · Market Stagnation Baseline (Helia): price floors, marketing efficiency penalty, scenario-dependent launch cadence · Antonio's LCC Space Model: Autonomous Systems (TAM ×1.5 + intermodal modularity), Rapid Reusability (variable costs −50% + ancillary revenue), SPaaS/Fractional Ownership (ARR contracts) · Aviation Blueprint integration (Salvatore) · Randomized Event Engine · Regulatory & Compliance slider · Spaceport Infrastructure Gate*
