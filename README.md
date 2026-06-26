# NDIS Utilisation Drivers and Participant Outcomes Modelling

Actuarial analysis of real NDIS data (March 2026 release) for the UNSW x Macquarie Actuarial Societies 2026 Joint Case Competition (EY-sponsored).

The client is a Senior NDIA executive who wants to understand what outcomes the NDIS has delivered, what's driving plan utilisation across different groups, and how to improve scheme accessibility and performance.

---

## The Problem

The NDIS supports over 600,000 Australians with disability through individualised funded plans. But persistent under-utilisation means a lot of that funding never actually reaches people. It sits committed but unspent. That's not just a financial issue, it's an accessibility problem: the plan is a voucher, and low utilisation means the voucher can't be redeemed.

This project tries to answer:
* **Who** is under-utilising their plans, and **why**?
* **Which groups** have the worst outcomes, and does that match who's under-utilising?
* **What should the NDIA actually do** about it?

---

## Data

All data is from the official NDIS Data Research Portal (March 2026 release):

* **Utilisation of Plan Budgets**: 144k rows of pre-aggregated group-level utilisation rates, broken down by state, district, disability, age, SIL/SDA, and support class
* **Longitudinal Outcomes**: participant-reported outcomes across 4 age bands and up to 10 plan reassessments, split by "Has NDIS helped" (level) and status questions (change from baseline)
* **Participant Numbers and Plan Budgets**: average annualised committed support budgets per segment, used to convert utilisation gaps into dollar figures

---

## What I Did (following the 4-step actuarial process)

### Step 1: Data Identification & Assessment
Cleaned both datasets and handled the pre-aggregated row structure (you can't just sum rows, since each row is already a group total). Parsed percentage strings, identified the NA-baseline split in the outcomes data, and reverse-coded 3 negatively-phrased questions.

### Step 2: Mathematical Modelling
**Utilisation EDA (Q1 to Q9):** single-factor breakdowns using an `isolate()` helper that holds all other dimensions at ALL while varying one. This is the only valid way to read this dataset. Key findings: sensory/speech disabilities (52%), Capacity Building budgets (58%), and young adults (65%) all under-utilise significantly.

**Fractional logit GLM:** fit on ~17k granular rows (no ALL rollups) with disability, age, SIL/SDA, support class, and region as predictors. Target is the utilisation rate, a proportion, so fractional logit was chosen because it handles the 0% and 100% boundary values that beta regression can't. Key output: ranked significant drivers with marginal effects in percentage points. The big finding: remoteness is NOT a significant independent driver once you control for who lives there.

**Longitudinal outcomes analysis:** split 43 hand-classified indicators into 4 themes using an explicit dictionary rather than keyword matching. I learned the hard way that keywords misfile things. Computed "NDIS helped" levels and status change per age band by theme by cohort.

**Severity:** joined real segment budgets from the participant-numbers dataset onto the GLM rows (98.2% match rate). Computed unspent-per-participant as (1 minus utilisation) times real budget. Key finding: dollar priority is not the same as rate priority. The groups leaving the most *money* unused are older participants with large Core plans, not the lowest-utilisation groups.

### Step 3: Risk Analysis
Base case: roughly $12.6bn of Core funding committed but undelivered annually (consistent with a ~$45bn scheme at ~74% utilisation, so this is unmet need, not destroyed money). Breakdown by disability, age, and region. Tail risk: the worst 5% of segments sit at 22% mean utilisation, dominated by the compounding-disadvantage profile of 98% no-SIL, 88% remote, 68% Capital, 35% sensory.

### Step 4: Recommendations
Three targeted recommendations, each with an explicit cause, mechanism, and effect chain.

---

## Key Findings

**The one cross-validated finding:**
Young adults (15 to 24) are the priority segment. They under-utilise their plans AND report the weakest outcomes (lowest perceived help, smallest improvement over time), with Employment/Education their worst domain on both measures. Both datasets independently point to the same group. This is the transition cliff: at around 18 they leave school, lose the scaffolding that structured their support use, and engagement drops.

**The plot-vs-model reconciliation:**
Raw plots showed remote districts with very low utilisation (Wheat Belt 56%, Darwin Remote 52%). The GLM showed remoteness has no significant independent effect once disability mix, age, and support class are controlled (p=0.063). The remote problem is driven by *who lives there*, not the location itself.

**The two-lens finding:**
* Rate lens (GLM): most under-served = sensory/speech, young adults, no-SIL
* Dollar lens (severity): most idle funding = older participants, large Core plans, remote

These are different groups. The NDIA needs different levers for each.

---

## Recommendations

1. **Transition support for 15 to 24:** a transition coordinator plus default SLES employment-skills funding. The only recommendation directly validated by outcomes data.
2. **Remote provider access:** thin-market loading, telehealth funding, and NDIA-commissioned visiting clinics for zero-provider districts.
3. **Plan-implementation support:** auto-funded support coordination for no-SIL, Capacity Building, and Capital participants, plus OT-led end-to-end equipment procurement.

---

## Limitations

* Utilisation rows are pre-aggregated (not individual-level), so the GLM is unweighted since participant counts aren't in the utilisation file
* Budget data has no SIL/SDA field, so severity excludes the strongest utilisation driver
* Outcomes data has only 4 age bands and no disability/region/support-class breakdown, so I could only validate on age
* Single March-2026 snapshot, so there's no multi-year or economic-cycle variation

---

## Stack

Python, pandas, numpy, statsmodels, matplotlib, all in Jupyter notebooks.

---

## Structure

```
├── data/                  # NDIS March 2026 datasets (not included, download from dataresearch.ndis.gov.au)
├── notebooks/
│   ├── utilisation_eda.ipynb        # Q1-Q9 + national district analysis
│   ├── outcomes_analysis.ipynb      # 8 plots + summary tables
│   ├── glm_modelling.ipynb          # fractional logit + marginal effects
│   ├── severity.ipynb               # real budget join + per-participant severity
│   └── risk_analysis.ipynb          # Step 4: base case, breakdown, tail
└── README.md
```

---

## Context

This was built for a case competition, not production, so there are places where I'd do things differently with more time (proper participant-level weighting, multi-year projections, a cleaner severity aggregation that handles support-class double-counting). The analysis is rigorous where it matters most, and the limitations are documented honestly throughout.
