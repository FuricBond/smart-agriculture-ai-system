import pandas as pd

# Load FAO dataset
df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield_global.csv\Production_Crops_Livestock_E_All_Data.csv",
low_memory=False
)

# Keep only useful columns
df = df[["Area","Item","Element"] + [col for col in df.columns if col.startswith("Y")]]

# Convert wide format → long format
df = df.melt(
    id_vars=["Area","Item","Element"],
    var_name="Year",
    value_name="Value"
)

# Clean Year column (remove 'Y')
df["Year"] = df["Year"].str.replace("Y","")
df["Year"] = df["Year"].str.extract(r'(\d+)')
df["Year"] = df["Year"].astype(int)

# Remove missing values
df = df.dropna()

# Save cleaned dataset
df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield_global_clean.csv",
index=False
)

print("Global dataset cleaned successfully ✅")
