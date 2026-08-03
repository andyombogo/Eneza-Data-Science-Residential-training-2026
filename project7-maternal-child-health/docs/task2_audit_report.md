# Task 2 Audit & Implementation Report

**Date:** 2026-08-03
**Scope:** Full audit of Task 2 (regional & wealth-quintile indicators) against
the requirements stated on the deployed app's
[Problem Statement page](https://maternalandchildhealthoutcomes.streamlit.app/Problem_Statement),
cross-checked against the analysis source (`Project7_task2.qmd`,
`Project7_task2_inla_*.qmd`, `Project7_task2_2_mbg_*.qmd`), followed by the
Streamlit app improvements this audit motivated.

**Environment constraints that shape every finding below:** this sandbox has
no R, no Quarto, and no `INLA`/`PrevMap` packages installed, and the raw KDHS
2022 microdata (`KEKR8BFL.DTA`) — restricted-access, requires an approved DHS
Program data request — is not and cannot be committed to this repository
(see `docs/ethics_data_protection.md` and the "Repository rules" section of
`PLAN.md`). Nothing below fabricates a result that would require running that
data through R/INLA. Where a requirement is genuinely blocked on data or
tooling this environment doesn't have, that is stated explicitly, with the
exact file/package that's missing — not silently skipped and not faked.

## 1. What was reviewed

| File | Lines | What it is |
|---|---|---|
| `Project7_task2.qmd` | 1,211 | Descriptive/exploratory analysis: national + county stunting, immunisation, SBA prevalence; concentration curves + adjusted ORs by wealth |
| `Project7_task2_inla_stunting.qmd` | 538 | Bayesian spatial (SPDE/INLA) small-area model — stunting |
| `Project7_task2_inla_immunisation.qmd` | 537 | Same model — full vaccination |
| `Project7_task2_inla_sba.qmd` | 574 | Same model — skilled birth attendance |
| `Project7_task2_2_mbg_stunting.qmd` | 833 | Model-based geostatistics (MBG) prep — stunting |
| `Project7_task2_2_mbg_immunisation.qmd` | 891 | MBG prep — immunisation |
| `Project7_task2_2_mbg_sba.qmd` | 810 | MBG prep — SBA |
| `Project7_task2_inla.qmd` | 531 | Earlier combined INLA draft (stunting only), superseded by the three per-indicator files above but left in place for reference |

All eight are **R/Quarto source only** — none has a rendered `.html`/`.pdf`
output committed alongside it (contrast with `Project7_task2.pdf`, which *is*
a rendered artifact of the descriptive analysis and is how the concentration
indices already in the app were recovered). None of the INLA/MBG files can be
executed in this environment: no R interpreter is installed, and even with
one, `INLA` isn't a CRAN package (needs
`install.packages("INLA", repos="https://inla.r-inla-download.org/R/stable")`)
and both approaches additionally require the DHS geographic cluster
shapefile (`KEGE8AFL.shp`) and, for the adjusted-OR chunks in
`Project7_task2.qmd`, three CSVs under `Data/Derived_estimates/` — none of
which exist in this repository.

Also reviewed: every existing `app/pages/*.py` file, `app/utils.py`,
`app/Home.py`, `README.md`, `PLAN.md`, `docs/methodology.md`,
`docs/data_dictionary.md`, and all files under `data/processed/` and
`outputs/`.

## 2. Gap analysis table

Requirement column follows the deployed Problem Statement page's Task 2
deliverables checklist verbatim, in the same order, plus the project-wide
items that gate Task 2's completeness.

