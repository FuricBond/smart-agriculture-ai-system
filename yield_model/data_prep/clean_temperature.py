import pandas as pd
import os

folder = r"C:\CropProject\yield_model\data\yield_data\raw_datasets\temperature.csv"

# Automatically find CSV file
file = [f for f in os.listdir(folder) if f.endswith(".csv")][0]
path = os.path.join(folder, file)

print("Using file:", path)

df = pd.read_csv(path)

print("Columns:", df.columns)

# Try to standardize column names
df.columns = [c.strip() for c in df.columns]

# Rename if needed (safe renaming)
rename_map = {}

if "YEAR" in df.columns:
    rename_map["YEAR"] = "Year"

if "Year" not in df.columns and "year" in df.columns:
    rename_map["year"] = "Year"

if "Temperature" not in df.columns:
    for c in df.columns:
        if "temp" in c.lower():
            rename_map[c] = "Temperature"

df.rename(columns=rename_map, inplace=True)

# Remove missing values
df = df.dropna()

# Save cleaned dataset
df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\temperature_clean.csv",
index=False
)

print("Temperature dataset cleaned successfully ✅")
