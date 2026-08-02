"""Shared data-loading helpers for all app pages.

One source of truth for file paths and loading/validation logic, so no page
duplicates another page's parsing or error handling. Every function reads
already-computed, committed aggregate outputs from data/processed/ or
outputs/ -- the app never touches restricted KDHS microdata and never
recomputes an analysis that scripts/*.R already owns.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"

REGIONAL_SUMMARY = DATA_PROCESSED / "task2_stunting_summary.json"
COUNTY_STUNTING = DATA_PROCESSED / "task2_stunting_by_county.csv"
WEALTH_QUINTILE = DATA_PROCESSED / "task2_wealth_quintile.csv"
PRIORITY_COUNTIES = DATA_PROCESSED / "task4_priority_counties.csv"
WEALTH_NOTE = DATA_PROCESSED / "task4_wealth_note.txt"
HAZ_HISTOGRAM = OUTPUTS / "figures" / "task2_haz_histogram.png"
COUNTY_MAP = OUTPUTS / "maps" / "county_stunting_map.png"

NATIONAL_STUNTING_PCT = 17.4  # mirrored from task2_stunting_summary.json for pages that need it before loading the full file


@st.cache_data(show_spinner=False)
def get_regional_summary() -> dict:
    with open(REGIONAL_SUMMARY, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def get_county_stunting() -> pd.DataFrame:
    df = pd.read_csv(COUNTY_STUNTING)
    expected = {"county", "prevalence_pct", "ci_lower", "ci_upper"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Missing expected county stunting columns: {', '.join(sorted(missing))}")
    return df.sort_values("prevalence_pct", ascending=False)


def has_wealth_quintile_data() -> bool:
    return WEALTH_QUINTILE.exists()


@st.cache_data(show_spinner=False)
def get_wealth_quintile() -> pd.DataFrame | None:
    if not has_wealth_quintile_data():
        return None
    return pd.read_csv(WEALTH_QUINTILE)


@st.cache_data(show_spinner=False)
def get_priority_counties() -> pd.DataFrame:
    df = pd.read_csv(PRIORITY_COUNTIES)
    return df.sort_values("priority_rank")


def get_wealth_note() -> str:
    if WEALTH_NOTE.exists():
        return WEALTH_NOTE.read_text(encoding="utf-8").strip()
    return (
        "Wealth-quintile data not yet available — county geography is "
        "currently the only prioritization axis. See the Wealth Analysis page."
    )
