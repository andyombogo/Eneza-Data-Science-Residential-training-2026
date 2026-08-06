"""Synthesis page: what the evidence supports.

Deliberately text-forward rather than another chart page -- this is the
page a judge or policymaker reads last, to walk away with the argument,
not just the data.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    get_county_stunting,
    get_immunisation_summary,
    get_priority_counties,
    get_regional_summary,
    get_sba_summary,
    get_wealth_concentration,
    page_footer,
)

st.set_page_config(page_title="Policy Recommendations — Project 7", page_icon="📋", layout="wide")

summary = get_regional_summary()
immun_summary = get_immunisation_summary()
sba_summary = get_sba_summary()
county = get_county_stunting()
priority = get_priority_counties()
flagged = priority[priority["priority"]]
conc = get_wealth_concentration()

stunting_pct = summary["national"]["stunting_prevalence_weighted_pct"]
immun_pct = immun_summary["national"]["full_immunisation_prevalence_weighted_pct"]
sba_pct = sba_summary["national"]["sba_prevalence_weighted_pct"]

st.title("📋 Policy Recommendations")
st.caption("Synthesis across Task 2 (regional & wealth indicators) and Task 4 (intervention targeting)")

st.divider()
st.subheader("Key insights")

st.markdown(
    f"""
1. **National child stunting stands at {stunting_pct:.1f}%**, full
   immunisation at **{immun_pct:.1f}%**, and skilled birth attendance at
   **{sba_pct:.1f}%** — survey-weighted, children aged 12–35 months, KDHS
   2022.

2. **Stunting is not evenly distributed.** The gap between the
   highest-prevalence county ({county.iloc[0]['county']}, {county.iloc[0]['prevalence_pct']:.1f}%)
   and the lowest ({county.iloc[-1]['county']}, {county.iloc[-1]['prevalence_pct']:.1f}%) is
   {county.iloc[0]['prevalence_pct'] - county.iloc[-1]['prevalence_pct']:.1f} percentage points —
   a national average alone would obscure where the problem actually is.

3. **{len(flagged)} counties are meaningfully worse than typical variation**
   on stunting alone, not just above the national average: {", ".join(flagged["county"].tolist())}.
   The multi-indicator vulnerability ranking (Intervention Prioritization,
   v2) corroborates several of these once immunisation and SBA are folded in.

4. **Wealth equity cuts in different directions by indicator.** Stunting
   (concentration index {conc['indicators'][0]['concentration_index']:+.2f})
   concentrates among **poorer** households; full immunisation
   ({conc['indicators'][1]['concentration_index']:+.2f}) and skilled birth
   attendance ({conc['indicators'][2]['concentration_index']:+.2f}) both
   concentrate among **wealthier** households — SBA's gap is by far the
   largest of the three, immunisation's the smallest. See Wealth Analysis
   for the full picture.
"""
)

st.divider()
st.subheader("Recommendations")

st.markdown(
    f"""
**Stunting**
- **Prioritize the {len(flagged)} flagged counties** ({", ".join(flagged["county"].tolist())})
  for the next round of nutrition programming, weighting resourcing by both
  the size of the gap vs. national prevalence and the certainty of the
  estimate (see Intervention Prioritization for CI width by county).
- Cross-check against the v2 multi-indicator ranking — a county that is
  moderate on stunting alone but poor across all three indicators is a
  stronger case than stunting alone suggests.

**Immunisation**
- At {immun_pct:.1f}% national full-vaccination coverage, roughly half of
  children 12–35 months are missing at least one scheduled dose. Because
  full immunisation is less common among poorer households (concentration
  index {conc['indicators'][1]['concentration_index']:+.2f}, concentrated
  among the wealthy), demand-side barriers (cost, distance, awareness) are
  a reasonable first hypothesis alongside supply-side coverage gaps.
- Target counties flagged in the v2 vulnerability ranking where
  immunisation is one of the contributing indicators.

**Skilled birth attendance**
- SBA is high nationally ({sba_pct:.1f}%) but has the sharpest wealth gap
  of the three indicators ({conc['indicators'][2]['concentration_index']:+.2f},
  concentrated among the wealthy) — treat this as a **wealth-access
  problem, not primarily a geographic one**. An intervention aimed only at
  low-coverage counties may miss the larger driver: cost/access barriers
  correlated with household wealth within a county.
- Counties with both low SBA and a wide wealth gap (Wealth Analysis page)
  are the strongest candidates for subsidized or community-based delivery
  support.
"""
)

st.info(
    "**Wealth is analysed via concentration indices and a 3-category "
    "(Low/Middle/High) breakdown**, establishing the direction and size of "
    "each indicator's wealth gap (see Wealth Analysis and Regional Analysis).",
    icon="ℹ️",
)

st.divider()
st.subheader("What this analysis does not claim")
st.markdown(
    "- This is a **prioritization signal, not a causal analysis** — "
    "prevalence differences reflect many upstream drivers (food security, "
    "water/sanitation, health service access) this dataset alone can't "
    "separate.\n"
    "- The v1 threshold rule (national + 1 SD) is one reasonable cut, not "
    "the only valid one — see `quarto/intervention_analysis.qmd` for the "
    "full derivation and how sensitive the flagged list is to that choice."
)

page_footer("Policy Recommendations")
