"""Task 1: predict maternal risk level from routine clinical measurements."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "maternal_health_risk.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "risk_classifier.joblib"

FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
TARGET = "RiskLevel"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/download_data.py first."
        )
    return pd.read_csv(path)


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Stratified train/test split shared by training and model-comparison code.

    Stratifying on RiskLevel keeps the ~40/33/27 class split intact in both
    halves; with only ~270 high-risk rows a plain random split can otherwise
    starve the test set of the minority class and make its recall estimate
    noisy (see notebooks/task1_risk_classifier_eda.ipynb, Section 6).
    """
    X = df[FEATURES]
    y = df[TARGET]
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def train(df: pd.DataFrame) -> tuple[RandomForestClassifier, dict]:
    X_train, X_test, y_train, y_test = split_data(df)

    # Hyperparameters chosen by grid search over n_estimators/max_depth/min_samples_leaf
    # in notebooks/task1_risk_classifier_eda.ipynb (Section 8), which beat the
    # untuned default (300 trees, unlimited depth) on 5-fold CV macro F1.
    model = RandomForestClassifier(
        n_estimators=200, max_depth=20, min_samples_leaf=1, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    matrix = confusion_matrix(y_test, y_pred, labels=model.classes_)

    return model, {"report": report, "confusion_matrix": matrix, "labels": model.classes_}


def main() -> None:
    df = load_data()
    model, results = train(df)

    print("Confusion matrix (rows=true, cols=predicted):")
    print(pd.DataFrame(
        results["confusion_matrix"], index=results["labels"], columns=results["labels"]
    ))
    print()
    print(pd.DataFrame(results["report"]).T)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
