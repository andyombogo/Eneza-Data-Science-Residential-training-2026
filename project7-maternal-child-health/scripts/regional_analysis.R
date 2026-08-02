#!/usr/bin/env Rscript
# Stage 3: national + county-level stunting prevalence, survey-weighted with
# design-based 95% CIs. This is the one script whose committed outputs are
# already live in the app (data/processed/task2_stunting_summary.json,
# task2_stunting_by_county.csv, outputs/figures/task2_haz_histogram.png).
#
# Usage: Rscript scripts/regional_analysis.R

pacman::p_load(tidyverse, survey, gtsummary, jsonlite, rKenyaCensus, sf)

if (!file.exists("data/raw/kdhs_survey_design.rds")) {
  stop("data/raw/kdhs_survey_design.rds not found. Run scripts/compute_indicators.R first.")
}
df <- readRDS("data/raw/kdhs_indicators.rds")
design_full <- readRDS("data/raw/kdhs_survey_design.rds")

df_stunting <- df |> filter(in_stunting_sample)
stunting_design <- subset(design_full, in_stunting_sample)

# --- National estimate ---
tbl <- tbl_svysummary(
  stunting_design,
  include = stunted,
  statistic = all_categorical() ~ "{n} ({p})",
  digits = all_categorical() ~ c(1, 1),
  missing = "ifany", missing_text = "Missing",
  label = stunted ~ "Stunting status"
)
national_pct <- svyciprop(~I(stunted == "Stunted"), stunting_design, na.rm = TRUE)
national_ci <- confint(national_pct)

dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
dir.create("outputs/figures", showWarnings = FALSE, recursive = TRUE)
dir.create("outputs/maps", showWarnings = FALSE, recursive = TRUE)

# --- HAZ histogram, exported (previously rendered inline only -- see docs/methodology.md) ---
p_hist <- df_stunting |>
  ggplot(aes(x = haz)) +
  geom_histogram(color = "white") +
  labs(x = "Height-for-age z-score (HAZ)", y = "Frequency") +
  theme_bw(base_size = 14) +
  theme(panel.grid = element_blank())
ggsave("outputs/figures/task2_haz_histogram.png", p_hist, width = 7, height = 4.5, dpi = 150)

# --- County-level estimates ---
county_stunting <- svyby(
  ~I(stunted == "Stunted"), by = ~v024, design = stunting_design,
  FUN = svyciprop, vartype = "ci", na.rm = TRUE
)

stunting_county_export <- county_stunting |>
  mutate(
    county = names(attr(df$v024, "labels"))[match(v024, attr(df$v024, "labels"))] |>
      str_to_title() |> str_replace_all("[[:punct:]]", " ")
  ) |>
  transmute(
    county,
    prevalence_pct = round(`I(stunted == "Stunted")` * 100, 1),
    ci_lower = round(ci_l * 100, 1),
    ci_upper = round(ci_u * 100, 1)
  )
stunting_county_export$county[stunting_county_export$county == "Nairobi City"] <- "Nairobi"

write_csv(stunting_county_export, "data/processed/task2_stunting_by_county.csv")

# --- County choropleth map, exported for the app ---
kenya_shp <- rKenyaCensus::KenyaCounties_SHP |>
  janitor::clean_names() |> st_as_sf() |> select(county) |>
  mutate(county = str_to_title(county) |> str_replace_all("[[:punct:]]", " "))
kenya_shp$county[kenya_shp$county == "Nairobi City"] <- "Nairobi"

merged <- kenya_shp |> left_join(stunting_county_export, by = "county")

p_map <- merged |>
  mutate(prevalence_bin = cut(
    prevalence_pct, breaks = c(0, 10, 20, 30, 40, 50),
    labels = c("0-10", "11-20", "21-30", "31-40", "41-50"), include.lowest = TRUE
  )) |>
  ggplot() + geom_sf(aes(fill = prevalence_bin)) +
  scale_fill_brewer(palette = "OrRd", na.value = "grey85") +
  labs(fill = "Prevalence (%)") +
  theme_minimal(base_size = 14) +
  theme(axis.text = element_blank(), panel.grid = element_blank())
ggsave("outputs/maps/county_stunting_map.png", p_map, width = 7, height = 7, dpi = 150)

# --- National summary JSON, matching the app's existing schema ---
summary_json <- list(
  source = "Kenya Demographic and Health Survey (KDHS) 2022, Kids' Recode (KR) file",
  source_access = "restricted -- obtained via an approved data request to The DHS Program (dhsprogram.com); the raw microdata file is not redistributable and is not committed to this repository",
  analysis_source_file = "quarto/regional_analysis.qmd",
  methodology = "Youngest living child per mother kept per household. Stunting defined as height-for-age z-score (HAZ) < -2 SD, WHO 2006 growth reference standards. Estimates are survey-weighted (v005) and account for the two-stage cluster sample design (primary sampling unit = v021, strata = v022).",
  sample = list(
    total_children_all_ages = nrow(df),
    total_clusters = length(unique(df$v001)),
    stunting_analysis_n_6_59_months = nrow(df_stunting)
  ),
  national = list(
    stunting_prevalence_weighted_pct = round(as.numeric(national_pct) * 100, 1),
    stunting_prevalence_ci_lower = round(national_ci[1] * 100, 1),
    stunting_prevalence_ci_upper = round(national_ci[2] * 100, 1)
  ),
  subnational = list(
    status = "available",
    county_stunting_csv = "data/processed/task2_stunting_by_county.csv",
    county_map_png = "outputs/maps/county_stunting_map.png",
    county_rows = nrow(stunting_county_export)
  ),
  not_yet_analysed = list(
    "immunisation coverage summary/export",
    "skilled birth attendance summary/export",
    "wealth quintile breakdown for stunting, immunisation, and skilled birth attendance"
  )
)
write_json(summary_json, "data/processed/task2_stunting_summary.json", auto_unbox = TRUE, pretty = TRUE)

message("Regional analysis complete -> data/processed/task2_*, outputs/figures/, outputs/maps/")
