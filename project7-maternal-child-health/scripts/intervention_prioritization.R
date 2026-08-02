#!/usr/bin/env Rscript
# Stage 4 (Task 4): rank counties for intervention priority from the already-
# committed, aggregate Task 2 outputs. Deliberately reads only
# data/processed/ files -- no restricted KDHS access is needed to run this
# script, so it isn't blocked on the wealth-quintile/immunisation/SBA work
# landing first. If task2_wealth_quintile.csv exists, its gap is folded in
# as a secondary signal; if not, prioritization runs on stunting alone.
#
# v1 rule: a county is flagged "priority" if its stunting prevalence is at
# or above (national prevalence + 1 population SD across counties) -- i.e.
# meaningfully worse than typical, not just above the national average.
#
# Usage: Rscript scripts/intervention_prioritization.R

pacman::p_load(tidyverse)

county_path <- "data/processed/task2_stunting_by_county.csv"
if (!file.exists(county_path)) {
  stop(county_path, " not found. Run scripts/regional_analysis.R first.")
}
county <- read_csv(county_path, show_col_types = FALSE)

summary_path <- "data/processed/task2_stunting_summary.json"
national_pct <- if (file.exists(summary_path)) {
  jsonlite::fromJSON(summary_path)$national$stunting_prevalence_weighted_pct
} else {
  mean(county$prevalence_pct)  # fallback if the summary file is regenerated out of order
}

county_sd <- sd(county$prevalence_pct)
threshold <- round(national_pct + county_sd, 1)

priority <- county |>
  mutate(
    gap_vs_national_pct = round(prevalence_pct - national_pct, 1),
    ci_width_pct = round(ci_upper - ci_lower, 1),
    priority = prevalence_pct >= threshold,
    priority_rank = rank(-prevalence_pct, ties.method = "min")
  ) |>
  arrange(desc(prevalence_pct)) |>
  select(priority_rank, county, prevalence_pct, ci_lower, ci_upper,
         gap_vs_national_pct, ci_width_pct, priority)

# Optional secondary signal: fold in wealth-quintile gap once it exists.
# (No county-level wealth breakdown exists in KDHS by design -- wealth
# quintile is a household-level measure -- so this stays a national-level
# equity check alongside the county ranking above, not a per-county merge.)
wealth_path <- "data/processed/task2_wealth_quintile.csv"
wealth_note <- if (file.exists(wealth_path)) {
  w <- read_csv(wealth_path, show_col_types = FALSE) |> filter(indicator == "stunting")
  poorest <- w$prevalence_pct[w$wealth_quintile == "Poorest"]
  richest <- w$prevalence_pct[w$wealth_quintile == "Richest"]
  sprintf(
    "Poorest-quintile stunting (%.1f%%) is %.1f points above richest-quintile (%.1f%%) nationally.",
    poorest, poorest - richest, richest
  )
} else {
  "Wealth-quintile data not yet available -- this run used geography (county) as the only prioritization axis."
}

dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
write_csv(priority, "data/processed/task4_priority_counties.csv")
writeLines(wealth_note, "data/processed/task4_wealth_note.txt")

message(sprintf(
  "%d of %d counties flagged as priority (threshold = national + 1 SD = %.1f%%) -> data/processed/task4_priority_counties.csv",
  sum(priority$priority), nrow(priority), threshold
))
