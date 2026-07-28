"""Task 3: fairness (across age groups) and calibration audit of the Task 1 model.

Reuses src/task3_fairness_audit.py for all computation -- this page is the
presentation layer, same pattern as Task 1's page and notebook.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from task1_risk_classifier import load_data  # noqa: E402
from task3_fairness_audit import (  # noqa: E402
    AGE_LABELS,
    RISK_ORDER,
    bootstrap_recall_ci,
    brier_scores,
    confusion_matrix_by_group,
    fairness_summary,
    get_oof_predictions,
    reliability_curve,
)

RISK_COLOR = {"low risk": "#4C9F70", "mid risk": "#E8A33D", "high risk": "#C1443C"}
AGE_COLOR = {AGE_LABELS[0]: "#3B6FA0", AGE_LABELS[1]: "#4C9F70", AGE_LABELS[2]: "#8E5A9E"}


@st.cache_data(show_spinner="Loading data...")
def get_data() -> pd.DataFrame:
    try:
        return load_data()
    except FileNotFoundError:
        from ucimlrepo import fetch_ucirepo

        dataset = fetch_ucirepo(id=863)
        df = dataset.data.features.copy()
        df[dataset.data.targets.columns[0]] = dataset.data.targets
        return df


@st.cache_resource(show_spinner="Generating out-of-fold predictions for the fairness audit...")
def get_audit():
    df = get_data()
    y_pred, y_proba, class_order = get_oof_predictions(df)
    return y_pred, y_proba, class_order


df = get_data()
y_pred, y_proba, class_order = get_audit()
summary_df = fairness_summary(df, y_pred)

st.title("⚖️ Task 3 — Fairness & Calibration Audit")
st.caption("Owners: John Andrew, Jared Onsomu")

st.markdown(
    "Does the Task 1 risk model perform **equally well across age groups**, "
    "and are its predicted probabilities **trustworthy** — not just the top "
    "predicted class? Audited using out-of-fold predictions across the full "
    "1,014-row dataset (5-fold CV, same tuned model as Task 1) rather than "
    "just the 203-row test set, since the smallest age/class combination "
    "has as few as ~39 cases — too little for a reliable subgroup estimate "
    "from the test set alone. Full derivation in "
    "`notebooks/task3_fairness_calibration_audit.ipynb`."
)

st.info(
    "⚠️ **Data-quality caveat:** `Age` in this dataset ranges 10–70, which "
    "includes biologically implausible values for a maternal-health "
    "dataset. A known property of the source data, not introduced here — "
    "but a reason to treat the age-extreme findings below with some care.",
    icon="⚠️",
)

st.divider()

# --------------------------------------------------------------------------
# Headline finding
# --------------------------------------------------------------------------

st.subheader("Headline finding: a real fairness gap in the youngest group")

ci_rows = []
for grp in AGE_LABELS:
    result = bootstrap_recall_ci(df, y_pred, grp, target_class="high risk")
    ci_rows.append({"age_group": grp, **result})
ci_df = pd.DataFrame(ci_rows).set_index("age_group")

m1, m2, m3 = st.columns(3)
for col, grp in zip([m1, m2, m3], AGE_LABELS):
    col.metric(
        f"High-risk recall — {grp.split(' ')[0]}",
        f"{ci_df.loc[grp, 'recall']:.1%}",
        help=f"95% CI: [{ci_df.loc[grp, 'ci_lower']:.1%}, {ci_df.loc[grp, 'ci_upper']:.1%}], "
        f"n={int(ci_df.loc[grp, 'n'])} true high-risk cases",
    )

fig, ax = plt.subplots(figsize=(8, 3))
y_pos = np.arange(len(AGE_LABELS))
ax.errorbar(
    ci_df["recall"], y_pos,
    xerr=[ci_df["recall"] - ci_df["ci_lower"], ci_df["ci_upper"] - ci_df["recall"]],
    fmt="o", color="#C1443C", capsize=5, markersize=8,
)
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{g}\n(n={int(n)} high-risk cases)" for g, n in zip(AGE_LABELS, ci_df["n"])])
ax.set_xlabel("high risk recall (95% bootstrap CI)")
ax.set_xlim(0.5, 1.05)
plt.tight_layout()
st.pyplot(fig)

st.markdown(
    "The **`<20` (adolescent) group's high-risk recall (≈85%) sits below "
    "the `20–34` reference group's (≈96%)**, with 95% confidence intervals "
    "that barely overlap — this is a real gap, not sampling noise. "
    "Precision for `high risk` in the adolescent group is actually perfect "
    "(no false alarms) — the failure mode is specifically **under-flagging** "
    "real high-risk adolescents as `mid risk` instead, not over-flagging."
)

st.divider()

# --------------------------------------------------------------------------
# Per-group performance
# --------------------------------------------------------------------------

st.subheader("Per-age-group performance")
st.dataframe(summary_df.style.format({"accuracy": "{:.3f}", "high_risk_recall": "{:.3f}", "macro_recall": "{:.3f}"}),
             use_container_width=True)

st.caption(
    "The `35+` group has the **lowest overall accuracy**, but that's a "
    "*separate* issue from the adolescent recall gap above — its high-risk "
    "recall (90%) is actually the second-best of the three groups; its "
    "weaker macro performance comes from confusing `low risk` and "
    "`mid risk` with each other, visible in the confusion matrices below."
)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, grp in zip(axes, AGE_LABELS):
    cm = confusion_matrix_by_group(df, y_pred, grp)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                xticklabels=RISK_ORDER, yticklabels=RISK_ORDER)
    ax.set_title(f"{grp}\n(n={int(summary_df.loc[grp, 'n'])})", fontsize=10)
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
plt.tight_layout()
st.pyplot(fig)

st.divider()

# --------------------------------------------------------------------------
# Calibration
# --------------------------------------------------------------------------

st.subheader("Calibration: are the predicted probabilities trustworthy?")
st.caption(
    "A model can rank classes correctly while still being poorly "
    "calibrated (e.g. its \"70% high risk\" calls might only be right 40% "
    "of the time). Checked via Brier score (lower = better) and reliability "
    "curves (predicted probability vs. observed frequency)."
)

brier = brier_scores(df, y_proba, class_order)
bcol1, bcol2, bcol3 = st.columns(3)
for col, cls in zip([bcol1, bcol2, bcol3], RISK_ORDER):
    col.metric(f"Brier score — {cls}", f"{brier[cls]:.3f}", help="Lower is better; 0 = perfect")

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, cls in zip(axes, RISK_ORDER):
    mean_pred, frac_pos = reliability_curve(df, y_proba, class_order, cls)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="perfect calibration")
    ax.plot(mean_pred, frac_pos, marker="o", color=RISK_COLOR[cls])
    ax.set_title(f"{cls} (Brier = {brier[cls]:.3f})", fontsize=10)
    ax.set_xlabel("mean predicted probability")
    ax.set_ylabel("observed frequency")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=7)
plt.tight_layout()
st.pyplot(fig)

st.markdown(
    "**`high risk` is best-calibrated** of the three classes (lowest Brier "
    "score, reliability curve closest to the diagonal) — reassuring, since "
    "it's the class where trust matters most. **`mid risk` is the least "
    "reliable** — consistent with Task 1's finding that it's the hardest "
    "class to separate from its neighbours. Trust the model's *top class* "
    "prediction across all three risk levels; treat its exact predicted "
    "*probability* for `mid risk` as a rougher signal."
)

st.divider()

# --------------------------------------------------------------------------
# Recommendations
# --------------------------------------------------------------------------

st.subheader("Recommendations")
st.markdown(
    """
- **Give adolescent `mid risk` predictions a closer look.** Since the model
  specifically under-detects true `high risk` cases in the `<20` group by
  relabelling them `mid risk`, a `mid risk` call in this age group carries
  more risk of masking a true high-risk case than the same call would for
  an older mother — worth a lower threshold for clinician follow-up in
  practice, not treating all `mid risk` labels as equally reassuring.
- **Prioritise more adolescent high-risk training examples** if this model
  is ever retrained — the `<20` group's blind spot is the single most
  actionable, statistically-supported finding here.
- **Don't over-read `mid risk` probability values** — the top-class
  prediction is trustworthy, but the exact confidence number for `mid risk`
  specifically is the least calibrated of the three classes.
- **Re-run this audit if the model is retrained on Kenyan data** (Task 2) —
  this fairness pattern was found on the Bangladeshi source data; whether
  it transfers is an open question, not an assumption.
    """
)
