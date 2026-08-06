# Project 7 — Where Kenya's Child Health Gaps Are, and Where to Act First

**Regional and wealth disparities in Kenyan child health, turned into a
ranked, evidence-based case for intervention.**

Part of the [Eneza Data Science Residential Training 2026](../README.md)
([project brief](../Project_7.md)).

**Author:** John Andrew ([@andyombogo](https://github.com/andyombogo))

## 📊 Final Report / Live Application

**➡️ [maternalandchildhealthoutcomes.streamlit.app](https://maternalandchildhealthoutcomes.streamlit.app)**

**The Streamlit application above *is* this project's final report and
presentation deliverable.** It is interactive, always up to date with the
data in this repository, and is the intended entry point for anyone
reviewing this submission — start there before reading source code. It
covers, page by page: the problem statement and SDG mapping, data
provenance, methodology, wealth-equity analysis, regional/county analysis,
spatial and Bayesian small-area estimation, intervention prioritization,
policy recommendations, and every underlying output file, downloadable.

The rest of this README documents the analysis and codebase behind that
app, for anyone who wants to inspect or reproduce the pipeline.

## Project overview

Maternal and child health is a national priority in Kenya, and resources
for nutrition and health programming are finite. A national average hides
where the problem actually concentrates. This project uses the **Kenya
Demographic and Health Survey (KDHS) 2022** — Kenya's national household
health survey — to make county- and wealth-level disparities in child
health visible and explicit, across all **47 counties**, and turns the
worst gaps into a ranked, defensible starting point for where to intervene
first, rather than leaving that judgment to intuition.

Three child-health indicators, each mapped to a UN Sustainable Development
Goal, are analysed among children aged 12–35 months:

| Indicator | SDG | National prevalence |
|---|---|---|
| Stunting (height-for-age z-score < −2 SD) | SDG 2.2.1 | 21.7% |
| Full immunisation | SDG 3.b.1 | 50.3% |
| Skilled birth attendance (SBA) | SDG 3.1.2 | 88.8% |

**Data sources:**

| Source | Used for | Access |
|---|---|---|
| [KDHS 2022](https://dhsprogram.com), Kids' Recode (`KEKR8BFL.DTA`) | All indicator estimation | Restricted — approved DHS Program data request required; never committed to this repo |
| [rKenyaCensus](https://github.com/Shelmith-Kariuki/rKenyaCensus) county shapefiles | County choropleth maps | Public R package |

## Objectives

1. **Regional analysis** — quantify how stunting, full immunisation, and
   skilled birth attendance vary across Kenya's 47 counties, with
   design-based 95% confidence intervals for every estimate.
2. **Wealth analysis** — quantify how the same three indicators vary by
   household wealth, via concentration indices (continuous wealth score)
   and a 3-category (Low/Middle/High) breakdown.
3. **Intervention prioritization** — turn that regional and wealth
   variation into a ranked, transparent case for where intervention should
   go first, with estimate uncertainty made explicit rather than hidden
   behind a point estimate.
4. **Policy recommendations** — translate the ranked evidence into
   concrete, indicator-specific recommendations, stated alongside what the
   analysis does and does not claim.

## Repository structure

```
project7-maternal-child-health/
├── app/                          # Streamlit final report (see Live Application above)
│   ├── Home.py                   # landing page: headline metrics, task status
│   ├── pages/
│   │   ├── 0_Problem_Statement.py       # objectives, SDG links, deliverables status
│   │   ├── 1_Data.py                    # sources, access terms, live data-completeness check
│   │   ├── 2_Methodology.py             # methodology + INLA/MBG model specification
│   │   ├── 3_Wealth_Analysis.py         # concentration indices, forest plot
│   │   ├── 4_Regional_Analysis.py       # county maps, interactive charts, wealth-category view
│   │   ├── 5_Spatial_Bayesian_Analysis.py  # observed prevalence, diagnostics, predicted-probability maps
│   │   ├── 6_Intervention_Prioritization.py  # v1 (stunting) + v2 (multi-indicator) rankings
│   │   ├── 7_Policy_Recommendations.py  # recommendations + what this analysis doesn't claim
│   │   ├── 8_Downloads.py               # every committed output file, downloadable
│   │   └── 9_About.py                   # team, tech stack, links
│   ├── utils.py                  # shared data loaders -- one source of truth for file paths
│   └── requirements.txt          # colocated with Home.py -- Streamlit Cloud looks here, not the project root
│
├── data/
│   ├── raw/                      # gitignored -- restricted KDHS file + individual-level intermediates
│   ├── processed/                # committed -- small, aggregate, non-identifying outputs
│   └── external/                 # reserved for supporting context data (e.g. facility layers), if pursued
│
├── quarto/                       # narrative analytical reports (read data/processed/, don't recompute it)
│   ├── regional_analysis.qmd
│   ├── wealth_analysis.qmd
│   ├── intervention_analysis.qmd
│   └── _quarto.yml
│
├── scripts/                      # the only code that touches restricted KDHS data
│   ├── clean_data.R
│   ├── compute_indicators.R
│   ├── regional_analysis.R
│   ├── wealth_quintile_analysis.R
│   ├── intervention_prioritization.R   # needs no restricted data -- reads data/processed/ only
│   └── export_streamlit_assets.R
│
├── outputs/
│   ├── figures/                  # HAZ histogram, etc.
│   ├── tables/                   # presentation-ready rendered tables
│   ├── maps/                     # county choropleths
│   └── report/                   # gitignored -- rendered Quarto HTML/PDF
│
├── docs/
│   ├── methodology.md            # full methodology detail
│   ├── data_dictionary.md        # column-level schema for every committed file
│   ├── presentation_notes.md     # live-demo flow and talking points
│   └── ethics_data_protection.md # KDHS handling, Data Protection Act notes, responsible-use guidance
│
├── README.md
├── LICENSE
├── environment.yml                # one-command conda env: Python + R + Quarto
├── Makefile                       # `make all` / `make report` / `make app`
└── .gitignore
```

Repo root (one level up) also holds the R/Quarto analysis source that feeds
the committed outputs above: `Presentation.Rmd` (slide deck),
`MCH_Kenya_Task2_Task4_Pipeline.qmd` (consolidated Task 2+4 pipeline),
`Project7_task2*.qmd` (descriptive analysis + INLA/MBG small-area models,
one file per indicator), `Plots/` and `figures/` (rendered analysis
outputs consumed by the app).

## Methods

**Regional & wealth indicators:** KDHS 2022 analyzed as a two-stage cluster
survey (`survey::svydesign()`, PSU = `v021`, strata = `v022`, weights =
`v005`), restricted to the youngest living child per household, aged
12–35 months per DHS convention for the immunisation and delivery-assistance
questions. Stunting = HAZ < −2 SD (WHO 2006 growth standards). County and
wealth-group estimates use `svyby()`/`svyciprop()` for correct design-based
95% confidence intervals — not naive proportions. Wealth equity is measured
two complementary ways: Erreygers/Wagstaff-style **concentration indices**
(`rineq::ci()`) against the continuous DHS wealth score, and a discrete
**3-category (Low/Middle/High)** breakdown. Full detail:
[`docs/methodology.md`](docs/methodology.md).

**Spatial & Bayesian small-area estimation:** two complementary approaches
— model-based geostatistics (MBG: covariate-adjusted regression, variogram
diagnosis of residual spatial correlation, kriging on a 5km prediction
grid) and a Bayesian spatial model (INLA, Stochastic Partial Differential
Equation approach) — producing continuous prevalence surfaces over Kenya
rather than one flat estimate per county, with observed-vs-fitted
diagnostics for both.

**Intervention prioritization:** a county is flagged priority (v1) if its
stunting prevalence is at or above national prevalence + 1 population
standard deviation across counties — meaningfully worse than typical
variation, not just above average. A second, multi-indicator ranking (v2)
scores each county 1 point per indicator (stunting, immunisation, SBA) in
its worst-performing tertile nationally, summed — corroborating the v1
stunting-only ranking once wealth and coverage indicators are folded in.
Full derivation: [`quarto/intervention_analysis.qmd`](quarto/intervention_analysis.qmd).

**Visualization:** Plotly for interactive charts (hoverable county bars,
forest plots with confidence intervals, threshold-flagged rankings),
static R/`ggplot2` maps and diagnostic panels for the spatial models,
assembled into the Streamlit app above.

## Results

**Stunting** — 21.7% national prevalence. County prevalence spans
**9.0% (Murang'a) to 38.6% (Kilifi)** on the v1 (6–59 month band) ranking —
a 29.6-point spread a national average alone would completely hide.
Concentrated among **poorer** households (concentration index −0.25, 95%
CI −0.28 to −0.21).

**Full immunisation** — 50.3% national prevalence. Concentrated among
**wealthier** households (+0.16, 95% CI 0.12 to 0.19) — the smallest wealth
gap of the three indicators, but the same direction as SBA.

**Skilled birth attendance** — 88.8% national prevalence, high overall but
the **sharpest wealth-equity gap found in this analysis** (+0.66, 95% CI
0.62 to 0.70) — heavily concentrated among wealthier households, larger
than either stunting's or immunisation's gap.

**County rankings** — 5 of 47 counties (**Kilifi, West Pokot, Samburu,
Meru, Bomet**) sit at or above national prevalence + 1 standard deviation
on the v1 stunting-only ranking. The v2 multi-indicator vulnerability
ranking's top 3 (**West Pokot, Mandera, Samburu**) corroborates two of
these once immunisation and SBA are folded in. An independently-computed
12–35 month county-level analysis ranks **Kilifi, West Pokot, and Samburu**
as the top 3 highest-stunting counties too — the same top 3 as the
6–59-month analysis, across two different age-band choices.

**Intervention prioritization** — flagged counties carry varying
confidence-interval widths (`data/processed/task4_priority_counties.csv`,
`ci_width_pct`); estimate certainty varies county to county and should
weigh into resourcing decisions, not just the point estimate.

Full narrative and every supporting figure: the live application linked at
the top of this README.

## How to run locally

**Just the app** (no restricted data or R installation needed — reads only
the already-committed aggregate outputs in `data/processed/` and
`outputs/`):

```bash
pip install -r app/requirements.txt
streamlit run app/Home.py
```

**Full pipeline** (requires Python 3.12, R 4.3+, and Quarto — see
`environment.yml` for a one-command setup):

```bash
conda env create -f environment.yml
conda activate project7-maternal-health
Rscript -e 'remotes::install_github("Shelmith-Kariuki/rKenyaCensus")'  # not on conda-forge

export KDHS_PATH=/path/to/your/KEKR8BFL.DTA   # requires an approved DHS Program data request
make all      # data -> indicators -> regional + wealth -> intervention -> assets -> report
```

Individual pipeline stages (`make data`, `make indicators`, `make regional`,
`make wealth`, `make intervention`, `make assets`, `make report`) and Quarto
usage (`quarto render quarto/`) are documented inline in the
[`Makefile`](Makefile).

**Deploy (Streamlit Community Cloud):** main file path
`project7-maternal-child-health/app/Home.py`. `main` and `task2-4-submission`
are kept identical — either is safe to point Streamlit Cloud's deploy
source at. `app/requirements.txt` is colocated with the entrypoint so
Cloud's build picks it up automatically.
`.python-version` (pinned to `3.12`) is committed in **three** places —
repository root, `project7-maternal-child-health/`, and `app/` — deliberately
redundant, since Streamlit Cloud's `uv` build tool has previously resolved
`app/requirements.txt`'s location independently of where it looks for the
Python pin, silently falling back to a newer interpreter without one of the
three. If `app/requirements.txt` moves again, move `app/.python-version`
with it.

## Authors

**John Andrew** — [@andyombogo](https://github.com/andyombogo)

### Team

| Task | Owners |
|---|---|
| Regional & wealth indicators | Kevinson Mwangi, Elphas Abok |
| Intervention prioritization | John Andrew, Kevinson Mwangi, Elphas Abok |

Every member can explain the whole submission, not only their own task.
Additional contributions to the underlying spatial/Bayesian analysis and
regional indicators pipeline: Zaneta Kidiavai, Wahura.

## Ethics & Data Protection

See [`docs/ethics_data_protection.md`](docs/ethics_data_protection.md) —
covers KDHS microdata handling, Kenya Data Protection Act 2019 applicability
for future work, and responsible use of the intervention ranking.

## License

MIT — see [`LICENSE`](LICENSE).
