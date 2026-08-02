"""Task 2 (wealth axis): indicators by DHS wealth quintile.

The single highest-priority remaining gap in the project -- Task 2 is
defined as indicators varying by region *and* wealth quintile, and this
axis currently has zero coverage. This page renders real data once
scripts/wealth_quintile_analysis.R has been run against KDHS, and an
honest, actionable "pending" state until then -- never placeholder numbers.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_wealth_quintile, has_wealth_quintile_data

st.set_page_config(page_title="Wealth Analysis — Project 7", page_icon="💰", layout="wide")

st.title("💰 Wealth Analysis")
st.caption("Owners: Kevinson Mwangi, Elphas Abok")
st.markdown(
    "How stunting, immunisation, and skilled birth attendance vary by "
    "household wealth quintile — the second axis Task 2 is defined against."
)

st.divider()

if not has_wealth_quintile_data():
    st.warning(
        "**Not yet generated.** This is the highest-priority remaining gap "
        "in the project — region-only analysis answers half of what Task 2 "
        "asks for.\n\n"
        "The analysis code is complete and ready: `scripts/wealth_quintile_analysis.R` "
        "reuses the exact survey design object built in `scripts/compute_indicators.R` "
        "(same KDHS two-stage cluster design, same weights) and groups by "
        "the DHS wealth index (`v190`) instead of county. Run `make wealth` "
        "against the real KDHS file to produce `data/processed/task2_wealth_quintile.csv`, "
        "and this page will render automatically — no code changes needed here.",
        icon="⏳",
    )
    st.code("make wealth   # runs scripts/wealth_quintile_analysis.R", language="bash")
    st.stop()

wealth = get_wealth_quintile()
order = ["Poorest", "Poorer", "Middle", "Richer", "Richest"]
wealth["wealth_quintile"] = wealth["wealth_quintile"].astype(
    pd.CategoricalDtype(categories=order, ordered=True)
)

for indicator in sorted(wealth["indicator"].unique()):
    st.subheader(indicator.replace("_", " ").title())
    subset = wealth[wealth["indicator"] == indicator].sort_values("wealth_quintile")
    st.bar_chart(subset.set_index("wealth_quintile")[["prevalence_pct"]])
    poorest = subset.iloc[0]
    richest = subset.iloc[-1]
    gap = poorest["prevalence_pct"] - richest["prevalence_pct"]
    st.caption(
        f"Poorest quintile: {poorest['prevalence_pct']:.1f}% · "
        f"Richest quintile: {richest['prevalence_pct']:.1f}% · "
        f"Gap: {gap:+.1f} points"
    )
    with st.expander("Table with 95% confidence intervals"):
        st.dataframe(
            subset.rename(columns={
                "wealth_quintile": "Wealth quintile", "prevalence_pct": "Prevalence (%)",
                "ci_lower": "CI lower", "ci_upper": "CI upper",
            })[["Wealth quintile", "Prevalence (%)", "CI lower", "CI upper"]],
            hide_index=True, use_container_width=True,
        )
    st.divider()
