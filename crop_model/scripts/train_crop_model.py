"""
Crop Recommendation Model — Professional Training Pipeline
============================================================
Trains a Soft Voting Ensemble (RandomForest + XGBoost + LightGBM)
with stratified k-fold cross-validation, evaluation metrics,
confusion matrix, and feature importance visualization.

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score
)
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
import xgboost as xgb
import lightgbm as lgb
import joblib

# Import shared feature engineering
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_utils import engineer_features, FEATURE_COLUMNS

warnings.filterwarnings('ignore', category=UserWarning)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DATA_PATH = r"D:\Project\CropProject\crop_model\data\combined\final_crop_dataset.csv"
MODEL_DIR = r"D:\Project\CropProject\crop_model\models"
REPORT_DIR = r"D:\Project\CropProject\crop_model\reports"

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 1. LOAD AND VALIDATE DATASET
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  CROP RECOMMENDATION MODEL — TRAINING PIPELINE")
print("=" * 60)

print("\n📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"   Total rows: {len(df):,}")
print(f"   Columns: {list(df.columns)}")

# Data Quality Checks
print("\n🔍 Data Quality Check:")
missing = df.isnull().sum()
if missing.sum() > 0:
    print(f"   ⚠ Missing values found:")
    for col in missing[missing > 0].index:
        print(f"     - {col}: {missing[col]} missing")
    df = df.dropna()
    print(f"   ✅ Dropped rows with missing values. Remaining: {len(df):,}")
else:
    print("   ✅ No missing values")

duplicates = df.duplicated().sum()
if duplicates > 0:
    print(f"   ⚠ Found {duplicates} duplicate rows — removing")
    df = df.drop_duplicates()
    print(f"   ✅ After dedup: {len(df):,} rows")
else:
    print("   ✅ No duplicate rows")

print(f"\n🌾 Crops: {df['Crop'].nunique()} unique classes")
print(f"   Distribution:")
crop_counts = df['Crop'].value_counts()
for crop, count in crop_counts.items():
    print(f"     {crop}: {count} samples")


# ═══════════════════════════════════════════════════════════════
# 2. FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════

print("\n⚙ Applying feature engineering...")
df = engineer_features(df)
print(f"   Features after engineering: {len(FEATURE_COLUMNS)}")

X = df[FEATURE_COLUMNS]
y = df['Crop']

# Encode target
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"   Target classes: {len(le.classes_)}")


# ═══════════════════════════════════════════════════════════════
# 3. TRAIN / TEST SPLIT
# ═══════════════════════════════════════════════════════════════

print("\n📊 Creating train/test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y_encoded
)
print(f"   Training samples: {len(X_train):,}")
print(f"   Test samples: {len(X_test):,}")


# ═══════════════════════════════════════════════════════════════
# 4. MODEL DEFINITION
# ═══════════════════════════════════════════════════════════════

print("\n🤖 Building Calibrated Ensemble Model...")

# ── Base estimators ───────────────────────────────────────────
rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=25,
    min_samples_split=3,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=RANDOM_STATE,
    n_jobs=-1
)

xgb_model = xgb.XGBClassifier(
    n_estimators=400,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_alpha=0.1,
    reg_lambda=1.0,
    eval_metric='mlogloss',
    random_state=RANDOM_STATE,
    verbosity=0,
    n_jobs=-1
)

lgb_model = lgb.LGBMClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=8,
    num_leaves=63,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=RANDOM_STATE,
    verbose=-1,
    n_jobs=-1
)

# ── C3: Wrap each base estimator with probability calibration ─
# isotonic for RF (more data), sigmoid (Platt) for boosters
print("   ↳ Wrapping estimators with CalibratedClassifierCV...")
rf_cal  = CalibratedClassifierCV(rf,        cv=5, method='isotonic')
xgb_cal = CalibratedClassifierCV(xgb_model, cv=5, method='sigmoid')
lgb_cal = CalibratedClassifierCV(lgb_model, cv=5, method='sigmoid')

ensemble = VotingClassifier(
    estimators=[
        ('rf',  rf_cal),
        ('xgb', xgb_cal),
        ('lgb', lgb_cal),
    ],
    voting='soft',
)

# ── C2: No StandardScaler — trees don't benefit from scaling ─
pipeline = Pipeline([
    ('model', ensemble)
])
print("   ✅ Pipeline: [CalibratedEnsemble] (no scaler)")


# ═══════════════════════════════════════════════════════════════
# 5. CROSS-VALIDATION
# ═══════════════════════════════════════════════════════════════

print("\n📈 Running Stratified 5-Fold Cross-Validation...")
skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=skf, scoring='accuracy', n_jobs=-1)

print(f"\n   Cross-Validation Results:")
for i, score in enumerate(cv_scores, 1):
    print(f"     Fold {i}: {score:.4f}")
print(f"   ────────────────────────")
print(f"   Mean Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")


# ═══════════════════════════════════════════════════════════════
# 6. FINAL TRAINING ON FULL TRAIN SET
# ═══════════════════════════════════════════════════════════════

print("\n🚀 Training final model on full training set...")
pipeline.fit(X_train, y_train)
print("   ✅ Training complete")


# ═══════════════════════════════════════════════════════════════
# 7. EVALUATION ON TEST SET
# ═══════════════════════════════════════════════════════════════

print("\n📋 Evaluating on test set...")
y_pred = pipeline.predict(X_test)

test_accuracy = accuracy_score(y_test, y_pred)
test_f1_macro = f1_score(y_test, y_pred, average='macro')
test_f1_weighted = f1_score(y_test, y_pred, average='weighted')
test_precision = precision_score(y_test, y_pred, average='weighted')
test_recall = recall_score(y_test, y_pred, average='weighted')

print(f"\n   ┌─────────────────────────────────┐")
print(f"   │  TEST SET RESULTS               │")
print(f"   ├─────────────────────────────────┤")
print(f"   │  Accuracy:    {test_accuracy:.4f}            │")
print(f"   │  F1 (Macro):  {test_f1_macro:.4f}            │")
print(f"   │  F1 (Wt):     {test_f1_weighted:.4f}            │")
print(f"   │  Precision:   {test_precision:.4f}            │")
print(f"   │  Recall:      {test_recall:.4f}            │")
print(f"   └─────────────────────────────────┘")


# ═══════════════════════════════════════════════════════════════
# 8. CLASSIFICATION REPORT
# ═══════════════════════════════════════════════════════════════

class_report = classification_report(
    y_test, y_pred,
    target_names=le.classes_,
    digits=4
)
print(f"\n📋 Classification Report:\n")
print(class_report)

# Save classification report
report_path = os.path.join(REPORT_DIR, "classification_report.txt")
with open(report_path, 'w') as f:
    f.write("CROP RECOMMENDATION MODEL — CLASSIFICATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Test Accuracy:       {test_accuracy:.4f}\n")
    f.write(f"F1 Score (Macro):    {test_f1_macro:.4f}\n")
    f.write(f"F1 Score (Weighted): {test_f1_weighted:.4f}\n")
    f.write(f"Precision (Weighted):{test_precision:.4f}\n")
    f.write(f"Recall (Weighted):   {test_recall:.4f}\n")
    f.write(f"\nCross-Validation:    {cv_scores.mean():.4f} ± {cv_scores.std():.4f}\n")
    f.write(f"\n{'=' * 60}\n\n")
    f.write(class_report)
print(f"   ✅ Report saved: {report_path}")


# ═══════════════════════════════════════════════════════════════
# 9. CONFUSION MATRIX
# ═══════════════════════════════════════════════════════════════

print("\n📊 Generating confusion matrix...")
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(16, 14))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=le.classes_,
    yticklabels=le.classes_,
    ax=ax,
    linewidths=0.5,
    square=True
)
ax.set_title('Crop Recommendation — Confusion Matrix', fontsize=16, fontweight='bold')
ax.set_xlabel('Predicted Crop', fontsize=12)
ax.set_ylabel('Actual Crop', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()

cm_path = os.path.join(REPORT_DIR, "confusion_matrix.png")
fig.savefig(cm_path, dpi=150)
plt.close(fig)
print(f"   ✅ Confusion matrix saved: {cm_path}")


# ═══════════════════════════════════════════════════════════════
# 10. FEATURE IMPORTANCE
# ═══════════════════════════════════════════════════════════════

print("\n📊 Generating feature importance plot...")

# Extract feature importance from the inner RF inside CalibratedClassifierCV
# CalibratedClassifierCV stores one fitted estimator per fold in calibrated_classifiers_
calibrated_rf = pipeline.named_steps['model'].estimators_[0]   # CalibratedClassifierCV for RF
importances = np.mean([
    clf.estimator.feature_importances_
    for clf in calibrated_rf.calibrated_classifiers_
], axis=0)

feat_imp_df = pd.DataFrame({
    'Feature': FEATURE_COLUMNS,
    'Importance': importances
}).sort_values('Importance', ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(feat_imp_df['Feature'], feat_imp_df['Importance'], color='steelblue', edgecolor='navy')
ax.set_title('Crop Recommendation — Feature Importance (RandomForest)', fontsize=14, fontweight='bold')
ax.set_xlabel('Importance', fontsize=12)
ax.set_ylabel('Feature', fontsize=12)
plt.tight_layout()

fi_path = os.path.join(REPORT_DIR, "feature_importance.png")
fig.savefig(fi_path, dpi=150)
plt.close(fig)
print(f"   ✅ Feature importance saved: {fi_path}")


# ═══════════════════════════════════════════════════════════════
# 11. SAVE MODELS
# ═══════════════════════════════════════════════════════════════

print("\n💾 Saving models...")

model_path = os.path.join(MODEL_DIR, "improved_crop_model.pkl")
encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")

joblib.dump(pipeline, model_path)
joblib.dump(le, encoder_path)

print(f"   ✅ Model saved: {model_path}")
print(f"   ✅ Encoder saved: {encoder_path}")

# Save training metadata
metadata = {
    "model_type": "VotingClassifier (RF + XGB + LGBM) — Calibrated",
    "voting": "soft",
    "calibration": {"rf": "isotonic", "xgb": "sigmoid", "lgb": "sigmoid"},
    "scaler": None,
    "features": FEATURE_COLUMNS,
    "n_classes": len(le.classes_),
    "classes": le.classes_.tolist(),
    "test_accuracy": round(test_accuracy, 4),
    "cv_mean_accuracy": round(cv_scores.mean(), 4),
    "cv_std": round(cv_scores.std(), 4),
    "f1_macro": round(test_f1_macro, 4),
    "train_samples": len(X_train),
    "test_samples": len(X_test),
    "phase": "2",
}

meta_path = os.path.join(MODEL_DIR, "model_metadata.json")
with open(meta_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✅ Metadata saved: {meta_path}")


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  ✅ CROP RECOMMENDATION MODEL — TRAINING COMPLETE")
print("=" * 60)
print(f"  Test Accuracy:    {test_accuracy:.4f}")
print(f"  CV Accuracy:      {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"  F1 (Macro):       {test_f1_macro:.4f}")
print(f"  Classes:          {len(le.classes_)}")
print(f"  Features:         {len(FEATURE_COLUMNS)}")
print("=" * 60)
print("  📁 Files saved:")
print(f"     Model:             {model_path}")
print(f"     Label Encoder:     {encoder_path}")
print(f"     Metadata:          {meta_path}")
print(f"     Classification:    {report_path}")
print(f"     Confusion Matrix:  {cm_path}")
print(f"     Feature Importance:{fi_path}")
print("=" * 60)