#!/usr/bin/env Rscript
# Stage 1 of the R pipeline: load the restricted KDHS 2022 Kids' Recode file
# and restrict it to one row per mother (youngest living child), per DHS
# convention. Writes an individual-level intermediate file to data/raw/,
# which stays gitignored -- KDHS microdata is restricted-access and must
# never be committed, aggregated or not, at this stage.
#
# Usage:
#   KDHS_PATH=/path/to/KEKR8BFL.DTA Rscript scripts/clean_data.R
#
# Requires an approved data request to The DHS Program (dhsprogram.com).

pacman::p_load(tidyverse, haven, labelled)

kdhs_path <- Sys.getenv("KDHS_PATH", unset = "data/raw/KEKR8BFL.DTA")
if (!file.exists(kdhs_path)) {
  stop(
    "KDHS microdata not found at '", kdhs_path, "'. Set KDHS_PATH to your ",
    "local copy of KEKR8BFL.DTA (obtained via an approved DHS Program data ",
    "request) -- this file is restricted-access and is never committed to ",
    "this repository."
  )
}

df <- read_dta(kdhs_path)

df_clean <- df |>
  mutate(age_months = v008 - b3) |>
  filter(
    b5 == 1,        # child is alive
    b9 == 0,        # child lives with the respondent
    !is.na(v003)    # mother's line number must be available
  ) |>
  group_by(v001, v002, v003) |>       # cluster, household, mother's line number
  mutate(bidxr = rank(bidx, ties.method = "first")) |>
  filter(bidxr == 1) |>               # keep the youngest living child only
  ungroup()

dir.create("data/raw", showWarnings = FALSE, recursive = TRUE)
saveRDS(df_clean, "data/raw/kdhs_clean.rds")

message(
  sprintf(
    "Cleaned %d children from %d clusters -> data/raw/kdhs_clean.rds",
    nrow(df_clean), length(unique(df_clean$v001))
  )
)
