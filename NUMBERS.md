# M.A.R.S. — Numbers Reference

A POC-ready breakdown of every constant, threshold, and formula in the game, with its justification and mechanical role.

---

## 1. Starting Conditions

| Number | Value | Why | Role |
|---|---|---|---|
| Starting budget | €500M | Realistic equity round for a Type 2 LEO operator (comparable to Virgin Galactic pre-revenue raise) | Sets the game's economic horizon; too small → frustrating, too large → no tension |
| Starting reputation | 50/100 | New entrant — some awareness, no track record | Gate for investor funding (requires 70+); shapes early demand |
| Starting vehicles | 1 | Single-vehicle operators are the norm at industry entry | Constrains launch cadence; forces fleet investment decisions |
| Game length | 10 turns | 10 in-game years mirrors realistic first-decade operational horizon | Determines how fast tech/reputation compound |
| Bankruptcy threshold | €0 | Hard floor — can't operate without capital | Immediate game-over trigger |

---

## 2. Mission Types

### Short Suborbital
| Number | Value | Why | Role |
|---|---|---|---|
| Base failure risk | 5% | Proven suborbital profile; Blue Origin NS has flown 25+ missions safely | Lowest-risk option; gateway mission for early turns |
| Revenue per pax | €200k–€400k | Matches 2021–2024 Blue Origin / Virgin Galactic ticket pricing band | Low ceiling; forces volume or mission-type upgrade |
| Failure penalty | €25M (50% of base) | Lower risk → lower operational stakes | Financial shock absorber for early-game failures |

### Long Orbital
| Number | Value | Why | Role |
|---|---|---|---|
| Base failure risk | 15% | ISS-era orbital crew transfer risk profile | Significant risk; rewards safety investment |
| Revenue per pax | €5M–€10M | Axiom Space ISS module pricing; SpaceX Inspiration4 commercial seat pricing | High ceiling; the main revenue engine mid-game |
| Safety tech requirement | Level 5 | Orbital missions need sustained safety investment (50M+ cumulative) before they're viable | Forces a choice: rush orbital or build the safety stack first |
| Failure penalty | €50M (1× base) | Higher mission complexity → higher recovery costs | Meaningful but survivable |

### Scientific
| Number | Value | Why | Role |
|---|---|---|---|
| Base failure risk | 25% | Experimental payload missions have historically higher failure rates (cf. early commercial satellite launches) | High-risk / high-reward; best R&D return |
| Revenue model | Fixed contract value | Government/agency contracts are fixed-fee, not per-pax | Revenue certainty but exposure to full failure penalty |
| Failure penalty | €75M (1.5× base) | Payload loss + contract damages | Punishing without contingency cover |
| R&D bonus on success | +2 points | Research mission accelerates in-house capability | Science missions can be the fastest path to tech unlocks |

---

## 3. Cost Structure

| Number | Value | Why | Role |
|---|---|---|---|
| Fixed costs | €5M/turn | Salaries, maintenance, facilities — minimum viable ops cost | Baseline burn even if no mission runs |
| Fuel cost per launch | €15M | Cryogenic propellant cost for a LEO-class vehicle (cf. Falcon 9 fuel ~$300k but total operational cost scales) | Largest variable cost driver |
| Base launch cost | €20M | Ground ops, range fees, recovery logistics | Combined with fuel: €35M variable floor per mission |
| Green tech cost reduction | 1%/point | Each green investment tranche marginally improves fuel efficiency | Incentivises green investment without making it mandatory |

**Variable cost reduction stack (multiplicative):**
- Reusable Stage 1 unlock: −20%
- Rapid Reusability unlock (LCC model): additional −50%
- HR efficiency: cost ÷ efficiency multiplier (max 2×, so up to −50%)

At full stack: base €35M variable → as low as ~€8.75M per launch.

---

## 4. Demand & Market Model

### Base Mechanics
| Number | Value | Why | Role |
|---|---|---|---|
| Orbital competitor combined share | 90% (SpaceX 45% + BO 25% + Axiom 20%) | Reflects real incumbent dominance; player starts with ~10% addressable orbital market | Forces differentiation rather than volume competition |
| Suborbital competitor combined share | 60% (Virgin Galactic 25% + BO New Shepard 35%) | Less consolidated than orbital; player starts with ~40% addressable suborbital market | Lower share cliff; more accessible early-game |
| Player base addressable share | ~10% orbital / ~40% suborbital (minimum 2%) | Whatever incumbents don't own | Starting point for share-stealing |
| Price steal cap | +15% share | Under-cutting price aggressively can chip away at competitors | Rewards pricing strategy without making price the only lever |
| Safety steal cap | +10% share | Out-performing on safety attracts safety-conscious buyers | Rewards safety investment with market upside, not just risk reduction |
| Marketing effectiveness cap | +100% demand at €50M | Logarithmic: big early gains, diminishing returns above €25M | Prevents "just spend more on marketing" as a dominant strategy |
| Safety score formula | 50 + safety_invest/€2M (cap 100) | €0 invest → 50/100 base score; €100M → capped at 100 | Linear safety-to-score conversion |

