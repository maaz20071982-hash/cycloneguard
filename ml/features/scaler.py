"""
CycloneGuard Training-Fitted Feature Scaler.

Ensures rigorous data normalization with zero data leakage:
1. Scalers must be fit ONLY on training set data.
2. Binary indicator columns (is_observed, sensor availability flags) remain unscaled (0/1).
3. Continuous features are standardized using mean and standard deviation (or median/IQR).
4. Fitted parameters are fully serializable to JSON for reproducible inference.
"""

import json
from typing import Dict, List, Optional
import numpy as np


class CycloneFeatureScaler:
    """
    StandardScaler that operates only on continuous features, preserving binary indicator flags.
    """

    def __init__(self, method: str = "standard"):
        """
        Args:
            method: 'standard' (z-score: (x - mean) / std) or 'robust' ((x - median) / IQR).
        """
        self.method = method
        self.means: Optional[np.ndarray] = None
        self.scales: Optional[np.ndarray] = None
        self.continuous_indices: List[int] = []
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit(self, X_train: np.ndarray, feature_names: List[str]) -> "CycloneFeatureScaler":
        """
        Fit scaling parameters exclusively on the training matrix.
        """
        if X_train.ndim != 2:
            raise ValueError(f"X_train must be a 2D array, got shape {X_train.shape}")
        if len(feature_names) != X_train.shape[1]:
            raise ValueError(
                f"Feature names count ({len(feature_names)}) must match columns ({X_train.shape[1]})"
            )

        self.feature_names = list(feature_names)
        n_features = X_train.shape[1]

        # Identify continuous vs indicator features
        # Binary flags end with '_is_observed', 'flag', 'available', 'code', etc.
        continuous_indices = []
        for i, name in enumerate(feature_names):
            if (
                name.endswith("_is_observed")
                or name.startswith("quality_")
                or name.endswith("_detected")
                or name.endswith("_code")
            ):
                continue
            continuous_indices.append(i)

        self.continuous_indices = continuous_indices
        means = np.zeros(n_features, dtype=np.float64)
        scales = np.ones(n_features, dtype=np.float64)

        if self.method == "standard":
            for idx in continuous_indices:
                col = X_train[:, idx]
                valid = col[np.isfinite(col)]
                if len(valid) > 0:
                    mean_val = float(np.mean(valid))
                    std_val = float(np.std(valid))
                    means[idx] = mean_val
                    scales[idx] = std_val if std_val > 1e-6 else 1.0
        elif self.method == "robust":
            for idx in continuous_indices:
                col = X_train[:, idx]
                valid = col[np.isfinite(col)]
                if len(valid) > 0:
                    med = float(np.median(valid))
                    q75 = float(np.percentile(valid, 75))
                    q25 = float(np.percentile(valid, 25))
                    iqr = q75 - q25
                    means[idx] = med
                    scales[idx] = iqr if iqr > 1e-6 else 1.0

        self.means = means
        self.scales = scales
        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features using training-fitted means and scales.
        """
        if not self.is_fitted:
            raise RuntimeError("CycloneFeatureScaler must be fitted on training data before transform.")

        X_out = np.array(X, dtype=np.float64, copy=True)
        for idx in self.continuous_indices:
            col = X_out[:, idx]
            valid_mask = np.isfinite(col)
            X_out[valid_mask, idx] = (col[valid_mask] - self.means[idx]) / self.scales[idx]

        return X_out

    def fit_transform(self, X_train: np.ndarray, feature_names: List[str]) -> np.ndarray:
        """Fit on training data and return scaled training matrix."""
        self.fit(X_train, feature_names)
        return self.transform(X_train)

    def save_json(self, file_path: str) -> None:
        """Serialize scaler parameters to JSON."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save an unfitted scaler.")

        data = {
            "method": self.method,
            "feature_names": self.feature_names,
            "continuous_indices": self.continuous_indices,
            "means": self.means.tolist(),
            "scales": self.scales.tolist(),
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_json(cls, file_path: str) -> "CycloneFeatureScaler":
        """Load scaler parameters from JSON."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scaler = cls(method=data["method"])
        scaler.feature_names = data["feature_names"]
        scaler.continuous_indices = data["continuous_indices"]
        scaler.means = np.array(data["means"], dtype=np.float64)
        scaler.scales = np.array(data["scales"], dtype=np.float64)
        scaler.is_fitted = True
        return scaler
