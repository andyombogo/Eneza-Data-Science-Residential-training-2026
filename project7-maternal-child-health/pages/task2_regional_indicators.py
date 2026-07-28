"""Task 2: Kenyan maternal/child indicators (KDHS 2022).

Reads pre-computed, aggregate, non-identifying numbers from
data/processed/ rather than any raw microdata: the underlying KDHS 2022
Kids' Recode file is restricted-access (obtained via an approved DHS
Program data request) and cannot be committed to this repo or fetched by
a script the way Task 1's UCI dataset is. See
notebooks/task2_regional_indicators.qmd for the source analysis.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "task2_stunting_summary.json"
HISTOGRAM_PATH = PROJECT_ROOT / "data" / "processed" / "task2_haz_histogram.png"


@st.cache_data(show_spinner=False)
def get_summary() -> dict:
    with open(SUMMARY_PATH, encoding="utf-8") as f:
        return json.load(f)


summary = get_summary()

st.title("📊 Task 2 — Regional & Wealth-Quintile Indicators")
st.caption("Owners: Kevinson Mwangi, Elphas Abok")

st.markdown(
    "How Kenyan maternal/child health indicators vary across the country — "
    "starting with **child stunting**, from the KDHS 2022 Kids' Recode "
    "dataset. Skilled birth attendance, immunisation, and a wealth-quintile "
    "breakdown are tracked below as upcoming additions, not filled in with "
    "placeholder numbers."
)

# --------------------------------------------------------------------------
# Headline metrics
# --------------------------------------------------------------------------

m1, m2, m3 = st.columns(3)
m1.metric(
    "National stunting prevalence",
    f"{summary['national']['stunting_prevalence_weighted_pct']:.1f}%",
    help="Survey-weighted; height-for-age z-score (HAZ) < -2 SD, WHO 2006 growth standards.",
)
m2.metric(
    "Children analysed (6–59 months)",
    f"{summary['sample']['stunting_analysis_n_6_59_months']:,}",
)
m3.metric(
    "Survey clusters",
    f"{summary['sample']['total_clusters']:,}",
    help=f"Out of {summary['sample']['total_children_all_ages']:,} children across all ages in the full sample.",
)

st.divider()

# --------------------------------------------------------------------------
# Stunting: what's actually available
# --------------------------------------------------------------------------

col_chart, col_hist = st.columns([1, 1])

with col_chart:
    st.subheader("From sample to estimate")
    funnel = pd.DataFrame(
        {
            "stage": [
                "Total children (all ages)",
                "Analysed for stunting (6–59 months)",
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
        "prevalence to the analysed sample — it's an estimate, not a raw "
        "headcount (DHS uses sample weights to correct for unequal "
        "selection probability across clusters)."
    )

with col_hist:
    st.subheader("Distribution of HAZ scores")
    st.image(
        str(HISTOGRAM_PATH),
        caption="Height-for-age z-scores, children 6–59 months (national). "
        "The WHO stunting cutoff is HAZ < -2.",
        use_container_width=True,
    )

with st.expander("Methodology"):
    st.markdown(summary["methodology"])
    st.caption(
        f"Source: {summary['source']} ({summary['source_access']}). "
        f"Full analysis code: `{summary['analysis_source_file']}`."
    )

st.divider()

# --------------------------------------------------------------------------
# Honest roadmap: what isn't here yet
# --------------------------------------------------------------------------

st.subheader("What's next")

with st.expander("🗺️ County-level breakdown — analysis written, not yet available"):
    st.markdown(summary["subnational"]["note"])

for item in summary["not_yet_analysed"]:
    st.markdown(f"- 🚧 {item}")

st.caption(
    "Tracked in `PLAN.md`. Once the county-level table is exported to "
    "`data/processed/`, this page grows an interactive map/filter — no "
    "sense building that UI around numbers that don't exist yet."
)
