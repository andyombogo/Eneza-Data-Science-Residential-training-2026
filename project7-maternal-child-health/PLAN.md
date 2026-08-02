# Project 7 — Maternal & Child Health Outcomes: Submission Plan

**Branch:** `task2-4-submission` — the final ENEZA submission, scoped to
**Task 2** (regional & wealth indicators) and **Task 4** (intervention
targeting) only. Cut from `project7-setup` on 2026-08-02.

Mini-project development window: **2026-07-27 – 2026-08-05**.
Final presentation: **2026-08-07**.

## Scope

| # | Task | Owners | Status |
|---|------|--------|--------|
| 2 | Kenyan maternal/child indicators by region & wealth (KDHS 2022) | Kevinson Mwangi, Elphas Abok | National + county stunting done. Immunisation, SBA, and wealth-equity code exists (recovered 2026-08-02, see below) but isn't yet reproduced inside this branch's own pipeline. |
| 4 | Where to target interventions | **John Andrew, Kevinson Mwangi, Elphas Abok** (assigned 2026-08-02) | v1 live: county prioritization from stunting data (`data/processed/task4_priority_counties.csv`). v2 (folding in the recovered equity findings) is the next step. |

Every member should be able to explain the whole submission, not just their
own task.

## Recovered analysis (2026-08-02)

`origin/task2-regional-indicators` received six new commits on 2026-07-29
through 2026-08-02 that were not visible in the earlier audit of this
branch. They add a materially more complete Task 2 analysis than what was
previously recovered — full immunisation and skilled-birth-attendance
pipelines, and a wealth-equity analysis via **concentration curves/indices**
(a continuous-wealth alternative to a 5-quintile breakdown, computed with
`rineq::ci()`).

**Important — this content is not reachable by a normal `git checkout` or
`git merge` of that branch.** The branch tip (`bff4dd1`) is in a broken
state: `Project7_task2.qmd`, `Project7_task2.pdf`, and
`Project7_task2_inla.qmd` all show real diffs in `git log`/`git show --stat`,
but none of them appear in the tip commit's actual tree (`git ls-tree`) —
most likely a broken commit produced by a GUI/desktop git client. The
content still exists as git blob objects and was recovered directly:

```bash
git fetch origin
git cat-file -p abc2b75 > Project7_task2.qmd        # full descriptive analysis, 1096 lines
git cat-file -p 3e917de > Project7_task2_inla.qmd    # Bayesian spatial (INLA) small-area model, 531 lines
git cat-file -p 5395ad0 > Project7_task2.pdf         # rendered output, 25 pages
```

(Blob hashes are stable as long as `origin/task2-regional-indicators` isn't
force-pushed over. If they stop resolving, re-derive them with
`git diff --no-renames --raw <parent> <commit>` against `f025184`, `f90440b`,
and `bff4dd1` respectively.)

**What's actually real and computed** (extracted from the rendered PDF's
figures, since the `.qmd`'s inline prose stats have a bug — missing the `r`
engine prefix on inline expressions, so they render as literal code instead
of values; the code-chunk-generated *plots* rendered correctly and include
their annotated statistics):

| Indicator | Concentration index (95% CI) | Reading |
|---|---|---|
| Stunting | −0.25 (−0.28, −0.21) | Concentrated among the poor |
| Non-full immunisation | −0.16 (−0.19, −0.12) | Concentrated among the poor (smaller gap) |
| Skilled birth attendance | **+0.66 (0.62, 0.70)** | Heavily concentrated among the wealthy — the largest gap of the three |

These are now in `data/processed/task2_wealth_concentration_indices.json`
(full provenance in the file) and surfaced on the Wealth Analysis app page,
clearly labeled as recovered/not-yet-reproduced rather than presented as
this branch's own output.

**Cross-check:** that branch's independently-computed county stunting
ranking (12–35 month age band) has the same top 3 counties — **Kilifi, West
Pokot, Samburu** — as this branch's committed county CSV (6–59 month band).
Two different age-band choices, same counties on top. That convergence is
worth citing as corroboration for the Task 4 priority list, not just a
coincidence to note in passing.

**A real discrepancy that needs a team decision, not a silent pick:** the
recovered analysis restricts to **12–35 months** (harmonized across
stunting/immunisation/SBA, since immunisation and SBA questions are only
asked for that age window in KDHS 2022) and gets **21.7%** national stunting
— vs. this branch's committed **17.4%** on a **6–59 month** band (the more
standard/comparable convention for headline stunting reporting). Both are
methodologically defensible; they answer slightly different questions. Do
not silently swap one for the other — this needs Kevinson/Elphas/John to
agree on which is "the" headline number before the final submission, and
the reasoning should go in `docs/methodology.md` once decided.

**Bonus, not yet integrated:** `Project7_task2_inla.qmd` is a Bayesian
spatial (SPDE/INLA) geostatistical model for smoothed stunting prevalence —
this is the project brief's "small-area estimation" stretch goal, already
started. Requires the `INLA` R package (not on CRAN, install via
`install.packages("INLA", repos = "https://inla.r-inla-download.org/R/stable")`)
and is a **stretch goal for after the core deliverables**, not a Aug 5
priority — flagging its existence so it isn't lost, not scheduling it.

