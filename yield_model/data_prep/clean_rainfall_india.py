import pandas as pd
import os

folder = r"C:\CropProject\yield_model\data\yield_data\raw_datasets\rainfall_india.csv"

# Find csv file automatically
file = [f for f in os.listdir(folder) if f.endswith(".csv")][0]

path = os.path.join(folder, file)

print("Using file:", path)

df = pd.read_csv(path)

# Convert wide → long format
df = df.melt(
    id_vars=["YEAR"],
    var_name="Area",
    value_name="Rainfall"
)

df.rename(columns={
"YEAR":"Year"
}, inplace=True)

df = df.dropna()

df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\rainfall_india_clean.csv",
index=False
)

print("Rainfall India dataset cleaned successfully ✅")
