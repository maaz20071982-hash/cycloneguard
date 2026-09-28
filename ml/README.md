# CycloneGuard — ML Subsystem (Phase 1 & Future Sprints)

## Notice: Sprint 1 Boundary
**As defined in the CycloneGuard Sprint 1 Specifications:**
- NO cyclone AI/ML models are implemented in this sprint.
- NO large datasets (satellite imagery, reanalysis data) are downloaded.
- NO prediction engines are executed.

This directory establishes the dedicated workspace for future AI/PyTorch development, keeping machine learning artifacts and pipeline scripts strictly decoupled from core web application logic.

## Directory Structure
```
ml/
├── models/         # Model architectures, weights, checkpoints (future sprints)
├── datasets/       # Preprocessing pipelines, data loaders, split definitions (future)
├── training/       # Training loops, loss functions, hyperparameter configs (future)
├── inference/      # Model serving wrappers, ONNX/TorchScript export routines (future)
└── README.md
```

## Future Integration Points
In future sprints, PyTorch-based neural models will implement the abstract contracts defined in:
`backend/app/services/ai/interfaces.py`

These contracts include:
1. `predict_cyclone(observation)`: Track and presence identification.
2. `estimate_intensity(observation)`: Current sustained wind and central pressure estimation.
3. `predict_ri_risk(observation, historical_series)`: Rapid Intensification (RI) probability classification.
4. `predict_trend(cyclone_id, horizon_hours)`: Forward-looking track/intensity cone projections.
5. `generate_explanation(prediction_id)`: Grad-CAM / feature attribution generation for explainable AI.
