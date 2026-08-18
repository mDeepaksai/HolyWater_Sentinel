"""
Single source of truth for "what is this village's current risk?".

Both app/routes/risk.py (POST /risk/predict/{village_id}) and
app/routes/alert.py (POST /alerts/check/{village_id}) call
run_prediction_for_village() instead of each computing risk their own
way. That guarantees they can never disagree about a village's risk
level within the same check.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.village import Village
from app.models.sensor_reading import SensorReading
from app.models.weather_data import WeatherData
from app.models.risk_prediction import RiskPrediction
from app.models.risk_factor import RiskFactor
from app.services.risk_service import predict_risk


def run_prediction_for_village(village_id: int, db: Session):
    """
    Pulls the latest sensor + weather data for a village, runs the ML
    model, stores a new RiskPrediction + RiskFactor rows, and returns
    (prediction, factors, village).

    Raises HTTPException(404) if the village or sensor data don't exist,
    and HTTPException(503) if the model file itself isn't available yet
    (i.e. train_model.py / train.py hasn't been run).
    """
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    latest_sensor = (
        db.query(SensorReading)
        .filter(SensorReading.village_id == village_id)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )
    if not latest_sensor:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings found for this village"
        )

    latest_weather = (
        db.query(WeatherData)
        .filter(WeatherData.village_id == village_id)
        .order_by(WeatherData.recorded_at.desc())
        .first()
    )

    rainfall = latest_weather.rainfall if latest_weather else 0.0
    humidity = latest_weather.humidity if latest_weather else 60.0

    features = {
        "temperature": latest_sensor.temperature,
        "ph": latest_sensor.ph,
        "turbidity": latest_sensor.turbidity,
        "tds": latest_sensor.tds,
        "rainfall": rainfall if rainfall is not None else 0.0,
        "humidity": humidity if humidity is not None else 60.0,
    }

    try:
        risk_level, risk_probability, factor_data = predict_risk(features)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    prediction = RiskPrediction(
        village_id=village_id,
        sensor_reading_id=latest_sensor.id,
        weather_data_id=latest_weather.id if latest_weather else None,
        risk_level=risk_level,
        risk_probability=risk_probability,
        model_name="RandomForest",
        model_version="v1"
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    factors = []
    for f in factor_data:
        factor = RiskFactor(
            risk_prediction_id=prediction.id,
            factor_name=f["factor_name"],
            feature_value=f["feature_value"],
            contribution=f["contribution"],
            explanation=f["explanation"]
        )
        db.add(factor)
        factors.append(factor)

    db.commit()
    for f in factors:
        db.refresh(f)

    return prediction, factors, village