**Still genuinely missing** (the recovered `.qmd` doesn't cover this): a
literal 5-quintile breakdown per indicator (`task2_wealth_quintile.csv`,
contract below) — the recovered work answers "does this vary by wealth"
via concentration index, not "what does each quintile look like," and the
Streamlit page's bar-chart view still needs the latter. `scripts/wealth_quintile_analysis.R`
in this branch already has that code ready; it hasn't been run against real
data by anyone yet.

## Branch workflow

- `task2-4-submission` is the integration branch for the final submission
  and the branch Streamlit Cloud should deploy from once ready (see README
  § Deploy).
- `project7-setup` (the team's full 4-task training branch) is untouched by
  this restructuring — nothing was deleted there, and it remains the
  correct place for any work outside this submission's scope.
- `origin/task2-regional-indicators` should still not be merged directly
  (unchanged advice from the earlier audit — its tree is both stale
  relative to this branch's app structure *and*, as of 2026-08-02, broken
  at the tip). Recover further content from it the same way as above:
  identify the useful blob, `git cat-file -p` it out, review, integrate by
  hand.
- New work branches off the latest `task2-4-submission`, PR'd back in after
  review. Keep branches short-lived given the compressed timeline.

## Repository rules

- Do not commit raw KDHS/DHS microdata, or any individual-level derivative
  of it, at any pipeline stage. `data/raw/` stays gitignored unconditionally.
- Export only aggregate, non-identifying outputs to `data/processed/`.
- Do not commit rendered Quarto HTML (`outputs/report/` is gitignored) —
  attach a rendered copy as a release asset or hosted link instead.
- Keep runtime Python dependencies pinned in `app/requirements.txt`
  (colocated with the Streamlit entrypoint so Streamlit Cloud's dependency
  discovery finds it); the R/Quarto environment is specified in
  `environment.yml`.
- When citing a number recovered from another branch/commit rather than
  reproduced in this branch's own pipeline, say so explicitly in the data
  file and in the app (see `task2_wealth_concentration_indices.json` for
  the pattern) — don't let a recovered number silently look identical to
  one this branch actually computed.

## Task 2 output contract

The Streamlit app (`app/pages/1_Regional_Analysis.py`, `2_Wealth_Analysis.py`)
reads these files from `data/processed/`:

| File | Status | Required columns/content |
|------|--------|--------------------------|
| `task2_stunting_summary.json` | Available | source, methodology, sample counts, national stunting prevalence |
| `task2_stunting_by_county.csv` | Available | `county`, `prevalence_pct`, `ci_lower`, `ci_upper` |
| `outputs/figures/task2_haz_histogram.png` | Available | national HAZ histogram image |
| `task2_wealth_concentration_indices.json` | **Recovered (preliminary)** | stunting/immunisation/SBA concentration indices — see Recovered analysis above |
| `outputs/maps/county_stunting_map.png` | Pending | county choropleth — code ready in `scripts/regional_analysis.R`, not yet run |
| `task2_immunisation_summary.json` | Pending in this branch's pipeline | full working code recovered (`Project7_task2.qmd`), not yet ported into `scripts/compute_indicators.R` or executed |
| `task2_skilled_birth_attendance_summary.json` | Pending in this branch's pipeline | full working code recovered, not yet ported or executed |
| `task2_wealth_quintile.csv` | Pending | `indicator`, `wealth_quintile`, `prevalence_pct`, `ci_lower`, `ci_upper` — code ready in `scripts/wealth_quintile_analysis.R`, **highest-priority remaining item not covered by the recovered work** |

## Task 4 output contract

| File | Status | Required columns/content |
|------|--------|--------------------------|
| `task4_priority_counties.csv` | Available (v1) | `priority_rank`, `county`, `prevalence_pct`, `ci_lower`, `ci_upper`, `gap_vs_national_pct`, `ci_width_pct`, `priority` |
| `task4_wealth_note.txt` | Available (placeholder note until the quintile CSV lands) | One-line equity note, auto-generated by `scripts/intervention_prioritization.R` |

## Deliverables checklist

- [x] National stunting summary (Task 2)
- [x] County stunting CSV + confidence intervals (Task 2)
- [x] v1 intervention prioritization from stunting data (Task 4)
- [x] Task 4 owners assigned — John Andrew, Kevinson Mwangi, Elphas Abok
- [x] Wealth-equity concentration indices recovered and surfaced (preliminary; see caveats above)
- [ ] Reconcile the 6–59 vs 12–35 month age-band discrepancy — **needs a team decision, not code**
- [ ] Port recovered immunisation/SBA analysis into `scripts/compute_indicators.R` and run against real KDHS data
- [ ] County choropleth map export
- [ ] Discrete wealth-quintile CSV (`scripts/wealth_quintile_analysis.R`) — **highest-priority code gap**
- [ ] Task 4 v2: fold immunisation/SBA/quintile data into prioritization once available
- [ ] Ethics / Data Protection notes (`docs/ethics_data_protection.md` — drafted, needs team review)
- [ ] Rendered Quarto report attached for submission (not committed as HTML)
- [ ] Stretch goal, not blocking: integrate the recovered INLA small-area estimation model
