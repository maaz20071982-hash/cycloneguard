import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

from ml.datasets.spatial_ri_dataset import (
    SpatialRIDatasetBuilder,
    SPATIAL_FEATURE_NAMES,
    TEMPORAL_FEATURE_NAMES,
)
from ml.features.scaler import CycloneFeatureScaler

# Load dataset
builder = SpatialRIDatasetBuilder()
dataset = builder.build()

train_ds = dataset.filter_by_partition("TRAIN")
val_ds = dataset.filter_by_partition("VAL")
test_ds = dataset.filter_by_partition("TEST")

print("=== PARTITION SUMMARY ===")
for name, ds in [("TRAIN", train_ds), ("VAL", val_ds), ("TEST", test_ds)]:
    sup = ds.get_supervised_samples()
    pos = sum(1 for s in sup if s.ri_target == 1)
    print(f"{name}: Total={len(ds)}, Supervised={len(sup)}, Positives={pos} ({pos/len(sup)*100:.1f}%)")

# Extract feature matrices
X_train_s, y_train, _ = train_ds.to_numpy(supervised_only=True)
X_val_s, y_val, _ = val_ds.to_numpy(supervised_only=True)
X_test_s, y_test, _ = test_ds.to_numpy(supervised_only=True)

X_train_t, _, _ = train_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
X_val_t, _, _ = val_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
X_test_t, _, _ = test_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)

X_train_st, _, _ = train_ds.to_numpy(supervised_only=True, include_temporal=True)
X_val_st, _, _ = val_ds.to_numpy(supervised_only=True, include_temporal=True)
X_test_st, _, _ = test_ds.to_numpy(supervised_only=True, include_temporal=True)

combined_names = list(TEMPORAL_FEATURE_NAMES) + list(SPATIAL_FEATURE_NAMES)

print(f"X_train_s: {X_train_s.shape}, X_train_t: {X_train_t.shape}, X_train_st: {X_train_st.shape}")

# Test Model S Candidates: Regularized Logistic Regression vs Gradient Boosting
print("\n--- MODEL S EXPLORATION (SPATIAL ONLY) ---")

# 1. Imputer + Scaler + Logistic Regression
# Imputer fit strictly on training set
imputer_s = SimpleImputer(strategy="median")
X_train_s_imp = imputer_s.fit_transform(X_train_s)
X_val_s_imp = imputer_s.transform(X_val_s)
X_test_s_imp = imputer_s.transform(X_test_s)

scaler_s = CycloneFeatureScaler(method="standard")
X_train_s_scaled = scaler_s.fit_transform(X_train_s_imp, list(SPATIAL_FEATURE_NAMES))
X_val_s_scaled = scaler_s.transform(X_val_s_imp)
X_test_s_scaled = scaler_s.transform(X_test_s_imp)

lr_s = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
lr_s.fit(X_train_s_scaled, y_train)

val_probs_lr_s = lr_s.predict_proba(X_val_s_scaled)[:, 1]
test_probs_lr_s = lr_s.predict_proba(X_test_s_scaled)[:, 1]

val_roc_s = roc_auc_score(y_val, val_probs_lr_s)
test_roc_s = roc_auc_score(y_test, test_probs_lr_s)
val_pr_s = average_precision_score(y_val, val_probs_lr_s)
test_pr_s = average_precision_score(y_test, test_probs_lr_s)

print(f"Logistic Regression S: Val ROC-AUC={val_roc_s:.4f}, PR-AUC={val_pr_s:.4f} | Test ROC-AUC={test_roc_s:.4f}, PR-AUC={test_pr_s:.4f}")

# 2. HistGradientBoostingClassifier (native NaN support)
hgb_s = HistGradientBoostingClassifier(max_iter=50, max_depth=3, class_weight="balanced", random_state=42)
hgb_s.fit(X_train_s, y_train)
val_probs_hgb_s = hgb_s.predict_proba(X_val_s)[:, 1]
test_probs_hgb_s = hgb_s.predict_proba(X_test_s)[:, 1]
print(f"HistGradientBoosting S: Val ROC-AUC={roc_auc_score(y_val, val_probs_hgb_s):.4f}, PR-AUC={average_precision_score(y_val, val_probs_hgb_s):.4f} | Test ROC-AUC={roc_auc_score(y_test, test_probs_hgb_s):.4f}, PR-AUC={average_precision_score(y_test, test_probs_hgb_s):.4f}")

