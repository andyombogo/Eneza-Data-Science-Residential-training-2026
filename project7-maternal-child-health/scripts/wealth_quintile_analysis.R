#!/usr/bin/env Rscript
# Stage 3b: stunting, immunisation, and SBA prevalence by DHS wealth quintile
# (v190: 1 = poorest ... 5 = richest). Mirrors regional_analysis.R's pattern
# exactly -- same survey design object, svyby() instead of a county grouping.
#
# STATUS: not yet run against the real KDHS file (owners: Kevinson Mwangi,
# Elphas Abok). The code below is correct and ready to run against an
# approved-access copy of KEKR8BFL.DTA -- see README.md § How to run locally.
# Wealth equity is covered in the meantime via concentration indices and a
# 3-category breakdown (data/processed/task2_wealth_concentration_indices.json,
# figures/fig-wealth-category-indicators-1.png).
#
# Usage: Rscript scripts/wealth_quintile_analysis.R

pacman::p_load(tidyverse, survey, jsonlite)

if (!file.exists("data/raw/kdhs_survey_design.rds")) {
  stop("data/raw/kdhs_survey_design.rds not found. Run scripts/compute_indicators.R first.")
}
df <- readRDS("data/raw/kdhs_indicators.rds")
design_full <- readRDS("data/raw/kdhs_survey_design.rds")

wealth_labels <- c("1" = "Poorest", "2" = "Poorer", "3" = "Middle", "4" = "Richer", "5" = "Richest")

by_wealth <- function(design, subset_expr, outcome_expr, indicator_name) {
  d <- subset(design, subset_expr)
  est <- svyby(outcome_expr, by = ~v190, design = d, FUN = svyciprop, vartype = "ci", na.rm = TRUE)
  tibble(
    indicator = indicator_name,
    wealth_quintile = wealth_labels[as.character(est$v190)],
    prevalence_pct = round(est[[2]] * 100, 1),
    ci_lower = round(est$ci_l * 100, 1),
    ci_upper = round(est$ci_u * 100, 1)
  )
}

stunting_by_wealth <- by_wealth(
  design_full, df$in_stunting_sample, ~I(stunted == "Stunted"), "stunting"
)
immunisation_by_wealth <- by_wealth(
  design_full, df$in_immunisation_sample, ~I(fully_vaccinated == "Fully vaccinated"), "immunisation"
)
sba_by_wealth <- by_wealth(
  design_full, rep(TRUE, nrow(df)), ~I(skilled_birth_attendance == "Skilled attendant"), "skilled_birth_attendance"
)

wealth_export <- bind_rows(stunting_by_wealth, immunisation_by_wealth, sba_by_wealth) |>
  mutate(wealth_quintile = factor(wealth_quintile, levels = wealth_labels)) |>
  arrange(indicator, wealth_quintile)

dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
write_csv(wealth_export, "data/processed/task2_wealth_quintile.csv")

message("Wealth-quintile analysis complete -> data/processed/task2_wealth_quintile.csv")
