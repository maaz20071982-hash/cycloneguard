"""
CycloneGuard Sprint 10 — Environmental Baseline & Multimodal Ablation Pipeline.

Trains, ablates, and evaluates:
1. MODEL T: Temporal Kinematic Baseline (23 features)
2. MODEL TS: Temporal + Spatial Multimodal Baseline (61 features)
3. MODEL E: Environmental Baseline (13 features)
4. MODEL TE: Temporal + Environmental Baseline (36 features)
5. MODEL STE: Full Multimodal Fusion (74 features)

Feature Group Ablations:
- E1: SST only (3 features)
- E2: Deep-layer Vertical Wind Shear only (6 features)
- E3: SST + Wind Shear (9 features)
- T + E1: Temporal + SST (26 features)
- T + E2: Temporal + Shear (29 features)
- T + E3: Temporal + SST + Shear (32 features)

Protocol:
- Imputer & Scaler fitted strictly on TRAIN (Phailin, Helen, Hudhud, Nilofar).
- Decision threshold tuned strictly on VAL (Megh) to maximize F1.
- Untouched TEST storm (Chapala, N=53, 10 RI+) evaluated once.
- Artifacts exported to models/ri/v3_environmental/ and models/ri/v3_combined/.
"""

import json
import os
import pickle
from datetime import datetime, timezone
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
    MODEL_E_FEATURES,
    MODEL_TE_FEATURES,
    MODEL_STE_FEATURES,
    E1_SST_FEATURE_NAMES,
    E2_SHEAR_FEATURE_NAMES,
    E3_SST_SHEAR_FEATURE_NAMES,
)


def evaluate_model(y_true: np.ndarray, y_probs: np.ndarray, threshold: float) -> Dict[str, Any]:
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
    roc_auc = float(roc_auc_score(y_true, y_probs)) if len(np.unique(y_true)) > 1 else None
    pr_auc = float(average_precision_score(y_true, y_probs)) if len(np.unique(y_true)) > 1 else None

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
        "prevalence_pct": round(float(np.mean(y_true == 1) * 100), 2),
    }