| # | Requirement | Implemented? | Evidence | What needs to be added |
|---|---|---|---|---|
| 1 | National stunting summary | **Yes** | `data/processed/task2_stunting_summary.json`; rendered on `app/pages/3_Regional_Analysis.py` | — |
| 2 | County stunting CSV + 95% CI | **Yes** | `data/processed/task2_stunting_by_county.csv` (47 rows); `utils.get_county_stunting()` | — |
| 3 | Wealth-equity concentration indices (stunting/immunisation/SBA) | **Partial** | `data/processed/task2_wealth_concentration_indices.json`, surfaced on `4_Wealth_Analysis.py` — real numbers, but recovered from a rendered PDF on another branch, not reproduced by this branch's own pipeline | Run `scripts/compute_indicators.R` + `rineq::ci()` against real `KEKR8BFL.DTA` to reproduce natively |
| 4 | County stunting choropleth map | **Partial** | `outputs/maps/county_stunting_map.png` on Regional Analysis — real map, but 12–35mo band (recovered), not the 6–59mo band used for this branch's headline number | Regenerate via `scripts/regional_analysis.R` on 6–59mo band once raw data is available |
| 5 | Immunisation & SBA county maps | **Partial** | `outputs/maps/county_immunisation_map.png`, `county_sba_map.png` exist, recovered; now surfaced on the new **Spatial & Bayesian Analysis** page with explicit provenance | Same regeneration path as #4 |
| 6 | Age-band reconciliation (6–59mo vs. 12–35mo) | **No** | `PLAN.md` § Recovered analysis documents the discrepancy (17.4% vs 21.7% national stunting) | Team decision (Kevinson/Elphas/John), not a coding task |
| 7 | Immunisation analysis ported into this branch's pipeline & executed | **No** | Source exists: `Project7_task2.qmd` lines 512–896 (national + county prevalence, concentration curve, adjusted OR) | Raw `KEKR8BFL.DTA` + R 4.3+ with `survey`, `gtsummary`, `sf`, `rineq`; then port into `scripts/compute_indicators.R` |
| 8 | SBA analysis ported & executed | **No** | Source exists: `Project7_task2.qmd` lines 898–1195 | Same as #7 |
| 9 | Stunting map regenerated on 6–59mo band | **No** | — | Same as #4 |
| 10 | Immunisation & SBA regional app pages | **Partial** | No county-level immunisation/SBA *numbers* exist in this branch (only the recovered national concentration index) to build a real regional page around — building one would mean either an empty page or a page with nothing but recovered PNGs. Instead: the recovered maps and the concentration indices are consolidated onto `4_Wealth_Analysis.py` and the new Spatial page, each labeled with exact provenance | County-level immunisation/SBA prevalence CSVs (same shape as `task2_stunting_by_county.csv`) — blocked on #7/#8 |
| 11 | Discrete wealth-quintile CSV (5-quintile breakdown per indicator) | **No** | `scripts/wealth_quintile_analysis.R` exists and is wired into `4_Wealth_Analysis.py` (`utils.has_wealth_quintile_data()` / `get_wealth_quintile()`) but has never been run against real data | Raw `KEKR8BFL.DTA`, then `make wealth` |
| 12 | Adjusted ORs by wealth status (stunting/immunisation/SBA) | **No** (source added this pass, unrun) | `Project7_task2.qmd` — `or_estimates`, `or_estimates_immun`, `or_estimates_sba` chunks | `Data/Derived_estimates/dhs_{stunting,immunisation,sba}_WI_adjusted_OR.csv` — none committed; must be generated by a (not-yet-written) adjusted-regression script against raw data |
| 13 | Small-area estimation (INLA + MBG) — stretch goal | **No** (prep source now covers all 3 indicators, added this pass) | 6 files listed in §1 | Raw microdata, DHS GPS cluster shapefile `KEGE8AFL.shp`, R + `INLA` (non-CRAN) + `PrevMap` + `sf`/`terra`/`tmap` — **none available in this environment** |
| 14 | Task 4 v1 (county prioritization from stunting) | **Yes** | `data/processed/task4_priority_counties.csv`; `6_Intervention_Prioritization.py` | — |
| 15 | Task 4 owners assigned | **Yes** | `PLAN.md`, `README.md` § Team | — |
| 16 | Task 4 v2 (fold in immunisation/SBA/quintile) | **No** | — | Blocked on #7, #8, #11 |
| 17 | Reproducible pipeline (Makefile, environment.yml, scripts/) | **Yes** | `Makefile`, `environment.yml`, `scripts/*.R` all present and documented | Executing it still needs R + raw data, which this sandbox doesn't have — the pipeline's existence is verified, its *execution* isn't |
| 18 | Ethics & Data Protection notes drafted | **Yes** | `docs/ethics_data_protection.md` | — |
| 19 | Ethics notes reviewed by team | **No** | — | Team action |
| 20 | Rendered Quarto report attached for submission | **No** | `quarto/*.qmd` exist, unrendered | Needs Quarto + R execution |

