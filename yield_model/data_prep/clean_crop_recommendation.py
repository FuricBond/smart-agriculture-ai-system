import pandas as pd

# Load dataset
df = pd.read_csv(
r"D:\Project\CropProject\yield_model\data\yield_data\raw_datasets\crop_recommendation.csv\Crop_recommendation.csv"
)

# Rename columns to standard format
df.rename(columns={
"label":"Crop",
"N":"Nitrogen",
"P":"Phosphorus",
"K":"Potassium",
"temperature":"Temperature",
"humidity":"Humidity",
"ph":"pH",
"rainfall":"Rainfall"
}, inplace=True)

# Save cleaned dataset
df.to_csv(
r"D:\Project\CropProject\yield_model\data\yield_data\cleaned\crop_recommendation_clean.csv",
index=False
)

print("Crop recommendation dataset cleaned ✅")
