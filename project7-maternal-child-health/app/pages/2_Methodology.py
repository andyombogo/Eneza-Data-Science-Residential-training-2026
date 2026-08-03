"""Full methodology, surfaced in-app instead of only reachable by reading the repo.

Two parts:
1. This branch's own committed methodology (docs/methodology.md), rendered
   directly -- one source of truth, no copy that can drift out of sync.
2. The INLA / MBG small-area-estimation methodology pulled from
   Project7_task2_inla_*.qmd and Project7_task2_2_mbg_*.qmd -- described
   honestly as prepared-but-not-executed source code, not results.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import PROJECT_ROOT, REPO_ROOT, page_footer

st.set_page_config(page_title="Methodology — Project 7", page_icon="🧪", layout="wide")

st.title("🧪 Methodology")
st.caption("Survey design, indicator definitions, and the spatial/Bayesian methods prepared but not yet run")

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
st.header("Small-area estimation: INLA & MBG (prepared, not executed)")
st.markdown(
    "Two complementary Bayesian/geostatistical approaches to a **smoothed, "
    "sub-county spatial surface** of each indicator — the project brief's "
    "\"small-area estimation\" stretch goal. Both are source-only in this "
    "repo: no model has been fit, no prediction surface exists anywhere in "
    "this project's history."
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
        "**Pipeline** (from the `.qmd` source, chunk labels in order): "
        "`data-prep` → `area-boundary` (Kenya boundary + mesh) → `spde-model` "
        "→ `estimation-stack` → `model-fitting` → `diagnostics` → "
        "`prediction-grid` → `prediction-covariates` → `prediction-refit` → "
        "`exceedance-probability` → `write-predictions` (writes a raster with "
        "**mean, SD, 95% lower/upper, and CI width** bands) → `maps`.\n\n"
        "**What it would produce, if run:** a raster (`.tif`) with per-pixel "
        "posterior mean prevalence, standard deviation, 95% credible interval "
        "width, and the probability of exceeding a policy-relevant "
        "prevalence threshold — genuine uncertainty-aware small-area "
        "estimates, not just a smoothed point estimate."
    )
    for label, path in INLA_FILES.items():
        exists = path.exists()
        st.markdown(f"{'✅' if exists else '⬜'} **{label}** — `{path.name}`" + (f" ({len(path.read_text(encoding='utf-8').splitlines())} lines)" if exists else " — not found"))
    st.info(
        "**Missing to run:** the raw KDHS microdata (`KEKR8BFL.DTA`), the DHS "
        "geographic cluster shapefile (`KEGE8AFL.shp`, a *separate* "
        "restricted-access DHS Program request), R 4.3+ with the `INLA` "
        "package (not on CRAN — "
        "`install.packages(\"INLA\", repos=\"https://inla.r-inla-download.org/R/stable\")`), "
        "plus `sf`, `terra`, `tmap`. None of these are available in the "
        "environment this app was built in.",
        icon="⏳",
    )

with tab_mbg:
    st.markdown(
        "**Approach:** model-based geostatistics — a covariate-adjusted "
        "regression (age, sex, parity, mother's age/education/employment, "
        "wealth, residence) followed by variogram-based diagnosis of "
        "residual spatial correlation, the standard precursor to a full "
        "geostatistical (e.g. `PrevMap`) kriging fit.\n\n"
        "**Pipeline** (chunk labels in order): `covariates` → `final-data` → "
        "`survey-setting` → `tbl-participant-characteristics` → "
        "`univariable-regression` → `multivariable-regression` → "
        "`recode-selected-variables` → `data-collapse` (cluster-level) → "
        "`exploratory-analysis` → `correlation-plot` → `spatial-data-prep` "
        "(merge to DHS cluster shapefile, project to UTM, build a 5km "
        "prediction grid over Kenya) → `empirical-logit` → "
        "`residual-spatial-correlation` (variogram diagnostic).\n\n"
        "**Where the source stops:** at the variogram diagnostic — this is "
        "genuinely *prep*, not a fitted model. The next step (not yet "
        "written anywhere) would be a `PrevMap` geostatistical fit on the "
        "prediction grid already built here."
    )
    for label, path in MBG_FILES.items():
        exists = path.exists()
        st.markdown(f"{'✅' if exists else '⬜'} **{label}** — `{path.name}`" + (f" ({len(path.read_text(encoding='utf-8').splitlines())} lines)" if exists else " — not found"))
    st.info(
        "**Missing to run:** raw KDHS microdata, DHS geographic cluster "
        "shapefile (`KEGE8AFL.shp`), R with `survey`, `gtsummary`, `sf`, "
        "`terra`, `tmap`, and `PrevMap` (for the kriging step past where this "
        "source currently stops). None available in this environment.",
        icon="⏳",
    )

st.caption("See the Spatial & Bayesian Analysis page for a code-level audit of these files, and `docs/task2_audit_report.md` for the full gap analysis.")

page_footer("Methodology")
