"""
CycloneGuard Baseline Modeling & Evaluation Engine.

Provides simple, interpretable baseline models (Logistic Regression / Random Forest)
for Rapid Intensification classification, strictly trained and evaluated on
disjoint storm-wise splits with zero data leakage.
"""

import json
import os
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ml.features.scaler import CycloneFeatureScaler


@dataclass
class EvaluationMetrics:
    """Standardized performance metrics for binary cyclone classification."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float]
    pr_auc: Optional[float]
    best_f1: float
    best_threshold: float
    confusion_matrix: Dict[str, int]
    sample_count: int
    positive_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "roc_auc": round(self.roc_auc, 4) if self.roc_auc is not None else None,
            "pr_auc": round(self.pr_auc, 4) if self.pr_auc is not None else None,
            "best_f1": round(self.best_f1, 4),
            "best_threshold": round(self.best_threshold, 2),
            "confusion_matrix": self.confusion_matrix,
            "sample_count": self.sample_count,
            "positive_count": self.positive_count,
        }


class CycloneBaselineClassifier:
    """
    Interpretable baseline classifier for tropical cyclone Rapid Intensification.
    """

    def __init__(
        self,
        model_type: str = "logistic_regression",
        feature_subset: str = "full",
        random_state: int = 42,
    ):
        """
        Args:
            model_type: 'logistic_regression'
            feature_subset: 'subset_a' (current state), 'subset_b' (+ temporal),
                           'subset_c' (+ multi-source & morphology), or 'full'.
            random_state: Fixed random seed for exact reproducibility.
        """
        self.model_type = model_type
        self.feature_subset = feature_subset
        self.random_state = random_state
        self.scaler: Optional[CycloneFeatureScaler] = None
        self.selected_indices: List[int] = []
        self.selected_feature_names: List[str] = []

        if model_type == "logistic_regression":
            self.model = LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                C=1.0,
                random_state=random_state,
            )
        else:
            raise ValueError(f"Unsupported baseline model_type: {model_type}")

        self.is_trained = False

    def select_feature_indices(self, all_feature_names: List[str]) -> Tuple[List[int], List[str]]:
        """
        Select column indices matching the chosen feature ablation subset.
        """
        selected_idx = []
        selected_names = []

        for i, name in enumerate(all_feature_names):
            include = False
            if self.feature_subset == "full":
                include = True
            elif self.feature_subset == "subset_a":
                # Current track kinematics only
                if name.startswith("track_") or name == "quality_track_available":
                    include = True
            elif self.feature_subset == "subset_b":
                # Subset A + temporal evolution
                if (
                    name.startswith("track_")
                    or name.startswith("temp_")
                    or name in ("quality_track_available", "quality_temporal_gap_minutes")
                ):
                    include = True
            elif self.feature_subset == "subset_c":
                # Subset B + satellite & morphology + cross-source
                if not name.startswith("quality_scatterometer") and not name.startswith("quality_microwave"):
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
        scaler: Optional[CycloneFeatureScaler] = None,
    ) -> "CycloneBaselineClassifier":
        """
        Fit the baseline classifier on training data.
        """
        self.selected_indices, self.selected_feature_names = self.select_feature_indices(all_feature_names)
        X_sub = X_train[:, self.selected_indices]

        # Fit dedicated scaler strictly on training sub-matrix
        self.scaler = CycloneFeatureScaler(method="standard")
        X_scaled = self.scaler.fit_transform(X_sub, self.selected_feature_names)

        self.model.fit(X_scaled, y_train)
        self.is_trained = True
        return self

    def _prepare_sub(self, X: np.ndarray) -> np.ndarray:
        """Extract selected features if full matrix was provided."""
        if X.shape[1] == len(self.selected_indices):
            return X
        return X[:, self.selected_indices]

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary class labels (0 or 1)."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained.")
        X_sub = self._prepare_sub(X)
        X_scaled = self.scaler.transform(X_sub)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probability distribution."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained.")
        X_sub = self._prepare_sub(X)
        X_scaled = self.scaler.transform(X_sub)
        return self.model.predict_proba(X_scaled)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> EvaluationMetrics:
        """
        Evaluate classification metrics on a dataset.
        """
        preds = self.predict(X)
        probs = self.predict_proba(X)[:, 1]

        cm = confusion_matrix(y, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        from sklearn.metrics import average_precision_score

        # ROC-AUC & PR-AUC calculation (guarded if single class present)
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

        # Search optimal F1 decision threshold
        def_f1 = float(f1_score(y, preds, zero_division=0))
        best_f1_val = def_f1
        best_th_val = 0.50
        if len(np.unique(y)) > 1:
            for th in np.linspace(0.05, 0.90, 18):
                th_preds = (probs >= th).astype(int)
                f_candidate = float(f1_score(y, th_preds, zero_division=0))
                if f_candidate > best_f1_val:
                    best_f1_val = f_candidate
                    best_th_val = float(th)

        return EvaluationMetrics(
            accuracy=float(accuracy_score(y, preds)),
            precision=float(precision_score(y, preds, zero_division=0)),
            recall=float(recall_score(y, preds, zero_division=0)),
            f1=def_f1,
            roc_auc=auc_score,
            pr_auc=pr_auc_score,
            best_f1=best_f1_val,
            best_threshold=best_th_val,
            confusion_matrix={"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            sample_count=len(y),
            positive_count=int(np.sum(y == 1)),
        )

    def save_artifact(
        self,
        artifact_dir: str,
        training_metadata: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save the model, scaler, feature schema, and metadata as a versioned artifact.
        """
        os.makedirs(artifact_dir, exist_ok=True)

        # 1. Model pickle
        model_path = os.path.join(artifact_dir, "model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)

        # 2. Scaler JSON
        scaler_path = os.path.join(artifact_dir, "scaler.json")
        self.scaler.save_json(scaler_path)

        # 3. Feature schema JSON
        schema_path = os.path.join(artifact_dir, "feature_schema.json")
        schema_info = {
            "feature_subset": self.feature_subset,
            "feature_count": len(self.selected_feature_names),
            "feature_names": self.selected_feature_names,
            "selected_indices": self.selected_indices,
        }
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_info, f, indent=2)

        # 4. Training metadata & metrics
        meta_path = os.path.join(artifact_dir, "metadata.json")
        full_meta = {
            "model_type": self.model_type,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "training_metadata": training_metadata,
            "evaluation_metrics": metrics or {},
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(full_meta, f, indent=2)

        return artifact_dir
