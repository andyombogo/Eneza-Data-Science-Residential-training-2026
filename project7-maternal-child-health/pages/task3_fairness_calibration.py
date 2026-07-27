"""Task 3 placeholder: fairness & calibration audit (not started yet)."""

import streamlit as st

st.title("⚖️ Task 3 — Fairness & Calibration Audit")
st.caption("Owners: TBD")

st.info(
    "🚧 Not started yet. This page will audit the Task 1 risk model for "
    "fairness across age groups (does it systematically under- or over-flag "
    "risk for any age band?) and check whether its predicted probabilities "
    "are well-calibrated, using the model artifact trained in Task 1.",
    icon="🚧",
)

st.markdown(
    "**Why it matters:** the Task 1 model was trained on data from health "
    "facilities in Bangladesh — this audit is the check on whether it behaves "
    "reliably and equitably before any claim is made about a Kenyan population. "
    "See the Task 1 page's *Methodology & Ethics* tab for the caveats this "
    "audit is meant to resolve."
)
