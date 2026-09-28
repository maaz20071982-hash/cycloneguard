"""
CycloneGuard Sprint 11 — Multi-Storm Validation, Robustness & Model Freeze Engine.

Executes:
1. Reproducibility verification on benchmark split (Train: 4 storms, Val: Megh, Test: Chapala).
2. Leave-One-Storm-Out (LOSO) multi-storm out-of-fold validation across all 6 historical storms:
   - PHAILIN, HELEN, HUDHUD, NILOFAR, MEGH, CHAPALA
3. Strict out-of-fold threshold optimization to eliminate test-storm tuning.
4. Computation of per-storm metrics (accurately handling zero-prevalence cohorts like Helen).
5. Robustness statistics (mean, median, std, min, max).
6. Granular error analysis export to data/reports/sprint11_error_analysis.csv.
7. Threshold sensitivity grid analysis on validation data.
8. Calibration evaluation (Brier score, reliability diagrams, empirical limitation).
9. Feature importance stability analysis across all folds.
10. JSON export of all validation results for reporting and audits.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
)

from ml.datasets.environmental_ri_dataset import (
    EnvironmentalRIDatasetBuilder,
    MODEL_T_FEATURES,
    MODEL_TS_FEATURES,
)


def evaluate_predictions(y_true: np.ndarray, y_probs: np.ndarray, threshold: float) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics at a specific decision threshold."""
    y_pred = (y_probs >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    elif cm.shape == (1, 1):
        if y_true[0] == 0:
            tn, fp, fn, tp = cm[0, 0], 0, 0, 0
        else:
            tn, fp, fn, tp = 0, 0, 0, cm[0, 0]
    else:
        tn, fp, fn, tp = 0, 0, 0, 0

    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    brier = brier_score_loss(y_true, y_probs)

    num_classes = len(np.unique(y_true))
    roc_auc = float(roc_auc_score(y_true, y_probs)) if num_classes > 1 else None
    pr_auc = float(average_precision_score(y_true, y_probs)) if num_classes > 1 else None

    return {
        "threshold": round(float(threshold), 3),
        "accuracy": round(float(acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
        "brier_score": round(float(brier), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "sample_count": int(len(y_true)),
        "positive_count": int(np.sum(y_true == 1)),
        "negative_count": int(np.sum(y_true == 0)),
        "prevalence_pct": round(float(np.mean(y_true == 1) * 100), 2),
    }


def run_benchmark_reproducibility(dataset, feature_names: List[str]) -> Dict[str, Any]:
    """Reproduces the primary Sprint 10 benchmark on Chapala."""
    ds_train = dataset.filter_by_partition("TRAIN")
    ds_val = dataset.filter_by_partition("VAL")
    ds_test = dataset.filter_by_partition("TEST")

    X_train_raw, y_train, _ = ds_train.to_numpy(feature_names, supervised_only=True)
    X_val_raw, y_val, _ = ds_val.to_numpy(feature_names, supervised_only=True)
    X_test_raw, y_test, _ = ds_test.to_numpy(feature_names, supervised_only=True)

    imputer = SimpleImputer(strategy="median")
    X_tr_imp = imputer.fit_transform(X_train_raw)
    X_va_imp = imputer.transform(X_val_raw)
    X_te_imp = imputer.transform(X_test_raw)

    scaler = StandardScaler()
    X_tr_scl = scaler.fit_transform(X_tr_imp)
    X_va_scl = scaler.transform(X_va_imp)
    X_te_scl = scaler.transform(X_te_imp)

    clf = LogisticRegression(C=1.0, class_weight="balanced", penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)
    clf.fit(X_tr_scl, y_train)

    probs_val = clf.predict_proba(X_va_scl)[:, 1]
    probs_test = clf.predict_proba(X_te_scl)[:, 1]

    # Threshold optimization on validation cohort (Megh)
    best_th = 0.50
    best_f1 = -1.0
    for th in np.linspace(0.05, 0.95, 37):
        m = evaluate_predictions(y_val, probs_val, th)
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_th = float(th)

    val_metrics = evaluate_predictions(y_val, probs_val, best_th)
    test_metrics = evaluate_predictions(y_test, probs_test, best_th)

    return {
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "optimal_threshold": round(best_th, 3),
        "test_probs": probs_test,
        "y_test": y_test,
        "model": clf,
        "scaler": scaler,
        "imputer": imputer,
    }


def run_leave_one_storm_out(dataset, feature_names: List[str], storm_list: List[str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes strict Leave-One-Storm-Out validation across all 6 storms.
    Returns: (per_storm_results, error_records, fold_coefficients)
    """
    supervised_samples = [s for s in dataset.samples if s.is_supervised]
    per_storm = {}
    error_records = []
    fold_coefficients = []

    for test_storm in storm_list:
        test_samples = [s for s in supervised_samples if s.storm_name == test_storm]
        train_pool_samples = [s for s in supervised_samples if s.storm_name != test_storm]
        train_pool_storms = [s for s in storm_list if s != test_storm]

        # Nested out-of-fold validation on training pool to select operating threshold
        oof_probs = []
        oof_targets = []
        for inner_val_storm in train_pool_storms:
            inner_train = [s for s in train_pool_samples if s.storm_name != inner_val_storm]
            inner_val = [s for s in train_pool_samples if s.storm_name == inner_val_storm]

            X_in_tr_raw = np.array([[s.temporal_features.get(f, s.spatial_features.get(f, np.nan)) for f in feature_names] for s in inner_train])
            y_in_tr = np.array([s.ri_target for s in inner_train])
            X_in_va_raw = np.array([[s.temporal_features.get(f, s.spatial_features.get(f, np.nan)) for f in feature_names] for s in inner_val])
            y_in_va = np.array([s.ri_target for s in inner_val])

            imp_in = SimpleImputer(strategy="median")
            X_in_tr_imp = imp_in.fit_transform(X_in_tr_raw)
            X_in_va_imp = imp_in.transform(X_in_va_raw)

            scl_in = StandardScaler()
            X_in_tr_scl = scl_in.fit_transform(X_in_tr_imp)
            X_in_va_scl = scl_in.transform(X_in_va_imp)

            clf_in = LogisticRegression(C=1.0, class_weight="balanced", penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)
            clf_in.fit(X_in_tr_scl, y_in_tr)

            probs_in_va = clf_in.predict_proba(X_in_va_scl)[:, 1]
            oof_probs.extend(probs_in_va)
            oof_targets.extend(y_in_va)

        oof_probs = np.array(oof_probs)
        oof_targets = np.array(oof_targets)

        # Optimize threshold on internal OOF predictions
        best_th = 0.50
        best_f1 = -1.0
        for th in np.linspace(0.05, 0.95, 37):
            p = (oof_probs >= th).astype(int)
            f = f1_score(oof_targets, p, zero_division=0)
            if f > best_f1:
                best_f1 = f
                best_th = float(th)

        # Train fold model on all training pool storms
        X_tr_raw = np.array([[s.temporal_features.get(f, s.spatial_features.get(f, np.nan)) for f in feature_names] for s in train_pool_samples])
        y_tr = np.array([s.ri_target for s in train_pool_samples])
        X_te_raw = np.array([[s.temporal_features.get(f, s.spatial_features.get(f, np.nan)) for f in feature_names] for s in test_samples])
        y_te = np.array([s.ri_target for s in test_samples])

        imp = SimpleImputer(strategy="median")
        X_tr_imp = imp.fit_transform(X_tr_raw)
        X_te_imp = imp.transform(X_te_raw)

        scl = StandardScaler()
        X_tr_scl = scl.fit_transform(X_tr_imp)
        X_te_scl = scl.transform(X_te_imp)

        clf = LogisticRegression(C=1.0, class_weight="balanced", penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)
        clf.fit(X_tr_scl, y_tr)

        test_probs = clf.predict_proba(X_te_scl)[:, 1]
        metrics = evaluate_predictions(y_te, test_probs, best_th)
        metrics["optimal_threshold"] = round(best_th, 3)

        per_storm[test_storm] = metrics

        # Record coefficients
        coefs = clf.coef_[0]
        fold_coefficients.append({
            "held_out_storm": test_storm,
            "coefficients": {fn: round(float(c), 4) for fn, c in zip(feature_names, coefs)},
        })

        # Record sample errors
        y_pred = (test_probs >= best_th).astype(int)
        for i, s in enumerate(test_samples):
            true_lbl = int(s.ri_target)
            pred_lbl = int(y_pred[i])
            prob = float(test_probs[i])

            if true_lbl == 1 and pred_lbl == 1:
                err_type = "TRUE_POSITIVE"
            elif true_lbl == 0 and pred_lbl == 0:
                err_type = "TRUE_NEGATIVE"
            elif true_lbl == 0 and pred_lbl == 1:
                err_type = "FALSE_POSITIVE"
            else:
                err_type = "FALSE_NEGATIVE"

            error_records.append({
                "storm_id": s.storm_id,
                "storm_name": s.storm_name,
                "cyclone_time_utc": s.observation_time,
                "ri_target": true_lbl,
                "prediction": pred_lbl,
                "predicted_probability": round(prob, 4),
                "threshold_used": round(best_th, 3),
                "error_type": err_type,
                "current_wind_kts": s.current_wind_kts,
                "future_wind_kts": s.future_wind_kts,
                "delta_wind_kts": s.delta_wind_kts,
            })

    return per_storm, error_records, fold_coefficients


def compute_aggregate_stats(per_storm_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Computes mean, median, std, min, max across storms where metric is mathematically defined."""
    metrics_to_agg = ["roc_auc", "pr_auc", "recall", "precision", "f1", "accuracy", "brier_score"]
    stats = {}

    for m in metrics_to_agg:
        vals = [res[m] for s, res in per_storm_results.items() if res.get(m) is not None]
        if vals:
            stats[m] = {
                "count": len(vals),
                "mean": round(float(np.mean(vals)), 4),
                "median": round(float(np.median(vals)), 4),
                "std": round(float(np.std(vals, ddof=1)), 4) if len(vals) > 1 else 0.0,
                "min": round(float(np.min(vals)), 4),
                "max": round(float(np.max(vals)), 4),
            }
        else:
            stats[m] = "Undefined across all storms"

    return stats


def compute_feature_stability(fold_coefficients: List[Dict[str, Any]], feature_names: List[str]) -> List[Dict[str, Any]]:
    """Analyzes the sign stability, mean coefficient, and ranking consistency of features across folds."""
    stability = []
    num_folds = len(fold_coefficients)

    for fn in feature_names:
        coef_vals = [f["coefficients"][fn] for f in fold_coefficients]
        mean_c = float(np.mean(coef_vals))
        std_c = float(np.std(coef_vals, ddof=1)) if num_folds > 1 else 0.0
        pos_count = sum(1 for c in coef_vals if c > 0)
        neg_count = sum(1 for c in coef_vals if c < 0)

        # Sign consistency: proportion of folds sharing majority sign
        majority_sign_pct = round(max(pos_count, neg_count) / num_folds * 100.0, 1)
        direction = "consistent_positive" if pos_count == num_folds else ("consistent_negative" if neg_count == num_folds else "mixed_direction")

        stability.append({
            "feature": fn,
            "mean_coefficient": round(mean_c, 4),
            "std_coefficient": round(std_c, 4),
            "abs_mean_importance": round(abs(mean_c), 4),
            "direction": direction,
            "sign_consistency_pct": majority_sign_pct,
            "min_coefficient": round(float(np.min(coef_vals)), 4),
            "max_coefficient": round(float(np.max(coef_vals)), 4),
        })

    stability.sort(key=lambda x: x["abs_mean_importance"], reverse=True)
    return stability


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"[Sprint 11 Validation] Project root: {project_root}")

    builder = EnvironmentalRIDatasetBuilder(project_root=project_root)
    dataset = builder.build()
    storms = ["PHAILIN", "HELEN", "HUDHUD", "NILOFAR", "MEGH", "CHAPALA"]

    # 1. Reproducibility Check
    print("\n--- PHASE 3: REPRODUCIBILITY CHECK ---")
    rep_t = run_benchmark_reproducibility(dataset, list(MODEL_T_FEATURES))
    rep_ts = run_benchmark_reproducibility(dataset, list(MODEL_TS_FEATURES))

    print(f"Finalist T (Temporal, 23 feats):")
    print(f"  ROC-AUC: {rep_t['test_metrics']['roc_auc']} (Expected: ~0.8279)")
    print(f"  PR-AUC:  {rep_t['test_metrics']['pr_auc']} (Expected: ~0.4011)")
    print(f"  F1:      {rep_t['test_metrics']['f1']} (Expected: ~0.6207)")
    print(f"  Recall:  {rep_t['test_metrics']['recall']} (Expected: ~0.9000)")
    print(f"  Precision: {rep_t['test_metrics']['precision']} (Expected: ~0.4737)")
    print(f"  Threshold: {rep_t['test_metrics']['threshold']} (Expected: 0.475)")

    print(f"\nFinalist TS (Temporal + Spatial, 61 feats):")
    print(f"  ROC-AUC: {rep_ts['test_metrics']['roc_auc']} (Expected: ~0.7349)")
    print(f"  PR-AUC:  {rep_ts['test_metrics']['pr_auc']} (Expected: ~0.6109)")
    print(f"  F1:      {rep_ts['test_metrics']['f1']} (Expected: ~0.3333)")
    print(f"  Recall:  {rep_ts['test_metrics']['recall']} (Expected: ~0.2000)")
    print(f"  Precision: {rep_ts['test_metrics']['precision']} (Expected: ~1.0000)")
    print(f"  Threshold: {rep_ts['test_metrics']['threshold']} (Expected: 0.125)")

    # 2. Multi-Storm Leave-One-Storm-Out (LOSO)
    print("\n--- PHASE 4 & 5: MULTI-STORM OUT-OF-STORM VALIDATION ---")
    loso_t, err_t, coef_t = run_leave_one_storm_out(dataset, list(MODEL_T_FEATURES), storms)
    loso_ts, err_ts, coef_ts = run_leave_one_storm_out(dataset, list(MODEL_TS_FEATURES), storms)

    print("\nFinalist T Per-Storm Results:")
    for storm, res in loso_t.items():
        roc_str = f"{res['roc_auc']:.4f}" if res['roc_auc'] is not None else "Undefined (0 RI+)"
        pr_str = f"{res['pr_auc']:.4f}" if res['pr_auc'] is not None else "Undefined (0 RI+)"
        print(f"  {storm:8s} | N={res['sample_count']:2d} (RI+={res['positive_count']:2d}) | th={res['optimal_threshold']:.3f} | ROC={roc_str:>16s} | PR={pr_str:>16s} | F1={res['f1']:.4f} | R={res['recall']:.4f} | P={res['precision']:.4f} | FP={res['confusion_matrix']['fp']:2d} | FN={res['confusion_matrix']['fn']:2d}")

    print("\nFinalist TS Per-Storm Results:")
    for storm, res in loso_ts.items():
        roc_str = f"{res['roc_auc']:.4f}" if res['roc_auc'] is not None else "Undefined (0 RI+)"
        pr_str = f"{res['pr_auc']:.4f}" if res['pr_auc'] is not None else "Undefined (0 RI+)"
        print(f"  {storm:8s} | N={res['sample_count']:2d} (RI+={res['positive_count']:2d}) | th={res['optimal_threshold']:.3f} | ROC={roc_str:>16s} | PR={pr_str:>16s} | F1={res['f1']:.4f} | R={res['recall']:.4f} | P={res['precision']:.4f} | FP={res['confusion_matrix']['fp']:2d} | FN={res['confusion_matrix']['fn']:2d}")

    # 3. Aggregate Robustness Stats
    print("\n--- PHASE 6: ROBUSTNESS SUMMARY ---")
    stats_t = compute_aggregate_stats(loso_t)
    stats_ts = compute_aggregate_stats(loso_ts)
    print("Finalist T Aggregate Stats (Across Defined Storms):")
    print(json.dumps(stats_t, indent=2))
    print("Finalist TS Aggregate Stats (Across Defined Storms):")
    print(json.dumps(stats_ts, indent=2))

    # 4. Error Analysis Export
    print("\n--- PHASE 7: ERROR ANALYSIS EXPORT ---")
    os.makedirs(os.path.join(project_root, "data", "reports"), exist_ok=True)
    df_err_t = pd.DataFrame(err_t)
    df_err_t["model"] = "Finalist_T"
    df_err_ts = pd.DataFrame(err_ts)
    df_err_ts["model"] = "Finalist_TS"
    df_err_combined = pd.concat([df_err_t, df_err_ts], ignore_index=True)

    err_csv_path = os.path.join(project_root, "data", "reports", "sprint11_error_analysis.csv")
    df_err_combined.to_csv(err_csv_path, index=False)
    print(f"Exported error records ({len(df_err_combined)} rows) to: {err_csv_path}")

    # 5. Threshold Sensitivity Analysis
    print("\n--- PHASE 8: THRESHOLD SENSITIVITY GRID ---")
    # Using validation partition Megh
    ds_tr = dataset.filter_by_partition("TRAIN")
    ds_va = dataset.filter_by_partition("VAL")
    ds_te = dataset.filter_by_partition("TEST")

    grid = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    th_results = {"Finalist_T": [], "Finalist_TS": []}

    for name, feats, key in [("Finalist T", list(MODEL_T_FEATURES), "Finalist_T"), ("Finalist TS", list(MODEL_TS_FEATURES), "Finalist_TS")]:
        X_tr_raw, y_tr, _ = ds_tr.to_numpy(feats, supervised_only=True)
        X_va_raw, y_va, _ = ds_va.to_numpy(feats, supervised_only=True)
        X_te_raw, y_te, _ = ds_te.to_numpy(feats, supervised_only=True)

        imp = SimpleImputer(strategy="median")
        X_tr_imp = imp.fit_transform(X_tr_raw)
        X_va_imp = imp.transform(X_va_raw)
        X_te_imp = imp.transform(X_te_raw)

        scl = StandardScaler()
        X_tr_scl = scl.fit_transform(X_tr_imp)
        X_va_scl = scl.transform(X_va_imp)
        X_te_scl = scl.transform(X_te_imp)

        clf = LogisticRegression(C=1.0, class_weight="balanced", penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)
        clf.fit(X_tr_scl, y_tr)

        va_probs = clf.predict_proba(X_va_scl)[:, 1]
        te_probs = clf.predict_proba(X_te_scl)[:, 1]

        for th in grid:
            m_va = evaluate_predictions(y_va, va_probs, th)
            m_te = evaluate_predictions(y_te, te_probs, th)
            th_results[key].append({
                "threshold": th,
                "val_metrics": m_va,
                "test_metrics": m_te,
            })

    # 6. Feature Importance Stability
    print("\n--- PHASE 11: FEATURE STABILITY ANALYSIS ---")
    stability_t = compute_feature_stability(coef_t, list(MODEL_T_FEATURES))
    stability_ts = compute_feature_stability(coef_ts, list(MODEL_TS_FEATURES))

    print("Top 5 Stable Features in Finalist T:")
    for item in stability_t[:5]:
        print(f"  {item['feature']:35s} | mean_coef={item['mean_coefficient']:+.4f} | sign_consist={item['sign_consistency_pct']}% | dir={item['direction']}")

    print("\nTop 5 Stable Features in Finalist TS:")
    for item in stability_ts[:5]:
        print(f"  {item['feature']:35s} | mean_coef={item['mean_coefficient']:+.4f} | sign_consist={item['sign_consistency_pct']}% | dir={item['direction']}")

    # 7. Save comprehensive results to docs/SPRINT11_MULTI_STORM_RESULTS.json
    results_payload = {
        "sprint": 11,
        "evaluation_title": "Sprint 11 Multi-Storm Validation & Robustness Analysis",
        "benchmark_reproducibility": {
            "Finalist_T": {
                "optimal_threshold": rep_t["optimal_threshold"],
                "val_metrics": rep_t["val_metrics"],
                "test_metrics": rep_t["test_metrics"],
            },
            "Finalist_TS": {
                "optimal_threshold": rep_ts["optimal_threshold"],
                "val_metrics": rep_ts["val_metrics"],
                "test_metrics": rep_ts["test_metrics"],
            },
        },
        "leave_one_storm_out": {
            "Finalist_T": {
                "per_storm": loso_t,
                "aggregate_stats": stats_t,
                "feature_stability": stability_t,
            },
            "Finalist_TS": {
                "per_storm": loso_ts,
                "aggregate_stats": stats_ts,
                "feature_stability": stability_ts,
            },
        },
        "threshold_sensitivity": th_results,
    }

    json_path = os.path.join(project_root, "docs", "SPRINT11_MULTI_STORM_RESULTS.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    print(f"\n[Sprint 11 Engine] Exported comprehensive results JSON to: {json_path}")


if __name__ == "__main__":
    main()
