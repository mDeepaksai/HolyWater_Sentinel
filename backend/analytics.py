import pandas as pd
import numpy as np

DATA_FILE = "data/health_data_long.csv"

MONTHS = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March"
]

MONTH_ORDER = {month: i for i, month in enumerate(MONTHS)}

df = pd.read_csv(DATA_FILE)

df["month_order"] = df["month"].map(MONTH_ORDER)


def get_districts():
    return sorted(df["district"].dropna().unique().tolist())


def get_parameters():
    return sorted(df["parameter"].dropna().unique().tolist())


def district_summary(district):
    data = df[df["district"] == district]

    if data.empty:
        return None

    result = (
        data.groupby("month", as_index=False)["total"]
        .sum()
    )

    result["month_order"] = result["month"].map(MONTH_ORDER)
    result = result.sort_values("month_order")

    return result[["month", "total"]].to_dict(orient="records")


def parameter_trend(district, parameter):
    data = df[
        (df["district"] == district) &
        (df["parameter"] == parameter)
    ].copy()

    if data.empty:
        return None

    data = data.sort_values("month_order")

    return data[
        [
            "month",
            "type",
            "total",
            "public",
            "private",
            "urban",
            "rural",
            "is_anomaly"
        ]
    ].to_dict(orient="records")


def district_parameter_total(district, parameter):
    data = df[
        (df["district"] == district) &
        (df["parameter"] == parameter)
    ]

    if data.empty:
        return None

    total = data["total"].sum()

    return {
        "district": district,
        "parameter": parameter,
        "total": float(total)
    }


def compare_districts(parameter):
    data = df[df["parameter"] == parameter]

    if data.empty:
        return []

    result = (
        data.groupby("district", as_index=False)["total"]
        .sum()
        .sort_values("total", ascending=False)
    )

    return result.to_dict(orient="records")


def detect_anomalies():
    data = df[df["is_anomaly"] == True]

    return data[
        [
            "district",
            "parameter",
            "type",
            "month",
            "total",
            "is_anomaly"
        ]
    ].to_dict(orient="records")


def monthly_change(district, parameter):
    data = df[
        (df["district"] == district) &
        (df["parameter"] == parameter)
    ].copy()

    if data.empty:
        return None

    data = data.sort_values("month_order")

    data["previous"] = data["total"].shift(1)

    data["change"] = data["total"] - data["previous"]

    data["change_percentage"] = np.where(
        data["previous"].notna() & (data["previous"] != 0),
        (data["change"] / data["previous"]) * 100,
        np.nan
    )

    return data[
        [
            "month",
            "total",
            "previous",
            "change",
            "change_percentage"
        ]
    ].to_dict(orient="records")