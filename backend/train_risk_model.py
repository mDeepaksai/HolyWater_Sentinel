"""
train_risk_model.py

Generates synthetic but physically-motivated training data (since no
real outbreak-labeled dataset exists yet), trains a RandomForest risk
classifier, and saves it to ml/risk_model.pkl for the FastAPI backend
to load at prediction time.

Run from backend/:
    python train_risk_model.py

Feature order MUST match app/services/risk_service.py's FEATURES list.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib


FEATURES = [
    "temperature",
    "ph",
    "turbidity",
    "tds",
    "rainfall",
    "humidity",
]

N_SAMPLES = 20000
RANDOM_SEED = 42

OUTPUT_DIR = "ml"
MODEL_PATH = os.path.join(OUTPUT_DIR, "risk_model.pkl")


def generate_synthetic_data(n=N_SAMPLES, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)

    temperature = rng.uniform(15, 40, n)
    ph = rng.uniform(5.0, 9.5, n)
    turbidity = rng.exponential(scale=5.0, size=n)
    turbidity = np.clip(turbidity, 0, 40)
    tds = rng.uniform(50, 900, n)
    rainfall = rng.exponential(scale=15.0, size=n)
    rainfall = np.clip(rainfall, 0, 200)
    humidity = rng.uniform(30, 100, n)

    # ----------------------------------------------------------
    # Physically-motivated risk score (0-1 scale, higher = worse)
    # ----------------------------------------------------------
    ph_penalty = np.abs(ph - 7.2) / 2.5          # deviation from neutral
    turbidity_penalty = turbidity / 40.0          # higher = dirtier
    tds_penalty = np.clip((tds - 300) / 600, 0, 1)
    rainfall_penalty = rainfall / 200.0            # runoff/contamination
    temp_penalty = np.clip((temperature - 25) / 15, 0, 1)  # bacterial growth
    humidity_penalty = np.clip((humidity - 60) / 40, 0, 1)

    score = (
        0.25 * turbidity_penalty
        + 0.20 * ph_penalty
        + 0.20 * tds_penalty
        + 0.15 * rainfall_penalty
        + 0.12 * temp_penalty
        + 0.08 * humidity_penalty
    )

    # Add noise so the model has to generalize, not memorize
    score += rng.normal(0, 0.05, n)
    score = np.clip(score, 0, 1)

    risk_level = np.select(
        [score < 0.33, score < 0.60],
        ["LOW", "MEDIUM"],
        default="HIGH"
    )

    df = pd.DataFrame({
        "temperature": temperature,
        "ph": ph,
        "turbidity": turbidity,
        "tds": tds,
        "rainfall": rainfall,
        "humidity": humidity,
        "risk_level": risk_level
    })

    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating synthetic training data...")
    df = generate_synthetic_data()

    print("\nClass distribution:")
    print(df["risk_level"].value_counts())

    X = df[FEATURES]
    y = df["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=RANDOM_SEED,
        class_weight="balanced"
    )

    print("\nTraining RandomForestClassifier...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n===== TEST SET PERFORMANCE =====")
    print(classification_report(y_test, y_pred))

    print("\n===== FEATURE IMPORTANCES =====")
    for name, importance in sorted(
        zip(FEATURES, model.feature_importances_),
        key=lambda x: -x[1]
    ):
        print(f"{name:15s} {importance:.4f}")

    joblib.dump(
        {"model": model, "features": FEATURES},
        MODEL_PATH
    )

    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()