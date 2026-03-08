import pandas as pd

print("Loading datasets...")

df1 = pd.read_csv(
r"D:\Project\CropProject\crop_model\data\raw_datasets\crop_rec1\Crop_recommendation.csv"
)

df2 = pd.read_csv(
r"D:\Project\CropProject\crop_model\data\raw_datasets\crop_rec2\Crop_recommendation.csv"
)

df3 = pd.read_csv(
r"D:\Project\CropProject\crop_model\data\raw_datasets\crop_rec3\Crop_recommendation.csv"
)

# Standardize column names
rename_map = {
"N":"Nitrogen",
"P":"Phosphorus",
"K":"Potassium",
"temperature":"Temperature",
"humidity":"Humidity",
"ph":"pH",
"rainfall":"Rainfall",
"label":"Crop"
}

df1.rename(columns=rename_map, inplace=True)
df2.rename(columns=rename_map, inplace=True)
df3.rename(columns=rename_map, inplace=True)

# Remove missing values
df1 = df1.dropna()
df2 = df2.dropna()
df3 = df3.dropna()

# Save cleaned datasets

df1.to_csv(
r"D:\Project\CropProject\crop_model\data\cleaned\crop1_clean.csv",
index=False
)

df2.to_csv(
r"D:\Project\CropProject\crop_model\data\cleaned\crop2_clean.csv",
index=False
)

df3.to_csv(
r"D:\Project\CropProject\crop_model\data\cleaned\crop3_clean.csv",
index=False
)

print("All crop datasets cleaned successfully ✅")
