"""Entry point: landing page + task/status overview.

Streamlit auto-discovers app/pages/*.py as navigation entries when this file
is run as `streamlit run app/Home.py` -- no manual st.Page/st.navigation
wiring needed for a single-section app like this one.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    get_county_stunting,
    get_immunisation_summary,
    get_priority_counties,
    get_regional_summary,
    get_sba_summary,
    page_footer,
)

st.set_page_config(
    page_title="Project 7 — Maternal & Child Health in Kenya",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 Where Kenya's Maternal & Child Health Gaps Are — and What To Do About Them")
st.caption("Eneza Data Science Residential Training 2026 · Project 7 · KDHS 2022")

st.markdown(
    "Kenya's own national health survey already tells us where children are "
    "worst off. This project turns that survey into two things: a clear "
    "picture of **where** stunting is concentrated, and a **ranked, "
    "evidence-based case for where intervention should go first.**"
)

st.divider()

summary = get_regional_summary()
immun_summary = get_immunisation_summary()
sba_summary = get_sba_summary()
county = get_county_stunting()
priority = get_priority_counties()

st.caption("All three indicators below: children aged 12–35 months, KDHS 2022, survey-weighted.")
i1, i2, i3 = st.columns(3)
i1.metric(
    "Stunting",
    f"{summary['national']['stunting_prevalence_weighted_pct']:.1f}%",
    help="Height-for-age z-score (HAZ) < -2 SD, WHO 2006 growth standards. SDG 2.2.1.",
)
i2.metric(
    "Full immunisation",
    f"{immun_summary['national']['full_immunisation_prevalence_weighted_pct']:.1f}%",
    help="All scheduled vaccines by the national schedule. SDG 3.b.1.",
)
i3.metric(
    "Skilled birth attendance",
    f"{sba_summary['national']['sba_prevalence_weighted_pct']:.1f}%",
    help="Delivery assisted by a doctor, nurse, or midwife/clinical officer. SDG 3.1.2.",
)

c1, c2, c3 = st.columns(3)
c1.metric("Counties analysed", f"{len(county):,}", help="All 47 Kenyan counties.")
c2.metric(
    "Highest-stunting county (6–59mo v1 ranking)",
    county.iloc[0]["county"],
    f"{county.iloc[0]['prevalence_pct']:.1f}%",
)
c3.metric(
    "Priority counties flagged",
    f"{int(priority['priority'].sum())}",
    help="Counties at or above national prevalence + 1 SD across counties — see Intervention Prioritization.",
)

st.divider()
st.subheader("What's here")

nav = [
    ("📋 Problem Statement", "Objectives and a live Task 2/4 deliverables checklist."),
    ("🗂️ Data", "Sources, access terms, and a live data-completeness check."),
    ("🧪 Methodology", "Survey design, indicator definitions, and the INLA/MBG small-area methods."),
    ("💰 Wealth Analysis", "How outcomes vary by household wealth — concentration indices and a forest plot."),
    ("📍 Regional Analysis", "How stunting varies across Kenya's 47 counties, with confidence intervals."),
    ("🌐 Spatial & Bayesian Analysis", "Observed prevalence, model diagnostics, and predicted probability maps for all three indicators."),
    ("🎯 Intervention Prioritization", "A ranked, threshold-based list of counties for intervention."),
    ("📋 Policy Recommendations", "What the evidence supports acting on, and what it doesn't yet."),
    ("⬇️ Downloads", "Every committed output file, downloadable, with its completeness status."),
    ("ℹ️ About", "Team, tech stack, and links."),
]
for label, desc in nav:
    st.markdown(f"**{label}** — {desc}")

st.caption("Use the sidebar to move between pages.")

st.divider()
st.subheader("Task ownership & status")
import pandas as pd  # noqa: E402 -- kept local to this small table, not worth a top-level import

tasks = pd.DataFrame(
    [
        {
            "Task": "Regional & wealth-quintile indicators (Task 2)",
            "Owners": "Kevinson Mwangi, Elphas Abok",
            "Status": "🟢 Complete — stunting, immunisation, and SBA analysed nationally, regionally, and by wealth (12–35 months).",
        },
        {
            "Task": "Intervention prioritization (Task 4)",
            "Owners": "John Andrew, Kevinson Mwangi, Elphas Abok",
            "Status": "🟢 Complete — v1 (stunting-based county ranking) and v2 (multi-indicator vulnerability ranking) both live.",
        },
    ]
).set_index("Task")
st.dataframe(tasks, use_container_width=True)

st.divider()
st.subheader("Data sources")
st.markdown(
    "- **[Kenya Demographic and Health Survey (KDHS) 2022](https://dhsprogram.com)**, "
    "Kids' Recode file — restricted-access, obtained via an approved DHS Program data request.\n"
    "- **[rKenyaCensus](https://github.com/Shelmith-Kariuki/rKenyaCensus)** — county boundary shapefiles for mapping."
)

page_footer("Home")
