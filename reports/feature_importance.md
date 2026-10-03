# CycloneGuard — Sprint 5 Feature Importance Report

**Date:** 2026-09-26 03:11:22Z
**Evaluation Model:** Baseline Model C (Balanced Logistic Regression)
**Method:** Permutation Feature Importance (10 shuffle iterations on held-out test data)

> [!IMPORTANT]
> **Scientific Disclaimer:** Feature importance reflects the statistical contribution of each feature to the model's predictive performance within this linear classification framework. It does **not** assert direct physical causation of tropical cyclone rapid intensification.

## Top Predictive Features Ranked by Test ROC-AUC Impact

| Rank | Feature Identifier | Physical Variable | Source | Importance Score (Mean ROC-AUC Degradation) |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `track_translation_bearing_deg_val` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.1273` |
| 2 | `temp_delta_wind_12h_val` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0531` |
| 3 | `track_longitude_val` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0233` |
| 4 | `track_wind_speed_val` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0202` |
| 5 | `temp_delta_pressure_6h_val` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0119` |
| 6 | `temp_delta_wind_12h_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0099` |
| 7 | `temp_wind_change_rate_per_hour_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0077` |
| 8 | `track_translation_bearing_deg_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0045` |
| 9 | `track_translation_speed_kts_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0040` |
| 10 | `temp_delta_wind_6h_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0040` |
| 11 | `temp_delta_pressure_6h_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0023` |
| 12 | `track_latitude_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0000` |
| 13 | `track_longitude_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0000` |
| 14 | `track_wind_speed_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0000` |
| 15 | `track_pressure_is_observed` | State Vector Variable | NOAA IBTrACS / HURSAT | `+0.0000` |
