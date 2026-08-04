# Methodology

## Data

**Kenya Demographic and Health Survey (KDHS) 2022**, Kids' Recode (KR) file
— a nationally representative, two-stage cluster sample covering all 47
counties. Restricted-access: obtained via an approved data request to
[The DHS Program](https://dhsprogram.com); the raw microdata file is not
redistributable and is never committed to this repository.

**County boundaries**: [rKenyaCensus](https://github.com/Shelmith-Kariuki/rKenyaCensus)
shapefiles, joined to survey estimates by county name.

## Sample restriction

Following DHS convention, the analysis keeps **one child per mother per
household — the youngest living child**:

```r
df <- df |>
  mutate(age_months = v008 - b3) |>
  filter(b5 == 1, b9 == 0, !is.na(v003)) |>   # alive, lives with respondent, mother identifiable
  group_by(v001, v002, v003) |>                # cluster, household, mother's line number
  mutate(bidxr = rank(bidx, ties.method = "first")) |>
  filter(bidxr == 1) |>
  ungroup()
```

This avoids over-weighting mothers with multiple young children and matches
how DHS itself reports child health indicators. It is not stated in the app
UI — this document is the canonical place it's recorded.

## Survey design

KDHS uses a two-stage cluster sample: primary sampling units (`v021`) are
stratified (`v022`) and individually weighted (`v005`, scaled by 1e6 per DHS
convention). All prevalence estimates use `survey::svydesign()` with this
design and `svyciprop()` / `svyby()` for design-based 95% confidence
intervals — a naive unweighted or non-clustered proportion would
misrepresent both the point estimate and its uncertainty.

```r
design <- svydesign(id = ~v021, strata = ~v022, weights = ~wt, data = df, nest = TRUE)
options(survey.lonely.psu = "adjust")
```

## Indicator definitions

| Indicator | Definition | Sample |
|---|---|---|
| Stunting | Height-for-age z-score (HAZ) < -2 SD, WHO 2006 growth reference standards | Children 12–35 months |
| Immunisation (full) | BCG, 3-dose polio + IPV, 3-dose DPT-HepB-Hib, 3-dose pneumococcal, 2-dose rotavirus, and measles-rubella all received (1 dose for 12–23mo, 2 doses for 24–35mo; KDHS `h`-series variables) | Children 12–35 months |
| Skilled birth attendance | Delivery assisted by a doctor, nurse/midwife, or clinical officer (`m3a`/`m3b` = 1) | Children 12–35 months (KDHS 2022 only asks delivery-assistance questions for a mother's most recent birth, aged 0–35 months at interview) |
| Wealth quintile | DHS wealth index (`v190`), household-level, 1 = poorest to 5 = richest | All households |

All three outcomes were standardized to the same **12–35 month** age band
(rather than each using its own natural range) so that stunting,
immunisation, and SBA are directly comparable across region and wealth —
see `Presentation.Rmd` § Approach.

## Intervention prioritization (Task 4)

**v1 rule**: a county is flagged priority if its stunting prevalence is at
or above national prevalence + 1 population standard deviation across
counties — i.e., meaningfully worse than typical inter-county variation,
not simply above the (arithmetic) national average. This threshold is a
defensible, transparent starting point, not the only valid one; see
`quarto/intervention_analysis.qmd` for the full derivation and how the
flagged list would change under alternative thresholds (e.g. top-quartile,
or a fixed percentage-point gap).

The rule is deliberately built on stunting alone (Task 2's only indicator
with full county coverage) so that Task 4 has real output without waiting
on wealth-quintile/immunisation/SBA data. `scripts/intervention_prioritization.R`
automatically folds in a wealth-quintile equity note if
`data/processed/task2_wealth_quintile.csv` exists.

## Why confidence intervals matter here

County sample sizes vary — some counties have far fewer surveyed clusters
than others. Two counties with the same point-estimate prevalence are not
equally strong evidence for action if one estimate rests on a much smaller
effective sample (visible as a wider 95% CI). Every county-level output in
this project carries its CI for this reason; the Intervention Prioritization
page surfaces CI width explicitly alongside the ranking rather than only
showing the point estimate.
