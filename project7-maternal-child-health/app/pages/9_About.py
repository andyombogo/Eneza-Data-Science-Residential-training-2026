"""Team, tech stack, and links -- pulled from README.md content, no new claims."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import page_footer

st.set_page_config(page_title="About — Project 7", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About")
st.caption("Project 7 — Where Kenya's Maternal & Child Health Gaps Are, and What To Do About Them")

st.markdown(
    "Part of the [Eneza Data Science Residential Training 2026](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026). "
    "Development window: 2026-07-27 – 2026-08-05. Final presentation: 2026-08-07."
)

st.divider()
st.subheader("Team")
st.markdown(
    "| Task | Owners |\n"
    "|---|---|\n"
    "| Task 2 — Regional & wealth-quintile indicators | Kevinson Mwangi, Elphas Abok |\n"
    "| Task 4 — Intervention targeting | John Andrew, Kevinson Mwangi, Elphas Abok |\n\n"
    "Per the brief's requirement, every member should be able to explain the "
    "whole submission, not only their own task."
)

st.divider()
st.subheader("Tech stack")
st.markdown(
    "- **Analysis:** R (`survey`, `gtsummary`, `sf`, `rineq`), Quarto\n"
    "- **App:** Python, Streamlit, Plotly\n"
    "- **Data:** [KDHS 2022](https://dhsprogram.com) (Kenya Demographic and "
    "Health Survey), [rKenyaCensus](https://github.com/Shelmith-Kariuki/rKenyaCensus)\n"
    "- **Reproducibility:** `Makefile`, `environment.yml` (one-command "
    "Python + R + Quarto env)"
)

st.divider()
st.subheader("Links")
st.markdown(
    "- [Repository](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026)\n"
    "- [Project brief (`Project_7.md`)](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/blob/main/Project_7.md)\n"
    "- [Live application](https://maternalandchildhealthoutcomes.streamlit.app) — this app, deployed"
)

st.divider()
st.subheader("Ethics & Data Protection")
st.markdown(
    "See `docs/ethics_data_protection.md` — covers KDHS microdata handling, "
    "Kenya Data Protection Act 2019 applicability, and responsible use of "
    "the intervention ranking."
)

st.divider()
st.subheader("License")
st.markdown("MIT — see `LICENSE`.")

page_footer("About")
