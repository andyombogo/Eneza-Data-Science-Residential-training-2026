"""Task 2 (region axis): county-level stunting, KDHS 2022."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    COMBINED_MAPS,
    COUNTY_MAP,
    COUNTY_STUNTING,
    FIG_HAZ_VIOLIN,
    FIG_WEALTH_CATEGORY_INDICATORS,
    HAZ_HISTOGRAM,
    NATIONAL_STUNTING_PCT_6_59_LEGACY,
    get_county_stunting,
    get_file_bytes,
    get_regional_summary,
    page_footer,
)

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
    "Children analysed (12-35 months)",
    f"{summary['sample']['stunting_analysis_n_12_35_months']:,}",
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
                "Analysed for stunting (12-35 months)",
                "Estimated stunted (weighted)",
            ],
            "count": [
                summary["sample"]["total_children_all_ages"],
                summary["sample"]["stunting_analysis_n_12_35_months"],
                round(
                    summary["sample"]["stunting_analysis_n_12_35_months"]
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
            caption="Height-for-age z-scores. WHO stunting cutoff: HAZ < -2.",
            use_container_width=True,
        )
    else:
        st.info("Not yet generated — run `make regional`.", icon="⏳")

if FIG_HAZ_VIOLIN.exists():
    st.image(
        str(FIG_HAZ_VIOLIN),
        caption="HAZ distribution by wealth category and residence (12-35 months).",
        use_container_width=True,
    )

with st.expander("Methodology"):
    st.markdown(summary["methodology"])
    st.caption(f"Full analysis: `quarto/regional_analysis.qmd` · pipeline: `scripts/regional_analysis.R`")

if FIG_WEALTH_CATEGORY_INDICATORS.exists():
    st.divider()
    st.subheader("All three indicators, by wealth category")
    st.image(
        str(FIG_WEALTH_CATEGORY_INDICATORS),
        caption="Weighted prevalence of stunting, full immunisation, and skilled birth attendance across Low/Middle/High wealth categories.",
        use_container_width=True,
    )
    st.caption("A 3-category wealth breakdown for all three indicators — see Wealth Analysis for the continuous-wealth concentration-index view.")

st.divider()
st.subheader("County-level stunting")

highest, lowest = county.iloc[0], county.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("Counties reported", f"{len(county):,}")
c2.metric("Highest county", highest["county"], f"{highest['prevalence_pct']:.1f}%",
          help="Survey-weighted prevalence; 95% CI in the table below.")
c3.metric("Lowest county", lowest["county"], f"{lowest['prevalence_pct']:.1f}%",
          help="Survey-weighted prevalence; 95% CI in the table below.")

tab_map, tab_interactive, tab_bar, tab_clustering = st.tabs(
    ["Map", "Interactive chart", "Ranked bar chart", "Regional clustering"]
)
with tab_map:
    if COUNTY_MAP.exists():
        st.image(str(COUNTY_MAP), caption="Weighted stunting prevalence by county (6–59 month band).", use_container_width=True)
    else:
        st.info(
            "Map not yet generated — run `make regional` (`scripts/regional_analysis.R`), "
            "which joins county estimates to rKenyaCensus shapefiles.",
            icon="⏳",
        )
    st.caption(
        "An interactive county *choropleth* (as opposed to this static image) needs "
        "county boundary geometry in GeoJSON form — not available in this repo yet "
        "(the R map above is built from `rKenyaCensus`, an R-only `.rda` object). "
        "See `docs/task2_audit_report.md` § 4 for what's needed."
    )
with tab_interactive:
    county_sorted = county.sort_values("prevalence_pct")
    fig = px.bar(
        county_sorted,
        x="prevalence_pct",
        y="county",
        orientation="h",
        error_x=county_sorted["ci_upper"] - county_sorted["prevalence_pct"],
        error_x_minus=county_sorted["prevalence_pct"] - county_sorted["ci_lower"],
        color="prevalence_pct",
        color_continuous_scale="Viridis",  # colorblind-safe
        labels={"prevalence_pct": "Prevalence (%)", "county": "County"},
        height=900,
    )
    fig.add_vline(
        x=NATIONAL_STUNTING_PCT_6_59_LEGACY,
        line_dash="dash",
        line_color="#813134",
        annotation_text="National (6–59mo)",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Hover a bar for the exact prevalence and 95% CI. This chart and its "
        "national reference line use the 6–59 month county data (matching "
        "the Intervention Prioritization v1 ranking); the current 12–35 "
        "month headline figure (21.7%) is shown at the top of this page. "
        "Viridis palette — readable under the common forms of color-vision "
        "deficiency."
    )
with tab_bar:
    st.bar_chart(county.set_index("county")[["prevalence_pct"]], horizontal=True, use_container_width=True)
with tab_clustering:
    if COMBINED_MAPS.exists():
        st.image(str(COMBINED_MAPS), caption="Regional clustering across stunting, immunisation, and SBA (12–35 months).", use_container_width=True)
    else:
        st.info("Not available.", icon="⏳")

with st.expander("County table with 95% confidence intervals"):
    st.dataframe(
        county.rename(columns={
            "county": "County", "prevalence_pct": "Prevalence (%)",
            "ci_lower": "CI lower", "ci_upper": "CI upper",
        }),
        hide_index=True, use_container_width=True,
    )
    county_bytes = get_file_bytes(COUNTY_STUNTING)
    if county_bytes:
        st.download_button(
            "⬇️ Download county stunting CSV",
            data=county_bytes,
            file_name="task2_stunting_by_county.csv",
            mime="text/csv",
        )

page_footer("Regional Analysis")
