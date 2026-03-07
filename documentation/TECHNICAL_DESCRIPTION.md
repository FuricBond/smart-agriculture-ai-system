# AI-Based Crop Health and Yield Prediction System with Advisory Support for Smart Agriculture

> **Complete Technical Description — Post Upgrade**
> *Updated: February 28, 2026*

---

## 1. Project Overview

This project implements a complete AI-based smart agriculture system that assists farmers through three core prediction modules powered by machine learning and deep learning:

| Module | Technique | Purpose |
|---|---|---|
| Disease Detection | Deep Learning (CNN) | Identify plant diseases from leaf images |
| Crop Recommendation | Ensemble ML | Recommend optimal crops based on soil & weather |
| Yield Prediction | Regression ML | Predict crop yield for a given region and year |

**Project Root:** `C:\CropProject`

### 1.1 Directory Structure

```
C:\CropProject\
├── disease_model\
│   ├── data\combined\                     # Combined disease image dataset (115K+ images)
│   ├── data_prep\                         # Archived data merge/cleaning scripts
│   │   ├── merge_datasets.py
│   │   ├── merge_cassava.py
│   │   ├── merge_plantdoc.py
│   │   └── test_disease_model.py          # Legacy test (archived)
│   ├── models\
│   │   ├── disease_model.pth              # Trained ResNet50 model
│   │   ├── class_names.json               # Class-to-index mapping
│   │   └── model_metadata.json            # Training metadata
│   ├── reports\                           # Evaluation outputs
│   │   ├── confusion_matrix.png
│   │   ├── classification_report.txt
│   │   ├── training_history.png
│   │   └── training_history.json
│   └── scripts\
│       ├── train_disease_model.py         # Professional training pipeline
│       ├── predict_disease.py             # Inference with top-5 predictions
│       └── evaluate_disease_model.py      # Full validation evaluation
│
├── crop_model\
│   ├── data\combined\final_crop_dataset.csv
│   ├── data_prep\                         # Archived data merge/cleaning scripts
│   │   ├── check_columns.py
│   │   ├── clean_crop.py
│   │   ├── merge_crop.py
│   │   └── test_improved_model.py         # Legacy test (archived)
│   ├── models\
│   │   ├── improved_crop_model.pkl        # Ensemble model
│   │   ├── label_encoder.pkl              # Label encoder
│   │   └── model_metadata.json            # Training metadata
│   ├── reports\                           # Evaluation outputs
│   │   ├── confusion_matrix.png
│   │   ├── classification_report.txt
│   │   └── feature_importance.png
│   └── scripts\
│       ├── train_crop_model.py            # Professional training pipeline
│       ├── predict_crop.py                # Inference with validation
│       └── feature_utils.py               # Shared feature engineering
│
├── yield_model\
│   ├── data\yield_data\combined\final_master_yield_dataset.csv
│   ├── data_prep\                         # Archived 12 data cleaning scripts
│   ├── models\
│   │   ├── yield_model.pkl                # Trained regressor
│   │   ├── area_encoder.pkl               # Area label encoder
│   │   ├── crop_encoder.pkl               # Crop label encoder
│   │   └── model_metadata.json            # Training metadata
│   ├── reports\                           # Evaluation outputs
│   │   ├── feature_importance.png
│   │   ├── actual_vs_predicted.png
│   │   └── regression_report.txt
│   └── scripts\
│       ├── train_yield_model.py           # Professional training pipeline
│       └── predict_yield.py               # Inference with validation
│
├── advisory_system\                       # (Planned) Rule-based farming advice
├── dashboard\                             # (Planned) Web interface for farmers
└── documentation\
    └── TECHNICAL_DESCRIPTION.md
```

---

## 2. Module 1 — Disease Detection Model

### 2.1 Objective

Detect plant diseases from leaf images using a deep learning convolutional neural network.

### 2.2 Input / Output

| | Description | Example |
|---|---|---|
| **Input** | RGB leaf image | Tomato leaf photograph |
| **Output** | Top-5 disease predictions with confidence | `Tomato___Late_blight (94.2%)` |

### 2.3 Dataset

| Source Dataset | Description |
|---|---|
| **PlantVillage** | Large-scale labeled plant leaf images |
| **PlantDoc** | Real-world plant disease images |
| **Cassava Leaf Disease** | Cassava-specific disease images |

