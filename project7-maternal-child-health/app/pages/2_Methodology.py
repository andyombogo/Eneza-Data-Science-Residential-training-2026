"""Full methodology, surfaced in-app instead of only reachable by reading the repo.

Two parts:
1. This branch's own committed methodology (docs/methodology.md), rendered
   directly -- one source of truth, no copy that can drift out of sync.
2. The INLA / MBG small-area-estimation methodology, pulled from
   Project7_task2_inla_*.qmd, Project7_task2_2_mbg_*.qmd, and
   Presentation.Rmd. Both models were fit by the team; the rendered
   diagnostics and predictions live on the Spatial & Bayesian Analysis page.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import PROJECT_ROOT, REPO_ROOT, page_footer

st.set_page_config(page_title="Methodology — Project 7", page_icon="🧪", layout="wide")

st.title("🧪 Methodology")
st.caption("Survey design, indicator definitions, and the spatial/Bayesian small-area models")

METHODOLOGY_MD = PROJECT_ROOT / "docs" / "methodology.md"

if METHODOLOGY_MD.exists():
    text = METHODOLOGY_MD.read_text(encoding="utf-8")
    # Drop the top-level "# Methodology" heading -- st.title already shows it.
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    st.markdown("\n".join(lines))
else:
    st.error(f"Missing `{METHODOLOGY_MD.relative_to(PROJECT_ROOT)}`.", icon="🚫")

st.divider()
st.header("Small-area estimation: INLA & MBG")
st.markdown(
    "Two complementary Bayesian/geostatistical approaches to a **smoothed, "
    "sub-county spatial surface** of each indicator — the project brief's "
    "\"small-area estimation\" stretch goal, extended to all three "
    "indicators. Rendered diagnostics and predicted-probability maps for "
    "both approaches are on the **Spatial & Bayesian Analysis** page."
)

st.subheader("Model specification")
st.markdown("**Likelihood:**")
st.latex(r"y_i \mid p_i \sim \text{Binomial}(n_i, p_i), \quad i = 1, \dots, N")
st.markdown("**Linear predictor:**")
st.latex(r"\text{logit}(p_i) = \beta_0 + \mathbf{X}_i^\top \boldsymbol{\beta} + Z(s_i) + \epsilon_i")
st.markdown(
    "Where $y_i$, $n_i$ are the number of cases and individuals sampled at "
    "cluster $i$; $\\mathbf{X}_i^\\top \\boldsymbol{\\beta}$ are the fixed "
    "effects (covariates); $Z(s_i)$ is the spatial random effect; and "
    "$\\epsilon_i$ is unstructured random noise (nugget). Source: "
    "`Presentation.Rmd` § MBG Model Specification."
)

INLA_FILES = {
    "Stunting": REPO_ROOT / "Project7_task2_inla_stunting.qmd",
    "Immunisation": REPO_ROOT / "Project7_task2_inla_immunisation.qmd",
    "Skilled birth attendance": REPO_ROOT / "Project7_task2_inla_sba.qmd",
}
MBG_FILES = {
    "Stunting": REPO_ROOT / "Project7_task2_2_mbg_stunting.qmd",
    "Immunisation": REPO_ROOT / "Project7_task2_2_mbg_immunisation.qmd",
    "Skilled birth attendance": REPO_ROOT / "Project7_task2_2_mbg_sba.qmd",
}

tab_inla, tab_mbg = st.tabs(["INLA (Bayesian spatial / SPDE)", "MBG (model-based geostatistics)"])

with tab_inla:
    st.markdown(
        "**Approach:** a Bayesian spatial model (Stochastic Partial "
        "Differential Equation / Integrated Nested Laplace Approximation) "
        "fit on DHS cluster-level prevalence, producing a continuous "
        "prediction surface over Kenya rather than one estimate per county.\n\n"
        "**Pipeline** (chunk labels in order): `data-prep` → `area-boundary` "
        "(Kenya boundary + mesh) → `spde-model` → `estimation-stack` → "
        "`model-fitting` → `diagnostics` → `prediction-grid` → "
        "`prediction-covariates` → `prediction-refit` → "
        "`exceedance-probability` → `write-predictions` (mean, SD, 95% "
        "lower/upper, and CI width) → `maps`.\n\n"
        "**Output:** per-pixel posterior mean prevalence, standard "
        "deviation, and 95% credible interval width — see the predicted "
        "probability maps on the Spatial & Bayesian Analysis page."
    )
    for label, path in INLA_FILES.items():
        exists = path.exists()
        st.markdown(f"{'✅' if exists else '⬜'} **{label}** — `{path.name}`" + (f" ({len(path.read_text(encoding='utf-8').splitlines())} lines)" if exists else " — not found"))

with tab_mbg:
    st.markdown(
        "**Approach:** model-based geostatistics — a covariate-adjusted "
        "regression (age, sex, parity, mother's age/education/employment, "
        "wealth, residence), followed by variogram diagnosis of residual "
        "spatial correlation and a geostatistical kriging fit on a 5km "
        "prediction grid over Kenya.\n\n"
        "**Pipeline** (chunk labels in order): `covariates` → `final-data` → "
        "`survey-setting` → `tbl-participant-characteristics` → "
        "`univariable-regression` → `multivariable-regression` → "
        "`recode-selected-variables` → `data-collapse` (cluster-level) → "
        "`exploratory-analysis` → `correlation-plot` → `spatial-data-prep` "
        "(merge to DHS cluster shapefile, project to UTM, build the "
        "prediction grid) → `empirical-logit` → `residual-spatial-correlation` "
        "(variogram diagnostic)."
    )
    for label, path in MBG_FILES.items():
        exists = path.exists()
        st.markdown(f"{'✅' if exists else '⬜'} **{label}** — `{path.name}`" + (f" ({len(path.read_text(encoding='utf-8').splitlines())} lines)" if exists else " — not found"))

st.caption("Rendered diagnostics and predictions: Spatial & Bayesian Analysis page. Full gap analysis: `docs/task2_audit_report.md`.")

page_footer("Methodology")
