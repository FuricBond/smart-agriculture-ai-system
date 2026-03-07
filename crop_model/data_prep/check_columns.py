import pandas as pd

print("=== Dataset 1 ===")
df1 = pd.read_csv(
r"C:\CropProject\crop_model\data\raw_datasets\crop_rec1\Crop_recommendation.csv"
)
print(df1.columns)

print("\n=== Dataset 2 ===")
df2 = pd.read_csv(
r"C:\CropProject\crop_model\data\raw_datasets\crop_rec2\Crop_recommendation.csv"
)
print(df2.columns)

print("\n=== Dataset 3 ===")
df3 = pd.read_csv(
r"C:\CropProject\crop_model\data\raw_datasets\crop_rec3\Crop_recommendation.csv"
)
print(df3.columns)
