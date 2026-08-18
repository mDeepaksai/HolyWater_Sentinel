"""
Build the training dataset for the risk-prediction model.

Strategy
--------
1. REAL DATA FIRST: for every HealthData record, try to find the village(s)
   it applies to (direct village_id match, else all villages sharing the
   same district), then pull the most recent SensorReading + WeatherData
   for that village within LOOKBACK_DAYS before the health report date.
   That gives a real (water conditions -> disease outcome) pair.

2. LABEL each real pair from case_count normalized by village population
   (cases per 1,000 people), using the thresholds below. This is a
   judgment call - tune HIGH_CASES_PER_1K / MEDIUM_CASES_PER_1K if you
   have domain guidance (e.g. from a health-worker mentor) to cite.

3. SYNTHETIC TOP-UP: real matched pairs will likely be sparse (district-
   level case data + optional village linkage means most HealthData rows
   won't cleanly join to a village's sensor history). If real rows fall
   below MIN_REAL_SAMPLES, generate synthetic rows from WHO/CDC-style
   water-quality thresholds so the model has enough data to train on.
   Every row is tagged is_synthetic so this is auditable, not silently
   faked.

Run this from your project root (same place you'd run uvicorn), so that
`app.database` and `app.models.*` imports resolve correctly:

    python -m app.ml.build_dataset

Output: app/ml/data/training_data.csv
"""

import random
from datetime import timedelta, datetime
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------
# CONFIG - tune these
# ------------------------------------------------------------------
LOOKBACK_DAYS = 14          # how far back to look for sensor/weather data
                             # relative to a health report date
MIN_REAL_SAMPLES = 2000     # if real matched rows are fewer than this,
                             # top up with synthetic rows to reach it
HIGH_CASES_PER_1K = 5.0     # >= this -> HIGH
MEDIUM_CASES_PER_1K = 1.0   # >= this -> MEDIUM, else LOW
DEFAULT_POPULATION = 2000   # used if a village has no population set

OUTPUT_PATH = Path(__file__).parent / "data" / "training_data.csv"

FEATURE_COLUMNS = ["temperature", "ph", "turbidity", "tds", "rainfall", "humidity"]


def label_from_case_rate(case_count: int, population: int) -> str:
    population = population or DEFAULT_POPULATION
    rate_per_1k = (case_count / population) * 1000
    if rate_per_1k >= HIGH_CASES_PER_1K:
        return "HIGH"
    if rate_per_1k >= MEDIUM_CASES_PER_1K:
        return "MEDIUM"
    return "LOW"


def build_real_rows():
    """Pull and join real data from the live database. Returns a list of dict rows."""
    # Imports are local so this file can still be *parsed* even outside
    # the FastAPI project (e.g. if you want to unit test the synthetic
    # generator in isolation).
    from app.database import SessionLocal
    from app.models.village import Village
    from app.models.health_data import HealthData
    from app.models.sensor_reading import SensorReading
    from app.models.weather_data import WeatherData

    db = SessionLocal()
    rows = []

    try:
        villages = db.query(Village).all()
        villages_by_district = {}
        villages_by_id = {}
        for v in villages:
            villages_by_id[v.id] = v
            villages_by_district.setdefault(v.district, []).append(v)

        health_records = db.query(HealthData).all()

        for record in health_records:
            # Figure out which village(s) this health record applies to
            if record.village_id and record.village_id in villages_by_id:
                candidate_villages = [villages_by_id[record.village_id]]
            else:
                candidate_villages = villages_by_district.get(record.district, [])

            for village in candidate_villages:
                # Bound the search window to [report_date - LOOKBACK_DAYS, report_date].
                # Without the upper bound, this would match ANY sensor reading ever
                # recorded for the village - including ones recorded long AFTER the
                # health report - which defeats the purpose of predicting risk from
                # conditions that preceded the outbreak.
                window_start = datetime.combine(
                    record.report_date - timedelta(days=LOOKBACK_DAYS),
                    datetime.min.time(),
                )
                window_end = datetime.combine(
                    record.report_date,
                    datetime.max.time(),
                )

                sensor = (
                    db.query(SensorReading)
                    .filter(SensorReading.village_id == village.id)
                    .filter(SensorReading.recorded_at >= window_start)
                    .filter(SensorReading.recorded_at <= window_end)
                    .order_by(SensorReading.recorded_at.desc())
                    .first()
                )
                if not sensor:
                    continue  # can't build features without a sensor reading

                weather = (
                    db.query(WeatherData)
                    .filter(WeatherData.village_id == village.id)
                    .filter(WeatherData.recorded_at >= window_start)
                    .filter(WeatherData.recorded_at <= window_end)
                    .order_by(WeatherData.recorded_at.desc())
                    .first()
                )

                rows.append({
                    "temperature": sensor.temperature,
                    "ph": sensor.ph,
                    "turbidity": sensor.turbidity,
                    "tds": sensor.tds,
                    "rainfall": weather.rainfall if weather and weather.rainfall is not None else 0.0,
                    "humidity": weather.humidity if weather and weather.humidity is not None else 60.0,
                    "risk_level": label_from_case_rate(record.case_count, village.population),
                    "is_synthetic": False,
                    "source": f"health_data:{record.id}|village:{village.id}",
                })
    finally:
        db.close()

    return rows


