"""Entry point: landing page + task/status overview.

Streamlit auto-discovers app/pages/*.py as navigation entries when this file
is run as `streamlit run app/Home.py` -- no manual st.Page/st.navigation
wiring needed for a single-section app like this one.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import get_county_stunting, get_priority_counties, get_regional_summary

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
county = get_county_stunting()
priority = get_priority_counties()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "National stunting prevalence",
    f"{summary['national']['stunting_prevalence_weighted_pct']:.1f}%",
    help="Survey-weighted; HAZ < -2 SD, WHO 2006 growth standards. KDHS 2022.",
)
c2.metric("Counties analysed", f"{len(county):,}", help="All 47 Kenyan counties.")
c3.metric(
    "Highest-prevalence county",
    county.iloc[0]["county"],
    f"{county.iloc[0]['prevalence_pct']:.1f}%",
)
c4.metric(
    "Priority counties flagged",
    f"{int(priority['priority'].sum())}",
    help="Counties at or above national prevalence + 1 SD across counties — see Intervention Prioritization.",
)

st.divider()
st.subheader("What's here")

nav = [
    ("📍 Regional Analysis", "How stunting varies across Kenya's 47 counties, with confidence intervals."),
    ("💰 Wealth Analysis", "How outcomes vary by household wealth quintile."),
    ("🎯 Intervention Prioritization", "A ranked, threshold-based list of counties for intervention."),
    ("📋 Policy Recommendations", "What the evidence supports acting on, and what it doesn't yet."),
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
            "Status": "🟡 Stunting: national + county done. Immunisation, skilled birth attendance, wealth quintile: pending.",
        },
        {
            "Task": "Intervention prioritization (Task 4)",
            "Owners": "[assign — see PLAN.md]",
            "Status": "🟢 v1 live: county ranking from stunting data. Refinement pending wealth/immunisation/SBA data.",
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