### Scenario A (Current Market)
| Number | Value | Why | Role |
|---|---|---|---|
| Per-persona demand cap | 1 pax/turn | Structural barrier: medical screening + training + remote site logistics kill conversion even with unlimited interest | Hard ceiling that money alone can't overcome |
| Structural suppression | ×0.30 (70% suppressed) | Helia: "the issue is the structure of the offer, not the lack of demand" — real addressable market is tiny today | Makes Scenario A a low-revenue grind regardless of pricing |
| Marketing efficiency | 50% | Interest ≠ conversion in Scenario A — awareness doesn't move people past the accessibility barrier | Marketing ROI halved vs. Scenario B |
| Max launch slots | 0–2/turn | Low operational cadence: regulatory bottlenecks, long turnarounds | Slot scarcity can force a rush fee or cancellation |
| Suborbital price floor | €450k | Virgin Galactic / Blue Origin New Shepard real market baseline | Reference for competitor pricing reality |
| Orbital price floor | €5M | ISS module pricing baseline | Reference for competitor pricing reality |

Note: the competitor avg price used in demand calculations is mission-type-specific — see Section 6.

### Scenario B (Evolved Market)
| Number | Value | Why | Role |
|---|---|---|---|
| Elastic multiplier (with spaceport) | ×2.5 | Aviation analogy: price drops → super-proportional demand growth (Jet Age) | Scenario B is dramatically more rewarding for low prices |
| Elastic multiplier (no spaceport) | ×1.2 | Partial benefit without infrastructure | Spaceport becomes a meaningful strategic unlock in Scenario B |
| Reusable Stage 1 elasticity bonus | +0.7 (2.5 → 3.2 effective) | Salvatore: repeated reuse transforms market economics, the "Jet Age turning point" | Stacking reusability + spaceport = max demand responsiveness |
| Max launch slots | 0–3/turn | Better infrastructure and cadence in evolved market | Meaningful improvement over Scenario A |

---

## 5. Customer Personas

Three personas respond differently to the same offer. All scores are 0–1 sensitivity weights.

| Persona | Price Sensitivity | Safety Sensitivity | Base Pool | Who they represent |
|---|---|---|---|---|
| UHNW Tourists | 0.4 (low) | 0.9 (high) | 5 pax | Ultra-high-net-worth thrill-seekers; will pay almost anything but won't risk their lives |
| Government | 0.2 (very low) | 1.5 (very high) | 3 pax | Agencies; budgets are fixed but safety is a political non-negotiable |
| Research / Industrial | 0.8 (high) | 0.6 (moderate) | 4 pax | Universities, corporates; budget-constrained but not as risk-averse as gov |

**Formula per persona:**
```
raw = base_pool × price_factor × safety_factor × marketing_factor × rep_factor
price_factor = (comp_avg_price / ticket_price) ^ price_sensitivity
safety_factor = (safety_score / 100) ^ safety_sensitivity
```

`comp_avg_price` is **mission-type-specific**: ~€479k for Short Suborbital, ~€10.67M for Long Orbital and Scientific. Using the correct market segment prevents the absurdity of a €1M suborbital ticket appearing ultra-cheap relative to a €10.67M orbital benchmark.

---

## 6. Competitor Reference Data

Fixed environmental constants (don't change during gameplay — they're the market backdrop). Competitors are split by mission type because suborbital and orbital are distinct markets with different price ranges.

### Suborbital Competitors (Short Suborbital missions)

| Competitor | Price | Safety | Market Share | Why these numbers |
|---|---|---|---|---|
| Virgin Galactic | €450k | 65/100 | 25% | SpaceShipTwo commercial ticket price before 2023 suspension; 2014 accident depresses safety score |
| Blue Origin (New Shepard) | €500k | 82/100 | 35% | Slight premium over VG; 2022 anomaly reduced score; returned to flight 2024; dominant post-VG |

