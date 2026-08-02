"""Synthesis page: what the evidence supports, and what it doesn't yet.

Deliberately text-forward rather than another chart page -- this is the
page a judge or policymaker reads last, to walk away with the argument,
not just the data.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_county_stunting, get_priority_counties, get_regional_summary, has_wealth_quintile_data

st.set_page_config(page_title="Policy Recommendations — Project 7", page_icon="📋", layout="wide")

summary = get_regional_summary()
county = get_county_stunting()
priority = get_priority_counties()
flagged = priority[priority["priority"]]

st.title("📋 Policy Recommendations")
st.caption("Synthesis across Task 2 (regional & wealth indicators) and Task 4 (intervention targeting)")

st.divider()
st.subheader("Key insights")

st.markdown(
    f"""
1. **National child stunting stands at {summary['national']['stunting_prevalence_weighted_pct']:.1f}%** —
   roughly 1 in 6 children aged 6–59 months, survey-weighted across
   {summary['sample']['total_clusters']:,} clusters nationwide (KDHS 2022).

2. **Stunting is not evenly distributed.** The gap between the
   highest-prevalence county ({county.iloc[0]['county']}, {county.iloc[0]['prevalence_pct']:.1f}%)
   and the lowest ({county.iloc[-1]['county']}, {county.iloc[-1]['prevalence_pct']:.1f}%) is
   {county.iloc[0]['prevalence_pct'] - county.iloc[-1]['prevalence_pct']:.1f} percentage points —
   a national average alone would obscure where the problem actually is.

3. **{len(flagged)} counties are meaningfully worse than typical variation**,
   not just above the national average: {", ".join(flagged["county"].tolist())}.
   These are ranked, evidence-based priority candidates for intervention —
   see Intervention Prioritization for the full methodology and confidence
   intervals.
"""
)

if not has_wealth_quintile_data():
    st.warning(
        "**The wealth-quintile axis is not yet in this analysis.** Task 2 "
        "is defined as indicators varying by region *and* wealth quintile — "
        "geography alone likely understates the true disparity, since "
        "poorer households are not evenly spread across counties. Treat the "
        "county ranking above as a first-pass, geography-only view.",
        icon="⚠️",
    )
else:
    st.success("Wealth-quintile data is incorporated — see the Wealth Analysis page and the note on the Intervention Prioritization page.")

st.divider()
st.subheader("Recommendations")

st.markdown(
    f"""
- **Prioritize the {len(flagged)} flagged counties for the next round of
  nutrition programming**, weighting resourcing by both the size of the gap
  vs. national prevalence and the certainty of the estimate (a county with a
  wide confidence interval needs more local data before resourcing decisions
  lean heavily on the point estimate alone — see Intervention Prioritization).
- **Close the wealth-quintile gap before finalizing county-level
  resourcing.** Geography and wealth are correlated but not identical —
  a county-only view can miss households that are underserved regardless of
  which county they're in.
- **Re-run this ranking once immunisation and skilled-birth-attendance data
  land** (`scripts/wealth_quintile_analysis.R`, `scripts/compute_indicators.R`).
  A county that ranks moderately on stunting alone but poorly across all
  three indicators is a stronger case than any single indicator suggests.
"""
)

st.divider()
st.subheader("What this analysis does not claim")
st.markdown(
    "- This is a **prioritization signal, not a causal analysis** — stunting "
    "prevalence differences reflect many upstream drivers (food security, "
    "water/sanitation, health service access) this dataset alone can't "
    "separate.\n"
    "- The v1 threshold rule (national + 1 SD) is one reasonable cut, not "
    "the only valid one — see `quarto/intervention_analysis.qmd` for the "
    "full derivation and how sensitive the flagged list is to that choice."
)
