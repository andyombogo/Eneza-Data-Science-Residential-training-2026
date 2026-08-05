"""Task 4: rank counties for intervention priority.

v1: data/processed/task4_priority_counties.csv, computed by
scripts/intervention_prioritization.R from Task 2's county stunting data
(6-59 month band).
v2: multi-indicator vulnerability ranking across all three indicators
(12-35 month band), recovered from origin/task2-regional-indicators.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    FIG_TOP_COUNTIES_RANKING,
    NATIONAL_STUNTING_PCT_6_59_LEGACY,
    PRIORITY_COUNTIES,
    get_county_immunisation,
    get_county_sba,
    get_file_bytes,
    get_immunisation_summary,
    get_priority_counties,
    get_regional_summary,
    get_sba_summary,
    get_wealth_note,
    page_footer,
)


def county_ranking_chart(df, national_pct, indicator_label, worse_direction, key):
    """Same visual design as the v1 stunting ranking chart: horizontal bar,
    sorted ascending, colored by a national +/- 1 SD threshold flag, with
    dashed (national) and dotted (threshold) reference lines.

    worse_direction: "high" (flag counties >= national + 1 SD, e.g. stunting)
                      or "low" (flag counties <= national - 1 SD, e.g. coverage indicators).
    """
    sd = df["prevalence_pct"].std(ddof=1)
    if worse_direction == "high":
        threshold = round(national_pct + sd, 1)
        is_flagged = df["prevalence_pct"] >= threshold
    else:
        threshold = round(national_pct - sd, 1)
        is_flagged = df["prevalence_pct"] <= threshold

    chart_df = df.sort_values("prevalence_pct").copy()
    chart_df["Flag status"] = is_flagged.reindex(chart_df.index).map({True: "Flagged", False: "Not flagged"})

    m1, m2, m3 = st.columns(3)
    m1.metric("Counties flagged", f"{int(is_flagged.sum())} of {len(df)}")
    m2.metric("Threshold", f"{threshold:.1f}%", help=f"National ({national_pct:.1f}%) {'+' if worse_direction == 'high' else '-'} 1 SD across counties.")
    worst = chart_df.iloc[-1] if worse_direction == "high" else chart_df.iloc[0]
    m3.metric("Most concerning county", worst["county"], f"{worst['prevalence_pct']:.1f}%")

    fig = px.bar(
        chart_df,
        x="prevalence_pct",
        y="county",
        orientation="h",
        color="Flag status",
        color_discrete_map={"Flagged": "#B84C4C", "Not flagged": "#3B6FA0"},
        labels={"prevalence_pct": f"{indicator_label} (%)", "county": "County"},
        height=900,
    )
    fig.add_vline(x=national_pct, line_dash="dash", line_color="black", annotation_text="National")
    fig.add_vline(x=threshold, line_dash="dot", line_color="#B84C4C", annotation_text="Threshold")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", legend_title=None)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.caption(
        f"Dashed line: national prevalence ({national_pct:.1f}%). Dotted "
        f"line: national {'+' if worse_direction == 'high' else '-'} 1 SD "
        f"across counties ({threshold:.1f}%), the same rule used for the v1 "
        "stunting ranking above, applied here for visual consistency — not "
        "a team-adopted threshold for this indicator. County-level values "
        "are extracted from the forest-plot image (see `docs/data_dictionary.md`), "
        "not a rendered R output — treat as approximate."
    )

st.set_page_config(page_title="Intervention Prioritization — Project 7", page_icon="🎯", layout="wide")

priority = get_priority_counties()
flagged = priority[priority["priority"]]
threshold = round(NATIONAL_STUNTING_PCT_6_59_LEGACY + priority["prevalence_pct"].std(ddof=1), 1)

st.title("🎯 Intervention Prioritization")
st.caption("Owners: John Andrew, Kevinson Mwangi, Elphas Abok")
st.markdown(
    "Where should intervention go first? Two views: a **v1 ranking** on "
    "stunting alone (all 47 counties, full CI), and a **v2 ranking** that "
    "folds in all three indicators."
)

stunting_summary = get_regional_summary()
immun_summary = get_immunisation_summary()
sba_summary = get_sba_summary()
i1, i2, i3 = st.columns(3)
i1.metric("Stunting (national, 12–35mo)", f"{stunting_summary['national']['stunting_prevalence_weighted_pct']:.1f}%")
i2.metric("Full immunisation (national, 12–35mo)", f"{immun_summary['national']['full_immunisation_prevalence_weighted_pct']:.1f}%")
i3.metric("Skilled birth attendance (national, 12–35mo)", f"{sba_summary['national']['sba_prevalence_weighted_pct']:.1f}%")

st.divider()
st.header("v1 — stunting-based county ranking")
st.markdown(
    "A county is flagged **priority** if its stunting prevalence sits at or "
    "above **national prevalence + 1 standard deviation across counties** "
    "(6–59 month band) — meaningfully worse than typical variation, not "
    "just above average."
)

m1, m2, m3 = st.columns(3)
m1.metric("Counties flagged", f"{len(flagged)} of {len(priority)}")
m2.metric("Threshold", f"{threshold:.1f}%", help=f"National ({NATIONAL_STUNTING_PCT_6_59_LEGACY}%, 6-59mo) + 1 SD across counties.")
m3.metric("Top priority county", flagged.iloc[0]["county"], f"{flagged.iloc[0]['prevalence_pct']:.1f}%")

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
fig.add_vline(x=NATIONAL_STUNTING_PCT_6_59_LEGACY, line_dash="dash", line_color="black", annotation_text="National (6–59mo)")
fig.add_vline(x=threshold, line_dash="dot", line_color="#B84C4C", annotation_text="Threshold")
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", legend_title=None)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    f"Dashed line: national prevalence ({NATIONAL_STUNTING_PCT_6_59_LEGACY}%, "
    f"6–59mo band). Dotted line: priority threshold ({threshold:.1f}%). Bars "
    "are color-split by flag status — red bars are the counties in the "
    "flagged table below."
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
st.header("Immunisation and SBA — county rankings")
st.markdown(
    "Same 47-county ranking view as the v1 stunting chart above, for the "
    "other two indicators (12–35 month band)."
)

tab_immun, tab_sba = st.tabs(["Full immunisation", "Skilled birth attendance"])
with tab_immun:
    county_immun = get_county_immunisation()
    county_ranking_chart(
        county_immun,
        immun_summary["national"]["full_immunisation_prevalence_weighted_pct"],
        "Full immunisation",
        worse_direction="low",
        key="immun_ranking",
    )
with tab_sba:
    county_sba = get_county_sba()
    county_ranking_chart(
        county_sba,
        sba_summary["national"]["sba_prevalence_weighted_pct"],
        "Skilled birth attendance",
        worse_direction="low",
        key="sba_ranking",
    )

st.divider()
st.header("v2 — multi-indicator vulnerability ranking")
st.markdown(
    "An equal-weight vulnerability index across all three indicators "
    "(stunting, non-immunisation, non-SBA; 12–35 month band): each county "
    "scores 1 point per indicator that places it in the worst-performing "
    "tertile nationally, summed. Source: `MCH_Kenya_Task2_Task4_Pipeline.qmd` "
    "Phase 13–14."
)

if FIG_TOP_COUNTIES_RANKING.exists():
    st.image(
        str(FIG_TOP_COUNTIES_RANKING),
        caption="Top 10 counties by vulnerability index.",
        use_container_width=True,
    )

st.markdown("**Summary table — all three indicators**")
V2_RANKING = [
    ("West Pokot", 3, "Stunting, immunisation, SBA"),
    ("Mandera", 3, "Stunting, immunisation, SBA"),
    ("Samburu", 3, "Stunting, immunisation, SBA"),
    ("Turkana", 2, "Immunisation, SBA (excl. stunting)"),
    ("Wajir", 2, "Immunisation, SBA (excl. stunting)"),
    ("Garissa", 2, "Immunisation, SBA (excl. stunting)"),
    ("Tana River", 3, "Stunting, immunisation, SBA"),
    ("Kilifi", 2, "Stunting, SBA (excl. immunisation)"),
    ("Baringo", 3, "Stunting, immunisation, SBA"),
    ("Kitui", 3, "Stunting, immunisation, SBA"),
]
v2_df = pd.DataFrame(V2_RANKING, columns=["County", "# indicators in worst tertile", "Which indicators"])
v2_df.insert(0, "Rank", range(1, len(v2_df) + 1))
st.dataframe(v2_df, hide_index=True, use_container_width=True)
st.caption(
    "Top 10 shown, read directly from the ranking's own county/tertile-count "
    "labels — see the image above for the full vulnerability-index scale. "
    "Full 47-county ranking: `Outputs/Tables/top_counties_ranked.csv`, "
    "produced by `MCH_Kenya_Task2_Task4_Pipeline.qmd` (not committed to this repo)."
)

st.divider()
st.subheader("Secondary signal: wealth-quintile gap")
st.markdown(get_wealth_note())

st.divider()
with st.expander("Methodology"):
    st.markdown(
        "**v1 rule**, built on Task 2's most complete county-level indicator "
        "(stunting, all 47 counties, 6–59mo band):\n\n"
        "- Threshold = national stunting prevalence + 1 population SD across counties.\n"
        "- Ranking = counties sorted by prevalence, highest first.\n\n"
        "**v2 rule**, folding in all three 12–35mo indicators:\n\n"
        "- Equal-weight vulnerability index — 1 point per indicator in the "
        "county's worst-performing tertile nationally, summed across the three.\n\n"
        "Full derivation: `quarto/intervention_analysis.qmd` (v1), "
        "`MCH_Kenya_Task2_Task4_Pipeline.qmd` Phase 13–14 (v2). "
        "Pipeline: `scripts/intervention_prioritization.R` (`make intervention`)."
    )

page_footer("Intervention Prioritization")