**Suborbital weighted-average price: ~€479k** — the benchmark for price_factor in Short Suborbital demand.  
**Suborbital weighted-average safety: ~75/100** — the reference for safety share-stealing.  
**Combined suborbital competitor share: 60%** — player starts with ~40% of addressable suborbital market.

### Orbital Competitors (Long Orbital and Scientific missions)

| Competitor | Price | Safety | Market Share | Why these numbers |
|---|---|---|---|---|
| SpaceX | €8M | 90/100 | 45% | Falcon 9 / Dragon per-seat pricing; highest safety record; dominant incumbent |
| Blue Origin | €12M | 75/100 | 25% | Projected New Glenn / orbital tourism pricing; less proven than SpaceX at orbital level |
| Axiom Space | €15M | 80/100 | 20% | ISS private astronaut missions at ~$55M/seat; premium for training and mission management |

**Orbital weighted-average price: ~€10.67M** — the benchmark for price_factor in Long Orbital and Scientific demand.  
**Orbital weighted-average safety: ~85/100** — the reference for safety share-stealing.  
**Combined orbital competitor share: 90%** — player starts with ~10% of addressable orbital market.

---

## 7. Technology Tree

| Unlock | R&D Threshold | Effect | Why |
|---|---|---|---|
| Reusable Stage 1 | 10 pts (€100M R&D) | −20% variable costs; +0.7 Scenario B elasticity | SpaceX Falcon 9 first-stage reuse reduces marginal cost by ~30% in reality |
| Green Hydrogen | 20 pts (€200M R&D) | −50% CO2 per launch | Liquid hydrogen propulsion is the leading zero-carbon propellant pathway |
| Autonomous Systems | 25 pts (€250M R&D) | +50% TAM across all personas; −50% Scientific failure penalty | Antonio: AI navigation removes 2–3 year physiological training requirement; opens older/corporate demographics |
| Rapid Reusability | 30 pts (€300M R&D) | Additional −50% variable costs on top of Stage 1; +15% per-pax tourist revenue (ancillary services) | Antonio: LCC model — standardised fleet + unbundled ancillaries (cf. Ryanair economics) |

**R&D progression rate:** every €10M R&D spend = +1 tech point. Scientific mission success = +2 bonus points (+3 with spaceport).

**Safety progression rate:** every €10M safety spend = +1 safety tech point.

---

## 8. HR System

| Number | Value | Why | Role |
|---|---|---|---|
| Efficiency formula | 1.0 + log₁₀(HR_millions) × 0.3 | Logarithmic: training ROI diminishes at scale; first investments have the highest impact | €1M → 1.0×; €10M → 1.3×; €100M → 1.6×; cap at 2.0× |
| Efficiency cap | 2.0× (200%) | Even the best-trained crew can't halve costs indefinitely | Prevents HR from becoming an infinite cost sink |
| Saving throw threshold | HR efficiency > 1.5× | High-efficiency crews can salvage a mission that statistically should have failed | Rewards sustained HR investment; not a first-turn trick |
| Saving throw success rate | 30% | Not a guarantee — a last resort | Creates meaningful tension, not a cheat code |
| Cost reduction from HR | variable costs ÷ efficiency | Better ops = lower per-launch operational overhead | Cross-system: HR investment lowers costs across all mission types |

---

## 9. Investor System

### Real-Time Investor Offers (player-controlled, Investor tab)

| Number | Value | Why | Role |
|---|---|---|---|
| Offer range | €10M – €500M | Player chooses the amount each time | Full capital flexibility; high offers carry lower acceptance chance |
| Base acceptance chance | 20% | Starting probability before any modifiers | Ensures no offer is ever automatically accepted |
| Offer size penalty | −0.005% per €1M | Larger asks face more investor scrutiny | Discourages reflexively maximizing offer size |
| Preference bonus — safety / CO2 / tech investors | up to +30% | Each investor type weights a specific company stat | Rewards building in the direction that matches who you pitch |
| Preference bonus — reputation / financial investors | up to +40% | Financial investors weight track record most heavily | Highest bonus type; reputation management has a direct investor payoff |
| Preference bonus — balanced investors | up to +25% | All factors contribute small amounts | No single-stat play dominates; hardest type to optimize for |
| Reputation bonus (all investor types) | +0.2% per reputation point | Universal credibility signal across all investor types | Stack this with the preference bonus for best results |
| Acceptance chance ceiling / floor | 5% – 95% | No outcome is ever fully certain | Maintains real risk even in ideal conditions |
| Budget impact if accepted | +full offer amount (immediately) | Funding added to budget outside the turn cycle | Real-time capital raise; no need to wait for a turn |
| Reputation if accepted | +2 to +5 (scales with offer size) | Market reads investor acceptance as validation | Small but real upside; larger accepted offers give more |
| Reputation if rejected | −1 to −3 (scales with offer size) | Rejection signals lack of investor confidence | Raises the cost of speculative high-amount pitches |
| ROI target after accepted offer | avg profit × 1.15 (min: offer × 10%) | Investor expects 15% above your historical profit track record | Post-funding accountability; uses the higher of historical or offer-based floor |