def generate_synthetic_row():
    """
    One synthetic (features, label) pair built from WHO/CDC-style water
    safety thresholds, mirroring the rule-based logic already used in
    app/routes/alert.py::evaluate_sensor_risk, but with continuous
    randomized inputs and a bit of label noise so the model doesn't
    just relearn a lookup table.
    """
    # Sample features across their realistic operating ranges
    ph = round(random.uniform(5.5, 9.0), 2)
    turbidity = round(random.gauss(6, 5), 2)
    turbidity = max(0.1, turbidity)
    tds = round(random.gauss(400, 200), 2)
    tds = max(50, tds)
    temperature = round(random.uniform(18, 40), 2)
    rainfall = round(max(0, random.gauss(15, 20)), 2)
    humidity = round(random.uniform(30, 95), 2)

    score = 0
    if ph < 6.5 or ph > 8.5:
        score += 1
    if turbidity > 10:
        score += 1
    if turbidity > 20:
        score += 1
    if tds > 600:
        score += 1
    if temperature > 35:
        score += 1
    if rainfall > 40:  # heavy rainfall -> runoff/contamination risk
        score += 1
    if humidity > 80 and temperature > 28:  # favorable for pathogen growth
        score += 1

    if score >= 3:
        label = "HIGH"
    elif score >= 1:
        label = "MEDIUM"
    else:
        label = "LOW"

    # 8% label noise so the model learns soft boundaries, not a hard rule table
    if random.random() < 0.08:
        label = random.choice(["LOW", "MEDIUM", "HIGH"])

    return {
        "temperature": temperature,
        "ph": ph,
        "turbidity": turbidity,
        "tds": tds,
        "rainfall": rainfall,
        "humidity": humidity,
        "risk_level": label,
        "is_synthetic": True,
        "source": "synthetic:who_cdc_rules",
    }


def build_dataset(try_real: bool = True) -> pd.DataFrame:
    real_rows = []
    if try_real:
        try:
            real_rows = build_real_rows()
        except Exception as e:
            print(f"[build_dataset] Could not read real data ({e}). Falling back to fully synthetic dataset.")

    n_real = len(real_rows)
    n_needed = max(0, MIN_REAL_SAMPLES - n_real)

    print(f"[build_dataset] Real matched rows: {n_real}")
    print(f"[build_dataset] Synthetic top-up rows: {n_needed}")

    if n_real > 0:
        real_df_check = pd.DataFrame(real_rows)
        n_unique_sensor_snapshots = real_df_check[FEATURE_COLUMNS].drop_duplicates().shape[0]
        print(f"[build_dataset] Distinct feature combinations among real rows: {n_unique_sensor_snapshots}")
        if n_unique_sensor_snapshots < 5:
            print(
                "[build_dataset] WARNING: fewer than 5 distinct sensor/weather snapshots "
                "found. The model will have almost no real signal to learn from - you "
                "likely need more varied SensorReading/WeatherData rows (across more "
                "dates and villages) before this dataset is useful for training."
            )

    synthetic_rows = [generate_synthetic_row() for _ in range(n_needed)]

    all_rows = real_rows + synthetic_rows
    df = pd.DataFrame(all_rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"[build_dataset] Wrote {len(df)} total rows to {OUTPUT_PATH}")
    print(df["risk_level"].value_counts())

    return df


if __name__ == "__main__":
    build_dataset()