"""Task 2 (region axis): county-level stunting, KDHS 2022."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import COUNTY_MAP, HAZ_HISTOGRAM, get_county_stunting, get_regional_summary

st.set_page_config(page_title="Regional Analysis — Project 7", page_icon="📍", layout="wide")

summary = get_regional_summary()
county = get_county_stunting()

st.title("📍 Regional Analysis")
st.caption("Owners: Kevinson Mwangi, Elphas Abok")
st.markdown(
    "How Kenyan child stunting varies across the country — the geographic "
    "half of Task 2, and the evidence base Intervention Prioritization "
    "ranks on."
)

m1, m2, m3 = st.columns(3)
m1.metric(
    "National stunting prevalence",
    f"{summary['national']['stunting_prevalence_weighted_pct']:.1f}%",
    help="Survey-weighted; height-for-age z-score (HAZ) < -2 SD, WHO 2006 growth standards.",
)
m2.metric(
    "Children analysed (6-59 months)",
    f"{summary['sample']['stunting_analysis_n_6_59_months']:,}",
)
m3.metric(
    "Survey clusters",
    f"{summary['sample']['total_clusters']:,}",
    help=f"Out of {summary['sample']['total_children_all_ages']:,} children across all ages in the full sample.",
)

st.divider()
col_chart, col_hist = st.columns([1, 1])

with col_chart:
    st.subheader("From sample to estimate")
    funnel = pd.DataFrame(
        {
            "stage": [
                "Total children (all ages)",
                "Analysed for stunting (6-59 months)",
                "Estimated stunted (weighted)",
            ],
            "count": [
                summary["sample"]["total_children_all_ages"],
                summary["sample"]["stunting_analysis_n_6_59_months"],
                round(
                    summary["sample"]["stunting_analysis_n_6_59_months"]
                    * summary["national"]["stunting_prevalence_weighted_pct"]
                    / 100
                ),
            ],
        }
    ).set_index("stage")
    st.bar_chart(funnel, horizontal=True)
    st.caption(
        "The weighted-stunted count applies the survey-weighted national "
        "prevalence to the analysed sample. It is an estimate, not a raw headcount."
    )

with col_hist:
    st.subheader("Distribution of HAZ scores")
    if HAZ_HISTOGRAM.exists():
        st.image(
            str(HAZ_HISTOGRAM),
            caption="Height-for-age z-scores, children 6-59 months. WHO stunting cutoff: HAZ < -2.",
            use_container_width=True,
        )
    else:
        st.info("Not yet generated — run `make regional`.", icon="⏳")

with st.expander("Methodology"):
    st.markdown(summary["methodology"])
    st.caption(f"Full analysis: `quarto/regional_analysis.qmd` · pipeline: `scripts/regional_analysis.R`")

st.divider()
st.subheader("County-level stunting")

highest, lowest = county.iloc[0], county.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("Counties reported", f"{len(county):,}")
c2.metric("Highest county", highest["county"], f"{highest['prevalence_pct']:.1f}%",
          help="Survey-weighted prevalence; 95% CI in the table below.")
c3.metric("Lowest county", lowest["county"], f"{lowest['prevalence_pct']:.1f}%",
          help="Survey-weighted prevalence; 95% CI in the table below.")

tab_map, tab_bar = st.tabs(["Map", "Ranked bar chart"])
with tab_map:
    if COUNTY_MAP.exists():
        st.image(str(COUNTY_MAP), caption="Weighted stunting prevalence by county.", use_container_width=True)
    else:
        st.info(
            "Map not yet generated — run `make regional` (`scripts/regional_analysis.R`), "
            "which joins county estimates to rKenyaCensus shapefiles.",
            icon="⏳",
        )
with tab_bar:
    st.bar_chart(county.set_index("county")[["prevalence_pct"]], horizontal=True, use_container_width=True)

with st.expander("County table with 95% confidence intervals"):
    st.dataframe(
        county.rename(columns={
            "county": "County", "prevalence_pct": "Prevalence (%)",
            "ci_lower": "CI lower", "ci_upper": "CI upper",
        }),
        hide_index=True, use_container_width=True,
    )

st.divider()
st.subheader("Remaining Task 2 work")
for item in summary.get("not_yet_analysed", []):
    st.markdown(f"- {item}")
st.caption("Tracked in `PLAN.md`. See the Wealth Analysis page for the wealth-quintile axis specifically.")
