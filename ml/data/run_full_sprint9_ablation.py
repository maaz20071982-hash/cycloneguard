import json
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
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
from ml.data.threshold_eval_helper import analyze_thresholds, evaluate_at_threshold

# 1. Load dataset
builder = SpatialRIDatasetBuilder()
dataset = builder.build()

train_ds = dataset.filter_by_partition("TRAIN")
val_ds = dataset.filter_by_partition("VAL")
test_ds = dataset.filter_by_partition("TEST")

# Feature sets
family_a = [f for f in SPATIAL_FEATURE_NAMES if f.startswith("irwin_") and not any(k in f for k in ["core", "ring", "outer", "azimuthal", "grad", "local_var", "entropy"])]
family_b = [f for f in SPATIAL_FEATURE_NAMES if any(k in f for k in ["core", "ring", "outer", "azimuthal"]) and f.startswith("irwin_")]
family_c = [f for f in SPATIAL_FEATURE_NAMES if any(k in f for k in ["grad", "local_variance", "entropy"])]
family_d = [f for f in SPATIAL_FEATURE_NAMES if "wv" in f or f == "has_irwvp"]
family_e = [f for f in SPATIAL_FEATURE_NAMES if "vschn" in f]

ablation_groups = {
    "Group A (IR Stats)": family_a,
    "Group B (IR Radial/Structural)": family_b,
    "Group C (IR + Water-Vapor)": family_a + family_b + family_d,
    "Group D (All Spatial)": list(SPATIAL_FEATURE_NAMES),
}

print(f"Family A count: {len(family_a)}")
print(f"Family B count: {len(family_b)}")
print(f"Family C count: {len(family_c)}")
print(f"Family D count: {len(family_d)}")
print(f"Family E count: {len(family_e)}")
print(f"Total Spatial features: {len(SPATIAL_FEATURE_NAMES)}")

# Labels
_, y_train, _ = train_ds.to_numpy(supervised_only=True)
_, y_val, _ = val_ds.to_numpy(supervised_only=True)
_, y_test, _ = test_ds.to_numpy(supervised_only=True)

# -----------------------------------------------------------------------------
# RUN SPATIAL FEATURE ABLATION (PHASE 11)
# -----------------------------------------------------------------------------
print("\n==================================================")
print("PHASE 11: SPATIAL FEATURE GROUP ABLATION")
print("==================================================")
group_results = {}
for g_name, g_feats in ablation_groups.items():
    X_tr, _, _ = train_ds.to_numpy(feature_names=g_feats, supervised_only=True)
    X_va, _, _ = val_ds.to_numpy(feature_names=g_feats, supervised_only=True)
    X_te, _, _ = test_ds.to_numpy(feature_names=g_feats, supervised_only=True)
    
    imp = SimpleImputer(strategy="median")
    X_tr_imp = imp.fit_transform(X_tr)
    X_va_imp = imp.transform(X_va)
    X_te_imp = imp.transform(X_te)
    
    scaler = CycloneFeatureScaler(method="standard")
    X_tr_s = scaler.fit_transform(X_tr_imp, g_feats)
    X_va_s = scaler.transform(X_va_imp)
    X_te_s = scaler.transform(X_te_imp)
    
    lr = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
    lr.fit(X_tr_s, y_train)
    
    va_prob = lr.predict_proba(X_va_s)[:, 1]
    te_prob = lr.predict_proba(X_te_s)[:, 1]
    
    opt_th, best_val_f1, _ = analyze_thresholds(y_val, va_prob)
    val_eval = evaluate_at_threshold(y_val, va_prob, opt_th)
    test_eval = evaluate_at_threshold(y_test, te_prob, opt_th)
    
    group_results[g_name] = {
        "n_features": len(g_feats),
        "val_roc_auc": round(float(roc_auc_score(y_val, va_prob)), 4),
        "val_pr_auc": round(float(average_precision_score(y_val, va_prob)), 4),
        "val_f1": val_eval["f1"],
        "opt_th": opt_th,
        "test_roc_auc": round(float(roc_auc_score(y_test, te_prob)), 4),
        "test_pr_auc": round(float(average_precision_score(y_test, te_prob)), 4),
        "test_f1": test_eval["f1"],
        "test_precision": test_eval["precision"],
        "test_recall": test_eval["recall"],
    }
    print(f"{g_name} ({len(g_feats)} feats): Val ROC={group_results[g_name]['val_roc_auc']}, PR={group_results[g_name]['val_pr_auc']} | Test ROC={group_results[g_name]['test_roc_auc']}, PR={group_results[g_name]['test_pr_auc']}, F1={test_eval['f1']} (th={opt_th})")

