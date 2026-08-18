"""
load_health_data.py

Loads data/health_data_long.csv (produced by reshape_data.py) into the
health_data table via the HealthData SQLAlchemy model.

Place this file in your backend/ folder (same level as main.py) and run:

    python load_health_data.py

Assumes the CSV has columns:
    district, s_no, parameter, type, month, total, public, private,
    urban, rural, is_anomaly

Maps:
    district      -> HealthData.district
    parameter     -> HealthData.disease_name
    total         -> HealthData.case_count
    month         -> HealthData.report_date (1st of that month)
    "HMIS Assam"  -> HealthData.source (hardcoded label)

Skips rows where total is NaN/blank (nothing to record) since
case_count is a required, non-null field on the model.
"""

import math
from datetime import date

import pandas as pd

from app.database import SessionLocal
from app.models.health_data import HealthData


CSV_FILE = "data/health_data_long.csv"

# HMIS financial year runs April -> March.
# Adjust FY_START_YEAR to match the actual year your dataset covers.
FY_START_YEAR = 2025

MONTH_TO_NUM = {
    "April": (4, FY_START_YEAR),
    "May": (5, FY_START_YEAR),
    "June": (6, FY_START_YEAR),
    "July": (7, FY_START_YEAR),
    "August": (8, FY_START_YEAR),
    "September": (9, FY_START_YEAR),
    "October": (10, FY_START_YEAR),
    "November": (11, FY_START_YEAR),
    "December": (12, FY_START_YEAR),
    "January": (1, FY_START_YEAR + 1),
    "February": (2, FY_START_YEAR + 1),
    "March": (3, FY_START_YEAR + 1),
}


def month_to_report_date(month_name: str) -> date:
    month_num, year = MONTH_TO_NUM[month_name]
    return date(year, month_num, 1)


def main():
    df = pd.read_csv(CSV_FILE, encoding="utf-8")

    db = SessionLocal()

    # Skip districts already loaded, so re-running after a Ctrl+C
    # does not duplicate rows. Comment this block out to force a
    # full reload after truncating the table yourself.
    already_loaded = {
        row[0] for row in db.query(HealthData.district).distinct().all()
    }
    if already_loaded:
        print("Already loaded districts (will be skipped):")
        print(sorted(already_loaded))
        df = df[~df["district"].isin(already_loaded)]

    inserted = 0
    skipped = 0
    batch = []
    BATCH_SIZE = 1000

    try:
        for _, row in df.iterrows():

            total = row["total"]

            # Skip rows with no case count value at all
            if pd.isna(total):
                skipped += 1
                continue

            case_count = int(total) if not math.isnan(total) else 0

            batch.append({
                "village_id": None,
                "district": str(row["district"]),
                "disease_name": str(row["parameter"])[:255],
                "case_count": case_count,
                "report_date": month_to_report_date(row["month"]),
                "source": "HMIS Assam",
            })
            inserted += 1

            # Bulk insert in batches for speed
            if len(batch) >= BATCH_SIZE:
                db.bulk_insert_mappings(HealthData, batch)
                db.commit()
                batch = []
                print(f"Committed {inserted} rows so far...")

        # Insert any leftover rows
        if batch:
            db.bulk_insert_mappings(HealthData, batch)
            db.commit()

    finally:
        db.close()

    print("\n===== LOAD COMPLETE =====")
    print("Inserted:", inserted)
    print("Skipped (no total value):", skipped)


if __name__ == "__main__":
    main()