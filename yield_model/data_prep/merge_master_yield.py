import pandas as pd

# ==========================
# Load datasets
# ==========================

dataset1 = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\combined\yield_dataset1_final.csv"
)

global_df = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield_global_clean.csv"
)

print("Dataset1 rows:", len(dataset1))
print("Global dataset rows:", len(global_df))

# ==========================
# Combine datasets
# ==========================

master_df = pd.concat(
    [dataset1, global_df],
    ignore_index=True
)

# ==========================
# Save master dataset
# ==========================

master_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\combined\master_yield_dataset.csv",
index=False
)

print("\nMASTER DATASET CREATED SUCCESSFULLY 🚀")
