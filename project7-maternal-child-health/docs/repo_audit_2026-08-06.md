# Repository & Streamlit App Audit — 2026-08-06

**Scope:** Full-repository branch audit, Streamlit app optimization, figure
audit, and branch-strategy cleanup ahead of the 2026-08-07 presentation.
Builds directly on `docs/task2_audit_report.md` (2026-08-03) and `PLAN.md`
— this pass does not repeat that gap analysis, only what changed since.

## 1. Branch state

| Branch | What it is | Status this pass |
|---|---|---|
| `main` | Untouched ENEZA training-repo template — **zero files** under `project7-maternal-child-health/` | Merged `task2-4-submission` in, pushed. Now mirrors it exactly. |
| `task2-4-submission` | The real submission — cut from `project7-setup` 2026-08-02, all Task 2/4 work lives here | Local/`origin` were briefly out of sync (an earlier `git log` showed 18 vs. 17 diverged commits from an independent rebase); resolved itself before any action was needed — both were at `e4994e2` by the time of inspection. Four new commits added this pass (below), pushed. **This remains the Streamlit Cloud deploy branch — unchanged.** |
| `origin/task2-regional-indicators` | Kevinson Mwangi's active working branch — source `.qmd` analysis, rendered figures | 45 commits ahead of what `task2-4-submission` had pulled, latest 2026-08-05. Pulled the 9 files that were pure re-renders of already-used images (county border lines added). Left his in-progress `.qmd` edits alone — **do not delete this branch, it's actively in use.** |
| `project7-setup` | Team's full 4-task training branch | Untouched, kept — out of this submission's scope by design. |

**Recommendation:** `main` = up to date, safe for the team to pull directly.
`task2-4-submission` = keep it as the Streamlit Cloud deploy source (README
already documents this; no reason to touch a working deploy the day before
presenting). Repoint Streamlit Cloud at `main` only after the hackathon, if
at all — there's no functional difference now, only risk in changing it today.

## 2. Changes made this pass

1. **Refreshed 9 MBG/INLA plots** (`Plots/*_predicted_prevalence.png`,
   `combined_diagnostics_graphs.png`, `combined_predicted_graphs.png`,
   `combined_cluster_observed_prev_graphs.png`, `fitted_vs_observed*.png`)
   from `origin/task2-regional-indicators` — same files, re-rendered with
   county border lines for geographic reference. Visually spot-checked.
2. **Downsampled 27 oversized figures** under `Plots/` from their native
   R/`ggsave` resolution (2500–7000px on the long edge, up to 2.2MB each)
   to a 1800px web ceiling — `Plots/` dropped from **19.8MB to 10.7MB**.
   Spot-checked the densest ones (`Sba_forest_plot.png`,
   `combined_diagnostics_graphs.png`) — axis labels and county names stay
   crisp. `figures/` and `outputs/` were already appropriately sized, left
   untouched.
3. **Fixed a Streamlit deprecation** present on every page: `streamlit==1.60.0`
   (the pinned version) logs a deprecation warning on every
   `use_container_width=True` call — confirmed by reading the installed
   package's source directly (`show_deprecation_warning`, stated removal
   date 2025-12-31, already past). Replaced all ~25 call sites
   (`st.image`, `st.dataframe`, `st.plotly_chart`, `st.bar_chart`) with
   `width="stretch"`, the current non-deprecated equivalent. Verified with
   Streamlit's `AppTest` harness — all 11 pages now run with **zero
   exceptions and zero warnings** in the server log (previously the log
   would carry ~25 deprecation lines per full click-through).
4. **Fixed a caption made stale by change #1** — the Spatial & Bayesian
   Analysis page said the predicted-prevalence maps showed "continuous
   gradients instead of hard county borders"; now that the refreshed maps
   do show county outlines (as a reference overlay, not prediction breaks),
   the caption was corrected to say so accurately.
5. **Committed the repo-root `.gitignore`** (Quarto render artifact
   exclusions) — it existed on disk but was never tracked, so it wasn't
   protecting anyone else's clone.

## 3. Verification

- `streamlit.testing.v1.AppTest` run against `app/Home.py` and all 10
  `app/pages/*.py` files: **11/11 pages, 0 exceptions.**
- Ran the app live (`streamlit run app/Home.py`) — clean startup, no
  warnings in the server log after exercising every page.
- `git diff --stat main task2-4-submission` is empty after the merge.

## 4. A significant finding: `Derived_data/task2_stunting_by_county.csv`

This file is **not** the duplicate its location/name suggests (it was
flagged for possible deletion going into this pass). It is a
27,818-line CSV with columns `county, county.y, prevalence, lb, ub,
geometry` — an R `sf` object written with `write.csv()` without
converting the `geometry` column to WKT first, so each county's polygon
boundary got dumped as literal R list syntax spanning many raw lines.

**Why this matters:** every page that discusses the missing interactive
choropleth (`app/pages/4_Regional_Analysis.py`, the Data page, and
`docs/task2_audit_report.md` §4) names the same blocker — no county
boundary geometry exists in this repo in a usable (GeoJSON) format, only
as an R-only `rKenyaCensus::KenyaCounties_SHP` `.rda` object. **This file
looks like exactly that missing asset**, accidentally exported in a broken
format instead of the intended one. The coordinate magnitudes (e.g.
`771766.8, 9794399.9`) are consistent with a projected CRS over Kenya —
most likely Arc 1960 / UTM zone 37S (EPSG:21037), the CRS `rKenyaCensus`
ships in.

**Not attempted this pass, and why:** turning this into a working
interactive choropleth needs `geopandas`/`shapely` (to parse the R list
syntax into real polygons) and reliable CRS confirmation before
reprojecting to WGS84 — a real feature build with genuine geometry/CRS
risk, not a polish fix, and this sandbox's Windows path-length limits
already made even a plain `pip install` fight for its life (see §5). Doing
this carelessly the day before a live demo is exactly the kind of
half-verified feature this project's own audit discipline has consistently
avoided. Left in place, undeleted, flagged here as the **highest-value
near-term follow-up** for whoever has bandwidth after the presentation —
likely a 1–2 hour job with `geopandas` in an environment without Windows
path-length issues (e.g. a Linux/Mac dev machine or Streamlit Cloud's own
build environment).

## 5. Remaining risks / blockers (carried forward, unchanged)

Everything below was already true per `docs/task2_audit_report.md` and
`PLAN.md`, and remains true — no raw KDHS microdata or R/INLA environment
was available in this pass either, so none of it was attempted:

- Raw KDHS microdata (`KEKR8BFL.DTA`) is restricted-access and correctly
  never committed — several analyses can only be reproduced by someone
  with an approved DHS data request.
- No R/INLA environment in this sandbox — the MBG/INLA source `.qmd`
  files are real and unchanged; their rendered outputs (pulled from
  `origin/task2-regional-indicators`) are what's shown in-app.
- The Task 4 v1 stunting ranking still runs on the 6–59 month county CSV,
  not the 12–35 month standard used everywhere else (no exact county-level
  12–35mo CSV exists yet, only images) — `NATIONAL_STUNTING_PCT_6_59_LEGACY`
  in `app/utils.py` keeps this explicit rather than silently mixing bands.
- No discrete 5-quintile wealth CSV (a 3-category Low/Middle/High
  breakdown exists instead).
- Adjusted ORs by wealth status: source exists in `Project7_task2.qmd`,
  still needs `Data/Derived_estimates/dhs_*_WI_adjusted_OR.csv`, not
  produced.
- The interactive-choropleth gap (§4 above) — now has a concrete,
  named path to closing it, but isn't closed.
