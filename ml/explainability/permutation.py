"""
CycloneGuard Permutation Feature Importance Explainer.

Measures the statistical contribution of each feature to model performance
by calculating the degradation in score when feature values are permuted.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import f1_score, roc_auc_score

from ml.explainability.base import BaseExplainer, ExplanationResult


class PermutationExplainer(BaseExplainer):
    """
    Computes permutation feature importance on evaluation datasets.
    """

    def __init__(self, metric: str = "f1", n_repeats: int = 5, random_state: int = 42):
        """
        Args:
            metric: 'f1' or 'roc_auc'
            n_repeats: Number of shuffle permutations per feature
            random_state: Random seed for exact reproducibility
        """
        self.metric = metric
        self.n_repeats = n_repeats
        self.random_state = random_state

    def explain(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        **kwargs,
    ) -> ExplanationResult:
        """
        Calculate permutation importance across feature columns.
        """
        rng = np.random.default_rng(self.random_state)
        n_samples, n_features = X.shape

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        # Baseline evaluation
        baseline_score = self._compute_score(model, X, y)

        importances: Dict[str, float] = {}
        for col_idx in range(n_features):
            permuted_scores = []
            for _ in range(self.n_repeats):
                X_perm = np.array(X, copy=True)
                # Shuffle the column
                col_values = X_perm[:, col_idx]
                rng.shuffle(col_values)
                X_perm[:, col_idx] = col_values

                score = self._compute_score(model, X_perm, y)
                permuted_scores.append(baseline_score - score)

            feat_name = feature_names[col_idx]
            importances[feat_name] = float(np.mean(permuted_scores))

        # Rank features descending by importance
        ranked = sorted(importances.keys(), key=lambda k: importances[k], reverse=True)

        return ExplanationResult(
            method_name="permutation_importance",
            feature_names=feature_names,
            importance_scores=importances,
            ranked_features=ranked,
            metric_evaluated=self.metric,
            baseline_score=baseline_score,
            metadata={
                "n_repeats": self.n_repeats,
                "n_samples": n_samples,
                "n_features": n_features,
            },
        )

    def _compute_score(self, model: Any, X: np.ndarray, y: np.ndarray) -> float:
        """Compute the evaluation score for the model on (X, y)."""
        if self.metric == "roc_auc":
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)[:, 1]
                if len(np.unique(y)) > 1:
                    return float(roc_auc_score(y, probs))
                return 0.5
            preds = model.predict(X)
            return float(f1_score(y, preds, zero_division=0))
        else:
            preds = model.predict(X)
            return float(f1_score(y, preds, zero_division=0))
