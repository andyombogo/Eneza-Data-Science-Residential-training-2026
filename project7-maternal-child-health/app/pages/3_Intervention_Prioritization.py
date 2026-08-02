"""Task 4: rank counties for intervention priority.

Reads data/processed/task4_priority_counties.csv, computed by
scripts/intervention_prioritization.R from Task 2's county stunting data
only -- no restricted KDHS access needed, so this doesn't block on
wealth-quintile/immunisation/SBA landing first.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import NATIONAL_STUNTING_PCT, get_priority_counties, get_wealth_note

st.set_page_config(page_title="Intervention Prioritization — Project 7", page_icon="🎯", layout="wide")

priority = get_priority_counties()
flagged = priority[priority["priority"]]
threshold = round(NATIONAL_STUNTING_PCT + priority["prevalence_pct"].std(ddof=1), 1)

st.title("🎯 Intervention Prioritization")
st.caption("Owners: [assign — see PLAN.md]")
st.markdown(
    "Where should intervention go first? A county is flagged **priority** "
    "if its stunting prevalence sits at or above **national prevalence + 1 "
    "standard deviation across counties** — meaningfully worse than typical "
    "variation, not just above average."
)

m1, m2, m3 = st.columns(3)
m1.metric("Counties flagged", f"{len(flagged)} of {len(priority)}")
m2.metric("Threshold", f"{threshold:.1f}%", help=f"National ({NATIONAL_STUNTING_PCT}%) + 1 SD across counties.")
m3.metric("Top priority county", flagged.iloc[0]["county"], f"{flagged.iloc[0]['prevalence_pct']:.1f}%")

st.divider()
st.subheader("All 47 counties, ranked")

chart_df = priority.set_index("county")[["prevalence_pct"]].sort_values("prevalence_pct")
st.bar_chart(chart_df, horizontal=True, use_container_width=True)
st.caption(
    f"Dashed reference: national prevalence {NATIONAL_STUNTING_PCT}%. "
    "Bars are not color-split by flag status in this chart type — see the flagged table below for exactly which counties cross the threshold."
)

st.divider()
st.subheader(f"Flagged counties ({len(flagged)})")
st.dataframe(
    flagged[["priority_rank", "county", "prevalence_pct", "ci_lower", "ci_upper", "gap_vs_national_pct", "ci_width_pct"]]
    .rename(columns={
        "priority_rank": "Rank", "county": "County", "prevalence_pct": "Prevalence (%)",
        "ci_lower": "CI lower", "ci_upper": "CI upper",
        "gap_vs_national_pct": "vs. national (pts)", "ci_width_pct": "CI width (pts)",
    }),
    hide_index=True, use_container_width=True,
)

st.info(
    "**Read the CI width alongside the ranking.** A county with a wide "
    "confidence interval (see `CI width (pts)`) rests on fewer sampled "
    "clusters — two counties with the same point estimate aren't equally "
    "strong cases for intervention if one estimate is far less certain.",
    icon="📏",
)

st.divider()
st.subheader("Secondary signal: wealth-quintile gap")
st.markdown(get_wealth_note())

st.divider()
with st.expander("Methodology & what would sharpen this ranking"):
    st.markdown(
        "**v1 rule**, built on Task 2's most complete indicator (stunting, "
        "all 47 counties) rather than waiting on other indicators to land:\n\n"
        "- Threshold = national stunting prevalence + 1 population SD across counties.\n"
        "- Ranking = counties sorted by prevalence, highest first.\n\n"
        "**Next refinements**, once available:\n"
        "- Fold in the wealth-quintile gap (Wealth Analysis page) as a second axis — "
        "a county that is both high-stunting and has a wide internal wealth gap "
        "is a stronger case than stunting alone suggests.\n"
        "- Add immunisation and skilled-birth-attendance prevalence per county "
        "as corroborating evidence.\n\n"
        "Full derivation: `quarto/intervention_analysis.qmd`. "
        "Pipeline: `scripts/intervention_prioritization.R` (`make intervention`)."
    )