---

## 10. Fleet Management

| Number | Value | Why | Role |
|---|---|---|---|
| Vehicle cost | €150M | Rough order of magnitude for a reusable LEO-class vehicle (cf. Starship development cost per vehicle, scaled) | Significant capital decision; changes budget trajectory for 2+ turns |
| Build time | 1 turn | Simplified for gameplay; real timelines are 3–5 years | Creates a 1-turn delay forcing forward planning |
| Rush launch fee | €10M | Priority range/FAA slot cost | Trade-off: pay now vs. wait for next slot |
| Cancellation fee | €5M | Contract break and rebooking cost | Penalises over-committing to launches without slots |

---

## 11. Regulatory Compliance

| Number | Value | Why | Role |
|---|---|---|---|
| Recommended minimum spend | €5M/turn | FAA/EASA ongoing compliance cost for commercial spaceflight | Players who skip this accumulate vulnerability |
| Zero-spend reputation penalty | −3 reputation | Public and regulatory optics of zero compliance investment | Soft early deterrent |
| Vulnerability penalty | +15 reputational vulnerability | Underspend creates structural risk to future demand even if nothing has gone wrong yet | Links regulatory neglect to long-term brand risk |

---

## 12. Spaceport

| Number | Value | Why | Role |
|---|---|---|---|
| Cost | €300M | Realistic range for greenfield commercial spaceport development (cf. Space Hub Sutherland, Spaceport Cornwall estimates) | Major capital allocation; takes 2 turns to pay back |
| Build time | 1 turn | Simplified; real permits + construction = 5–10 years | Forces 1-turn planning lag |
| Scenario B benefit | Unlocks full ×2.5 elasticity multiplier | Infrastructure is the prerequisite for Evolved Market dynamics | Scenario B is largely gated behind the spaceport investment |
| Scientific mission R&D bonus | +1 extra R&D point per success | Salvatore: "aviation addressed practical transportation needs through functional use" | Stacks with the base +2 for Scientific missions |
| SPaaS contract unlock | +1 contract per successful Scientific mission (max 5) | Antonio: Fractional Ownership — research institutions buy shares of modules rather than full missions | Generates €5M ARR per contract per turn |
| SPaaS ARR per contract | €5M/turn | Stable recurring revenue in line with small reseaؤrch satellite leasing rates | Creates reliable baseline cash flow late-game |

---

## 13. Safety Streak Bonus

| Number | Value | Why | Role |
|---|---|---|---|
| Demand boost per consecutive safe mission | +5% | Salvatore: sustained safety record builds public trust → routine activity | Rewards consistency over single-turn optimisation |
| Maximum streak bonus | +15% (3 missions) | Cap prevents compounding into an unrealistic multiplier | Achievable ceiling; one failure resets to zero |

---

## 14. Failure Penalties & Contingency

| Number | Value | Why | Role |
|---|---|---|---|
| Base penalty | €50M | Loss of vehicle, insurance payouts, investigation costs | Significant without being company-ending on first occurrence |
| Short Suborbital multiplier | 0.5× → €25M | Lower stakes, lower operational scope | Proportional to mission complexity |
| Long Orbital multiplier | 1.0× → €50M | Standard orbital risk profile | Baseline |
| Scientific multiplier | 1.5× → €75M | Payload loss + agency contract damages | Highest single-event cost |
| Intermodal failure reduction (Autonomous Systems) | −50% Scientific penalty | Antonio: plug-and-play modularity reduces total payload loss on anomaly | Autonomous Systems unlock has a safety economics benefit |
| Contingency formula | `actual_loss = max(0, penalty − contingency_budget)` | Contingency acts as an insurance reserve | Clean trade-off: set aside capital now vs. absorb shock later |

---

## 15. Reputation Dynamics

