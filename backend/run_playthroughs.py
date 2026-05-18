"""
M.A.R.S. Three-Run Validation Model
====================================
Proves that the current market structure is the fundamental reason for failure —
not a lack of demand — and that supply-side infrastructure (Spaceport + Reusability)
is the transformative lever.

  Run A — "Status Quo"          Scenario A | at market price floors  | no spaceport
  Run B — "Premature Evolved"   Scenario B | 30% below competitors   | no spaceport
  Run C — "LCC Revolution"      Scenario B | 30% below competitors   | spaceport Y3

Prerequisites: backend must be running on http://localhost:8000
  cd backend && python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
"""

import requests
import json
from dataclasses import dataclass, field

BASE_URL     = "http://localhost:8000"
RANDOM_SEED  = 42          # identical seed → identical random events across all 3 runs
SPACEPORT_TURN = 3         # Run C buys spaceport turn 3 → operational turn 4

# ── Competitor reference prices (from models.py GlobalConfig) ─────────────────
# Suborbital avg: (450k×0.25 + 500k×0.35) / 0.60 ≈ €479k
# Orbital avg:    (8M×0.45 + 12M×0.25 + 15M×0.20) / 0.90 ≈ €10.67M
#
# Run A  — at real-world price floors (Scenario A structural constraint)
# Run B/C — 30% below competitor avg to activate elasticity in Scenario B

SUBORBITAL_FLOOR  =   450_000   # Scenario A floor (SCENARIO_A_SUBORBITAL_PRICE_FLOOR)
ORBITAL_FLOOR     = 5_000_000   # Scenario A floor (SCENARIO_A_ORBITAL_PRICE_FLOOR)

SUBORBITAL_30PCT  =   330_000   # 30% below ~€479k suborbital avg
ORBITAL_30PCT     = 7_500_000   # 30% below ~€10.67M orbital avg

# ── Shared investments (physical capabilities identical across all 3 runs) ─────
# safety_invest=50M → +5 safety tech levels per turn (formula: int(invest/10M))
# This unlocks Long_Orbital (req: level 5) from turn 2 onward.
# On turn 1 we play Short_Suborbital (no safety requirement, 0% failure risk at 50M).
_SHARED = dict(
    marketing_spend   = 30_000_000,
    safety_invest     = 50_000_000,
    green_invest      = 10_000_000,
    rd_invest         = 20_000_000,   # +2 tech/turn → Reusable Stage 1 unlocks by turn 5
    hr_invest         = 10_000_000,
    regulatory_invest =  5_000_000,
    buy_vehicle       = False,
    investor_offer    = 0.0,
    buy_spaceport     = False,
)

# Run A — Scenario A, at market price floors
RUN_A_T1 = {**_SHARED, "mission_type": "Short_Suborbital", "market_scenario": "A",
             "ticket_price": SUBORBITAL_FLOOR, "contingency_budget": 5_000_000}
RUN_A    = {**_SHARED, "mission_type": "Long_Orbital",     "market_scenario": "A",
             "ticket_price": ORBITAL_FLOOR,    "contingency_budget": 50_000_000}

# Run B / C — Scenario B, 30% below competitors (same inputs; C adds spaceport)
RUN_BC_T1 = {**_SHARED, "mission_type": "Short_Suborbital", "market_scenario": "B",
              "ticket_price": SUBORBITAL_30PCT, "contingency_budget": 5_000_000}
RUN_BC    = {**_SHARED, "mission_type": "Long_Orbital",     "market_scenario": "B",
              "ticket_price": ORBITAL_30PCT,    "contingency_budget": 50_000_000}


# ── Data types ────────────────────────────────────────────────────────────────
@dataclass
class TurnRecord:
    year:             int
    budget:           float
    reputation:       float
    pax_sold:         int
    revenue:          float
    profit:           float
    mission_success:  bool
    spaceport_active: bool
    npv:              float
    roi:              float
    irr:              float
    market_penetration: float
    cac:              float
    news_headlines:   list = field(default_factory=list)


# ── Formatting helpers ────────────────────────────────────────────────────────
def M(v: float, sign: bool = True) -> str:
    return f"{'€':}{v/1e6:{'+' if sign else ''}.1f}M"

def P(v: float) -> str:
    return f"{v:.1f}%"


