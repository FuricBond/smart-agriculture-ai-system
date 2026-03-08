import os
import shutil
import pandas as pd

# ==========================
# PATHS (FINAL CORRECT)
# ==========================

plantvillage = r"D:\Project\CropProject\disease_model\data\plantvillage"

# New Plant Diseases Dataset
newdataset = r"D:\Project\CropProject\disease_model\data\newdataset\New Plant Diseases Dataset(Augmented)\train"

# Rice Dataset
rice = r"D:\Project\CropProject\disease_model\data\archive (1)\Rice Leaf Bacterial and Fungal Disease Dataset\Augmented\Augmented Images"

# Cassava Dataset
cassava = r"D:\Project\CropProject\disease_model\data\cassava-leaf-disease-classification\train_images"
cassava_csv = r"D:\Project\CropProject\disease_model\data\cassava-leaf-disease-classification\train.csv"

# Combined Dataset
combined = r"D:\Project\CropProject\disease_model\data\combined"

os.makedirs(combined, exist_ok=True)


# ==========================
# 1. PlantVillage
# ==========================

print("Copying PlantVillage...")

for class_name in os.listdir(plantvillage):

    src_folder = os.path.join(plantvillage, class_name)
    dst_folder = os.path.join(combined, class_name)

    os.makedirs(dst_folder, exist_ok=True)

    for file in os.listdir(src_folder):

        shutil.copy(
            os.path.join(src_folder, file),
            os.path.join(dst_folder, file)
        )

print("PlantVillage copied!")


# ==========================
# 2. NewDataset
# ==========================

print("Copying NewDataset...")

for class_name in os.listdir(newdataset):

    src_folder = os.path.join(newdataset, class_name)
    dst_folder = os.path.join(combined, class_name)

    os.makedirs(dst_folder, exist_ok=True)

    for file in os.listdir(src_folder):

        shutil.copy(
            os.path.join(src_folder, file),
            os.path.join(dst_folder, file)
        )

print("NewDataset copied!")


# ==========================
# 3. Rice Dataset
# ==========================

print("Copying Rice Dataset...")

for class_name in os.listdir(rice):

    src_folder = os.path.join(rice, class_name)

    dst_folder = os.path.join(
        combined,
        "Rice___" + class_name.replace(" ", "_")
    )

    os.makedirs(dst_folder, exist_ok=True)

    for file in os.listdir(src_folder):

        shutil.copy(
            os.path.join(src_folder, file),
            os.path.join(dst_folder, file)
        )

print("Rice Dataset copied!")


# ==========================
# 4. Cassava Dataset
# ==========================

print("Copying Cassava Dataset...")

df = pd.read_csv(cassava_csv)

label_map = {
    0: "Cassava___Bacterial_Blight",
    1: "Cassava___Brown_Streak",
    2: "Cassava___Green_Mottle",
    3: "Cassava___Mosaic",
    4: "Cassava___Healthy"
}

for i, row in df.iterrows():

    image_name = row["image_id"]
    label = row["label"]

    src_file = os.path.join(cassava, image_name)

    class_name = label_map[label]

    dst_folder = os.path.join(combined, class_name)

    os.makedirs(dst_folder, exist_ok=True)

    shutil.copy(
        src_file,
        os.path.join(dst_folder, image_name)
    )

print("Cassava Dataset copied!")


print("\nALL DATASETS MERGED SUCCESSFULLY 🚀")
