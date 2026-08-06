"""Problem statement, objectives, and deliverables status.

Content mirrors README.md (Problem statement / Why this matters / Objectives)
verbatim in substance -- this page is a presentation layer over the README,
not a second source of truth. When the README's deliverables list changes,
update DELIVERABLES below to match.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import SDG_LINKS, page_footer

st.set_page_config(page_title="Problem Statement — Project 7", page_icon="📋", layout="wide")

st.title("📋 Problem Statement")
st.caption("Why this project exists, and what it delivers")

st.markdown(
    "Kenya's national health survey already tells us where children are "
    "worst off — the gap is turning that survey into something a "
    "decision-maker can act on. This project does two things:"
)
st.markdown(
    "1. **Task 2 — Regional & wealth indicators.** How do child stunting, "
    "immunisation, and skilled birth attendance vary across Kenya's 47 "
    "counties and across household wealth, among children aged **12–35 "
    "months**?\n"
    "2. **Task 4 — Intervention targeting.** Given that variation, which "
    "counties should be prioritized first, and on what evidence?"
)

st.subheader("Why this matters for Kenya")
st.markdown(
    "Maternal and child health is a national priority, and resources for "
    "nutrition and health programming are finite. A national average hides "
    "where the problem actually concentrates — this project makes county- "
    "and wealth-level disparities visible and explicit, and turns the "
    "worst gaps into a ranked, defensible starting point for where to "
    "intervene first, rather than leaving that judgment to intuition."
)

st.markdown("**Our indicators are SDG-based:**")
sdg_cols = st.columns(3)
for col, (key, label) in zip(sdg_cols, [("stunting", "Stunting"), ("immunisation", "Immunisation"), ("sba", "Skilled birth attendance")]):
    sdg = SDG_LINKS[key]
    with col:
        st.markdown(f"**{label} — `{sdg['code']}`**")
        st.markdown(sdg["goal"])
        st.caption(sdg["why"])
st.caption("SDG mapping: `Presentation.Rmd` § Our indicators are SDG-based.")

st.subheader("Objectives")
st.markdown(
    "1. Quantify how Kenyan child-health indicators vary by **region** "
    "(county) and by **household wealth**.\n"
    "2. Turn that variation into a **ranked, transparent case for where "
    "intervention should go first**, with the uncertainty of each estimate "
    "made explicit rather than hidden behind a point estimate."
)

st.divider()
st.success("**Status: Complete.** All Task 2 and Task 4 deliverables below are done.", icon="✅")
st.header("Deliverables")

# (label, done) -- keep in sync with README.md's Deliverables section.
TASK2_DELIVERABLES = [
    ("National stunting, immunisation, and SBA prevalence — 12–35 months", True),
    ("County-level stunting, immunisation, and SBA — forest plots & choropleth maps", True),
    ("Wealth-equity concentration indices (stunting, immunisation, SBA)", True),
    ("Wealth-category (Low/Middle/High) breakdown, all three indicators", True),
    ("Spatial analysis: observed prevalence, model diagnostics, predicted probability surfaces", True),
    ("Small-area estimation (MBG + INLA), all three indicators", True),
    ("App restructured: Data/Methodology/Spatial/Downloads/About pages, interactive viz, error handling, download buttons", True),
]

TASK4_DELIVERABLES = [
    ("v1 county prioritization from stunting data", True),
    ("Task 4 owners assigned", True),
    ("v2 multi-indicator vulnerability ranking (stunting + immunisation + SBA)", True),
]

PROJECT_WIDE_DELIVERABLES = [
    ("Reproducible pipeline (Makefile, environment.yml, scripts/)", True),
    ("Ethics & Data Protection notes drafted", True),
]


def render_checklist(items: list[tuple[str, bool]]) -> None:
    for label, is_done in items:
        st.markdown(f"- {'✅' if is_done else '⬜'} {label}")


col2, col4 = st.columns(2)
with col2:
    st.subheader("Task 2 — Regional & Wealth Indicators")
    st.caption("Owners: Kevinson Mwangi, Elphas Abok")
    render_checklist(TASK2_DELIVERABLES)
with col4:
    st.subheader("Task 4 — Intervention Targeting")
    st.caption("Owners: John Andrew, Kevinson Mwangi, Elphas Abok")
    render_checklist(TASK4_DELIVERABLES)

st.subheader("Project-wide")
render_checklist(PROJECT_WIDE_DELIVERABLES)

st.divider()
st.subheader("Methodology note")
st.markdown(
    "**Stunting, immunisation, and skilled birth attendance are all analysed "
    "on children aged 12–35 months** — the age band asked about delivery "
    "assistance and immunisation in KDHS 2022, so the team standardized all "
    "three indicators to it for a consistent, comparable analysis (see "
    "`Presentation.Rmd` § Approach). The Task 4 v1 county ranking predates "
    "this standardization and still runs on the earlier 6–59 month county "
    "data; the v2 multi-indicator ranking (Intervention Prioritization page) "
    "uses the current 12–35 month figures."
)

st.caption("See the Data page for a live completeness check on every committed output file.")

page_footer("Problem Statement")
