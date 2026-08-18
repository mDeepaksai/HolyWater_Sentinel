import pandas as pd

# Load dataset
df = pd.read_csv(
    "data/health_data.csv",
    encoding="latin1"
)

print("===== DATASET QUALITY CHECK =====")

# --------------------------------------------------
# 1. DUPLICATE ROWS
# --------------------------------------------------

duplicates = df.duplicated().sum()

print("\n===== DUPLICATE ROWS =====")
print("Duplicate rows:", duplicates)


# --------------------------------------------------
# 2. NEGATIVE VALUES
# --------------------------------------------------

numeric_columns = df.select_dtypes(include="number").columns

negative_counts = (df[numeric_columns] < 0).sum()

negative_counts = negative_counts[negative_counts > 0]

print("\n===== NEGATIVE VALUES =====")

if len(negative_counts) == 0:
    print("No negative values found.")
else:
    print(negative_counts)


# --------------------------------------------------
# 3. DISTRICT COUNT
# --------------------------------------------------

print("\n===== DISTRICTS =====")

print("Number of districts:", df["District"].nunique())

print("\nDistricts:")
print(sorted(df["District"].dropna().unique()))


# --------------------------------------------------
# 4. ROWS PER DISTRICT
# --------------------------------------------------

print("\n===== ROWS PER DISTRICT =====")

district_counts = df["District"].value_counts()

print(district_counts)


# --------------------------------------------------
# 5. TYPE DISTRIBUTION
# --------------------------------------------------

print("\n===== TYPE DISTRIBUTION =====")

print(df["Type"].value_counts())


# --------------------------------------------------
# 6. PARAMETERS WITH VERY FEW ROWS
# --------------------------------------------------

print("\n===== PARAMETERS WITH FEW ROWS =====")

parameter_counts = df["Parameters"].value_counts()

print(parameter_counts[parameter_counts < 100])


# --------------------------------------------------
# 7. TOTAL CONSISTENCY
# --------------------------------------------------

print("\n===== TOTAL CONSISTENCY =====")

months = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January",
    "February", "March"
]

for month in months:

    total = df[f"{month} - Total [(A+B) or (C+D)]"]
    public = df[f"{month} - Public [A]"]
    private = df[f"{month} - Private [B]"]

    mismatch = (
        total.notna()
        & public.notna()
        & private.notna()
        & (total != public + private)
    ).sum()

    print(month, "Public + Private mismatches:", mismatch)


# --------------------------------------------------
# 8. URBAN + RURAL CONSISTENCY
# --------------------------------------------------

print("\n===== URBAN/RURAL CONSISTENCY =====")

for month in months:

    total = df[f"{month} - Total [(A+B) or (C+D)]"]
    urban = df[f"{month} - Urban [C]"]
    rural = df[f"{month} - Rural [D]"]

    mismatch = (
        total.notna()
        & urban.notna()
        & rural.notna()
        & (total != urban + rural)
    ).sum()

    print(month, "Urban + Rural mismatches:", mismatch)


print("\n===== QUALITY CHECK COMPLETE =====")