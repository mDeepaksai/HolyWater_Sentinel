import pandas as pd

INPUT_FILE = "data/health_data_clean.csv"
OUTPUT_FILE = "data/health_data_long.csv"

months = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March"
]

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8"
)

rows = []

for _, row in df.iterrows():

    for month in months:

        total = row[f"{month} - Total [(A+B) or (C+D)]"]
        public = row[f"{month} - Public [A]"]
        private = row[f"{month} - Private [B]"]
        urban = row[f"{month} - Urban [C]"]
        rural = row[f"{month} - Rural [D]"]

        rows.append({
            "district": row["District"],
            "s_no": row["S.No."],
            "parameter": row["Parameters"],
            "type": row["Type"],
            "month": month,
            "total": total,
            "public": public,
            "private": private,
            "urban": urban,
            "rural": rural,
            "is_anomaly": row["is_anomaly"]
        })

long_df = pd.DataFrame(rows)

long_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("===== LONG DATASET CREATED =====")
print("Rows:", len(long_df))
print("Columns:", len(long_df.columns))
print("Output:", OUTPUT_FILE)

print("\n===== COLUMNS =====")
print(long_df.columns.tolist())

print("\n===== FIRST 10 ROWS =====")
print(long_df.head(10).to_string(index=False))

print("\n===== ANOMALIES =====")
print(
    long_df[long_df["is_anomaly"] == True]
    .to_string(index=False)
)