"""Task 1: interactive maternal risk predictor + model report.

Trains itself in-memory on first load (cached after that) instead of relying
on a committed model/data file, so it deploys cleanly from a clean clone or a
cloud host with no local `data/raw/` present.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from task1_risk_classifier import (  # noqa: E402
    FEATURES,
    TARGET,
    load_data,
    split_data,
    train,
)

RISK_ORDER = ["low risk", "mid risk", "high risk"]
RISK_COLOR = {"low risk": "#4C9F70", "mid risk": "#E8A33D", "high risk": "#C1443C"}
RNG = 42


# --------------------------------------------------------------------------
# Cached data / model
# --------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading maternal health data...")
def get_data() -> pd.DataFrame:
    try:
        return load_data()
    except FileNotFoundError:
        from ucimlrepo import fetch_ucirepo

        dataset = fetch_ucirepo(id=863)
        df = dataset.data.features.copy()
        df[dataset.data.targets.columns[0]] = dataset.data.targets
        return df


@st.cache_resource(show_spinner="Training the risk classifier...")
def get_trained():
    return train(get_data())


@st.cache_resource(show_spinner="Cross-validating candidate models (Logistic Regression / Random Forest / Gradient Boosting)...")
def get_model_comparison() -> pd.DataFrame:
    df = get_data()
    X_train, _, y_train, _ = split_data(df)

    candidates = {
        "Logistic Regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=RNG)
        ),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=RNG),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RNG),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG)

    rows = []
    for name, est in candidates.items():
        scores = cross_validate(
            est, X_train, y_train, cv=cv, scoring=["accuracy", "recall_macro", "f1_macro"]
        )
        rows.append(
            {
                "Model": name,
                "CV accuracy": scores["test_accuracy"].mean(),
                "CV recall (macro)": scores["test_recall_macro"].mean(),
                "CV F1 (macro)": scores["test_f1_macro"].mean(),
            }
        )
    return pd.DataFrame(rows).set_index("Model").sort_values("CV F1 (macro)", ascending=False)


@st.cache_data(show_spinner="Checking why the split is stratified...")
def get_stratification_demo():
    df = get_data()
    X, y = df[FEATURES], df[TARGET]

    unstratified_shares = []
    for seed in range(20):
        _, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
        unstratified_shares.append((y_te == "high risk").mean())

    _, _, _, y_te_strat = split_data(df)
    return {
        "population": (y == "high risk").mean(),
        "stratified": (y_te_strat == "high risk").mean(),
        "unstratified": unstratified_shares,
    }


df = get_data()
model, results = get_trained()

st.title("🔮 Task 1 — Maternal Health Risk Predictor")
st.caption("Owners: John Andrew, Jared Onsomu")

tab_predict, tab_performance, tab_explore, tab_about = st.tabs(
    ["🔮 Predict", "📊 Model Performance", "🔍 Explore the Data", "📖 Methodology & Ethics"]
)

# --------------------------------------------------------------------------
# Tab 1: Predict
# --------------------------------------------------------------------------

with tab_predict:
    st.subheader("Enter routine clinical measurements")
    st.caption(
        "This mirrors what can be measured at a basic antenatal visit — no lab "
        "infrastructure required."
    )

    ranges = {f: (float(df[f].min()), float(df[f].max()), float(df[f].median())) for f in FEATURES}
    units = {
        "Age": "years", "SystolicBP": "mmHg", "DiastolicBP": "mmHg",
        "BS": "mmol/L", "BodyTemp": "°F", "HeartRate": "bpm",
    }

    col1, col2, col3 = st.columns(3)
    inputs = {}
    for i, feature in enumerate(FEATURES):
        lo, hi, default = ranges[feature]
        col = [col1, col2, col3][i % 3]
        inputs[feature] = col.number_input(
            f"{feature} ({units[feature]})",
            min_value=round(lo - abs(lo) * 0.2, 1),
            max_value=round(hi + abs(hi) * 0.2, 1),
            value=round(default, 1),
            help=f"Observed training range: {lo:g}–{hi:g} {units[feature]}",
        )

    out_of_range = [
        f for f in FEATURES if not (ranges[f][0] <= inputs[f] <= ranges[f][1])
    ]
    if out_of_range:
        st.warning(
            "Outside the observed training range for: "
            + ", ".join(out_of_range)
            + ". The prediction below is an extrapolation and less reliable."
        )

    if st.button("Predict risk level", type="primary"):
        X_input = pd.DataFrame([inputs], columns=FEATURES)
        proba = model.predict_proba(X_input)[0]
        pred = model.classes_[proba.argmax()]

        badge = {
            "low risk": st.success,
            "mid risk": st.warning,
            "high risk": st.error,
        }[pred]
        badge(f"Predicted risk level: **{pred.upper()}**  ({proba.max():.0%} confidence)")

        prob_df = pd.Series(proba, index=model.classes_).reindex(RISK_ORDER)
        fig, ax = plt.subplots(figsize=(6, 2.5))
        ax.barh(prob_df.index, prob_df.values, color=[RISK_COLOR[c] for c in prob_df.index])
        ax.set_xlim(0, 1)
        ax.set_xlabel("predicted probability")
        for i, v in enumerate(prob_df.values):
            ax.text(v + 0.01, i, f"{v:.0%}", va="center")
        plt.tight_layout()
        st.pyplot(fig)

    st.info(
        "⚠️ **This is a decision-support screening tool, not a diagnostic device.** "
        "It must not replace clinical judgement — see the Methodology & Ethics tab.",
        icon="⚠️",
    )

# --------------------------------------------------------------------------
# Tab 2: Model performance
# --------------------------------------------------------------------------

with tab_performance:
    st.subheader("Final model: tuned Random Forest")

    report_df = pd.DataFrame(results["report"]).T
    class_report = report_df.loc[RISK_ORDER, ["precision", "recall", "f1-score", "support"]]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Test accuracy", f"{report_df.loc['accuracy', 'precision']:.1%}")
    m2.metric("High-risk recall", f"{class_report.loc['high risk', 'recall']:.1%}")
    m3.metric("Mid-risk recall", f"{class_report.loc['mid risk', 'recall']:.1%}")
    m4.metric("Low-risk recall", f"{class_report.loc['low risk', 'recall']:.1%}")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Confusion matrix (test set)**")
        disp = ConfusionMatrixDisplay(
            confusion_matrix=results["confusion_matrix"], display_labels=results["labels"]
        )
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        plt.tight_layout()
        st.pyplot(fig)

    with col_right:
        st.markdown("**Classification report**")
        st.dataframe(class_report.style.format("{:.3f}"), use_container_width=True)

        st.markdown("**Feature importance**")
        importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
        fig, ax = plt.subplots(figsize=(5, 3))
        importances.plot(kind="barh", ax=ax, color="#3B6FA0")
        ax.set_xlabel("mean decrease in impurity")
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()
    st.subheader("Why Random Forest? A cross-validated comparison, not an assumption")
    st.caption(
        "5-fold stratified cross-validation on the training split only "
        "(test set never touched during model selection)."
    )
    comparison_df = get_model_comparison()
    st.dataframe(comparison_df.style.format("{:.3f}").highlight_max(axis=0, color="#d4edda"),
                 use_container_width=True)
    st.bar_chart(comparison_df)

    st.markdown(
        "The linear baseline (Logistic Regression) is clearly outmatched, confirming "
        "that risk boundaries in this data aren't linear — blood sugar in particular "
        "behaves more like a threshold effect (see **Explore the Data**). Random "
        "Forest is preferred over Gradient Boosting when the two are close, since it "
        "overfits less readily on a dataset this size (~1,000 rows)."
    )

    st.markdown(
        "**Hyperparameter tuning** (grid search over `n_estimators`, `max_depth`, "
        "`min_samples_leaf`; 27 candidates, 5-fold CV, full run in "
        "`notebooks/task1_risk_classifier_eda.ipynb`):"
    )
    tuning_df = pd.DataFrame(
        {
            "n_estimators": [300, 200],
            "max_depth": ["unlimited", "20"],
            "min_samples_leaf": [1, 1],
            "CV macro F1": [0.819, 0.827],
        },
        index=["Untuned default", "Tuned (shipped)"],
    )
    st.dataframe(tuning_df, use_container_width=True)

# --------------------------------------------------------------------------
# Tab 3: Explore the data
# --------------------------------------------------------------------------

with tab_explore:
    st.subheader("Class distribution")
    counts = df[TARGET].value_counts().reindex(RISK_ORDER)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(counts.index, counts.values, color=[RISK_COLOR[c] for c in counts.index])
    for i, v in enumerate(counts):
        ax.text(i, v + 5, str(v), ha="center")
    ax.set_ylabel("count")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Feature distributions by risk level")
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, feature in zip(axes.ravel(), FEATURES):
        sns.boxplot(
            data=df, x=TARGET, y=feature, order=RISK_ORDER, ax=ax, hue=TARGET,
            palette=RISK_COLOR, legend=False,
        )
        ax.set_title(feature)
        ax.set_xlabel("")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Feature correlation")
    corr = df[FEATURES].corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

# --------------------------------------------------------------------------
# Tab 4: Methodology & ethics
# --------------------------------------------------------------------------

with tab_about:
    st.subheader("Why a stratified train/test split?")
    demo = get_stratification_demo()
    c1, c2, c3 = st.columns(3)
    c1.metric("True population share", f"{demo['population']:.1%}")
    c2.metric("Stratified split (used)", f"{demo['stratified']:.1%}")
    c3.metric(
        "20× unstratified splits",
        f"{min(demo['unstratified']):.1%} – {max(demo['unstratified']):.1%}",
        help="Range across 20 random (non-stratified) 80/20 splits",
    )
    st.markdown(
        "With only ~270 `high risk` rows to begin with, an 80/20 split leaves just "
        "~55 in the test fold — small enough that an unstratified random split can "
        "swing the minority-class share by several points (as shown above). "
        "Stratification pins it to the true ratio, which is what makes the "
        "`high risk` recall reported in **Model Performance** trustworthy rather "
        "than a roll of the dice."
    )

    st.divider()
    st.subheader("Limitations & ethical considerations")
    st.markdown(
        """
- **Not a clinical diagnostic tool.** This model supports triage/screening
  discussions; it must not replace clinical judgement or be deployed without
  supervision by qualified health workers.
- **Population mismatch risk.** The training data comes from health facilities
  in Bangladesh (UCI Maternal Health Risk dataset). Vitals thresholds and risk
  patterns may not transfer directly to a Kenyan population — a key caveat
  motivating the fairness/calibration audit in Task 3 of this project.
- **Class imbalance & cost asymmetry.** `high risk` is the minority class
  (~27%) and also the class where a missed detection is most dangerous — which
  is why this app reports per-class recall, not just accuracy.
- **Fairness across subgroups.** Task 3 (see the project's `PLAN.md`) audits
  this model's performance and calibration across age groups.
- **Data protection.** This dataset is de-identified and public; any future
  work with real patient-level data (e.g. Kenyan facility records) must follow
  the Kenya Data Protection Act, 2019.
        """
    )