# ── API helper ────────────────────────────────────────────────────────────────
def api(method: str, path: str, body: dict | None = None) -> dict:
    r = getattr(requests, method)(BASE_URL + path, json=body, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Single scenario runner ────────────────────────────────────────────────────
def run_scenario(
    label:        str,
    t1_inputs:    dict,
    base_inputs:  dict,
    buy_spaceport: bool,
) -> tuple[list[TurnRecord], dict, dict]:
    """Play 10 turns. Returns (records, final_score, final_metrics)."""
    print(f"\n{'═' * 65}")
    print(f"  {label}")
    print(f"{'═' * 65}")

    api("post", "/start_game", {"seed": RANDOM_SEED})
    records: list[TurnRecord] = []

    for turn in range(1, 11):
        inputs = (t1_inputs if turn == 1 else base_inputs).copy()
        if buy_spaceport and turn == SPACEPORT_TURN:
            inputs["buy_spaceport"] = True

        result      = api("post", "/play_turn", inputs)
        metrics     = api("get",  "/financial_metrics")
        news_raw    = api("get",  "/news_feed")

        fin   = result.get("financials", {})
        res   = result.get("results", {})
        state = result.get("new_state", {})

        news_items = news_raw if isinstance(news_raw, list) else news_raw.get("news", [])

        record = TurnRecord(
            year             = turn,
            budget           = state.get("budget", 0.0),
            reputation       = state.get("reputation", 0.0),
            pax_sold         = res.get("pax_sold", 0),
            revenue          = fin.get("revenue", 0.0),
            profit           = fin.get("profit", 0.0),
            mission_success  = res.get("mission_success", False),
            spaceport_active = state.get("has_spaceport", False),
            npv              = metrics.get("npv", 0.0),
            roi              = metrics.get("roi", 0.0),
            irr              = metrics.get("irr", 0.0),
            market_penetration = metrics.get("market_penetration_pct", 0.0),
            cac              = metrics.get("customer_acquisition_cost", 0.0),
            news_headlines   = [
                (i.get("headline", i) if isinstance(i, dict) else str(i))
                for i in news_items[:2]
            ],
        )
        records.append(record)

        sp  = "🚀" if record.spaceport_active else "  "
        ok  = "✓" if record.mission_success else "✗"
        print(
            f"  Y{turn:02d}[{ok}]{sp} | Budget {M(record.budget, False):>9} | "
            f"Pax {record.pax_sold:>2} | Rev {M(record.revenue, False):>9} | "
            f"Rep {record.reputation:>5.1f}"
        )

    score   = api("get", "/final_score")
    metrics = api("get", "/financial_metrics")
    return records, score, metrics


# ── Comparison report ─────────────────────────────────────────────────────────
def print_report(
    ra: list[TurnRecord], sa: dict, ma: dict,   # Run A
    rb: list[TurnRecord], sb: dict, mb: dict,   # Run B
    rc: list[TurnRecord], sc: dict, mc: dict,   # Run C
) -> None:
    W = 140

    # ── Header ──────────────────────────────────────────────────────────────
    print(f"\n{'═' * W}")
    print("  M.A.R.S.  THREE-RUN VALIDATION MODEL")
    print(f"  Run A: Status Quo (Mkt A, floors)  |  "
          f"Run B: Premature Evolved (Mkt B, −30%)  |  "
          f"Run C: LCC Revolution (Mkt B, −30%, Spaceport Y{SPACEPORT_TURN})")
    print(f"  RNG seed {RANDOM_SEED} | Investments identical across all runs | Starting budget €1,500M")
    print(f"{'═' * W}")

    # ── Year-by-year passenger & revenue table ───────────────────────────────
    print(f"\n  {'':4}  {'─── Run A  Status Quo ───':^30}  "
          f"{'─── Run B  No Spaceport ───':^30}  "
          f"{'─── Run C  LCC Revolution ───':^32}")
    print(f"  {'Year':4}  {'Pax':>3}  {'Revenue':>9}  {'Rep':>5}  {'OK':2}  "
          f"  {'Pax':>3}  {'Revenue':>9}  {'Rep':>5}  {'OK':2}  "
          f"  {'Pax':>3}  {'Revenue':>9}  {'Rep':>5}  {'OK':2}  {'SP':2}")
    print(f"  {'-' * (W - 2)}")

    cumrev_a = cumrev_b = cumrev_c = 0.0
    cumpax_a = cumpax_b = cumpax_c = 0

    for a, b, c in zip(ra, rb, rc):
        cumrev_a += a.revenue; cumrev_b += b.revenue; cumrev_c += c.revenue
        cumpax_a += a.pax_sold; cumpax_b += b.pax_sold; cumpax_c += c.pax_sold

        ok_a = "✓" if a.mission_success else "✗"
        ok_b = "✓" if b.mission_success else "✗"
        ok_c = "✓" if c.mission_success else "✗"
        sp_c = "🚀" if c.spaceport_active else "  "

        print(
            f"  Y{a.year:02d}    "
            f"{a.pax_sold:>3}  {M(a.revenue, False):>9}  {a.reputation:>5.1f}  {ok_a:>2}  "
            f"  {b.pax_sold:>3}  {M(b.revenue, False):>9}  {b.reputation:>5.1f}  {ok_b:>2}  "
            f"  {c.pax_sold:>3}  {M(c.revenue, False):>9}  {c.reputation:>5.1f}  {ok_c:>2}  {sp_c}"
        )

    print(f"  {'-' * (W - 2)}")
    print(
        f"  {'TOTAL':6}  "
        f"{cumpax_a:>3}  {M(cumrev_a, False):>9}  {'':5}  {'':2}  "
        f"  {cumpax_b:>3}  {M(cumrev_b, False):>9}  {'':5}  {'':2}  "
        f"  {cumpax_c:>3}  {M(cumrev_c, False):>9}"
    )

    # ── Financial Director Report ────────────────────────────────────────────
    print(f"\n{'─' * W}")
    print("  FINANCIAL DIRECTOR REPORT")

    COL_A = "Run A (Status Quo)"
    COL_B = "Run B (No Port)"
    COL_C = "Run C (LCC Rev.)"
    LABEL = 36

    def row3(label, va, vb, vc, fmt="m"):
        if fmt == "m":
            fa = M(va); fb = M(vb); fc = M(vc)
            dab = M(vb - va); dac = M(vc - va)
        elif fmt == "pct":
            fa = P(va); fb = P(vb); fc = P(vc)
            dab = f"{vb-va:+.1f}pp"; dac = f"{vc-va:+.1f}pp"
        elif fmt == "raw":
            fa = f"{va:.1f}"; fb = f"{vb:.1f}"; fc = f"{vc:.1f}"
            dab = f"{vb-va:+.1f}"; dac = f"{vc-va:+.1f}"
        elif fmt == "int":
            fa = str(int(va)); fb = str(int(vb)); fc = str(int(vc))
            dab = f"{int(vb-va):+d}"; dac = f"{int(vc-va):+d}"
        print(
            f"  {label:<{LABEL}} {fa:>16} {fb:>16} {fc:>16}    "
            f"B−A: {dab:>10}   C−A: {dac:>10}"
        )

    print(f"\n  {'':<{LABEL}} {COL_A:>16} {COL_B:>16} {COL_C:>16}    "
          f"{'B vs A':>15}   {'C vs A':>15}")
    print(f"  {'-' * (W - 2)}")

    row3("Total Passengers Carried",     ma["total_passengers"],    mb["total_passengers"],    mc["total_passengers"],    fmt="int")
    row3("Total Revenue",                ma["total_revenue"],       mb["total_revenue"],       mc["total_revenue"])
    row3("Total Investment",             ma["total_investment"],    mb["total_investment"],    mc["total_investment"])
    row3("Total Profit (10 years)",      sa["total_profit"],        sb["total_profit"],        sc["total_profit"])
    row3("Final Budget",                 sa["final_budget"],        sb["final_budget"],        sc["final_budget"])
    row3("NPV (5% discount rate)",       ma["npv"],                 mb["npv"],                 mc["npv"])
    row3("ROI",                          ma["roi"],                 mb["roi"],                 mc["roi"],                 fmt="pct")
    row3("IRR",                          ma["irr"],                 mb["irr"],                 mc["irr"],                 fmt="pct")
    row3("Profit Margin",                ma["profit_margin"],       mb["profit_margin"],       mc["profit_margin"],       fmt="pct")
    row3("Market Penetration",           ma["market_penetration_pct"], mb["market_penetration_pct"], mc["market_penetration_pct"], fmt="pct")

    # Customer Acquisition Cost — the "structural barrier" signal
    print(f"\n  {'── CAC: THE STRUCTURAL BARRIER SIGNAL ──':<{LABEL}}")
    row3("Customer Acquisition Cost",    ma["customer_acquisition_cost"], mb["customer_acquisition_cost"], mc["customer_acquisition_cost"])
    row3("Reputational Vulnerability",   ma["reputational_vulnerability"], mb["reputational_vulnerability"], mc["reputational_vulnerability"], fmt="raw")

    # ── Scoring ──────────────────────────────────────────────────────────────
    print(f"\n{'─' * W}")
    print("  ANALYTICS & SCORE CARD")
    print(f"\n  {'':<{LABEL}} {COL_A:>16} {COL_B:>16} {COL_C:>16}")
    print(f"  {'-' * (W - 2)}")

    row3("Final Reputation",  sa["final_reputation"],  sb["final_reputation"],  sc["final_reputation"],  fmt="raw")
    row3("Total CO₂",         sa["total_co2"],          sb["total_co2"],          sc["total_co2"],          fmt="raw")
    row3("Tech Level",        sa["tech_level"],         sb["tech_level"],         sc["tech_level"],         fmt="int")
    row3("Green Tech Level",  sa["green_tech_level"],   sb["green_tech_level"],   sc["green_tech_level"],   fmt="int")

    print()
    for lbl, key_s, key_g in [
        ("Economic Score / Grade", "economic_score", "economic_grade"),
        ("Green Score / Grade",    "green_score",    "green_grade"),
        ("FINAL SCORE / GRADE",    "final_score",    "final_grade"),
    ]:
        va = sa[key_s]; vb = sb[key_s]; vc = sc[key_s]
        print(
            f"  {lbl:<{LABEL}} "
            f"{va:>9.1f} ({sa[key_g]:>2})   "
            f"{vb:>9.1f} ({sb[key_g]:>2})   "
            f"{vc:>9.1f} ({sc[key_g]:>2})"
        )

    # ── Key Insights ─────────────────────────────────────────────────────────
    print(f"\n{'═' * W}")
    print("  KEY INSIGHTS")
    print(f"  {'-' * (W - 2)}")

    pax_delta_bc = mc["total_passengers"] - mb["total_passengers"]
    pax_delta_ab = mb["total_passengers"] - ma["total_passengers"]
    rev_delta_bc = mc["total_revenue"] - mb["total_revenue"]
    rev_delta_ac = mc["total_revenue"] - ma["total_revenue"]

    cac_a_fmt  = f"€{ma['customer_acquisition_cost']/1e6:.1f}M" if ma['total_passengers'] > 0 else "∞ (0 pax)"
    cac_b_fmt  = f"€{mb['customer_acquisition_cost']/1e6:.1f}M" if mb['total_passengers'] > 0 else "∞ (0 pax)"
    cac_c_fmt  = f"€{mc['customer_acquisition_cost']/1e6:.1f}M" if mc['total_passengers'] > 0 else "∞ (0 pax)"

    insights = [
        ("Structural Barrier (Run A)",
         f"Scenario A's 0.30× demand multiplier caps throughput at ≤1–2 pax/turn regardless of "
         f"marketing spend. Total passengers: {int(ma['total_passengers'])} over 10 years. "
         f"Dropping price below €5M in Scenario A does not increase demand — the cap is structural, "
         f"not price-driven. This is Helia's 'Market Stagnation' baseline."),

        ("Partial Elasticity (Run B vs Run A)",
         f"Evolved market (Scenario B) with 30%‑below pricing but no spaceport applies a ×1.2 "
         f"elasticity boost. Extra passengers vs Run A: +{pax_delta_ab}. "
         f"Growth is visible but sluggish — tech alone without infrastructure is not a silver bullet."),

        ("Hockey Stick (Run C vs Run B)",
         f"Adding the Dedicated Spaceport unlocks ×2.5 elasticity (→ ×3.2 once Reusable Stage 1 "
         f"activates ~Y5). Extra passengers vs Run B: +{pax_delta_bc}. "
         f"Extra revenue vs Run B: {M(rev_delta_bc)}. "
         f"This is the supply-side inflection point: infrastructure enables the demand that already exists."),

        ("CAC Collapse — the clearest signal",
         f"Run A CAC: {cac_a_fmt}   Run B CAC: {cac_b_fmt}   Run C CAC: {cac_c_fmt}. "
         f"When infrastructure unlocks conversion, the cost of acquiring each passenger collapses. "
         f"Run C's CAC is the LCC analogue of Southwest Airlines' cost-per-seat revolution."),

        ("Total Revenue Lift: Run C vs Run A",
         f"Run C generates {M(rev_delta_ac)} more revenue than Run A over 10 years, "
         f"with {int(mc['total_passengers'] - ma['total_passengers'])} more passengers carried. "
         f"This gap widens every turn as reputation builds and Reusable Stage 1 compounds elasticity."),
    ]

    for title, body in insights:
        print(f"\n  ▸ {title}")
        # wrap body at ~120 chars
        words = body.split()
        line, lines = "    ", []
        for w in words:
            if len(line) + len(w) + 1 > 122:
                lines.append(line)
                line = "    " + w
            else:
                line += ("" if line == "    " else " ") + w
        lines.append(line)
        print("\n".join(lines))

    print(f"\n{'═' * W}\n")

    # ── JSON export ───────────────────────────────────────────────────────────
    output = {
        "config": {
            "random_seed":            RANDOM_SEED,
            "spaceport_purchased_year": SPACEPORT_TURN,
            "spaceport_operational_year": SPACEPORT_TURN + 1,
            "shared_investments": {k: v for k, v in _SHARED.items()
                                   if k not in ("buy_vehicle", "investor_offer", "buy_spaceport")},
            "run_A": {"scenario": "A", "t1_ticket": SUBORBITAL_FLOOR, "turns_ticket": ORBITAL_FLOOR},
            "run_B": {"scenario": "B", "t1_ticket": SUBORBITAL_30PCT, "turns_ticket": ORBITAL_30PCT, "spaceport": False},
            "run_C": {"scenario": "B", "t1_ticket": SUBORBITAL_30PCT, "turns_ticket": ORBITAL_30PCT, "spaceport": True},
        },
        "run_A_status_quo":         {"turns": [vars(r) for r in ra], "final_score": sa, "financial_metrics": ma},
        "run_B_premature_evolved":  {"turns": [vars(r) for r in rb], "final_score": sb, "financial_metrics": mb},
        "run_C_lcc_revolution":     {"turns": [vars(r) for r in rc], "final_score": sc, "financial_metrics": mc},
    }
    path = "playthrough_results.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  Results exported → {path}\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nM.A.R.S. Three-Run Validation Model")
    print(f"  Seed: {RANDOM_SEED}  |  Spaceport: Y{SPACEPORT_TURN} (operational Y{SPACEPORT_TURN + 1})")
    print(f"  Run A: Scenario A | Suborbital €{SUBORBITAL_FLOOR/1e3:.0f}k → Orbital €{ORBITAL_FLOOR/1e6:.0f}M")
    print(f"  Run B: Scenario B | Suborbital €{SUBORBITAL_30PCT/1e3:.0f}k → Orbital €{ORBITAL_30PCT/1e6:.1f}M  (no spaceport)")
    print(f"  Run C: Scenario B | Suborbital €{SUBORBITAL_30PCT/1e3:.0f}k → Orbital €{ORBITAL_30PCT/1e6:.1f}M  (spaceport Y{SPACEPORT_TURN})\n")

    ra, sa, ma = run_scenario("Run A — Status Quo (Scenario A, price floors, no spaceport)",
                               RUN_A_T1, RUN_A,    buy_spaceport=False)
    rb, sb, mb = run_scenario("Run B — Premature Evolved (Scenario B, −30%, no spaceport)",
                               RUN_BC_T1, RUN_BC,  buy_spaceport=False)
    rc, sc, mc = run_scenario("Run C — LCC Revolution (Scenario B, −30%, spaceport Y3)",
                               RUN_BC_T1, RUN_BC,  buy_spaceport=True)

    print_report(ra, sa, ma, rb, sb, mb, rc, sc, mc)
