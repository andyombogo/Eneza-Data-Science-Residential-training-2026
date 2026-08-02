"""Task 2 (wealth axis): indicators by household wealth.

Two complementary views:
1. Concentration indices (preliminary, recovered from a rendered PDF on a
   teammate's branch -- see data/processed/task2_wealth_concentration_indices.json
   for full provenance). Real, sourced numbers, not yet reproduced inside
   this branch's own pipeline.
2. A discrete 5-quintile breakdown (data/processed/task2_wealth_quintile.csv),
   which scripts/wealth_quintile_analysis.R can produce once run against
   real KDHS data -- still pending as of this page's last update.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_PROCESSED, get_wealth_quintile, has_wealth_quintile_data

CONCENTRATION_PATH = DATA_PROCESSED / "task2_wealth_concentration_indices.json"

st.set_page_config(page_title="Wealth Analysis — Project 7", page_icon="💰", layout="wide")

st.title("💰 Wealth Analysis")
st.caption("Owners: Kevinson Mwangi, Elphas Abok")
st.markdown(
    "How stunting, immunisation, and skilled birth attendance vary by "
    "household wealth — the second axis Task 2 is defined against."
)

st.divider()
st.subheader("Preliminary equity findings")

if CONCENTRATION_PATH.exists():
    with open(CONCENTRATION_PATH, encoding="utf-8") as f:
        conc = json.load(f)

    st.info(
        "Concentration indices — a continuous-wealth alternative to a "
        "5-quintile breakdown. **Negative = concentrated among the poor, "
        "positive = concentrated among the wealthy.** Recovered from a "
        "rendered report on a teammate's branch, not yet reproduced inside "
        "this branch's own pipeline — see the provenance note below before "
        "treating these as final.",
        icon="📎",
    )

    cols = st.columns(len(conc["indicators"]))
    for col, ind in zip(cols, conc["indicators"]):
        col.metric(
            ind["indicator"].replace("_", " ").title(),
            f"{ind['concentration_index']:+.2f}",
            help=f"95% CI: ({ind['ci_lower']:+.2f}, {ind['ci_upper']:+.2f})",
        )
        col.caption(ind["interpretation"])

    with st.expander("Provenance & caveats"):
        p = conc["provenance"]
        st.markdown(
            f"- **Source:** `{p['source_file']}`, branch `{p['source_branch']}`, "
            f"commit `{p['source_commit'][:10]}`, rendered {p['rendered_date']}.\n"
            f"- **How this was recovered:** {p['extracted_by']}\n"
            f"- **Sample caveat:** {p['sample_note']}\n"
            f"- **Repo state note:** {p['note']}"
        )
    st.divider()
else:
    st.warning("Concentration-index findings not found — see PLAN.md § Recovered analysis.", icon="⏳")

st.subheader("Full wealth-quintile breakdown")

if not has_wealth_quintile_data():
    st.warning(
        "**Not yet generated as a discrete 5-quintile table.** The concentration "
        "indices above already answer \"does this vary by wealth\" with real "
        "numbers; this section is the complementary quintile-by-quintile view.\n\n"
        "`scripts/wealth_quintile_analysis.R` reuses the exact survey design "
        "object built in `scripts/compute_indicators.R` (same KDHS two-stage "
        "cluster design, same weights) and groups by the DHS wealth index "
        "(`v190`) instead of county. Run `make wealth` against the real KDHS "
        "file to produce `data/processed/task2_wealth_quintile.csv`, and this "
        "section will render automatically — no code changes needed here.",
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
    st.markdown(f"**{indicator.replace('_', ' ').title()}**")
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
