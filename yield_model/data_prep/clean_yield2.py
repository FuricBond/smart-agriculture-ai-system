import pandas as pd

# Load dataset
df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield2.csv\India Agriculture Crop Production.csv"
)

# Keep important columns
df = df[[
"State",
"District",
"Crop",
"Year",
"Season",
"Area",
"Production",
"Yield"
]]

# Rename columns to match master dataset style
df.rename(columns={
"Crop":"Item",
"State":"Area"
}, inplace=True)

# Remove missing values
df = df.dropna()

# Save cleaned dataset
df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield2_clean.csv",
index=False
)

print("Yield2 dataset cleaned successfully ✅")
