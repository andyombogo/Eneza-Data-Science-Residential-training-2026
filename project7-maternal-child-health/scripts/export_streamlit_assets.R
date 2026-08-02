#!/usr/bin/env Rscript
# Final pipeline stage: (1) verify every file the Streamlit app reads
# actually exists before `make app` hands off to Python, so a broken
# pipeline fails loudly at build time, not silently as a missing image in
# the deployed app; (2) render one presentation-ready table (top priority
# counties) to outputs/tables/ for reuse in slides/docs, generated from
# data, not typed by hand.
#
# Usage: Rscript scripts/export_streamlit_assets.R

pacman::p_load(tidyverse, gt)

required <- c(
  "data/processed/task2_stunting_summary.json",
  "data/processed/task2_stunting_by_county.csv",
  "data/processed/task4_priority_counties.csv",
  "outputs/figures/task2_haz_histogram.png"
)
missing <- required[!file.exists(required)]
if (length(missing) > 0) {
  stop(
    "Missing required app assets:\n  ", paste(missing, collapse = "\n  "),
    "\nRun `make report` (regional_analysis.R + intervention_prioritization.R) first."
  )
}

optional <- c("data/processed/task2_wealth_quintile.csv", "outputs/maps/county_stunting_map.png")
for (f in optional) {
  if (!file.exists(f)) message("Note: optional asset not yet generated: ", f)
}

dir.create("outputs/tables", showWarnings = FALSE, recursive = TRUE)

priority <- read_csv("data/processed/task4_priority_counties.csv", show_col_types = FALSE)
priority_table <- priority |>
  filter(priority) |>
  select(priority_rank, county, prevalence_pct, ci_lower, ci_upper, gap_vs_national_pct) |>
  gt() |>
  cols_label(
    priority_rank = "Rank", county = "County", prevalence_pct = "Prevalence (%)",
    ci_lower = "CI lower", ci_upper = "CI upper", gap_vs_national_pct = "vs. national (pts)"
  ) |>
  tab_header(title = "Priority counties for intervention", subtitle = "Stunting prevalence ≥ national average + 1 SD")

gtsave(priority_table, "outputs/tables/task4_priority_counties.png")

message("All required app assets present. outputs/tables/task4_priority_counties.png regenerated.")