def optimize_threshold_on_validation(
    y_val: np.ndarray, y_probs_val: np.ndarray, num_steps: int = 37
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """Finds decision threshold maximizing F1 score strictly on validation partition."""
    thresholds = np.linspace(0.05, 0.95, num_steps)
    analysis = []
    best_th = 0.50
    best_f1 = -1.0

    for th in thresholds:
        metrics = evaluate_model(y_val, y_probs_val, th)
        analysis.append({
            "threshold": round(float(th), 3),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "accuracy": metrics["accuracy"],
        })
        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_th = float(th)

    return best_th, best_f1, analysis


class EnvironmentalPipelineTrainer:
    """Manages training, ablation, and evaluation across multimodal configurations."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.dataset_builder = EnvironmentalRIDatasetBuilder(project_root=project_root)
        self.dataset = self.dataset_builder.build()

    def train_and_evaluate_config(
        self,
        config_name: str,
        feature_names: List[str],
        c_reg: float = 1.0,
    ) -> Dict[str, Any]:
        """Trains logistic regression and evaluates on validation and untouched test storm."""
        print(f"\n=======================================================")
        print(f"Running Experiment: {config_name} ({len(feature_names)} features)")
        print(f"=======================================================")

        # Partitions
        ds_train = self.dataset.filter_by_partition("TRAIN")
        ds_val = self.dataset.filter_by_partition("VAL")
        ds_test = self.dataset.filter_by_partition("TEST")

        X_train_raw, y_train, _ = ds_train.to_numpy(feature_names, supervised_only=True)
        X_val_raw, y_val, _ = ds_val.to_numpy(feature_names, supervised_only=True)
        X_test_raw, y_test, meta_test = ds_test.to_numpy(feature_names, supervised_only=True)

        # 1. Fit Imputer strictly on TRAIN
        imputer = SimpleImputer(strategy="median")
        X_train_imp = imputer.fit_transform(X_train_raw)
        X_val_imp = imputer.transform(X_val_raw)
        X_test_imp = imputer.transform(X_test_raw)

        # 2. Fit Scaler strictly on TRAIN
        scaler = StandardScaler()
        X_train_scl = scaler.fit_transform(X_train_imp)
        X_val_scl = scaler.transform(X_val_imp)
        X_test_scl = scaler.transform(X_test_imp)

        # 3. Fit Model on TRAIN
        model = LogisticRegression(
            C=c_reg,
            class_weight="balanced",
            penalty="l2",
            solver="lbfgs",
            max_iter=1000,
            random_state=42,
        )
        model.fit(X_train_scl, y_train)

        # 4. Predict on VAL for Threshold Selection
        probs_val = model.predict_proba(X_val_scl)[:, 1]
        best_th, val_f1, th_curve = optimize_threshold_on_validation(y_val, probs_val)
        val_metrics = evaluate_model(y_val, probs_val, best_th)

        # 5. Evaluate on Untouched TEST Storm (Chapala)
        probs_test = model.predict_proba(X_test_scl)[:, 1]
        test_metrics_opt = evaluate_model(y_test, probs_test, best_th)
        test_metrics_default = evaluate_model(y_test, probs_test, 0.50)

        # 6. Extract Feature Importances (Standardized Logistic Coefficients)
        coefs = model.coef_[0]
        feature_importance = [
            {
                "feature": fn,
                "coefficient": round(float(coefs[i]), 4),
                "odds_ratio": round(float(np.exp(coefs[i])), 4),
                "abs_importance": round(float(abs(coefs[i])), 4),
                "direction": "positive_risk" if coefs[i] > 0 else "protective_negative",
            }
            for i, fn in enumerate(feature_names)
        ]
        feature_importance.sort(key=lambda x: x["abs_importance"], reverse=True)

        print(f"Validation F1 (Megh) at th={best_th:.3f}: {val_f1:.4f} (ROC-AUC={val_metrics['roc_auc']}, PR-AUC={val_metrics['pr_auc']})")
        print(f"Test (Chapala) Metrics at th={best_th:.3f}:")
        print(f"  ROC-AUC:   {test_metrics_opt['roc_auc']}")
        print(f"  PR-AUC:    {test_metrics_opt['pr_auc']}")
        print(f"  F1:        {test_metrics_opt['f1']}")
        print(f"  Precision: {test_metrics_opt['precision']}")
        print(f"  Recall:    {test_metrics_opt['recall']}")
        print(f"  Accuracy:  {test_metrics_opt['accuracy']}")
        print(f"  Brier:     {test_metrics_opt['brier_score']}")
        print(f"  Confusion: {test_metrics_opt['confusion_matrix']}")

        return {
            "config_name": config_name,
            "feature_count": len(feature_names),
            "feature_names": feature_names,
            "optimal_threshold": best_th,
            "validation_metrics": val_metrics,
            "test_metrics": test_metrics_opt,
            "test_metrics_default_threshold": test_metrics_default,
            "feature_importance": feature_importance,
            "sample_counts": {
                "train_samples": len(y_train),
                "val_samples": len(y_val),
                "test_samples": len(y_test),
                "test_positive_count": int(np.sum(y_test == 1)),
            },
            "_model": model,
            "_imputer": imputer,
            "_scaler": scaler,
            "_test_probs": probs_test.tolist(),
            "_test_y": y_test.tolist(),
        }

    def run_all_ablations(self) -> Dict[str, Any]:
        """Runs full ablation matrix across core models and environmental groups."""
        experiments = [
            ("Model T (Temporal)", list(MODEL_T_FEATURES)),
            ("Model TS (Temporal + Spatial)", list(MODEL_TS_FEATURES)),
            ("Model E (Environmental Only)", list(MODEL_E_FEATURES)),
            ("Model TE (Temporal + Environmental)", list(MODEL_TE_FEATURES)),
            ("Model STE (Full Multimodal Fusion)", list(MODEL_STE_FEATURES)),
            ("Group E1 (SST Only)", list(E1_SST_FEATURE_NAMES)),
            ("Group E2 (Shear Only)", list(E2_SHEAR_FEATURE_NAMES)),
            ("Group E3 (SST + Shear)", list(E3_SST_SHEAR_FEATURE_NAMES)),
            ("Model T + E1 (Temporal + SST)", list(MODEL_T_FEATURES) + list(E1_SST_FEATURE_NAMES)),
            ("Model T + E2 (Temporal + Shear)", list(MODEL_T_FEATURES) + list(E2_SHEAR_FEATURE_NAMES)),
            ("Model T + E3 (Temporal + SST + Shear)", list(MODEL_T_FEATURES) + list(E3_SST_SHEAR_FEATURE_NAMES)),
        ]

        results = {}
        for name, feats in experiments:
            res = self.train_and_evaluate_config(name, feats)
            results[name] = res

        return results

    def export_artifacts(self, results: Dict[str, Any]) -> None:
        """Saves trained models and comprehensive scientific results."""
        # 1. Export Model E artifacts
        model_e_dir = os.path.join(self.project_root, "models", "ri", "v3_environmental")
        os.makedirs(model_e_dir, exist_ok=True)
        res_e = results["Model E (Environmental Only)"]
        with open(os.path.join(model_e_dir, "model.pkl"), "wb") as f:
            pickle.dump(res_e["_model"], f)
        with open(os.path.join(model_e_dir, "imputer.pkl"), "wb") as f:
            pickle.dump(res_e["_imputer"], f)
        with open(os.path.join(model_e_dir, "scaler.pkl"), "wb") as f:
            pickle.dump(res_e["_scaler"], f)
        meta_e = {k: v for k, v in res_e.items() if not k.startswith("_")}
        meta_e["trained_at_utc"] = datetime.now(timezone.utc).isoformat()
        with open(os.path.join(model_e_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_e, f, indent=2)

        # 2. Export Model TE artifacts
        model_te_dir = os.path.join(self.project_root, "models", "ri", "v3_te")
        os.makedirs(model_te_dir, exist_ok=True)
        res_te = results["Model TE (Temporal + Environmental)"]
        with open(os.path.join(model_te_dir, "model.pkl"), "wb") as f:
            pickle.dump(res_te["_model"], f)
        with open(os.path.join(model_te_dir, "imputer.pkl"), "wb") as f:
            pickle.dump(res_te["_imputer"], f)
        with open(os.path.join(model_te_dir, "scaler.pkl"), "wb") as f:
            pickle.dump(res_te["_scaler"], f)
        meta_te = {k: v for k, v in res_te.items() if not k.startswith("_")}
        meta_te["trained_at_utc"] = datetime.now(timezone.utc).isoformat()
        with open(os.path.join(model_te_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_te, f, indent=2)

        # 3. Export Model STE artifacts
        model_ste_dir = os.path.join(self.project_root, "models", "ri", "v3_combined")
        os.makedirs(model_ste_dir, exist_ok=True)
        res_ste = results["Model STE (Full Multimodal Fusion)"]
        with open(os.path.join(model_ste_dir, "model.pkl"), "wb") as f:
            pickle.dump(res_ste["_model"], f)
        with open(os.path.join(model_ste_dir, "imputer.pkl"), "wb") as f:
            pickle.dump(res_ste["_imputer"], f)
        with open(os.path.join(model_ste_dir, "scaler.pkl"), "wb") as f:
            pickle.dump(res_ste["_scaler"], f)
        meta_ste = {k: v for k, v in res_ste.items() if not k.startswith("_")}
        meta_ste["trained_at_utc"] = datetime.now(timezone.utc).isoformat()
        with open(os.path.join(model_ste_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta_ste, f, indent=2)

        # 4. Export Complete Ablation Summary
        ablation_summary = {
            "sprint": 10,
            "evaluation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "test_storm": "CHAPALA",
            "val_storm": "MEGH",
            "train_storms": ["PHAILIN", "HELEN", "HUDHUD", "NILOFAR"],
            "experiments": {
                name: {k: v for k, v in data.items() if not k.startswith("_")}
                for name, data in results.items()
            }
        }
        summary_path = os.path.join(self.project_root, "docs", "SPRINT10_ABLATION_RESULTS.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(ablation_summary, f, indent=2)
        print(f"\n[EnvironmentalPipelineTrainer] Successfully exported models and ablation results to {summary_path}")


if __name__ == "__main__":
    trainer = EnvironmentalPipelineTrainer(project_root=os.getcwd())
    results = trainer.run_all_ablations()
    trainer.export_artifacts(results)
