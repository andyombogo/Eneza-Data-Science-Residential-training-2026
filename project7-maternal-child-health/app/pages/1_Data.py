"""Data sources, provenance, and a live completeness check.

Every fact on this page is either read from a committed file or is a
file-existence check re-run on every page load -- nothing here is a static
claim that can silently drift out of date the way a hand-written status
paragraph can.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import PROJECT_ROOT, data_inventory, get_regional_summary, page_footer

st.set_page_config(page_title="Data — Project 7", page_icon="🗂️", layout="wide")

st.title("🗂️ Data")
st.caption("Sources, access terms, and what's actually landed in this repo")

st.subheader("Sources")
st.markdown(
    "| Source | Used for | Access |\n"
    "|---|---|---|\n"
    "| [KDHS 2022](https://dhsprogram.com) (Kenya Demographic and Health "
    "Survey), Kids' Recode (`KEKR8BFL.DTA`) | Task 2, Task 4 | **Restricted** "
    "— approved DHS Program data request required; never committed to this "
    "repo (see `docs/ethics_data_protection.md`) |\n"
    "| [rKenyaCensus](https://github.com/Shelmith-Kariuki/rKenyaCensus) county "
    "shapefiles | County choropleth map | Public R package (`.rda`, R-only — "
    "not exported to GeoJSON in this repo yet) |\n"
    "| DHS geographic cluster shapefile (`KEGE8AFL.shp`) | Spatial/Bayesian "
    "(INLA, MBG) models | **Restricted** — separate DHS Program geographic "
    "data request; not present in this repo |"
)

st.warning(
    "**Raw KDHS microdata is never committed to this repository, by design.** "
    "Every number on every page below is computed from that restricted file "
    "*outside* this repo and only the small, aggregate, non-identifying "
    "output is committed to `data/processed/` — see `PLAN.md` § Repository "
    "rules.",
    icon="🔒",
)

st.divider()
st.subheader("Sample")

try:
    summary = get_regional_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("Children in cleaned sample (all ages)", f"{summary['sample']['total_children_all_ages']:,}")
    c2.metric("Survey clusters", f"{summary['sample']['total_clusters']:,}")
    c3.metric("Stunting analysis sample (6–59mo)", f"{summary['sample']['stunting_analysis_n_6_59_months']:,}")
    st.caption(summary["source"] if "source" in summary else "KDHS 2022, Kids' Recode.")
except Exception:
    st.info("Sample metrics unavailable — see completeness table below.")

st.divider()
st.subheader("Data completeness")
st.caption(
    "Live check against every file listed in `docs/data_dictionary.md` — "
    "re-verified on every page load, not a hand-maintained claim."
)

STATUS_ICON = {"available": "✅", "preliminary": "🟡", "missing": "⬜"}
STATUS_LABEL = {"available": "Available", "preliminary": "Preliminary / recovered", "missing": "Missing"}

inventory = data_inventory()
available = sum(1 for f in inventory if f.status == "available")
preliminary = sum(1 for f in inventory if f.status == "preliminary")
missing = sum(1 for f in inventory if f.status == "missing")

m1, m2, m3 = st.columns(3)
m1.metric("Available", available)
m2.metric("Preliminary / recovered", preliminary)
m3.metric("Missing", missing)

for task in ["Task 2", "Task 4"]:
    st.markdown(f"**{task}**")
    for f in inventory:
        if f.task != task:
            continue
        rel = f.path.relative_to(PROJECT_ROOT) if f.path.is_relative_to(PROJECT_ROOT) else f.path
        st.markdown(f"{STATUS_ICON[f.status]} `{rel}` — {STATUS_LABEL[f.status]}")
        st.caption(f.note)

st.divider()
st.subheader("Full data dictionary")
st.markdown(
    "Column-level schema for every file above: "
    "[`docs/data_dictionary.md`](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/blob/task2-4-submission/project7-maternal-child-health/docs/data_dictionary.md)."
)

page_footer("Data")