### User-specified categories (mapped onto the same evidence)

| Category | Status | Notes |
|---|---|---|
| County-level analysis | Partial | Stunting: complete (47 counties). Immunisation/SBA: no county-level numbers exist anywhere in either branch — only a national concentration index was recovered |
| Regional indicator comparisons | Partial | Stunting only; see #10 |
| Spatial analysis | Partial | Static recovered choropleths (real, preliminary) exist; no fitted spatial model exists anywhere in this repo |
| Bayesian/INLA outputs | **Not produced** | Prep code exists (this pass), never executed — see #13. No INLA output (raster, exceedance probability, credible interval) exists to show |
| Missing maternal/child health indicators | Immunisation and SBA at the *county* level; discrete wealth quintiles for all three indicators | See #7, #8, #11 |
| Model outputs | **None exist** | The concentration index (`rineq::ci()`) is a descriptive statistic, not a fitted model. No regression, MBG, or INLA model has been fit anywhere in this project's history |
| Interpretation summaries | **Yes, strong** | Every existing page already carries interpretation text/captions beneath its charts (`app/pages/*.py`); extended further in this pass (see §3) |
| Downloadable results | **No, before this pass** | No `st.download_button` existed anywhere in the app before this audit |
| Reproducibility | Partial | Pipeline is documented and modular; not executable in this sandbox (no R); the **app itself** was already fully reproducible without restricted data (a real strength, preserved) |

## 3. Implemented this pass

Everything below uses **only data that was already real and committed** —
no indicator value, concentration index, or model output was invented.
Where a visualization category the brief asked for is data-blocked (e.g. an
interactive choropleth needs county boundary geometry this repo doesn't
have in a usable format), it's listed as **not implemented** with the exact
missing asset, not silently attempted with placeholder numbers.

- **Navigation restructured** into a logical 11-page flow: Home → Problem
  Statement → Data → Methodology → Regional Analysis → Wealth Analysis →
  Spatial & Bayesian Analysis → Intervention Prioritization → Policy
  Recommendations → Downloads → About. (Existing page slugs for Regional
  Analysis, Wealth Analysis, Intervention Prioritization, and Policy
  Recommendations were preserved — only their sidebar order number changed —
  so no existing bookmarked/shared URL breaks.)
- **New Data page** (`1_Data.py`): KDHS 2022 provenance, restricted-access
  notice, sample-size metrics pulled live from `task2_stunting_summary.json`,
  and a **data completeness table** built from real file-existence checks
  across every file in `docs/data_dictionary.md` — not a static claim, it
  re-checks on every run.
- **New Methodology page** (`2_Methodology.py`): consolidates
  `docs/methodology.md` into the app (previously only reachable by reading
  the repo directly) and adds an honest **INLA/MBG methodology section**
  describing what those models are designed to do, generated directly from
  the qmd files' own section headers, with the missing prerequisites listed
  explicitly.
- **New Spatial & Bayesian Analysis page** (`7_Spatial_Bayesian_Analysis.py`):
  a status/audit page, not a fake-results page. Shows a code inventory table
  (file, line count, what each stage computes), what a completed run *would*
  produce (prediction raster with mean/SD/95% CI width, exceedance
  probability — read directly from the `write-predictions` chunk in
  `Project7_task2_inla_stunting.qmd`), the recovered static maps with
  provenance, and a **precise "what's missing to run this" checklist**.