# -----------------------------------------------------------------------------
# PRIMARY COMPARISON: MODEL T vs MODEL S vs MODEL ST
# -----------------------------------------------------------------------------
print("\n==================================================")
print("PHASES 6, 7, 8, 9: PRIMARY MODEL ABLATION")
print("==================================================")

# 1. MODEL S: Spatial Baseline (All 38 Spatial features)
X_tr_s, _, _ = train_ds.to_numpy(feature_names=list(SPATIAL_FEATURE_NAMES), supervised_only=True)
X_va_s, _, _ = val_ds.to_numpy(feature_names=list(SPATIAL_FEATURE_NAMES), supervised_only=True)
X_te_s, _, _ = test_ds.to_numpy(feature_names=list(SPATIAL_FEATURE_NAMES), supervised_only=True)

imp_s = SimpleImputer(strategy="median")
X_tr_s_imp = imp_s.fit_transform(X_tr_s)
X_va_s_imp = imp_s.transform(X_va_s)
X_te_s_imp = imp_s.transform(X_te_s)

scaler_s = CycloneFeatureScaler(method="standard")
X_tr_s_sc = scaler_s.fit_transform(X_tr_s_imp, list(SPATIAL_FEATURE_NAMES))
X_va_s_sc = scaler_s.transform(X_va_s_imp)
X_te_s_sc = scaler_s.transform(X_te_s_imp)

model_s = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
model_s.fit(X_tr_s_sc, y_train)

val_probs_s = model_s.predict_proba(X_va_s_sc)[:, 1]
test_probs_s = model_s.predict_proba(X_te_s_sc)[:, 1]

# 2. MODEL T (Historical Train on 23 Temporal Features)
X_tr_t, _, _ = train_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
X_va_t, _, _ = val_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
X_te_t, _, _ = test_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)

scaler_t = CycloneFeatureScaler(method="standard")
X_tr_t_sc = scaler_t.fit_transform(X_tr_t, list(TEMPORAL_FEATURE_NAMES))
X_va_t_sc = scaler_t.transform(X_va_t)
X_te_t_sc = scaler_t.transform(X_te_t)

model_t = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
model_t.fit(X_tr_t_sc, y_train)

val_probs_t = model_t.predict_proba(X_va_t_sc)[:, 1]
test_probs_t = model_t.predict_proba(X_te_t_sc)[:, 1]

# Also load frozen Sprint 6 Model T for comparison
with open("models/ri/v1/model.pkl", "rb") as f:
    s6_model = pickle.load(f)
with open("models/ri/v1/scaler.json", "r") as f:
    s6_scaler_data = json.load(f)
s6_scaler = CycloneFeatureScaler()
s6_scaler.means = np.array(s6_scaler_data["means"])
s6_scaler.scales = np.array(s6_scaler_data["scales"])
s6_scaler.continuous_indices = s6_scaler_data["continuous_indices"]
s6_scaler.feature_names = s6_scaler_data["feature_names"]
s6_scaler.is_fitted = True

val_probs_t_s6 = s6_model.predict_proba(s6_scaler.transform(X_va_t))[:, 1]
test_probs_t_s6 = s6_model.predict_proba(s6_scaler.transform(X_te_t))[:, 1]

# 3. MODEL ST: Combined Temporal + Spatial (61 Features)
combined_features = list(TEMPORAL_FEATURE_NAMES) + list(SPATIAL_FEATURE_NAMES)
X_tr_st, _, _ = train_ds.to_numpy(supervised_only=True, include_temporal=True)
X_va_st, _, _ = val_ds.to_numpy(supervised_only=True, include_temporal=True)
X_te_st, _, _ = test_ds.to_numpy(supervised_only=True, include_temporal=True)

imp_st = SimpleImputer(strategy="median")
X_tr_st_imp = imp_st.fit_transform(X_tr_st)
X_va_st_imp = imp_st.transform(X_va_st)
X_te_st_imp = imp_st.transform(X_te_st)

scaler_st = CycloneFeatureScaler(method="standard")
X_tr_st_sc = scaler_st.fit_transform(X_tr_st_imp, combined_features)
X_va_st_sc = scaler_st.transform(X_va_st_imp)
X_te_st_sc = scaler_st.transform(X_te_st_imp)

model_st = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
model_st.fit(X_tr_st_sc, y_train)

val_probs_st = model_st.predict_proba(X_va_st_sc)[:, 1]
test_probs_st = model_st.predict_proba(X_te_st_sc)[:, 1]

# -----------------------------------------------------------------------------
# THRESHOLD SELECTION ON VALIDATION PARTITION (PHASE 13)
# -----------------------------------------------------------------------------
print("\n--- THRESHOLD OPTIMIZATION (VALIDATION STORM: MEGH) ---")
models_dict = {
    "Model T (Historical)": (val_probs_t, test_probs_t, 23),
    "Model T (Sprint 6 Frozen)": (val_probs_t_s6, test_probs_t_s6, 23),
    "Model S (Spatial Only)": (val_probs_s, test_probs_s, 38),
    "Model ST (Combined)": (val_probs_st, test_probs_st, 61),
}

