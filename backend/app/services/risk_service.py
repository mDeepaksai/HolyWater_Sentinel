"""
Loads the trained RandomForest risk model and exposes predict_risk(),
which app/routes/risk.py already imports and calls.

    risk_level, risk_probability, factor_data = predict_risk(features)

- risk_level: "LOW" | "MEDIUM" | "HIGH"
- risk_probability: model's confidence in that predicted class (0-1)
- factor_data: list of dicts, one per contributing feature, shaped to
  match RiskFactor: factor_name, feature_value, contribution, explanation.
  Uses SHAP TreeExplainer when available for true per-prediction
  attribution; falls back to a feature_importance x z-score approximation
  if shap isn't installed, so the endpoint never hard-fails on that.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "risk_model.joblib"

_model_bundle = None  # lazy-loaded singleton

try:
    import shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False

_shap_explainer = None


# Human-readable labels + safe-range bounds used in generated explanations.
# "safe" is display text; (low, high) are numeric bounds used to actually
# check whether a value is in range - None means no bound on that side.
FEATURE_META = {
    "temperature": {"label": "Water temperature", "unit": "°C", "safe": "20-35°C", "range": (20, 35)},
    "ph": {"label": "pH level", "unit": "", "safe": "6.5-8.5", "range": (6.5, 8.5)},
    "turbidity": {"label": "Turbidity", "unit": "NTU", "safe": "below 10 NTU", "range": (None, 10)},
    "tds": {"label": "Total dissolved solids", "unit": "ppm", "safe": "below 600 ppm", "range": (None, 600)},
    "rainfall": {"label": "Recent rainfall", "unit": "mm", "safe": "below 40mm", "range": (None, 40)},
    "humidity": {"label": "Humidity", "unit": "%", "safe": "below 80%", "range": (None, 80)},
}


def _is_out_of_range(feature_name: str, value: float) -> bool:
    low, high = FEATURE_META.get(feature_name, {}).get("range", (None, None))
    if low is not None and value < low:
        return True
    if high is not None and value > high:
        return True
    return False


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Run `python -m app.ml.build_dataset` then "
                "`python -m app.ml.train_model` first."
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def _get_shap_explainer(model):
    global _shap_explainer
    if _shap_explainer is None:
        _shap_explainer = shap.TreeExplainer(model)
    return _shap_explainer


def _explanation_text(feature_name: str, value: float, contribution_magnitude_rank_is_high: bool) -> str:
    meta = FEATURE_META.get(feature_name, {"label": feature_name, "unit": "", "safe": "the normal range"})
    out_of_range = _is_out_of_range(feature_name, value)
    direction = "outside" if out_of_range else "within"
    weight = "major" if contribution_magnitude_rank_is_high else "minor"
    return (
        f"{meta['label']} is {value}{meta['unit']}, {direction} the typical safe range "
        f"({meta['safe']}), and was a {weight} factor in this prediction."
    )


def _factors_via_shap(model, class_order, feature_columns, X_row, predicted_class):
    explainer = _get_shap_explainer(model)
    shap_values = explainer.shap_values(X_row)

    # shap_values shape handling: list-of-arrays (per class) for older API,
    # or a single (1, n_features, n_classes) array for newer API.
    class_idx = class_order.index(predicted_class)
    if isinstance(shap_values, list):
        contributions = shap_values[class_idx][0]
    else:
        arr = np.array(shap_values)
        if arr.ndim == 3:
            contributions = arr[0, :, class_idx]
        else:
            contributions = arr[0]

    row_values = X_row.iloc[0].values
    factors = []
    for name, value, contribution in zip(feature_columns, row_values, contributions):
        factors.append({
            "factor_name": name,
            "feature_value": float(value),
            "contribution": float(contribution),
        })

    factors.sort(key=lambda f: abs(f["contribution"]), reverse=True)
    for i, f in enumerate(factors):
        f["explanation"] = _explanation_text(f["factor_name"], f["feature_value"], i < 2)
    return factors


def _factors_via_fallback(model, feature_columns, feature_means, feature_stds, X_row):
    """
    Used only if shap isn't installed / TreeExplainer fails. Approximates
    per-prediction contribution as global feature_importance * how many
    std-deviations this reading is from the training mean, signed by
    whether it's above or below average.
    """
    importances = model.feature_importances_
    row_values = X_row.iloc[0].values
    factors = []
    for i, name in enumerate(feature_columns):
        value = float(row_values[i])
        mean = feature_means.get(name, value)
        std = feature_stds.get(name, 1) or 1
        z = (value - mean) / std
        contribution = float(importances[i] * z)
        factors.append({
            "factor_name": name,
            "feature_value": value,
            "contribution": contribution,
        })

    factors.sort(key=lambda f: abs(f["contribution"]), reverse=True)
    for i, f in enumerate(factors):
        f["explanation"] = _explanation_text(f["factor_name"], f["feature_value"], i < 2)
    return factors


def predict_risk(features: dict):
    """
    features: dict with keys temperature, ph, turbidity, tds, rainfall, humidity
    returns: (risk_level: str, risk_probability: float, factor_data: list[dict])
    """
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]
    class_order = bundle["class_order"]
    feature_means = bundle.get("feature_means", {})
    feature_stds = bundle.get("feature_stds", {})

    X_row = pd.DataFrame([[features[col] for col in feature_columns]], columns=feature_columns)

    predicted_class = model.predict(X_row)[0]
    proba = model.predict_proba(X_row)[0]
    class_index = list(model.classes_).index(predicted_class)
    risk_probability = float(proba[class_index])

    try:
        if _SHAP_AVAILABLE:
            factor_data = _factors_via_shap(model, class_order, feature_columns, X_row, predicted_class)
        else:
            raise RuntimeError("shap not installed")
    except Exception:
        factor_data = _factors_via_fallback(model, feature_columns, feature_means, feature_stds, X_row)

    # Keep the top 4 most influential factors for the RiskFactor rows
    return predicted_class, risk_probability, factor_data[:4]