import os
import shutil
import pandas as pd

# ==========================
# PATHS
# ==========================

cassava = r"D:\Project\CropProject\disease_model\data\cassava-leaf-disease-classification\train_images"
cassava_csv = r"D:\Project\CropProject\disease_model\data\cassava-leaf-disease-classification\train.csv"

combined = r"D:\Project\CropProject\disease_model\data\combined"


# ==========================
# Cassava Merge
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

print("Cassava Dataset copied successfully!")

print("\nFINAL DATASET READY 🚀")
