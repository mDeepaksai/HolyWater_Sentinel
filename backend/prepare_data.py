import pandas as pd

INPUT_FILE = "data/health_data.csv"
OUTPUT_FILE = "data/health_data_clean.csv"

months = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March"
]

df = pd.read_csv(
    INPUT_FILE,
    encoding="latin1"
)

# Remove completely empty rows
df = df.dropna(how="all")

# Keep original negative values.
# They represent potential data anomalies and should not be silently changed.
df["is_anomaly"] = False

for month in months:
    total_col = f"{month} - Total [(A+B) or (C+D)]"

    if total_col in df.columns:
        df.loc[df[total_col] < 0, "is_anomaly"] = True

# Save cleaned dataset
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("===== CLEAN DATASET CREATED =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Output:", OUTPUT_FILE)

print("\n===== ANOMALIES =====")
anomalies = df[df["is_anomaly"]]

print("Anomaly rows:", len(anomalies))

if len(anomalies) > 0:
    print(
        anomalies[
            [
                "District",
                "Parameters",
                "Type",
                "is_anomaly"
            ]
        ].to_string(index=False)
    )