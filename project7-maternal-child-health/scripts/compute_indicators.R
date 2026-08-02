#!/usr/bin/env Rscript
# Stage 2 of the R pipeline: derive the outcome indicators (stunting,
# immunisation, skilled birth attendance) and build the survey design object
# that accounts for KDHS's two-stage cluster sample. Reads the individual-
# level intermediate from clean_data.R; writes another individual-level
# intermediate. Both stay in data/raw/ (gitignored) -- only the aggregate
# outputs computed downstream (regional_analysis.R, wealth_quintile_analysis.R)
# are safe to commit to data/processed/.
#
# Usage: Rscript scripts/compute_indicators.R

pacman::p_load(tidyverse, survey)

if (!file.exists("data/raw/kdhs_clean.rds")) {
  stop("data/raw/kdhs_clean.rds not found. Run scripts/clean_data.R first.")
}
df <- readRDS("data/raw/kdhs_clean.rds")

# --- Stunting: height-for-age z-score (HAZ) < -2 SD, WHO 2006 standards ---
df <- df |>
  mutate(
    age_months = v008 - b3,
    hw70 = ifelse(hw70 > 1000, NA, hw70),  # hw70 is HAZ * 100
    haz = hw70 / 100,
    stunted = ifelse(haz < -2, "Stunted", "Not stunted"),
    in_stunting_sample = age_months > 5 & age_months < 60
  )

# --- Immunisation: fully vaccinated by 12-23 months, KDHS 2022 schedule ---
# Fixes the malformed ifelse() pattern from the original task2-regional-
# indicators branch draft (commit eb33de3), which this pipeline supersedes.
df <- df |>
  mutate(
    in_immunisation_sample = age_months >= 12 & age_months < 24,
    fully_vaccinated = case_when(
      !in_immunisation_sample ~ NA_character_,
      h2  %in% c(1, 2, 3) & h0  %in% c(1, 2, 3) & h4  %in% c(1, 2, 3) &
      h6  %in% c(1, 2, 3) & h8  %in% c(1, 2, 3) & h60 %in% c(1, 2, 3) &
      h3  %in% c(1, 2, 3) & h5  %in% c(1, 2, 3) & h7  %in% c(1, 2, 3) &
      h54 %in% c(1, 2, 3) & h55 %in% c(1, 2, 3) & h56 %in% c(1, 2, 3) &
      h57 %in% c(1, 2, 3) & h58 %in% c(1, 2, 3) & h9  %in% c(1, 2, 3)
        ~ "Fully vaccinated",
      TRUE ~ "Not fully vaccinated"
    )
  )

# --- Skilled birth attendance: delivery assisted by a skilled provider ---
# m3a-m3i are the standard KDHS "assistance at delivery" flags; m3a/b/c
# (doctor/nurse-midwife/clinical officer) count as skilled per WHO/DHS
# convention.
df <- df |>
  mutate(
    skilled_birth_attendance = case_when(
      m3a == 1 | m3b == 1 | m3c == 1 ~ "Skilled attendant",
      TRUE ~ "Unskilled / none"
    )
  )

dir.create("data/raw", showWarnings = FALSE, recursive = TRUE)
saveRDS(df, "data/raw/kdhs_indicators.rds")

# --- Survey design: two-stage cluster sample ---
df_svy <- df |> mutate(wt = v005 / 1000000)
design <- svydesign(
  id = ~v021, strata = ~v022, weights = ~wt, data = df_svy, nest = TRUE
)
options(survey.lonely.psu = "adjust")
saveRDS(design, "data/raw/kdhs_survey_design.rds")

message("Indicators computed -> data/raw/kdhs_indicators.rds, kdhs_survey_design.rds")