# Check Sprint 6 Model T on Test Storm Chapala
print("\n--- MODEL T EXPLORATION (TEMPORAL ONLY) ---")
with open("models/ri/v1/model.pkl", "rb") as f:
    s6_model = pickle.load(f)
with open("models/ri/v1/scaler.json", "r") as f:
    s6_scaler_data = json.load(f)

# Scale X_test_t using Sprint 6 scaler parameters
s6_scaler = CycloneFeatureScaler()
s6_scaler.means = np.array(s6_scaler_data["means"])
s6_scaler.scales = np.array(s6_scaler_data["scales"])
s6_scaler.continuous_indices = s6_scaler_data["continuous_indices"]
s6_scaler.feature_names = s6_scaler_data["feature_names"]
s6_scaler.is_fitted = True

X_val_t_scaled_s6 = s6_scaler.transform(X_val_t)
X_test_t_scaled_s6 = s6_scaler.transform(X_test_t)

s6_val_probs = s6_model.predict_proba(X_val_t_scaled_s6)[:, 1]
s6_test_probs = s6_model.predict_proba(X_test_t_scaled_s6)[:, 1]

print(f"Sprint 6 Frozen Model T (Transfer): Val ROC-AUC={roc_auc_score(y_val, s6_val_probs):.4f}, PR-AUC={average_precision_score(y_val, s6_val_probs):.4f} | Test ROC-AUC={roc_auc_score(y_test, s6_test_probs):.4f}, PR-AUC={average_precision_score(y_test, s6_test_probs):.4f}")

# Train Model T on Historical Train Partition
scaler_t_hist = CycloneFeatureScaler(method="standard")
X_train_t_scaled = scaler_t_hist.fit_transform(X_train_t, list(TEMPORAL_FEATURE_NAMES))
X_val_t_scaled = scaler_t_hist.transform(X_val_t)
X_test_t_scaled = scaler_t_hist.transform(X_test_t)

lr_t_hist = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
lr_t_hist.fit(X_train_t_scaled, y_train)

val_probs_t_hist = lr_t_hist.predict_proba(X_val_t_scaled)[:, 1]
test_probs_t_hist = lr_t_hist.predict_proba(X_test_t_scaled)[:, 1]

print(f"Historical Train Model T: Val ROC-AUC={roc_auc_score(y_val, val_probs_t_hist):.4f}, PR-AUC={average_precision_score(y_val, val_probs_t_hist):.4f} | Test ROC-AUC={roc_auc_score(y_test, test_probs_t_hist):.4f}, PR-AUC={average_precision_score(y_test, test_probs_t_hist):.4f}")

# Train Combined Model ST (Temporal + Spatial)
print("\n--- MODEL ST EXPLORATION (COMBINED TEMPORAL + SPATIAL) ---")
imputer_st = SimpleImputer(strategy="median")
X_train_st_imp = imputer_st.fit_transform(X_train_st)
X_val_st_imp = imputer_st.transform(X_val_st)
X_test_st_imp = imputer_st.transform(X_test_st)

scaler_st = CycloneFeatureScaler(method="standard")
X_train_st_scaled = scaler_st.fit_transform(X_train_st_imp, combined_names)
X_val_st_scaled = scaler_st.transform(X_val_st_imp)
X_test_st_scaled = scaler_st.transform(X_test_st_imp)

lr_st = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
lr_st.fit(X_train_st_scaled, y_train)

val_probs_st = lr_st.predict_proba(X_val_st_scaled)[:, 1]
test_probs_st = lr_st.predict_proba(X_test_st_scaled)[:, 1]

print(f"Model ST (Logistic Regression): Val ROC-AUC={roc_auc_score(y_val, val_probs_st):.4f}, PR-AUC={average_precision_score(y_val, val_probs_st):.4f} | Test ROC-AUC={roc_auc_score(y_test, test_probs_st):.4f}, PR-AUC={average_precision_score(y_test, test_probs_st):.4f}")
