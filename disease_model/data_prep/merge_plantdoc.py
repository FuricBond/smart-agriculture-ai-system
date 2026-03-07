import os
import shutil

# PlantDoc images folder
plantdoc = r"C:\CropProject\disease_model\data\archive\images"

# Combined dataset
combined = r"C:\CropProject\disease_model\data\combined"

print("Copying PlantDoc images...")

# Put them into one folder
plantdoc_folder = os.path.join(combined, "PlantDoc_RealImages")

os.makedirs(plantdoc_folder, exist_ok=True)

for file in os.listdir(plantdoc):

    shutil.copy(
        os.path.join(plantdoc, file),
        plantdoc_folder
    )

print("PlantDoc merged successfully!")

print("\nDATASET FINALIZED 🚀")
