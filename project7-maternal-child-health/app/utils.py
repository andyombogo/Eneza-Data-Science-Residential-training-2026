"""Shared data-loading helpers for all app pages.

One source of truth for file paths and loading/validation logic, so no page
duplicates another page's parsing or error handling. Every function reads
already-computed, committed aggregate outputs from data/processed/ or
outputs/ -- the app never touches restricted KDHS microdata and never
recomputes an analysis that scripts/*.R already owns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent  # the qmd source files (Project7_task2*.qmd) live here, not under project7-maternal-child-health/
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"

REGIONAL_SUMMARY = DATA_PROCESSED / "task2_stunting_summary.json"
COUNTY_STUNTING = DATA_PROCESSED / "task2_stunting_by_county.csv"
WEALTH_QUINTILE = DATA_PROCESSED / "task2_wealth_quintile.csv"
WEALTH_CONCENTRATION = DATA_PROCESSED / "task2_wealth_concentration_indices.json"
PRIORITY_COUNTIES = DATA_PROCESSED / "task4_priority_counties.csv"
WEALTH_NOTE = DATA_PROCESSED / "task4_wealth_note.txt"
HAZ_HISTOGRAM = OUTPUTS / "figures" / "task2_haz_histogram.png"
COUNTY_MAP = OUTPUTS / "maps" / "county_stunting_map.png"
IMMUNISATION_MAP = OUTPUTS / "maps" / "county_immunisation_map.png"
SBA_MAP = OUTPUTS / "maps" / "county_sba_map.png"

NATIONAL_STUNTING_PCT = 17.4  # mirrored from task2_stunting_summary.json for pages that need it before loading the full file


def _fail(message: str) -> None:
    """Show a clear, actionable error instead of an uncaught traceback, then halt the page."""
    st.error(message, icon="🚫")
    st.stop()


@st.cache_data(show_spinner=False)
def get_regional_summary() -> dict:
    try:
        with open(REGIONAL_SUMMARY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        _fail(
            f"Missing `{REGIONAL_SUMMARY.relative_to(PROJECT_ROOT)}`. "
            "Run `make regional` (`scripts/regional_analysis.R`) against real KDHS data to generate it."
        )
    except json.JSONDecodeError as e:
        _fail(f"`{REGIONAL_SUMMARY.relative_to(PROJECT_ROOT)}` is not valid JSON: {e}")


@st.cache_data(show_spinner=False)
def get_county_stunting() -> pd.DataFrame:
    try:
        df = pd.read_csv(COUNTY_STUNTING)
    except FileNotFoundError:
        _fail(
            f"Missing `{COUNTY_STUNTING.relative_to(PROJECT_ROOT)}`. "
            "Run `make regional` (`scripts/regional_analysis.R`) against real KDHS data to generate it."
        )
    expected = {"county", "prevalence_pct", "ci_lower", "ci_upper"}
    missing = expected.difference(df.columns)
    if missing:
        _fail(
            f"`{COUNTY_STUNTING.relative_to(PROJECT_ROOT)}` is missing expected "
            f"column(s): {', '.join(sorted(missing))}."
        )
    return df.sort_values("prevalence_pct", ascending=False)


def has_wealth_quintile_data() -> bool:
    return WEALTH_QUINTILE.exists()


@st.cache_data(show_spinner=False)
def get_wealth_quintile() -> pd.DataFrame | None:
    if not has_wealth_quintile_data():
        return None
    return pd.read_csv(WEALTH_QUINTILE)


def has_wealth_concentration_data() -> bool:
    return WEALTH_CONCENTRATION.exists()


@st.cache_data(show_spinner=False)
def get_wealth_concentration() -> dict | None:
    if not has_wealth_concentration_data():
        return None
    with open(WEALTH_CONCENTRATION, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def get_priority_counties() -> pd.DataFrame:
    try:
        df = pd.read_csv(PRIORITY_COUNTIES)
    except FileNotFoundError:
        _fail(
            f"Missing `{PRIORITY_COUNTIES.relative_to(PROJECT_ROOT)}`. "
            "Run `make intervention` (`scripts/intervention_prioritization.R`) to generate it."
        )
    return df.sort_values("priority_rank")


def get_wealth_note() -> str:
    if WEALTH_NOTE.exists():
        return WEALTH_NOTE.read_text(encoding="utf-8").strip()
    return (
        "Wealth-quintile data not yet available — county geography is "
        "currently the only prioritization axis. See the Wealth Analysis page."
    )


@st.cache_data(show_spinner=False)
def get_file_bytes(path: Path) -> bytes | None:
    """Cached raw bytes for a committed file, for st.download_button. None if missing."""
    p = Path(path)
    if not p.exists():
        return None
    return p.read_bytes()


@dataclass(frozen=True)
class DataFile:
    label: str
    path: Path
    task: str
    status: str  # "available" | "preliminary" | "missing"
    note: str


def data_inventory() -> list[DataFile]:
    """Live status of every file in docs/data_dictionary.md -- re-checked on every call.

    Single source of truth for the Data page's completeness table and the
    Downloads page's file list, so the two can never drift out of sync.
    """
    return [
        DataFile(
            "National stunting summary", REGIONAL_SUMMARY, "Task 2",
            "available" if REGIONAL_SUMMARY.exists() else "missing",
            "Sample sizes, methodology, national prevalence.",
        ),
        DataFile(
            "County stunting (47 counties, 95% CI)", COUNTY_STUNTING, "Task 2",
            "available" if COUNTY_STUNTING.exists() else "missing",
            "6–59 month band, survey-weighted.",
        ),
        DataFile(
            "HAZ histogram", HAZ_HISTOGRAM, "Task 2",
            "available" if HAZ_HISTOGRAM.exists() else "missing",
            "National distribution of height-for-age z-scores.",
        ),
        DataFile(
            "Wealth-equity concentration indices", WEALTH_CONCENTRATION, "Task 2",
            "preliminary" if WEALTH_CONCENTRATION.exists() else "missing",
            "Stunting/immunisation/SBA — recovered from a rendered PDF on another branch, not yet reproduced in this branch's pipeline.",
        ),
        DataFile(
            "County stunting choropleth", COUNTY_MAP, "Task 2",
            "preliminary" if COUNTY_MAP.exists() else "missing",
            "Recovered, 12–35mo band; pending regeneration on 6–59mo.",
        ),
        DataFile(
            "County immunisation choropleth", IMMUNISATION_MAP, "Task 2",
            "preliminary" if IMMUNISATION_MAP.exists() else "missing",
            "Recovered map image; no county-level immunisation number computed in this branch yet.",
        ),
        DataFile(
            "County SBA choropleth", SBA_MAP, "Task 2",
            "preliminary" if SBA_MAP.exists() else "missing",
            "Recovered map image; no county-level SBA number computed in this branch yet.",
        ),
        DataFile(
            "Discrete wealth-quintile breakdown", WEALTH_QUINTILE, "Task 2",
            "available" if WEALTH_QUINTILE.exists() else "missing",
            "5-quintile table per indicator — highest-priority remaining gap; blocked on raw KDHS access.",
        ),
        DataFile(
            "Priority counties (Task 4 v1)", PRIORITY_COUNTIES, "Task 4",
            "available" if PRIORITY_COUNTIES.exists() else "missing",
            "Ranked, from stunting data only.",
        ),
        DataFile(
            "Wealth-equity note (Task 4)", WEALTH_NOTE, "Task 4",
            "available" if WEALTH_NOTE.exists() else "missing",
            "Auto-generated placeholder until the quintile CSV lands.",
        ),
    ]


def page_footer(extra: str | None = None) -> None:
    """Consistent provenance/vintage caption at the bottom of every page."""
    st.divider()
    text = "KDHS 2022 · Eneza Data Science Residential Training 2026 · Project 7"
    if extra:
        text += f" · {extra}"
    st.caption(text)
