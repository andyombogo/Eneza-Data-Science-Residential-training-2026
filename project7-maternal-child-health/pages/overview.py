"""Landing page: project summary and per-task status/ownership."""

import pandas as pd
import streamlit as st

st.title("🩺 Project 7 — Maternal & Child Health Outcomes")
st.caption("Eneza Data Science Residential Training 2026")

st.markdown(
    "Maternal and child health is a national priority in Kenya. This project "
    "works with open health data at two levels: an **individual-level clinical "
    "dataset** to flag which mothers are most at risk, and **Kenyan survey "
    "indicators** to see where health services are falling short for particular "
    "communities — audited for fairness, not just accuracy."
)

st.divider()
st.subheader("Tasks & ownership")

tasks = pd.DataFrame(
    [
        {
            "#": 1,
            "Task": "Predict maternal risk level from clinical measurements",
            "Owners": "John Andrew, Jared Onsomu",
            "Status": "✅ Done",
        },
        {
            "#": 2,
            "Task": "Kenyan maternal/child indicators by region & wealth quintile",
            "Owners": "Kevinson Mwangi, Elphas Abok",
            "Status": "🟡 In progress (stunting: national done, county-level pending)",
        },
        {
            "#": 3,
            "Task": "Fairness audit (age groups) & calibration check",
            "Owners": "John Andrew, Jared Onsomu",
            "Status": "✅ Done (on task3-fairness-calibration branch, pending review/merge)",
        },
        {
            "#": 4,
            "Task": "Where to target interventions",
            "Owners": "TBD",
            "Status": "🚧 Not started",
        },
    ]
).set_index("#")

st.dataframe(tasks, use_container_width=True)
st.caption(
    "Use the sidebar to open a task. Every member should be able to explain "
    "the whole project, not just their own task."
)

st.divider()
st.subheader("Links")
st.markdown(
    "- [Project brief](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/blob/main/Project_7.md)\n"
    "- [Group plan (`PLAN.md`)](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/blob/project7-setup/project7-maternal-child-health/PLAN.md)\n"
    "- [Full source & notebooks](https://github.com/andyombogo/Eneza-Data-Science-Residential-training-2026/tree/project7-setup/project7-maternal-child-health)"
)