final_comparison = {}
for m_name, (v_prob, te_prob, n_feats) in models_dict.items():
    opt_th, best_f1, th_grid = analyze_thresholds(y_val, v_prob)
    val_res = evaluate_at_threshold(y_val, v_prob, opt_th)
    test_res = evaluate_at_threshold(y_test, te_prob, opt_th)
    
    val_roc = float(roc_auc_score(y_val, v_prob))
    val_pr = float(average_precision_score(y_val, v_prob))
    test_roc = float(roc_auc_score(y_test, te_prob))
    test_pr = float(average_precision_score(y_test, te_prob))
    
    final_comparison[m_name] = {
        "n_features": n_feats,
        "opt_threshold": opt_th,
        "val_roc_auc": round(val_roc, 4),
        "val_pr_auc": round(val_pr, 4),
        "val_f1": val_res["f1"],
        "val_recall": val_res["recall"],
        "val_precision": val_res["precision"],
        "val_accuracy": val_res["accuracy"],
        "test_roc_auc": round(test_roc, 4),
        "test_pr_auc": round(test_pr, 4),
        "test_f1": test_res["f1"],
        "test_recall": test_res["recall"],
        "test_precision": test_res["precision"],
        "test_accuracy": test_res["accuracy"],
        "test_brier": test_res["brier"],
        "confusion_matrix": {"tn": test_res["tn"], "fp": test_res["fp"], "fn": test_res["fn"], "tp": test_res["tp"]}
    }
    print(f"\n{m_name}:")
    print(f"  Validation: ROC={val_roc:.4f}, PR={val_pr:.4f}, Best F1={val_res['f1']:.4f} at th={opt_th:.3f} (P={val_res['precision']:.4f}, R={val_res['recall']:.4f})")
    print(f"  Test Storm Chapala (Untouched): ROC={test_roc:.4f}, PR={test_pr:.4f}, F1={test_res['f1']:.4f}, P={test_res['precision']:.4f}, R={test_res['recall']:.4f}, Acc={test_res['accuracy']:.4f}, Brier={test_res['brier']:.4f}")
    print(f"  Test Confusion Matrix: TN={test_res['tn']}, FP={test_res['fp']}, FN={test_res['fn']}, TP={test_res['tp']}")

# -----------------------------------------------------------------------------
# FEATURE IMPORTANCE FOR MODEL S (PHASE 10)
# -----------------------------------------------------------------------------
print("\n==================================================")
print("PHASE 10: FEATURE IMPORTANCE FOR MODEL S")
print("==================================================")
coefs = model_s.coef_[0]
feat_importance = []
for name, coef in zip(SPATIAL_FEATURE_NAMES, coefs):
    feat_importance.append({
        "feature": name,
        "coef": round(float(coef), 4),
        "abs_coef": round(float(abs(coef)), 4),
        "direction": "positive (higher -> more RI)" if coef > 0 else "negative (lower -> more RI)"
    })
feat_importance_df = pd.DataFrame(feat_importance).sort_values("abs_coef", ascending=False)
print("Top 15 most predictive spatial features in Model S:")
print(feat_importance_df.head(15).to_string(index=False))

# -----------------------------------------------------------------------------
# CALIBRATION EVALUATION (PHASE 12)
# -----------------------------------------------------------------------------
print("\n==================================================")
print("PHASE 12: CALIBRATION EVALUATION ON VALIDATION SET")
print("==================================================")
# Check Brier score before calibration
brier_uncal = brier_score_loss(y_val, val_probs_s)
print(f"Model S Uncalibrated Validation Brier Score: {brier_uncal:.4f}")

# Attempt Platt Scaling (sigmoid) on validation set only
try:
    from sklearn.calibration import CalibratedClassifierCV
    # Note: Fitting CalibratedClassifierCV on training with cv='prefit' using validation data
    calibrator = CalibratedClassifierCV(estimator=model_s, method="sigmoid", cv="prefit")
    calibrator.fit(X_va_s_sc, y_val)
    val_probs_cal = calibrator.predict_proba(X_va_s_sc)[:, 1]
    brier_cal = brier_score_loss(y_val, val_probs_cal)
    print(f"Platt Scaled Validation Brier Score: {brier_cal:.4f}")
    print("Calibration technically converged, but validation set has only N=42 (6 positives).")
    print("Scientific assessment: Calibration is NOT statistically reliable due to small positive event count (N=6).")
except Exception as e:
    print(f"Calibration failed: {e}")
