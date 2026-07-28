"""Task 3: audit the Task 1 risk model for fairness across age groups and calibration.

Shared by the notebook and the Streamlit page so there is one source of truth
for how the audit is computed. Reuses the exact model configuration shipped
in task1_risk_classifier.py.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, confusion_matrix, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task1_risk_classifier import FEATURES, TARGET  # noqa: E402

RNG = 42
RISK_ORDER = ["low risk", "mid risk", "high risk"]

# ACOG-convention age groups: adolescent / reference / advanced maternal age.
AGE_BIN_EDGES = [9, 19, 34, 120]
AGE_LABELS = ["<20 (adolescent)", "20-34 (reference)", "35+ (advanced maternal age)"]


def get_age_groups(df: pd.DataFrame) -> pd.Series:
    return pd.cut(df["Age"], bins=AGE_BIN_EDGES, labels=AGE_LABELS)


def get_oof_predictions(df: pd.DataFrame):
    """Out-of-fold predictions across the full dataset.

    Uses 5-fold CV so every row is scored by a model that never trained on
    it, but pools all 1,014 rows rather than only the ~203-row held-out test
    set -- with age groups as small as ~40 high-risk cases, the single test
    split doesn't have enough per-group sample size for a trustworthy
    fairness comparison. Same tuned config as the shipped production model.
    """
    X, y = df[FEATURES], df[TARGET]
    model = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_leaf=1, random_state=RNG)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG)

    y_pred = cross_val_predict(model, X, y, cv=cv, method="predict")
    y_proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")

    model.fit(X, y)
    class_order = list(model.classes_)
    return y_pred, y_proba, class_order


def fairness_summary(df: pd.DataFrame, y_pred: np.ndarray) -> pd.DataFrame:
    age_groups = get_age_groups(df)
    y = df[TARGET]

    rows = []
    for grp in AGE_LABELS:
        mask = (age_groups == grp).values
        rows.append(
            {
                "age_group": grp,
                "n": mask.sum(),
                "accuracy": (y_pred[mask] == y[mask]).mean(),
                "high_risk_recall": recall_score(
                    y[mask], y_pred[mask], labels=["high risk"], average="macro", zero_division=0
                ),
                "macro_recall": recall_score(y[mask], y_pred[mask], average="macro", zero_division=0),
            }
        )
    return pd.DataFrame(rows).set_index("age_group")


def confusion_matrix_by_group(df: pd.DataFrame, y_pred: np.ndarray, group: str) -> pd.DataFrame:
    age_groups = get_age_groups(df)
    mask = (age_groups == group).values
    y = df[TARGET]
    cm = confusion_matrix(y[mask], y_pred[mask], labels=RISK_ORDER)
    return pd.DataFrame(cm, index=RISK_ORDER, columns=RISK_ORDER)


def bootstrap_recall_ci(
    df: pd.DataFrame, y_pred: np.ndarray, group: str, target_class: str = "high risk",
    n_boot: int = 2000, seed: int = RNG,
):
    """95% bootstrap CI on recall for `target_class`, within one age group."""
    age_groups = get_age_groups(df)
    mask = (age_groups == group).values
    y_true_grp = df[TARGET][mask].values
    y_pred_grp = np.asarray(y_pred)[mask]

    target_mask = y_true_grp == target_class
    n_target = int(target_mask.sum())
    idx_target = np.where(target_mask)[0]

    rng = np.random.default_rng(seed)
    boot_recalls = []
    for _ in range(n_boot):
        sample_idx = rng.choice(idx_target, size=n_target, replace=True)
        boot_recalls.append((y_pred_grp[sample_idx] == target_class).mean())

    point = (y_pred_grp[idx_target] == target_class).mean()
    lo, hi = np.percentile(boot_recalls, [2.5, 97.5])
    return {"n": n_target, "recall": point, "ci_lower": lo, "ci_upper": hi}


def brier_scores(df: pd.DataFrame, y_proba: np.ndarray, class_order: list) -> dict:
    y = df[TARGET]
    return {
        cls: brier_score_loss((y == cls).astype(int), y_proba[:, i])
        for i, cls in enumerate(class_order)
    }


def reliability_curve(df: pd.DataFrame, y_proba: np.ndarray, class_order: list, cls: str, n_bins: int = 10):
    y = df[TARGET]
    i = class_order.index(cls)
    frac_pos, mean_pred = calibration_curve(
        (y == cls).astype(int), y_proba[:, i], n_bins=n_bins, strategy="quantile"
    )
    return mean_pred, frac_pos
