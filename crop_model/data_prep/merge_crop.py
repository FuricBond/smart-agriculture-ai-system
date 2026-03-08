import pandas as pd

print("Loading cleaned datasets...")

df1 = pd.read_csv(
r"D:\Project\CropProject\crop_model\cleaned\crop1_clean.csv"
)

df2 = pd.read_csv(
r"D:\Project\CropProject\crop_model\cleaned\crop2_clean.csv"
)

df3 = pd.read_csv(
r"D:\Project\CropProject\crop_model\cleaned\crop3_clean.csv"
)

print("Dataset1 rows:", len(df1))
print("Dataset2 rows:", len(df2))
print("Dataset3 rows:", len(df3))


print("\nMerging datasets...")

final_df = pd.concat([
    df1,
    df2,
    df3
], ignore_index=True)


print("\nSaving final dataset...")

final_df.to_csv(
r"D:\Project\CropProject\crop_model\data\combined\final_crop_dataset.csv",
index=False
)

print("\nFINAL CROP DATASET CREATED 🌱🚀")