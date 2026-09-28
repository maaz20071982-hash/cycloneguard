"""
CycloneGuard AI Explainability Base Interface.

Establishes the foundation for model transparency and interpretability.
Strictly adheres to Scientific Rule 8:
"No causal interpretation of feature importance. Use wording: 'feature contributed
to the model prediction' or 'feature importance within this model'."
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExplanationResult:
    """Standardized explanation envelope for AI models."""
    method_name: str
    feature_names: List[str]
    importance_scores: Dict[str, float]
    ranked_features: List[str]
    metric_evaluated: str
    baseline_score: float
    disclaimer: str = (
        "Statutory Notice: Feature importance represents statistical contribution "
        "to model predictions within this specific model family. It does not establish "
        "direct physical causation of tropical cyclone intensification."
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method_name": self.method_name,
            "feature_names": self.feature_names,
            "importance_scores": {k: round(v, 4) for k, v in self.importance_scores.items()},
            "ranked_features": self.ranked_features,
            "metric_evaluated": self.metric_evaluated,
            "baseline_score": round(self.baseline_score, 4),
            "disclaimer": self.disclaimer,
            "metadata": self.metadata,
        }


class BaseExplainer(ABC):
    """Abstract base class for CycloneGuard model explainers."""

    @abstractmethod
    def explain(self, model: Any, X: Any, y: Any, **kwargs) -> ExplanationResult:
        """Generate an explainability result for the given model and dataset."""
        pass
