# Project 7 -- Maternal & Child Health Outcomes (Task 2 + Task 4)
#
# One command per pipeline stage, one command for the whole thing:
#   make all      full pipeline, raw KDHS -> app-ready outputs
#   make report   render the Quarto reports (reads outputs of `make all`)
#   make app      run the Streamlit dashboard
#
# Requires KDHS_PATH to point at your local, approved-access copy of
# KEKR8BFL.DTA for the `data`/`indicators`/`regional`/`wealth` stages.
# `intervention` and `app` need no restricted data -- they run on the
# already-committed aggregate outputs in data/processed/.

KDHS_PATH ?= data/raw/KEKR8BFL.DTA

.PHONY: all data indicators regional wealth intervention assets report app clean deps

all: wealth assets report

deps:
	pip install -r app/requirements.txt

data:
	KDHS_PATH=$(KDHS_PATH) Rscript scripts/clean_data.R

indicators: data
	Rscript scripts/compute_indicators.R

regional: indicators
	Rscript scripts/regional_analysis.R

wealth: indicators
	Rscript scripts/wealth_quintile_analysis.R

intervention: regional
	Rscript scripts/intervention_prioritization.R

assets: intervention
	Rscript scripts/export_streamlit_assets.R

report: assets
	quarto render quarto/

app:
	streamlit run app/Home.py

clean:
	rm -f data/raw/kdhs_clean.rds data/raw/kdhs_indicators.rds data/raw/kdhs_survey_design.rds
	rm -rf outputs/report/*
	find . -name __pycache__ -type d -exec rm -rf {} +
