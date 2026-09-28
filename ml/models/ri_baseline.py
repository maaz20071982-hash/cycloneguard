"""
CycloneGuard Rapid Intensification Baseline Classifier (RI Model v1).

Implements:
1. Primary Baseline: Balanced Regularized Logistic Regression
2. Comparative Baseline: Balanced Compact Random Forest
3. Feature subset ablation (Model A vs Model B vs Model C)
4. Probability calibration on validation partition (Platt Scaling)
5. Decision threshold tuning optimizing operational F1 score
6. Comprehensive evaluation metrics (PR-AUC, ROC-AUC, Brier score, Confusion Matrix)
"""

from dataclasses import dataclass, asdict
import json
import os
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)

from ml.features.scaler import CycloneFeatureScaler


@dataclass
class RIMetrics:
    """Evaluation metrics container for RI models."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float]
    pr_auc: Optional[float]
    brier_score: float
    decision_threshold: float
    confusion_matrix: Dict[str, int]
    sample_count: int
    positive_count: int
    prevalence_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RITaskBaseline:
    """
    Supervised classifier for 24-hour Rapid Intensification prediction.
    """

    def __init__(
        self,
        model_type: str = "logistic_regression",
        feature_subset: str = "subset_b",
        random_state: int = 42,
    ):
        """
        Args:
            model_type: 'logistic_regression' or 'random_forest'
            feature_subset: 
                - 'subset_a': Current state kinematics only (13 features)
                - 'subset_b': Current state + temporal evolution (23 features)
                - 'subset_c': Current state + temporal + multi-source/morphology (67 features)
                - 'full': All 69 features in state vector
            random_state: Fixed random seed for exact reproducibility
        """
        self.model_type = model_type
        self.feature_subset = feature_subset
        self.random_state = random_state

        self.scaler: Optional[CycloneFeatureScaler] = None
        self.calibrator: Optional[CalibratedClassifierCV] = None
        self.selected_indices: List[int] = []
        self.selected_feature_names: List[str] = []
        self.decision_threshold: float = 0.50
        self.is_trained: bool = False
        self.is_calibrated: bool = False

        if model_type == "logistic_regression":
            self.raw_model = LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                C=1.0,
                random_state=random_state,
            )
        elif model_type == "random_forest":
            self.raw_model = RandomForestClassifier(
                n_estimators=50,
                max_depth=3,
                class_weight="balanced",
                random_state=random_state,
            )
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")

    def select_feature_indices(self, all_feature_names: List[str]) -> Tuple[List[int], List[str]]:
        """
        Map designated ablation subset to vector column indices.
        """
        selected_idx: List[int] = []
        selected_names: List[str] = []

        for i, name in enumerate(all_feature_names):
            include = False
            if self.feature_subset in ("full", "subset_c"):
                # All features except unobserved microwave/scatterometer flags in subset_c
                if self.feature_subset == "full":
                    include = True
                else:
                    if not name.startswith("quality_scatterometer") and not name.startswith("quality_microwave"):
                        include = True
            elif self.feature_subset == "subset_a":
                # Current state kinematics & track flags
                if name.startswith("track_") or name == "quality_track_available":
                    include = True
            elif self.feature_subset == "subset_b":
                # Subset A + temporal dynamics
                if (
                    name.startswith("track_")
                    or name.startswith("temp_")
                    or name in ("quality_track_available", "quality_temporal_gap_minutes")
                ):
                    include = True

            if include:
                selected_idx.append(i)
                selected_names.append(name)

        return selected_idx, selected_names

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        all_feature_names: List[str],
    ) -> "RITaskBaseline":
        """
        Fit model and feature scaler strictly on the training partition.
        """
        self.selected_indices, self.selected_feature_names = self.select_feature_indices(all_feature_names)
        X_sub = X_train[:, self.selected_indices]

        # Fit training scaler
        self.scaler = CycloneFeatureScaler(method="standard")
        X_scaled = self.scaler.fit_transform(X_sub, self.selected_feature_names)

        self.raw_model.fit(X_scaled, y_train)
        self.is_trained = True
        return self

    def calibrate(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray,
        method: str = "sigmoid",
    ) -> bool:
        """
        Calibrate model probabilities using the validation partition via Platt scaling.
        Guarded against partitions with insufficient class diversity.
        """
        if not self.is_trained:
            raise RuntimeError("Cannot calibrate untrained model.")

        if len(np.unique(y_val)) < 2 or np.sum(y_val == 1) < 2:
            self.is_calibrated = False
            return False

        X_sub = X_val[:, self.selected_indices]
        X_scaled = self.scaler.transform(X_sub)

        try:
            calibrator = CalibratedClassifierCV(estimator=self.raw_model, method=method, cv="prefit")
            calibrator.fit(X_scaled, y_val)
            self.calibrator = calibrator
            self.is_calibrated = True
            return True
        except Exception:
            self.is_calibrated = False
            return False

    def optimize_decision_threshold(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray,
        target_metric: str = "f1",
    ) -> Tuple[float, List[Dict[str, float]]]:
        """
        Search validation partition for the decision threshold optimizing operational F1 score.
        """
        probs = self.predict_proba(X_val)[:, 1]
        candidate_thresholds = np.linspace(0.02, 0.80, 40)
        
        analysis: List[Dict[str, float]] = []
        best_score = -1.0
        best_th = 0.50

        for th in candidate_thresholds:
            preds = (probs >= th).astype(int)
            p = float(precision_score(y_val, preds, zero_division=0))
            r = float(recall_score(y_val, preds, zero_division=0))
            f = float(f1_score(y_val, preds, zero_division=0))
            
            analysis.append({
                "threshold": round(float(th), 4),
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(f, 4),
            })

            score = f if target_metric == "f1" else r
            if score > best_score:
                best_score = score
                best_th = float(th)

        self.decision_threshold = round(best_th, 4)
        return self.decision_threshold, analysis

    def predict_proba(self, X: np.ndarray, use_calibrated: bool = False) -> np.ndarray:
        """
        Return predicted probability array of shape (N, 2).
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained.")

        if X.shape[1] != len(self.selected_indices):
            X_sub = X[:, self.selected_indices]
        else:
            X_sub = X

        X_scaled = self.scaler.transform(X_sub)

        if use_calibrated and self.is_calibrated and self.calibrator is not None:
            return self.calibrator.predict_proba(X_scaled)
        
        return self.raw_model.predict_proba(X_scaled)

    def predict(self, X: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
        """
        Predict binary labels applying the configured decision threshold.
        """
        th = threshold if threshold is not None else self.decision_threshold
        probs = self.predict_proba(X)[:, 1]
        return (probs >= th).astype(int)

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        threshold: Optional[float] = None,
        use_calibrated: bool = False,
    ) -> RIMetrics:
        """
        Evaluate full operational metrics on any partition.
        """
        th = threshold if threshold is not None else self.decision_threshold
        probs = self.predict_proba(X, use_calibrated=use_calibrated)[:, 1]
        preds = (probs >= th).astype(int)

        cm = confusion_matrix(y, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        # ROC-AUC & PR-AUC
        try:
            if len(np.unique(y)) > 1:
                auc_score = float(roc_auc_score(y, probs))
                pr_auc_score = float(average_precision_score(y, probs))
            else:
                auc_score = None
                pr_auc_score = None
        except Exception:
            auc_score = None
            pr_auc_score = None

        brier = float(brier_score_loss(y, probs))

        return RIMetrics(
            accuracy=round(float(accuracy_score(y, preds)), 4),
            precision=round(float(precision_score(y, preds, zero_division=0)), 4),
            recall=round(float(recall_score(y, preds, zero_division=0)), 4),
            f1=round(float(f1_score(y, preds, zero_division=0)), 4),
            roc_auc=round(auc_score, 4) if auc_score is not None else None,
            pr_auc=round(pr_auc_score, 4) if pr_auc_score is not None else None,
            brier_score=round(brier, 4),
            decision_threshold=th,
            confusion_matrix={"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            sample_count=len(y),
            positive_count=int(np.sum(y == 1)),
            prevalence_pct=round(float(np.sum(y == 1) / len(y) * 100), 2) if len(y) > 0 else 0.0,
        )

    def save_artifact(
        self,
        artifact_dir: str,
        training_metadata: Dict[str, Any],
        validation_metrics: Optional[RIMetrics] = None,
        test_metrics: Optional[RIMetrics] = None,
        threshold_analysis: Optional[List[Dict[str, float]]] = None,
    ) -> str:
        """
        Save reproducible, versioned model package.
        """
        os.makedirs(artifact_dir, exist_ok=True)

        # 1. Model binary
        model_path = os.path.join(artifact_dir, "model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.raw_model, f)

        # 2. Calibrator binary if present
        if self.is_calibrated and self.calibrator is not None:
            calib_path = os.path.join(artifact_dir, "calibrator.pkl")
            with open(calib_path, "wb") as f:
                pickle.dump(self.calibrator, f)

        # 3. Scaler JSON
        scaler_path = os.path.join(artifact_dir, "scaler.json")
        self.scaler.save_json(scaler_path)

        # 4. Feature schema
        schema_path = os.path.join(artifact_dir, "feature_schema.json")
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": "state_schema_v1",
                "feature_subset": self.feature_subset,
                "selected_indices": self.selected_indices,
                "selected_feature_names": self.selected_feature_names,
                "total_features": len(self.selected_feature_names),
            }, f, indent=2)

        # 5. Comprehensive Metadata & Metrics JSON
        metadata_path = os.path.join(artifact_dir, "metadata.json")
        meta = {
            "model_name": f"CycloneGuard-RI-v1-{self.model_type}",
            "version": "v1.0.0",
            "model_type": self.model_type,
            "feature_subset": self.feature_subset,
            "forecast_horizon_hours": 24.0,
            "ri_threshold_kts": 30.0,
            "decision_threshold": self.decision_threshold,
            "calibration_status": "Calibrated (Platt Scaling)" if self.is_calibrated else "Uncalibrated (Validation data limited)",
            "training_metadata": training_metadata,
            "validation_metrics": validation_metrics.to_dict() if validation_metrics else None,
            "test_metrics": test_metrics.to_dict() if test_metrics else None,
            "threshold_analysis": threshold_analysis,
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return artifact_dir
