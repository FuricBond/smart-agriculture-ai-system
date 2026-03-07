import pandas as pd

# ==========================
# Load Cleaned Files
# ==========================

yield_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield_clean.csv"
)

rainfall_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\rainfall_clean.csv"
)

temp_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\temp_clean.csv"
)

pesticide_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\pesticides_clean.csv"
)

# ==========================
# Merge Step by Step
# ==========================

print("Merging Yield + Rainfall...")

merged_df = pd.merge(
    yield_df,
    rainfall_df,
    on=["Area","Year"],
    how="left"
)

print("Merging Temperature...")

merged_df = pd.merge(
    merged_df,
    temp_df,
    on=["Area","Year"],
    how="left"
)

print("Merging Pesticides...")

merged_df = pd.merge(
    merged_df,
    pesticide_df,
    on=["Area","Item","Year"],
    how="left"
)

# ==========================
# Save Final Dataset
# ==========================

merged_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\combined\yield_dataset1_final.csv",
index=False
)

print("Dataset #1 FINAL created successfully 🚀")
