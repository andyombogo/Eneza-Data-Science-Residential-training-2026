# Project 7 — Maternal & Child Health Outcomes

### Task 1: Predict a mother's risk level from routine clinical measurements

Part of the [Eneza Data Science Residential Training 2026](../README.md) mini-project
on maternal & child health outcomes ([full brief](../Project_7.md), [group plan](PLAN.md)).
This README documents Task 1 in full; see `PLAN.md` for how it fits into the
project's other three tasks (regional/wealth disaggregation, fairness &
calibration audit, and intervention targeting) and for group ownership.

**Task 1 owners:** John Andrew, Jared Onsomu.

## At a glance

| | |
|---|---|
| **Question** | Given age, blood pressure, blood sugar, body temperature and heart rate, is a mother `low`, `mid`, or `high` risk? |
| **Data** | [UCI Maternal Health Risk](https://archive.ics.uci.edu/dataset/863/maternal+health+risk) — 1,014 rows, 6 features, 3 classes, ~1.5:1 class imbalance |
| **Model** | Random Forest (tuned) — chosen over 5 alternatives spanning different assumptions after cross-validated comparison, not by default |
| **Result** | 86.2% test accuracy; **94.5% recall on `high risk`**, the class that matters most operationally |
| **Reproduce** | `python scripts/download_data.py && python src/task1_risk_classifier.py`, or open `notebooks/task1_risk_classifier_eda.ipynb` |
| **Live demo** | `streamlit run streamlit_app.py` (interactive predictor + full model report — see [Section 12](#12-live-demo-app)) |

## Contents

1. [Problem statement](#1-problem-statement)
2. [Dataset](#2-dataset)
3. [Repository layout](#3-repository-layout)
4. [Setup](#4-setup)
5. [Reproducing the results](#5-reproducing-the-results)
6. [Is the class imbalance a problem? A SMOTE check](#6-is-the-class-imbalance-a-problem-a-smote-check)
7. [Why a stratified train/test split](#7-why-a-stratified-traintest-split)
8. [Modelling approach: choosing and tuning the model](#8-modelling-approach-choosing-and-tuning-the-model)
9. [Results](#9-results)
10. [Limitations & ethical considerations](#10-limitations--ethical-considerations)
11. [Status](#11-status)
12. [Live demo app](#12-live-demo-app)

## 1. Problem statement

Maternal mortality is often preventable when at-risk pregnancies are flagged
early. Task 1 builds a classifier that predicts a mother's **risk level** —
`low risk`, `mid risk`, or `high risk` — from six routine clinical measurements
that can be collected at a basic antenatal visit, without lab infrastructure:

| Feature       | Description                  | Unit    |
|---------------|-------------------------------|---------|
| `Age`         | Mother's age                  | years   |
| `SystolicBP`  | Upper blood pressure reading  | mmHg    |
| `DiastolicBP` | Lower blood pressure reading  | mmHg    |
| `BS`          | Blood glucose level           | mmol/L  |
| `BodyTemp`    | Body temperature              | °F      |
| `HeartRate`   | Resting heart rate            | bpm     |

Target: `RiskLevel` ∈ {`low risk`, `mid risk`, `high risk`}.

This model is a **decision-support screening tool**, not a diagnostic device —
see [Limitations & ethics](#10-limitations--ethical-considerations).

## 2. Dataset

- **Source:** [UCI Maternal Health Risk Data Set](https://archive.ics.uci.edu/dataset/863/maternal+health+risk) (id `863`), collected from rural health facilities and hospitals in Bangladesh via IoT-based risk monitoring.
- **Size:** 1,014 rows × 7 columns (6 features + target).
- **Class balance:** low risk 406 (40%), mid risk 336 (33%), high risk 272 (27%) — an imbalance ratio of ~1.5:1 (largest:smallest class). Mild enough that it doesn't turn out to need correcting (Section 6), but real enough that the split strategy (Section 7) and per-class metrics (Section 9) matter.
- **Access:** not committed to the repo (see `.gitignore`). Fetched on demand via `scripts/download_data.py`, which pulls it through the [`ucimlrepo`](https://pypi.org/project/ucimlrepo/) package and writes it to `data/raw/maternal_health_risk.csv`.

## 3. Repository layout

```
project7-maternal-child-health/
├── PLAN.md                       # group task breakdown, owners, workflow
├── requirements.txt               # pinned deps to RUN the app/scripts (kept light)
├── requirements-dev.txt           # + jupyterlab, imbalanced-learn — notebook work only
├── .python-version                 # pins the app's Python version for cloud deploys
├── streamlit_app.py               # app entry point — routes to one page per task
├── pages/
│   ├── overview.py                # landing page: project summary, task ownership/status
│   ├── task1_risk_classifier.py  # Task 1: interactive predictor + model report
│   ├── task2_regional_indicators.py  # Task 2: stunting metrics/charts from data/processed/
│   ├── task3_fairness_calibration.py # Task 3: age-group fairness + calibration audit
│   └── task4_interventions.py        # Task 4 placeholder (not started)
├── .streamlit/config.toml         # app theme
├── scripts/
│   └── download_data.py          # fetches raw dataset from UCI repo (not committed)
├── src/
│   ├── task1_risk_classifier.py  # Task 1: load data, split, train, evaluate, save model
│   └── task3_fairness_audit.py   # Task 3: age grouping, out-of-fold predictions, fairness/calibration metrics
├── notebooks/
│   ├── task1_risk_classifier_eda.ipynb          # Task 1: EDA, SMOTE check, model comparison, tuning
│   ├── task2_regional_indicators.qmd            # Task 2: KDHS analysis source (needs R + restricted data)
│   └── task3_fairness_calibration_audit.ipynb   # Task 3: fairness + calibration audit
├── data/
│   ├── raw/                      # gitignored — populated by download_data.py
│   └── processed/                # committed — small, aggregate, non-restricted derived data
│       ├── task2_stunting_summary.json
│       └── task2_haz_histogram.png
└── models/
    └── risk_classifier.joblib    # gitignored — trained model artifact
```

## 4. Setup

Requires Python 3.10+. Dependencies are pinned for reproducibility, and split
in two so the deployed app stays light:

```bash
# from project7-maternal-child-health/
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt      # to run the app or scripts
pip install -r requirements-dev.txt  # + also want to edit the notebook (adds jupyterlab, imbalanced-learn)
```

`requirements.txt` is what Streamlit Cloud installs to deploy the app —
`jupyterlab` alone pulls in dozens of transitive packages (`jupyter-server`,
`notebook`, `tornado`, ...) that the app never uses at runtime, so it lives in
`requirements-dev.txt` instead, kept in sync via `-r requirements.txt`.
`imbalanced-learn` (for the SMOTE check, Section 6) lives there too, since
production training doesn't end up using it.

## 5. Reproducing the results

```bash
# 1. Download the raw dataset (writes data/raw/maternal_health_risk.csv)
python scripts/download_data.py

# 2. Train and evaluate the classifier (writes models/risk_classifier.joblib)
python src/task1_risk_classifier.py

# 3. (optional, needs requirements-dev.txt) open the full EDA + model-selection notebook
jupyter lab notebooks/task1_risk_classifier_eda.ipynb
```

Running `task1_risk_classifier.py` will:

1. Load `data/raw/maternal_health_risk.csv` (raises `FileNotFoundError` with a
   clear message if the download step hasn't been run yet).
2. Split into train/test sets via `split_data()` — 80/20, **stratified** by
   `RiskLevel`, `random_state=42` for reproducibility (why: Section 7).
3. Train a `RandomForestClassifier` with hyperparameters chosen by the grid
   search in the notebook (Section 8 below).
4. Print a confusion matrix and a per-class precision/recall/F1 classification
   report on the held-out test set.
5. Save the fitted model to `models/risk_classifier.joblib` for reuse (e.g. by
   the Task 3 fairness/calibration audit).

`notebooks/task1_risk_classifier_eda.ipynb` imports `load_data` / `split_data` /
`train` directly from `src/task1_risk_classifier.py` — one source of truth for
data loading and the train/test split — and builds the full narrative on top:
data-quality checks, class-balance and per-feature distribution plots, an
empirical SMOTE check, a live demonstration of why the split is stratified, a
cross-validated comparison of six candidate algorithms, a hyperparameter
search, and final evaluation with a feature-importance chart. It is committed
with outputs already populated; run `download_data.py` first so it can find
the raw CSV, and re-run the notebook if you want fresh numbers after a code
change.

## 6. Is the class imbalance a problem? A SMOTE check

A ~1.5:1 imbalance ratio (Section 2) is mild — [SMOTE](https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html)
(synthetic minority oversampling) is usually reached for around 4:1 or worse,
or when the minority class has only a handful of examples. `high risk` still
has 272 real rows here. Rather than skip resampling on that assumption alone,
the notebook tests it empirically: a Random Forest cross-validated (5-fold,
training split only) with SMOTE applied *only inside the training folds* (via
an `imblearn` pipeline — never touching the validation fold, to avoid
synthetic-data leakage) against the same model without it.

| Strategy | CV accuracy | CV recall (macro) | CV F1 (macro) |
|---|---|---|---|
| Without SMOTE | 0.815 | 0.819 | 0.819 |
| With SMOTE | 0.818 | 0.821 | 0.821 |

The difference (+0.002 F1) is within noise. That's the expected outcome at
this imbalance ratio: Random Forest's per-tree bootstrap sampling and 272 real
`high risk` examples already give it enough minority-class signal that
synthetic examples add little. **Decision: no resampling in the production
pipeline** (`src/task1_risk_classifier.py`) — it would add a dependency and a
leakage risk for no measurable benefit. Task 3's fairness audit (now
complete — see [Section 12](#12-live-demo-app) and
`notebooks/task3_fairness_calibration_audit.ipynb`) checked this from a
different angle: overall `high risk` recall is strong (91–96% across age
groups), but recall specifically for adolescent mothers is lower (~85%) — a
real, CI-supported gap, though a subgroup fairness issue rather than the
class-wide imbalance problem SMOTE targets.

## 7. Why a stratified train/test split?

`RiskLevel` is imbalanced (Section 2: ~40/33/27%). `train_test_split(...,
stratify=y)` forces the train and test sets to each preserve that same ratio.
Without it, a single unlucky random split could under-represent `high risk` in
the test set — the class where a missed detection is most costly — making its
recall estimate unreliable.

The notebook demonstrates this rather than just asserting it: it draws 20
random 80/20 splits *without* stratification and compares the `high risk`
test-set share against the stratified split actually used for training.

| | `high risk` share of test set |
|---|---|
| True population share | 26.8% |
| Stratified split (`random_state=42`, used for training) | 27.1% |
| 20× unstratified splits | mean 27.6%, **range 23.2% – 31.5%** |

With only ~270 high-risk rows to begin with, an 80/20 split leaves just ~55 in
the test fold — small enough that luck-of-the-draw shifts the minority-class
share by several points. Stratification pins it to the true ratio, which is
what makes the `high risk` recall figure reported in Section 9 trustworthy
rather than a roll of the dice.

## 8. Modelling approach: choosing and tuning the model

Random Forest was **not** picked by default. The notebook cross-validates six
candidates spanning different underlying assumptions (5-fold stratified,
evaluated on accuracy and macro recall/F1 so the majority `low risk` class
can't hide a weak `high risk` score) before choosing one to tune. Logistic
Regression is deliberately excluded from this round — it's a fully valid
multiclass classifier in scikit-learn (multinomial/softmax or one-vs-rest, not
limited to two classes), but the slots were spent on a wider spread of model
families instead:

| Model | What it is | Why it might win here | Why it might lose here |
|---|---|---|---|
| **Decision Tree** | A single tree — the building block Random Forest ensembles | Captures non-linear thresholds natively | One tree tends to overfit its training split |
| **K-Nearest Neighbors** | Classifies by majority vote of nearest training points (scaled features) | No training phase, simple | Assumes Euclidean distance across differently-scaled vitals is meaningful "similarity" — a stretch here |
| **Naive Bayes** | Fast probabilistic baseline (Gaussian) | Cheap, well-calibrated when assumptions hold | Assumes features are conditionally independent per class; `SystolicBP`/`DiastolicBP` are directly correlated, violating that |
| **SVM (RBF)** | Maximum-margin boundary in a non-linear kernel space (scaled features) | Powerful in general | Margin/kernel geometry doesn't map naturally onto the axis-aligned threshold behaviour seen in the data (Section 6's histograms in the notebook) |
| **Gradient Boosting** | Trees built sequentially to correct prior errors | Can outperform Random Forest on some tabular problems | More hyperparameters to get wrong; higher overfitting risk on a dataset this size (~1,000 rows) |
| **Random Forest** | Ensemble of independent decision trees, bootstrap-averaged | Captures non-linear thresholds/interactions without scaling; averaging tempers a single tree's overfitting | Less directly interpretable than a linear model (mitigated with feature importances, Section 9) |

**Cross-validated results (5-fold, training split only):**

| Model | CV accuracy | CV recall (macro) | CV F1 (macro) |
|---|---|---|---|
| **Random Forest** | 0.815 | 0.819 | **0.819** |
| Decision Tree | 0.798 | 0.801 | 0.801 |
| Gradient Boosting | 0.788 | 0.789 | 0.792 |
| SVM (RBF) | 0.694 | 0.688 | 0.683 |
| K-Nearest Neighbors | 0.671 | 0.665 | 0.667 |
| Naive Bayes | 0.605 | 0.587 | 0.565 |

**Several converging reasons, not one:**

- **Random Forest wins outright**, and is the model tuned and shipped below.
- **Decision Tree is the closest competitor** — a single tree already captures
  most of the structure, confirming the boundary really is threshold-like
  (matching the feature-distribution shapes in Section 9 of the notebook)
  rather than needing a smooth/linear model. Random Forest's edge over it is
  exactly the variance reduction ensembling is supposed to buy.
- **Gradient Boosting trails Random Forest** — plausible on a dataset this
  small, where sequential boosting has more room to overfit than bagged
  averaging.
- **SVM and KNN both underperform substantially**, despite feature scaling —
  both rely on distance/margin geometry, and a threshold rule like "BS above
  X" is a single axis-aligned cut for a tree but an awkward shape for a
  Euclidean-distance or kernel-margin boundary to learn.
- **Naive Bayes is weakest by a wide margin** — its independence assumption is
  directly violated by the `SystolicBP`/`DiastolicBP` correlation, and
  clinical vitals aren't well described by per-class Gaussians to begin with.

**Hyperparameter tuning:** a grid search over `n_estimators` (200/300/500),
`max_depth` (None/10/20), and `min_samples_leaf` (1/2/4) — 27 candidates,
5-fold CV, scored on macro F1 — found a configuration that beats the untuned
default:

| | `n_estimators` | `max_depth` | `min_samples_leaf` | CV macro F1 |
|---|---|---|---|---|
| Untuned default | 300 | unlimited | 1 | 0.819 |
| **Tuned (shipped)** | **200** | **20** | **1** | **0.827** |

The gain is modest (+0.008), which is itself informative: the untuned default
was already close to this model family's ceiling on this dataset. The tuned
configuration is what `src/task1_risk_classifier.py` ships, since it's a free
improvement with no added inference cost.

## 9. Results

Final model (tuned Random Forest) on the held-out test set (203 rows, never
used during model selection or tuning):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| **high risk** | 0.963 | **0.945** | 0.954 | 55 |
| mid risk | 0.753 | 0.866 | 0.806 | 67 |
| low risk | 0.903 | 0.802 | 0.850 | 81 |
| **Accuracy** | | | **0.862** | 203 |

`high risk` recall (0.945) is the number that matters most operationally —
of 55 truly high-risk mothers in the test set, the model flags 52. Feature
importances confirm the model leans on `BS` and the two blood-pressure
readings most heavily, matching both the EDA and clinical expectation; full
breakdown and plots are in the notebook.

### Suggested next steps

- ~~Probability calibration check~~ — **done**, see Task 3
  (`notebooks/task3_fairness_calibration_audit.ipynb`): `high risk` is
  well-calibrated (lowest Brier score of the three classes), `mid risk` is
  the least reliable.
- SHAP values for per-prediction explanations, useful if this were ever shown
  to a clinician rather than just reported in aggregate — still not
  implemented.

## 10. Limitations & ethical considerations

- **Not a clinical diagnostic tool.** This model supports triage/screening
  discussions; it must not replace clinical judgement or be deployed without
  supervision by qualified health workers.
- **Population mismatch risk.** The training data comes from health facilities
  in Bangladesh. Vitals thresholds and risk patterns may not transfer directly
  to a Kenyan population — this is a key caveat to flag before any real-world
  use. Task 3's fairness audit was run on this same Bangladeshi data; whether
  its findings (below) replicate on a Kenyan population is an open question.
- **Class imbalance & cost asymmetry.** `high risk` is the minority class
  (27%) and also the class where false negatives (predicting `low`/`mid` when
  truly `high risk`) are most dangerous. This is why the split is stratified
  (Section 7) and why recall — not just accuracy — is reported per class
  (Section 9), even though the imbalance was mild enough not to need
  resampling (Section 6).
- **Fairness across subgroups — a real gap found.** Task 3 audited this
  model's performance and calibration across age groups (see Section 12 and
  `notebooks/task3_fairness_calibration_audit.ipynb`). Finding: the model
  catches true `high risk` cases less often for mothers under 20 (~85%
  recall) than for the 20–34 reference group (~96%) — a statistically
  real gap (95% CIs barely overlap), not noise. Precision stays perfect for
  the under-20 group, so the failure mode is specifically under-flagging,
  not over-flagging. See Task 3's recommendations for mitigation.
- **Data protection.** Although this dataset is de-identified and public,
  any future work with real patient-level data (e.g. Kenyan facility records)
  must follow the Kenya Data Protection Act, 2019, and be documented in the
  project's ethics/Data Protection notes.

## 11. Status

**Done:** data download script, EDA (class balance, feature distributions,
correlation), an empirical SMOTE check, a justified and cross-validated model
choice across six algorithm families, hyperparameter tuning, final evaluation
with confusion matrix + classification report + feature importances, a live
demonstration of why the split is stratified, saved model artifact, fully
executed reproducible notebook, pinned dependencies.

**Open (optional refinement, not a blocker):** per-prediction explanations
(SHAP). Probability calibration is now checked — see Task 3.

See `PLAN.md` for the status of Tasks 2 and 4 (regional/wealth EDA,
intervention targeting) and for task ownership within the group.

## 12. Live demo app

`streamlit_app.py` is an interactive companion to this README — a whole-project
presentation shell, not just a Task 1 demo. It's a multipage app, one page per
project task, so it's ready to grow as Tasks 2–4 land without a rebuild:

- **🏠 Overview** — project summary and a task table (owner + status per task)
  — the "who's doing what" a judge or teammate wants first.
- **🔮 Task 1 — Risk Classifier** — the full working demo, in four tabs:
  - **Predict** — enter clinical measurements, get a risk prediction with
    class probabilities; flags when an input falls outside the training
    data's observed range.
  - **Model Performance** — confusion matrix, classification report, feature
    importances, and (on demand, via a button) the live cross-validated
    6-model comparison from Section 8.
  - **Explore the Data** — class balance, per-feature histograms by risk
    level (not boxplots — see Section 8's reasoning), correlation heatmap.
  - **Methodology & Ethics** — the stratification demonstration from
    Section 7 (recomputed live), the SMOTE decision from Section 6, and
    limitations.
- **📊 Task 2 — Regional Indicators** — national child-stunting prevalence
  (17.4%, KDHS 2022) with metrics, a real HAZ-score histogram, and a
  sample-to-estimate funnel chart, all read from a small committed aggregate
  file (`data/processed/task2_stunting_summary.json`) rather than any
  restricted microdata. An honest "what's next" section lists county-level
  breakdown, immunisation, skilled birth attendance, and wealth quintile as
  pending — no placeholder numbers standing in for unfinished analysis.
- **⚖️ Task 3 — Fairness & Calibration Audit** — audits the Task 1 model
  using out-of-fold predictions across the full dataset (more statistical
  power per age subgroup than the 203-row test set alone). Headline metrics,
  a high-risk-recall-by-age-group chart with 95% CIs, per-group confusion
  matrices, per-class Brier scores and reliability curves, and concrete
  recommendations — same page structure and rigor as Task 1, on
  `task3-fairness-calibration` branch pending merge into this one.
- **🎯 Task 4** — placeholder page showing the task's description, owners,
  and status; becomes a real page once built.

Task 1 and Task 3 import the heavy stack (pandas/sklearn/matplotlib) since
both train/evaluate models; Task 2 needs only `pandas` plus the standard
library; Task 4 imports nothing beyond `streamlit`. The 6-model comparison
on Task 1 and the out-of-fold audit on Task 3 are the two heavier
computations in the app — Task 1's is gated behind a button (first paint
~3s cold); Task 3's runs eagerly since it *is* the page's content (~3.5s
cold), cached after that.

**Why Task 2 isn't a standalone report:** the original Task 2 work
(`task2-regional-indicators` branch) was a Quarto/R document
(`Project7_task2.qmd`) rendered to a static HTML file. That HTML has been
removed from the repo — investigation before merging found it was stale
(rendered before the branch's last commit) and referenced a chart image that
was never committed, so keeping it would have shipped a broken, out-of-date
report. The `.qmd` source is kept (`notebooks/task2_regional_indicators.qmd`,
content untouched) since it's the authored analysis and needs a restricted
DHS microdata file to re-run; its actual output numbers were extracted once
into `data/processed/` for the Streamlit page to use, so the whole project
now lives in one cohesive app instead of one task being a separate document.

**No committed model or data file is required to run it.** On first load the
Task 1 page tries `data/raw/maternal_health_risk.csv`; if that's absent (e.g.
a fresh clone or a cloud deploy) it fetches the dataset directly via
`ucimlrepo`, trains the same tuned Random Forest as
`src/task1_risk_classifier.py` (imported directly, not reimplemented), and
caches both for the life of the app process.

### Run locally

```bash
# from project7-maternal-child-health/, with requirements.txt installed
streamlit run streamlit_app.py
```

### Deploy (Streamlit Community Cloud — free, GitHub-integrated)

1. Push this branch to GitHub (already done for `project7-setup`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. **New app** → repository `andyombogo/Eneza-Data-Science-Residential-training-2026`,
   branch `project7-setup`, **main file path**
   `project7-maternal-child-health/streamlit_app.py`.
4. Deploy. `requirements.txt` sits in the same folder as the entry point, so
   Streamlit Cloud picks it up automatically — no extra config needed.
5. **Sharing:** in the app's Settings → General, set "Who can view this app"
   to public — a fresh app defaults to restricted, which redirects anonymous
   visitors to a login wall that never resolves for them.

Streamlit Community Cloud was chosen over alternatives (Render, Railway,
Hugging Face Spaces) because it deploys directly from a GitHub branch with
zero infrastructure setup or cost, redeploys automatically on push, and is
purpose-built for exactly this kind of small data-science demo — the fastest
path to a shareable public link for a presentation.

**Python version pin:** `.python-version` (`3.12`) is committed at the actual
**repository root** (not inside this subfolder) so Streamlit Cloud's build
tool (`uv`) — which runs from the repo root, not the app's subdirectory —
actually finds it, rather than provisioning whatever bleeding-edge Python it
defaults to. Without this, a very new Python can have no prebuilt wheel for
pinned packages like `scipy`, forcing a from-source build that fails in
Cloud's sandbox (no Fortran compiler). If a deploy ever fails on a package
build step, check the Python version in the log first before touching
dependency versions.

**Reading build logs without downloading the whole file:** a failed
dependency build (like the scipy case above) can produce a log tens of
thousands of lines long. In the Streamlit Cloud dashboard, use **Manage app →
Logs** and read it in the browser panel rather than downloading it — the
panel auto-scrolls to the failure and lets you search/copy just the relevant
traceback instead of pulling the whole file.