| Metric | Value |
|---|---|
| Total Classes | 52 |
| Total Images | 115,932 |
| Training Images | 92,745 (80%) |
| Validation Images | 23,187 (20%) |

### 2.4 Model Architecture (Upgraded)

```
┌─────────────────────────────────────────────────────────────────┐
│                   ResNet50 (ImageNet V2 Pretrained)             │
├─────────────────────────────────────────────────────────────────┤
│  Input           →  224 × 224 × 3 (RGB)                       │
│  Frozen Layers   →  Conv1, Layer1, Layer2 (transfer learning)  │
│  Fine-tuned      →  Layer3, Layer4                             │
│  FC Head         →  Dropout(0.3) → Linear(2048, 512) → ReLU   │
│                     → Dropout(0.2) → Linear(512, 52)           │
│  Output          →  Softmax (52 classes)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.5 Training Features (New)

| Feature | Description |
|---|---|
| **Separate Transforms** | Training (augmentation) vs Validation (clean) |
| **Augmentation Pipeline** | RandomCrop, HFlip, VFlip, Rotation, ColorJitter, Affine |
| **ImageNet Normalization** | Applied to both training and inference |
| **LR Scheduler** | ReduceLROnPlateau (patience=2, factor=0.5) |
| **Early Stopping** | Stops if no improvement for 4 epochs |
| **Best Checkpoint** | Saves only the model with highest validation accuracy |
| **Mixed Precision** | AMP (Automatic Mixed Precision) for GPU speed |
| **Multi-worker Loading** | 4 DataLoader workers with pinned memory |
| **Class Mapping** | Saved as `class_names.json` for prediction |

### 2.6 Evaluation Outputs

| Report | Description |
|---|---|
| `confusion_matrix.png` | 52×52 confusion matrix heatmap |
| `classification_report.txt` | Per-class precision, recall, F1 |
| `training_history.png` | Loss & accuracy curves |
| Top-1 & Top-5 Accuracy | Computed on full validation set |

---

## 3. Module 2 — Crop Recommendation Model

### 3.1 Objective

Recommend the best crop to cultivate based on soil nutrient levels and environmental weather conditions.

### 3.2 Input / Output

| | Description | Example |
|---|---|---|
| **Input** | 7 soil & weather features | N=90, P=40, K=40, Temp=28, Hum=70, pH=6.5, Rain=200 |
| **Output** | Top-5 recommended crops with probability | Rice (87.3%), Wheat (5.1%), ... |

### 3.3 Feature Engineering (21 features from 7 raw inputs)

| Category | Features |
|---|---|
| **Raw** (7) | Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall |
| **Nutrient Ratios** (3) | N/P, N/K, P/K |
| **Log Transforms** (2) | log(Rainfall), log(Humidity) |
| **Interactions** (3) | Temp×Humidity, Temp×Rainfall, Humidity×Rainfall |
| **Composite** (1) | Soil Index (N×P×K / 1000) |
| **Stress** (2) | Heat Stress (T>32), Drought Stress (Rain<80) |
| **Soil pH** (3) | Acidic (<6), Neutral (6–7.5), Alkaline (>7.5) |

**Key Improvement:** Feature engineering is now in a **shared module** (`feature_utils.py`) guaranteeing identical transforms between training and prediction.

### 3.4 Model Architecture

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ RandomForest │   │   XGBoost    │   │   LightGBM   │
│  500 trees   │   │  400 trees   │   │  400 trees   │
│  depth=25    │   │   depth=7    │   │   depth=8    │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       └─────────┬────────┘──────────────────┘
                 ▼
    ┌────────────────────────┐
    │  Soft Voting Ensemble  │
    │  + StandardScaler      │
    └────────────────────────┘
```

### 3.5 Training Features (New)

| Feature | Description |
|---|---|
| **5-Fold Stratified CV** | Cross-validation with per-fold metrics |
| **Confusion Matrix** | Saved as `confusion_matrix.png` |
| **Classification Report** | Per-crop precision, recall, F1-score |
| **Feature Importance** | Bar chart from RandomForest estimator |
| **Input Validation** | Range checks for all 7 input features |
| **Model Metadata** | JSON with accuracy, features, class list |

---

## 4. Module 3 — Yield Prediction Model

### 4.1 Objective

Predict crop yield for a given geographic area, crop type, and year.

### 4.2 Input / Output

