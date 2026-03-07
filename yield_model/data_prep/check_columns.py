import pandas as pd

print("=== Yield Dataset ===")
print(pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\yield.csv"
).columns)

print("\n=== Rainfall Dataset ===")
print(pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\rainfall.csv"
).columns)

print("\n=== Temperature Dataset ===")
print(pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\temp.csv"
).columns)

print("\n=== Pesticides Dataset ===")
print(pd.read_csv(
r"C:\CropProject\yield_model\data\yield_data\raw_datasets\yield1.csv\pesticides.csv"
).columns)