| Number | Value | Why | Role |
|---|---|---|---|
| Success bonus | +2/turn | Incremental trust from reliable operations | Slow but steady accumulation |
| Failure penalty | −20/turn | One failure erases ~10 turns of successful operation | High asymmetry; reputation is fragile |
| Marketing boost | +0.1 per €1M | Brand investment builds awareness → reputation | Caps at impractical marketing levels; not a substitute for operations |
| Long Orbital Scenario B bonus | +3 on success | Axiom-style destination experience raises perceived brand value | Scenario B-only reward for committing to the harder mission |
| Reputation range | 0–100 | Normalised score | Input to demand formula and investor gate |

---

## 16. Financial Metrics

| Metric | Formula | Parameters | Why |
|---|---|---|---|
| NPV | Σ(cash_flow_t / (1+r)^t) | r = 5% discount rate | 5% approximates a risk-free rate + minimal space industry risk premium; keeps NPV meaningful without penalising early turns too heavily |
| ROI | (total_profit / total_investment) × 100 | Investments = all non-fixed spending | Simple capital efficiency measure |
| IRR | Newton-Raphson on NPV = 0; range clamped to [−99%, 1000%] | Initial investment = €500M (starting budget) | Rate at which the game's cash flows pay back the starting capital; **can be negative** if cumulative cash flows never recover the starting budget — meaningful signal in Scenario A |
| Total Revenue | `GameState.total_revenue_earned` accumulated each turn | Mission revenue + SPaaS ARR + ancillary | Tracked directly, not derived from profit sign — prevents mislabelling negative profits as "costs" |
| Total Costs | total_revenue − total_profit | Derived from actual revenue | All money spent (fixed, variable, investments) expressed as revenue minus net profit |
| Profit Margin | (total_profit / total_revenue) × 100 | — | Revenue efficiency; negative if cumulative losses exceed cumulative gains |
| Market penetration | (total_passengers / cumulative_potential_demand) × 100 | — | Low in Scenario A (structural barriers), high in Scenario B |
| Customer Acquisition Cost | total_marketing_spend / total_passengers | — | Measures marketing efficiency over the game |
| Reputational Vulnerability | `((100 − rep)/100 + min(incidents×0.05, 0.50) + min(zero_reg_turns×0.05, 0.25)) × 100` | — | Composite risk score: reputation deficit + safety incident history + regulatory neglect streak; regulatory term (max +25 pts) penalises zero-compliance cost-cutting even with no direct failures |

---

## 17. CO2 Tracking

| Number | Value | Why | Role |
|---|---|---|---|
| Base CO2 per launch | 100 units | Normalised index (not real tonnes; comparable to a Falcon 9 profile) | Environmental KPI for scoring |
| Green tech reduction | 2%/point | Each green investment tranche reduces emissions slightly | Long-term sustainability track |
| Green Hydrogen unlock | additional −50% | Hydrogen propulsion eliminates most carbon emissions (H₂ + O₂ → H₂O) | Significant jump at the 20-point tech threshold |

---

## 18. Competitor Price Reference Points

Competitor prices are **fixed constants** defined in `GlobalConfig` — they do not drift during gameplay. The market backdrop is static; what changes is the player's position relative to it. The weighted averages by segment:

| Segment | Weighted Avg Price | Weighted Avg Safety |
|---|---|---|
| Short Suborbital | ~€479k | ~75/100 |
| Long Orbital / Scientific | ~€10.67M | ~85/100 |

These averages are the reference points for price_factor and safety share-stealing in all demand calculations. They also appear verbatim in the ControlPanel Market Intel tooltip and the News Ticker competitor landscape panel, so the numbers players see in the UI always match the numbers the engine uses.

---

## Key Interdependencies to Discuss with POC

1. **Safety investment has three separate roles:** (a) reduces failure probability, (b) unlocks Long Orbital at level 5, (c) increases market share via safety score — these should be surfaced clearly in the UI.

2. **Scenario A vs B is the central strategic fork.** All of Helia's supply-side research (barriers, cadence, pricing floors) lives in Scenario A numbers. All of Salvatore's aviation-analogy and Antonio's LCC model numbers become active in Scenario B. The spaceport is the gate.

3. **The 10% discount rate on NPV vs. 5%:** currently 5% — deliberately conservative to keep NPV numbers legible in a 10-turn game. A 10% rate would roughly halve later-year cash flow present values and make the IRR calculation more demanding. Worth discussing whether to match a specific real-world benchmark.

4. **The reputation asymmetry (+2 success / −20 failure)** is intentional design tension, not a balance mistake. It mirrors how brand damage in public-safety industries works (one incident = years of trust recovery). Can be adjusted if playtesting shows it makes the game too punishing.