| | Description | Example |
|---|---|---|
| **Input** | Area, Crop, Year | India, Rice, 2020 |
| **Output** | Predicted yield value | 3,542.75 |

### 4.3 Model Architecture (Upgraded)

| Detail | Before | After |
|---|---|---|
| Encoding | `pd.get_dummies()` (broken at inference) | **LabelEncoder** (saved for reuse) |
| Trees | 50 | **200** |
| Max Depth | Unlimited | **30** |
| Features | 3 (Area, Item, Year) | **5+** (+ Decade, Years_since_2000, optional Rainfall/Temp) |
| Metrics | MAE only | **R², MAE, RMSE, MAPE** |
| CV | None | **5-Fold Cross-Validation** |
| Predict Script | ❌ Missing | ✅ **Created** |

### 4.4 Training Features (New)

| Feature | Description |
|---|---|
| **Proper Label Encoding** | Area/Crop encoded with saved LabelEncoders |
| **Feature Engineering** | Decade, Years_since_2000, optional Rainfall/Temp |
| **5-Fold CV** | Cross-validation on subsample for speed |
| **Feature Importance** | Bar chart saved to reports |
| **Actual vs Predicted** | Scatter plot for visual quality check |
| **Regression Report** | R², MAE, RMSE, MAPE saved to file |
| **Input Validation** | Validates Area/Crop against training data with suggestions |

---

## 5. Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.13 |
| Deep Learning | PyTorch, Torchvision |
| Machine Learning | scikit-learn, XGBoost, LightGBM |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Serialization | Joblib, JSON |
| GPU Acceleration | CUDA + AMP (Mixed Precision) |

---

## 6. System Flow

```
                    ┌─────────────────────────────────────────────────┐
                    │         SMART AGRICULTURE SYSTEM                │
                    └─────────────────────────────────────────────────┘

  ┌─────────────┐        ┌──────────────────┐        ┌──────────────────┐
  │  Leaf Image  │──────▶│  Disease Model   │──────▶│  Top-5 Diseases   │
  │  (Camera)    │        │  ResNet50 CNN    │        │  with Confidence  │
  └─────────────┘        └──────────────────┘        └──────────────────┘

  ┌─────────────┐        ┌──────────────────┐        ┌──────────────────┐
  │  Soil +      │──────▶│  Crop Model      │──────▶│  Top-5 Crops      │
  │  Weather     │        │  Voting Ensemble │        │  with Probability │
  └─────────────┘        └──────────────────┘        └──────────────────┘

  ┌─────────────┐        ┌──────────────────┐        ┌──────────────────┐
  │  Area +      │──────▶│  Yield Model     │──────▶│  Predicted Yield  │
  │  Crop + Year │        │  RandomForest    │        │  with R² Score    │
  └─────────────┘        └──────────────────┘        └──────────────────┘
```

---

## 7. Bugs Fixed During Upgrade

| # | Module | Bug | Impact | Fix |
|---|---|---|---|---|
| 1 | Disease Predict | Missing ImageNet normalization during inference | Wrong predictions | Added `Normalize(mean, std)` to inference transform |
| 2 | Disease Test | Hardcoded 53 classes (model has 52) | Crash/wrong output | Archived; new evaluation script uses JSON class map |
| 3 | Crop Model | `soil_index` formula differs between train and test | Inconsistent predictions | Shared `feature_utils.py` module |
| 4 | Yield Model | `pd.get_dummies()` for encoding | Cannot predict on new Area/Crop values | Replaced with saved `LabelEncoder` |
| 5 | Yield Model | No prediction script | No way to make predictions | Created `predict_yield.py` |

---

## 8. Project Status

### ✅ Completed

- [x] Disease Detection Model — trained and upgraded
- [x] Crop Recommendation Model — trained and upgraded
- [x] Yield Prediction Model — trained and upgraded
- [x] All critical bugs fixed
- [x] Professional evaluation metrics added
- [x] Confusion matrices and classification reports
- [x] Feature importance visualizations
- [x] Cross-validation for all models
- [x] Shared feature engineering module
- [x] Model metadata JSON files
- [x] Project structure cleaned and organized

### 🔲 Remaining

- [ ] **Advisory Support System** — Rule-based farming advice engine
- [ ] **Web Dashboard** — User-friendly interface for farmers

---

*Document generated for: AI-Based Crop Health and Yield Prediction System*
*Project Root: `C:\CropProject`*
