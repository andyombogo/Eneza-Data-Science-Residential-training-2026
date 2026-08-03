"""Problem statement, objectives, and Task 2 / Task 4 deliverables status.

Content mirrors README.md (Problem statement / Why this matters / Objectives)
and PLAN.md (Deliverables checklist) verbatim in substance -- this page is a
presentation layer over those files, not a second source of truth. When
PLAN.md's checklist changes, update DELIVERABLES below to match.
"""

import streamlit as st

st.set_page_config(page_title="Problem Statement — Project 7", page_icon="📋", layout="wide")

st.title("📋 Problem Statement")
st.caption("Why this project exists, and what it's actually delivered so far")

st.markdown(
    "Kenya's national health survey already tells us where children are "
    "worst off — the gap is turning that survey into something a "
    "decision-maker can act on. This project does two things:"
)
st.markdown(
    "1. **Task 2 — Regional & wealth-quintile indicators.** How does child "
    "stunting (and, as the remaining analysis lands, immunisation and "
    "skilled birth attendance) vary across Kenya's 47 counties and across "
    "household wealth quintiles?\n"
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

st.subheader("Objectives")
st.markdown(
    "1. Quantify how Kenyan child-health indicators vary by **region** "
    "(county) and by **household wealth quintile**.\n"
    "2. Turn that variation into a **ranked, transparent case for where "
    "intervention should go first**, with the uncertainty of each estimate "
    "made explicit rather than hidden behind a point estimate."
)

st.divider()
st.header("Deliverables")
st.caption(
    "Mirrors `PLAN.md` § Deliverables checklist — that file is the source "
    "of truth; this is a presentation of the same list."
)

# (label, done) -- keep in sync with PLAN.md's checklist.
TASK2_DELIVERABLES = [
    ("National stunting summary", True),
    ("County stunting CSV + confidence intervals", True),
    ("Wealth-equity concentration indices (stunting, immunisation, SBA)", True),
    ("County stunting choropleth map", True),
    ("Immunisation & SBA county maps (recovered, not yet on a page)", True),
    ("Age-band reconciliation (6–59mo vs. 12–35mo stunting definitions)", False),
    ("Immunisation analysis ported into this branch's pipeline & executed", False),
    ("Skilled birth attendance analysis ported into this branch's pipeline & executed", False),
    ("Stunting map regenerated on the 6–59mo band", False),
    ("Immunisation & SBA regional app pages built", False),
    ("Discrete wealth-quintile CSV (5-quintile breakdown per indicator)", False),
    ("Adjusted ORs by wealth status (stunting/immunisation/SBA) — source pulled 2026-08-03, not yet run", False),
    ("Small-area estimation (INLA + MBG, now prepped for all 3 indicators) — stretch goal", False),
]

TASK4_DELIVERABLES = [
    ("v1 county prioritization from stunting data", True),
    ("Task 4 owners assigned", True),
    ("v2: fold in immunisation/SBA/wealth-quintile data once available", False),
]

PROJECT_WIDE_DELIVERABLES = [
    ("Reproducible pipeline (Makefile, environment.yml, scripts/)", True),
    ("Ethics & Data Protection notes drafted", True),
    ("Ethics & Data Protection notes reviewed by the team", False),
    ("Rendered Quarto report attached for submission", False),
]


def render_checklist(items: list[tuple[str, bool]]) -> None:
    done = [label for label, is_done in items if is_done]
    not_done = [label for label, is_done in items if not is_done]
    st.progress(len(done) / len(items), text=f"{len(done)} of {len(items)} done")
    for label in done:
        st.markdown(f"- ✅ ~~{label}~~")
    for label in not_done:
        st.markdown(f"- ⬜ {label}")


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
st.header("What's remaining")
st.markdown(
    "Ranked by impact on the final submission, not by file order — see "
    "`PLAN.md` for full detail on each:\n\n"
    "1. **Discrete wealth-quintile CSV** — the single highest-priority gap. "
    "Task 2 is defined as indicators varying by region *and* wealth "
    "quintile; the concentration indices already answer *whether* wealth "
    "matters, but not *which quintiles* specifically.\n"
    "2. **Age-band reconciliation** (6–59mo vs. 12–35mo stunting) — a team "
    "decision, not a coding task. Blocks treating any single stunting "
    "number as final.\n"
    "3. **Port immunisation & SBA analysis into this branch's own "
    "pipeline** and run against real KDHS data — the code exists "
    "(recovered from a teammate's branch) but hasn't been executed here.\n"
    "4. **Task 4 v2** — fold the above into the intervention ranking once "
    "available; currently v1 uses stunting alone.\n"
    "5. **Team review of the Ethics & Data Protection notes** and a "
    "rendered Quarto report attached for submission."
)
