import pandas as pd

# ==========================
# Load datasets
# ==========================

yield_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\yield.csv"
)

rainfall_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\rainfall.csv"
)

temp_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\temp.csv"
)

pesticide_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\pesticides.csv"
)

# ==========================
# Clean Column Names
# ==========================

rainfall_df.rename(columns={
" Area":"Area",
"average_rain_fall_mm_per_year":"Rainfall"
}, inplace=True)

temp_df.rename(columns={
"country":"Area",
"year":"Year",
"avg_temp":"Temperature"
}, inplace=True)

# ==========================
# Keep Only Important Columns
# ==========================

yield_df = yield_df[["Area","Item","Year","Element","Value"]]

rainfall_df = rainfall_df[["Area","Year","Rainfall"]]

temp_df = temp_df[["Area","Year","Temperature"]]

pesticide_df = pesticide_df[["Area","Item","Year","Value"]]

pesticide_df.rename(columns={
"Value":"Pesticides"
}, inplace=True)

# ==========================
# Save Cleaned Files
# ==========================

yield_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield_clean.csv",
index=False
)

rainfall_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\rainfall_clean.csv",
index=False
)

temp_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\temp_clean.csv",
index=False
)

pesticide_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\pesticides_clean.csv",
index=False
)

print("Dataset #1 cleaned successfully ✅")
