import pandas as pd

print("Loading datasets...")

master = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\combined\master_yield_dataset.csv",
low_memory=False
)

yield2 = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\yield2_clean.csv"
)

crop_rec = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\crop_recommendation_clean.csv"
)

rainfall_india = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\rainfall_india_clean.csv"
)

temperature = pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\cleaned\temperature_clean.csv"
)

print("Master rows:", len(master))
print("Yield2 rows:", len(yield2))
print("Crop rec rows:", len(crop_rec))
print("Rainfall India rows:", len(rainfall_india))
print("Temperature rows:", len(temperature))


print("\nCombining datasets...")

final_df = pd.concat([
    master,
    yield2
], ignore_index=True)


print("\nSaving final dataset...")

final_df.to_csv(
r"C:\CropProject\yield_model\data\yield_data\combined\final_master_yield_dataset.csv",
index=False
)

print("\nFINAL MASTER YIELD DATASET CREATED 🚀")
