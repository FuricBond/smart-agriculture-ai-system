"""
Yield Prediction Model — Phase 3 Training Pipeline
=====================================================
Improvements over Phase 1/2:
  Y4: XGBoost replaces RandomForestRegressor (115MB → ~5MB, faster)
  Y3: Season encoded as feature (where available from India sub-dataset)

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib

warnings.filterwarnings('ignore')


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DATA_PATH  = r"C:\CropProject\yield_model\data\yield_data\combined\final_master_yield_dataset.csv"
MODEL_DIR  = r"C:\CropProject\yield_model\models"
REPORT_DIR = r"C:\CropProject\yield_model\reports"

RANDOM_STATE = 42
TEST_SIZE    = 0.1

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Season mapping for encoding
SEASON_MAP = {
    'Kharif':     1,
    'Rabi':       2,
    'Whole Year': 3,
    'Autumn':     4,
    'Summer':     5,
    'Winter':     6,
}


# ═══════════════════════════════════════════════════════════════
# 1. LOAD DATASET
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  YIELD PREDICTION MODEL — PHASE 3 TRAINING PIPELINE")
print("  Y3: Season feature  |  Y4: XGBoost regressor")
print("=" * 60)

print("\n📂 Loading dataset (chunked — skipping non-yield rows)...")

# The combined CSV has 8.7M rows but only ~340k have Yield data.
# Read in chunks and keep only rows with a valid Yield value.
chunks = []
for chunk in pd.read_csv(DATA_PATH, low_memory=False, chunksize=200_000):
    # Keep rows that have a Yield column and a numeric value
    if 'Yield' in chunk.columns:
        sub = chunk[chunk['Yield'].notna()].copy()
    elif 'Element' in chunk.columns and 'Value' in chunk.columns:
        sub = chunk[chunk['Element'] == 'Yield'].copy()
        sub = sub.rename(columns={'Value': 'Yield'})
    else:
        continue
    sub['Yield'] = pd.to_numeric(sub['Yield'], errors='coerce')
    sub = sub[sub['Yield'] > 0]
    if len(sub) > 0:
        chunks.append(sub)

df = pd.concat(chunks, ignore_index=True)
print(f"   Yield rows loaded: {len(df):,}")
print(f"   Columns: {list(df.columns)[:8]}...")


# ═══════════════════════════════════════════════════════════════
# 2. DATA CLEANING
# ═══════════════════════════════════════════════════════════════

print("\n🔍 Data Cleaning...")

# Ensure Yield column exists
if 'Yield' not in df.columns:
    if 'Element' in df.columns and 'Value' in df.columns:
        df = df[df['Element'] == 'Yield'].copy()
        df = df.rename(columns={'Value': 'Yield'})
        print("   ✅ Extracted Yield from Element/Value columns")
    else:
        print("   ❌ Cannot find Yield column."); sys.exit(1)

# Keep only rows with valid yield
df = df.dropna(subset=['Yield'])
df['Yield'] = pd.to_numeric(df['Yield'], errors='coerce')
df = df.dropna(subset=['Yield'])
df = df[df['Yield'] > 0]

# Clean text cols
for col in ['Area', 'Item']:
    df[col] = df[col].astype(str).str.strip()
df['Year'] = df['Year'].astype(str).str[:4]
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df.dropna(subset=['Year'])
df['Year'] = df['Year'].astype(int)

print(f"   Rows with valid Yield: {len(df):,}")
print(f"   Unique Areas: {df['Area'].nunique()}")
print(f"   Unique Crops: {df['Item'].nunique()}")
print(f"   Year Range:   {df['Year'].min()} — {df['Year'].max()}")


# ═══════════════════════════════════════════════════════════════
# 3. FEATURE ENGINEERING (Y3 + Y4)
# ═══════════════════════════════════════════════════════════════

print("\n⚙ Feature Engineering...")

# Categorical encoders
area_encoder = LabelEncoder()
crop_encoder = LabelEncoder()
df['Area_encoded'] = area_encoder.fit_transform(df['Area'])
df['Item_encoded'] = crop_encoder.fit_transform(df['Item'])

# Time features
df['Decade']          = (df['Year'] // 10) * 10
df['Years_since_2000'] = df['Year'] - 2000

# Y3 — Season feature (encode where available, 0 = unknown)
if 'Season' in df.columns:
    df['Season_encoded'] = df['Season'].map(SEASON_MAP).fillna(0).astype(int)
    season_coverage = (df['Season_encoded'] > 0).sum()
    print(f"   ✅ Season encoded: {season_coverage:,} rows have season data ({season_coverage/len(df)*100:.1f}%)")
else:
    df['Season_encoded'] = 0
    print("   ⚠ Season column not found — defaulting to 0")

# Final feature list
numeric_features = [
    'Area_encoded', 'Item_encoded',
    'Year', 'Decade', 'Years_since_2000',
    'Season_encoded',    # Y3
]
print(f"   Final features: {numeric_features}")

X = df[numeric_features].copy()
y = df['Yield'].copy()

# Remove any NaN rows
mask = X.notna().all(axis=1) & y.notna()
X, y = X[mask], y[mask]

print(f"\n   Final dataset: {len(X):,} samples")
print(f"   Yield — Mean: {y.mean():.2f}  Median: {y.median():.2f}  Std: {y.std():.2f}")


# ═══════════════════════════════════════════════════════════════
# 4. TRAIN / TEST SPLIT
# ═══════════════════════════════════════════════════════════════

print("\n📊 Train / Test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
print(f"   Training: {len(X_train):,}  |  Test: {len(X_test):,}")


# ═══════════════════════════════════════════════════════════════
# 5. Y4 — XGBOOST MODEL
# ═══════════════════════════════════════════════════════════════

print("\n🤖 Building XGBoost Regressor (Y4)...")

model = xgb.XGBRegressor(
    n_estimators=500,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    tree_method='hist',          # Fast CPU histogram method
    verbosity=0,
)

print("   Training XGBoost... (this may take a few minutes)")
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False,
)
print("   ✅ Training complete")


# ═══════════════════════════════════════════════════════════════
# 6. EVALUATION
# ═══════════════════════════════════════════════════════════════

print("\n📋 Evaluating on test set...")
y_pred = model.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)
mask_nonzero = y_test != 0
mape = np.mean(np.abs((y_test[mask_nonzero] - y_pred[mask_nonzero]) / y_test[mask_nonzero])) * 100 \
       if mask_nonzero.sum() > 0 else float('nan')

print(f"\n   ┌─────────────────────────────────┐")
print(f"   │  TEST SET RESULTS (XGBoost)    │")
print(f"   ├─────────────────────────────────┤")
print(f"   │  R² Score:    {r2:.4f}            │")
print(f"   │  MAE:         {mae:.2f}           │")
print(f"   │  RMSE:        {rmse:.2f}          │")
print(f"   │  MAPE:        {mape:.2f}%          │")
print(f"   └─────────────────────────────────┘")


# ═══════════════════════════════════════════════════════════════
# 7. CROSS-VALIDATION (subsample for speed)
# ═══════════════════════════════════════════════════════════════

print("\n📈 5-Fold Cross-Validation (50k subsample)...")
cv_n   = min(50000, len(X_train))
cv_idx = np.random.RandomState(RANDOM_STATE).choice(len(X_train), cv_n, replace=False)
X_cv   = X_train.iloc[cv_idx]
y_cv   = y_train.iloc[cv_idx]

cv_model = xgb.XGBRegressor(
    n_estimators=200, max_depth=7, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    random_state=RANDOM_STATE, n_jobs=-1,
    tree_method='hist', verbosity=0
)

cv_scores = cross_val_score(cv_model, X_cv, y_cv, cv=5, scoring='r2', n_jobs=-1)
for i, s in enumerate(cv_scores, 1):
    print(f"     Fold {i}: {s:.4f}")
print(f"   Mean R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")


# ═══════════════════════════════════════════════════════════════
# 8. FEATURE IMPORTANCE PLOT
# ═══════════════════════════════════════════════════════════════

print("\n📊 Feature importance plot...")
importances = model.feature_importances_
feat_df = pd.DataFrame({'Feature': numeric_features, 'Importance': importances}) \
            .sort_values('Importance', ascending=True)

fig, ax = plt.subplots(figsize=(9, 5))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(feat_df)))
ax.barh(feat_df['Feature'], feat_df['Importance'], color=colors, edgecolor='navy')
ax.set_title('Yield Prediction — Feature Importance (XGBoost Phase 3)', fontsize=13, fontweight='bold')
ax.set_xlabel('Importance')
plt.tight_layout()
fi_path = os.path.join(REPORT_DIR, "feature_importance_phase3.png")
fig.savefig(fi_path, dpi=150)
plt.close(fig)
print(f"   ✅ Saved: {fi_path}")


# ═══════════════════════════════════════════════════════════════
# 9. ACTUAL VS PREDICTED PLOT
# ═══════════════════════════════════════════════════════════════

plot_n = min(5000, len(y_test))
idx    = np.random.RandomState(RANDOM_STATE).choice(len(y_test), plot_n, replace=False)
yt     = y_test.values[idx]
yp     = y_pred[idx]
max_v  = max(yt.max(), yp.max())

fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(yt, yp, alpha=0.3, s=10, color='steelblue')
ax.plot([0, max_v], [0, max_v], 'r--', linewidth=2, label='Perfect')
ax.set_title('Yield — Actual vs Predicted (XGBoost Phase 3)', fontsize=13, fontweight='bold')
ax.set_xlabel('Actual Yield'); ax.set_ylabel('Predicted Yield')
ax.legend(); plt.tight_layout()
sp = os.path.join(REPORT_DIR, "actual_vs_predicted_phase3.png")
fig.savefig(sp, dpi=150); plt.close(fig)
print(f"   ✅ Saved: {sp}")


# ═══════════════════════════════════════════════════════════════
# 10. SAVE MODEL AND ENCODERS
# ═══════════════════════════════════════════════════════════════

print("\n💾 Saving models...")

model_path    = os.path.join(MODEL_DIR, "yield_model.pkl")
area_enc_path = os.path.join(MODEL_DIR, "area_encoder.pkl")
crop_enc_path = os.path.join(MODEL_DIR, "crop_encoder.pkl")

joblib.dump(model,        model_path)
joblib.dump(area_encoder, area_enc_path)
joblib.dump(crop_encoder, crop_enc_path)

model_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"   ✅ Model:        {model_path} ({model_mb:.1f} MB)")
print(f"   ✅ Area encoder: {area_enc_path}")
print(f"   ✅ Crop encoder: {crop_enc_path}")

# Save metadata
metadata = {
    "model_type":       "XGBoostRegressor",
    "phase":            "3",
    "improvements":     ["Y3: Season feature", "Y4: XGBoost (replaced RandomForest)"],
    "features":         numeric_features,
    "season_map":       SEASON_MAP,
    "n_areas":          len(area_encoder.classes_),
    "n_crops":          len(crop_encoder.classes_),
    "areas":            area_encoder.classes_.tolist(),
    "crops":            crop_encoder.classes_.tolist(),
    "test_r2":          round(r2, 4),
    "test_mae":         round(mae, 2),
    "test_rmse":        round(rmse, 2),
    "test_mape":        round(mape, 2),
    "cv_mean_r2":       round(cv_scores.mean(), 4),
    "cv_std_r2":        round(cv_scores.std(), 4),
    "train_samples":    len(X_train),
    "test_samples":     len(X_test),
    "year_range":       [int(df['Year'].min()), int(df['Year'].max())],
    "model_size_mb":    round(model_mb, 2),
}

meta_path = os.path.join(MODEL_DIR, "model_metadata.json")
with open(meta_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✅ Metadata: {meta_path}")

# Regression report
rpt = os.path.join(REPORT_DIR, "regression_report_phase3.txt")
with open(rpt, 'w') as f:
    f.write("YIELD PREDICTION MODEL — PHASE 3 REGRESSION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Model Type:          XGBoostRegressor\n")
    f.write(f"Improvements:        Y3 (Season), Y4 (XGBoost)\n\n")
    f.write(f"R² Score:            {r2:.4f}\n")
    f.write(f"Mean Absolute Error: {mae:.2f}\n")
    f.write(f"Root MSE:            {rmse:.2f}\n")
    f.write(f"MAPE:                {mape:.2f}%\n")
    f.write(f"CV R² (50k):         {cv_scores.mean():.4f} ± {cv_scores.std():.4f}\n\n")
    f.write(f"Dataset Size:        {len(X):,} samples\n")
    f.write(f"Features:            {numeric_features}\n")
    f.write(f"Areas:               {len(area_encoder.classes_)}\n")
    f.write(f"Crops:               {len(crop_encoder.classes_)}\n")
    f.write(f"Model File Size:     {model_mb:.1f} MB\n")
print(f"   ✅ Report: {rpt}")


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  ✅ YIELD PREDICTION MODEL — PHASE 3 TRAINING COMPLETE")
print("=" * 60)
print(f"  R²:        {r2:.4f}")
print(f"  MAE:       {mae:.2f}")
print(f"  RMSE:      {rmse:.2f}")
print(f"  CV R²:     {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"  Model:     {model_mb:.1f} MB  (was ~115 MB)")
print(f"  Areas:     {len(area_encoder.classes_)}")
print(f"  Crops:     {len(crop_encoder.classes_)}")
print("=" * 60)
