"""
Train the RandomForest risk-prediction model.

Reads app/ml/data/training_data.csv (produced by build_dataset.py),
trains a RandomForestClassifier, evaluates it on a held-out split,
and saves the model + metadata to app/ml/models/risk_model.joblib.

Run from your project root:

    python -m app.ml.train_model
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DATA_PATH = Path(__file__).parent / "data" / "training_data.csv"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"

FEATURE_COLUMNS = ["temperature", "ph", "turbidity", "tds", "rainfall", "humidity"]
LABEL_COLUMN = "risk_level"
CLASS_ORDER = ["LOW", "MEDIUM", "HIGH"]  # fixed, consistent ordering everywhere


def train():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No training data at {DATA_PATH}. Run `python -m app.ml.build_dataset` first."
        )

    df = pd.read_csv(DATA_PATH)

    missing = [c for c in FEATURE_COLUMNS + [LABEL_COLUMN] if c not in df.columns]
    if missing:
        raise ValueError(f"Training data is missing required columns: {missing}")

    df = df.dropna(subset=FEATURE_COLUMNS + [LABEL_COLUMN])

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    print(f"[train_model] Training on {len(df)} rows")
    if "is_synthetic" in df.columns:
        print(f"[train_model]   real: {(~df['is_synthetic']).sum()}  synthetic: {df['is_synthetic'].sum()}")
    print(f"[train_model] Class balance:\n{y.value_counts()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[train_model] Test accuracy: {acc:.3f}")
    print("[train_model] Classification report:")
    print(classification_report(y_test, y_pred))
    print("[train_model] Confusion matrix (rows=actual, cols=predicted), classes =", sorted(y.unique()))
    print(confusion_matrix(y_test, y_pred, labels=sorted(y.unique())))

    print("\n[train_model] Feature importances:")
    for name, importance in sorted(
        zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:12s} {importance:.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "class_order": CLASS_ORDER,
            # reference means, used by the fallback explainer in risk_service.py
            "feature_means": X_train.mean().to_dict(),
            "feature_stds": X_train.std().replace(0, 1).to_dict(),
        },
        MODEL_PATH,
    )
    print(f"\n[train_model] Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()