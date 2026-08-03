"""Task 4: rank counties for intervention priority.

Reads data/processed/task4_priority_counties.csv, computed by
scripts/intervention_prioritization.R from Task 2's county stunting data
only -- no restricted KDHS access needed, so this doesn't block on
wealth-quintile/immunisation/SBA landing first.
"""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import NATIONAL_STUNTING_PCT, PRIORITY_COUNTIES, get_file_bytes, get_priority_counties, get_wealth_note, page_footer

st.set_page_config(page_title="Intervention Prioritization — Project 7", page_icon="🎯", layout="wide")

priority = get_priority_counties()
flagged = priority[priority["priority"]]
threshold = round(NATIONAL_STUNTING_PCT + priority["prevalence_pct"].std(ddof=1), 1)

st.title("🎯 Intervention Prioritization")
st.caption("Owners: John Andrew, Kevinson Mwangi, Elphas Abok")
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

chart_df = priority.sort_values("prevalence_pct").copy()
chart_df["Priority status"] = chart_df["priority"].map({True: "Flagged priority", False: "Not flagged"})
fig = px.bar(
    chart_df,
    x="prevalence_pct",
    y="county",
    orientation="h",
    color="Priority status",
    color_discrete_map={"Flagged priority": "#B84C4C", "Not flagged": "#3B6FA0"},  # colorblind-distinguishable, differ in lightness too
    labels={"prevalence_pct": "Prevalence (%)", "county": "County"},
    height=900,
)
fig.add_vline(x=NATIONAL_STUNTING_PCT, line_dash="dash", line_color="black", annotation_text="National")
fig.add_vline(x=threshold, line_dash="dot", line_color="#B84C4C", annotation_text="Threshold")
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", legend_title=None)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    f"Dashed line: national prevalence ({NATIONAL_STUNTING_PCT}%). Dotted line: "
    f"priority threshold ({threshold:.1f}%). Bars are color-split by flag status — "
    "red bars are the counties in the flagged table below."
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

priority_bytes = get_file_bytes(PRIORITY_COUNTIES)
if priority_bytes:
    st.download_button(
        "⬇️ Download full ranked county CSV",
        data=priority_bytes,
        file_name="task4_priority_counties.csv",
        mime="text/csv",
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

page_footer("Intervention Prioritization")
