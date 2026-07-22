"""Fetch the UCI Maternal Health Risk dataset and save it locally.

Raw data is not committed to the repo; run this script to regenerate it.
"""

from pathlib import Path

from ucimlrepo import fetch_ucirepo

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def download_maternal_health_risk() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset = fetch_ucirepo(id=863)

    df = dataset.data.features.copy()
    df[dataset.data.targets.columns[0]] = dataset.data.targets

    out_path = RAW_DIR / "maternal_health_risk.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    return out_path


if __name__ == "__main__":
    download_maternal_health_risk()
