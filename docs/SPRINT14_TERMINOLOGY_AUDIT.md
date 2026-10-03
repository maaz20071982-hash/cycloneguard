# SPRINT 14 — PRODUCT TERMINOLOGY AUDIT

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** 2026-09-27  
**Document:** `docs/SPRINT14_TERMINOLOGY_AUDIT.md`  

---

## 1. Terminology Governance Standard

To maintain strict scientific integrity and avoid misleading claims during judge evaluation or operational review, CycloneGuard enforces non-negotiable terminology standards across all user interfaces, API responses, and technical documentation.

| Prohibited / Misleading Term | Permitted / Preferred Term | Scientific Rationale |
| :--- | :--- | :--- |
| **"Probability" / "Calibrated Probability"** | **"Empirical RI Risk Index"** | The frozen model (Regularized Balanced Logistic Regression with class-balanced weighting) outputs an empirical ranking risk score. Calibration is not mathematically established on the small 6-storm sample. |
| **"Guaranteed prediction" / "Certainty"** | **"Model-estimated RI risk" / "Decision threshold (τ = 0.125)"** | Meteorological rapid intensification is inherently chaotic. Model outputs represent statistical decision support, not physical certainty. |
| **"Official alert" / "Operational warning"** | **"AI-assisted decision-support alert" / "Research advisory"** | Official meteorological warnings and landfall advisories remain the sole statutory authority of designated agencies (IMD, JTWC, RSMC New Delhi). |
| **"Evacuation recommendation / mandate"** | **"Disaster-management decision support"** | Civil protection and evacuation orders must strictly originate from local government and meteorological authorities. CycloneGuard never issues evacuation commands. |
| **"Real-time operational system"** | **"Historical verified surveillance mode" / "Research prototype"** | Automated live geostationary ingest pipelines are not connected; all current evaluations use verified historical archives (IBTrACS + HURSAT-B1). |
| **"Grad-CAM" / "Deep Neural / ResNet"** | **"Standardized Linear Feature Attribution"** | The production frozen model is a 61-feature Regularized Balanced Logistic Regression model ($L_2$, $C=1.0$, `lbfgs`). Feature attribution is calculated via standardized linear coefficients, not gradient-weighted convolutional activation maps. |
| **"Physical cause of RI"** | **"Statistical model attribution / correlation"** | Feature attributions reflect mathematical contributions to the model's decision function, not physical thermodynamic causation. |

---

## 2. Codebase Audit & Remediation Log

| File Path | Original Inappropriate Term | Updated Compliant Term | Status |
| :--- | :--- | :--- | :--- |
| `frontend/app/page.tsx:157` | "Grad-CAM attention attribution maps" | "Standardized feature attribution isolating primary linear decision factors" | **REMEDIATED** |
| `frontend/app/page.tsx:182` | "evaluate 24-hour RI probability" | "evaluate 24-hour empirical RI risk index" | **REMEDIATED** |
| `frontend/app/user/monitor/page.tsx:60` | "neural probability envelope" | "model-estimated empirical RI risk envelope" | **REMEDIATED** |
| `frontend/components/ui/ExplanationPanel.tsx` | "Grad-CAM isolating visual features driving neural inference" / "ResNet-50 Feature Layer" | Replaced with explicit research prototype status declaring standardized linear feature attribution for the 61-feature frozen model | **REMEDIATED** |
| `frontend/app/about/page.tsx` | "deep learning spatiotemporal ConvLSTM & ViT encoders" / "Grad-CAM" | Replaced with 10-section scientific guide describing frozen Regularized Balanced Logistic Regression, 61 features, and validation approach | **REMEDIATED** |
| `frontend/app/user/cyclones/[id]/page.tsx:368` | "automated neural pipelines" | "frozen statistical machine learning models" | **REMEDIATED** |
| `frontend/app/admin/alerts/page.tsx:93` | "scheduled for Sprint 4" | "Not available in current research prototype" | **REMEDIATED** |
| `frontend/app/admin/data/page.tsx:73` | "Sprint 3 Foundation" | "Verified Observational Ingestion Registry" | **REMEDIATED** |
| `frontend/app/admin/models/page.tsx:69` | "Sprint 9 Architecture Audit" | "Production Model Card & Validation Registry" | **REMEDIATED** |

---

## 3. Preservation of Negative Disclaimers

The search identified instances of words like "guaranteed" and "evacuation" inside mandatory disclaimers, e.g.:
> *"This statistical decision-support index does not guarantee rapid intensification, exact track landfall, or district-level evacuation timing. Official meteorological warnings issued by national weather centers (IMD, JTWC) remain strictly authoritative."*

These occurrences are **preserved and highlighted** because their explicit presence is legally and scientifically required.