- **Interactive visualizations**, replacing static `st.bar_chart` calls where
  real per-category data supports it:
  - Regional Analysis: interactive Plotly bar (hover tooltips, sortable,
    Viridis colorblind-safe scale) alongside the existing static map.
  - Wealth Analysis: a genuine **forest plot** (point + 95% CI whiskers) for
    the three concentration indices — this was fully supported by existing
    real numbers and is a direct implementation of the brief's "forest
    plots / coefficient plots" and "uncertainty interval visualizations"
    asks.
  - Intervention Prioritization: interactive bar, color-split by priority
    flag (fixes a limitation the page's own caption used to admit —
    *"Bars are not color-split by flag status in this chart type"*).
- **Downloads page** (`8_Downloads.py`) plus inline download buttons on
  Regional/Wealth/Intervention pages — every real committed CSV/JSON in
  `data/processed/` is downloadable, each labeled with its actual
  completeness status (not just "download" with no caveat).
- **About page** (`9_About.py`): team, data sources, tech stack, links —
  pulled from `README.md`, not new claims.
- **Robustness in `utils.py`:**
  - All loaders now catch `FileNotFoundError`/parse errors and surface a
    clear `st.error` with the exact missing path and remediation command,
    instead of an uncaught traceback.
  - New `data_inventory()` helper: single source of truth for "does this
    file exist," used by both the Data page and Downloads page.
  - Cached image-existence + byte-loading so download buttons and repeated
    page loads don't re-stat the filesystem.
  - No hardcoded absolute paths anywhere — confirmed; every path was already
    built from `Path(__file__).resolve()`, preserved as-is.
- **Styling consistency**: shared `page_footer()` helper (data-vintage +
  provenance caption) used across all pages instead of ad hoc per-page text.

## 4. Deliberately not attempted (and why)

- **Interactive choropleth map (folium/pydeck/plotly with county polygons).**
  The existing static maps are built in R from `rKenyaCensus::KenyaCounties_SHP`
  (an `.rda` object, R-only, not exported to this repo as GeoJSON). Searching
  for a substitute turned up only unverified, near-zero-star community
  GeoJSON repos of Kenya county boundaries — using one of those would mean
  shipping unvetted geographic data in a project that otherwise documents
  every provenance claim carefully (see `PLAN.md`'s repeated emphasis on
  this). **What's needed:** someone with the R environment exports
  `rKenyaCensus::KenyaCounties_SHP` to `data/external/kenya_counties.geojson`
  once (`sf::st_write()`); the interactive map is a small addition after
  that file exists. Flagged in the Data page as a known gap, not silently
  dropped.
- **Any INLA/MBG numeric output** (prediction surfaces, exceedance
  probabilities, coefficient estimates). Requires R, the non-CRAN `INLA`
  package, `PrevMap`, and the restricted DHS microdata + GPS cluster
  shapefile — none available here. Producing anything here would mean
  inventing numbers, which the brief explicitly prohibits.
- **Adjusted ORs, immunisation/SBA county tables, discrete wealth quintiles.**
  All blocked on the same raw-microdata restriction. Each has an explicit
  "what needs to be added" row in §2 rather than a fabricated value.
- **Rendered Quarto report.** Needs Quarto + R; not available in this
  sandbox. `quarto/*.qmd` files are unchanged and still the correct source
  once someone with that environment runs `quarto render`.

## 5. Final requirement checklist

- [x] Read and understood `Project7_task2.qmd` and all INLA/MBG qmd files
- [x] Compared against the deployed Problem Statement page's requirements
- [x] Gap analysis table produced (§2), every row backed by a file/line
      reference
- [x] Every requirement implementable without fabricated data has been
      implemented (§3)
- [x] Every requirement blocked by missing data/tooling is explicitly named,
      with the exact missing file/package (§2, §4) — none silently skipped
- [x] No indicator, concentration index, model coefficient, or map value was
      invented
- [x] App restructured with production-oriented navigation, error handling,
      caching, download buttons, and interpretation text throughout
- [x] `README.md`, `PLAN.md`, and the Problem Statement checklist updated to
      match reality after this pass — see the commit for exact diffs
