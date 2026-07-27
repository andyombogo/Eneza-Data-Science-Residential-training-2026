"""Entry point for the Project 7 app: routes to one page per task.

Each page is self-contained; heavy imports (sklearn/pandas/matplotlib) only
happen inside the Task 1 page, so switching to a not-yet-built task page
stays instant.
"""

import streamlit as st

st.set_page_config(
    page_title="Project 7 — Maternal & Child Health Outcomes",
    page_icon="🩺",
    layout="wide",
)

overview = st.Page("pages/overview.py", title="Overview", icon="🏠", default=True)
task1 = st.Page("pages/task1_risk_classifier.py", title="Task 1 — Risk Classifier", icon="🔮")
task2 = st.Page("pages/task2_regional_indicators.py", title="Task 2 — Regional & Wealth EDA", icon="📊")
task3 = st.Page("pages/task3_fairness_calibration.py", title="Task 3 — Fairness & Calibration", icon="⚖️")
task4 = st.Page("pages/task4_interventions.py", title="Task 4 — Interventions", icon="🎯")

pg = st.navigation({
    "Project 7": [overview],
    "Tasks": [task1, task2, task3, task4],
})
pg.run()
