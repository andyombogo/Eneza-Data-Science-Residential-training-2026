"""Every real, committed output file, in one place, downloadable.

Built entirely from utils.data_inventory() -- the same source of truth the
Data page's completeness table uses, so this list can't drift out of sync
with what's actually on disk.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import PROJECT_ROOT, data_inventory, get_file_bytes, page_footer

st.set_page_config(page_title="Downloads — Project 7", page_icon="⬇️", layout="wide")

st.title("⬇️ Downloads")
st.caption("Every committed Task 2 / Task 4 output — each labeled with its actual completeness status")

MIME = {".csv": "text/csv", ".json": "application/json", ".png": "image/png", ".txt": "text/plain"}
STATUS_ICON = {"available": "✅", "preliminary": "🟡", "missing": "⬜"}
STATUS_LABEL = {
    "available": "Available — produced by this branch's own pipeline",
    "preliminary": "Preliminary — recovered from another branch, not yet reproduced here",
    "missing": "Not yet generated",
}

for task in ["Task 2", "Task 4"]:
    st.subheader(task)
    for f in data_inventory():
        if f.task != task:
            continue
        rel = f.path.relative_to(PROJECT_ROOT) if f.path.is_relative_to(PROJECT_ROOT) else f.path
        col_label, col_status, col_dl = st.columns([3, 3, 2])
        col_label.markdown(f"**{f.label}**")
        col_label.caption(f.note)
        col_status.markdown(f"{STATUS_ICON[f.status]} {STATUS_LABEL[f.status]}")
        data = get_file_bytes(f.path)
        if data is not None:
            col_dl.download_button(
                "Download",
                data=data,
                file_name=f.path.name,
                mime=MIME.get(f.path.suffix, "application/octet-stream"),
                key=f"dl_{f.path.name}",
            )
        else:
            col_dl.caption("Not on disk")
    st.divider()

st.caption(
    "Column-level schema for each file: "
    "[`docs/data_dictionary.md`](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/blob/main/project7-maternal-child-health/docs/data_dictionary.md)."
)

page_footer("Downloads")
