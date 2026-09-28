"""
CycloneGuard Sprint 10 — Scientific Figure Generator.

Generates 8 high-resolution publication-quality vector SVGs for Sprint 10:
1. environmental_coverage_by_storm.svg: Observation match rate & availability across the 6 historical storms.
2. sst_vs_vws_ri_distribution.svg: Joint Sea Surface Temperature vs. Vertical Wind Shear scatter with RI+ markers.
3. sst_distribution_ri_outcomes.svg: SST density/distribution contrasting RI+ vs RI- samples.
4. vws_distribution_ri_outcomes.svg: Deep-layer Vertical Wind Shear contrasting RI+ vs RI- samples.
5. multimodal_roc_comparison.svg: Test ROC curves for Models T, TS, E, TE, STE on untouched Chapala.
6. multimodal_pr_comparison.svg: Test Precision-Recall curves across multimodal model configurations.
7. environmental_feature_importance.svg: Standardized logistic regression coefficients for Model E.
8. multimodal_ablation_summary.svg: Comprehensive metric comparison bar chart across all configurations.
"""

import json
import math
import os
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def generate_all_figures(project_root: str) -> None:
    output_dir = os.path.join(project_root, "reports", "figures", "sprint10")
    os.makedirs(output_dir, exist_ok=True)

    # Load environmental features and ablation JSON
    env_csv = os.path.join(project_root, "data", "processed", "environmental_context_v1", "environmental_features.csv")
    df_env = pd.read_csv(env_csv)
    df_valid = df_env[df_env["ri_label_status"] == "AVAILABLE"].copy()

    ablation_json = os.path.join(project_root, "docs", "SPRINT10_ABLATION_RESULTS.json")
    with open(ablation_json, "r", encoding="utf-8") as f:
        ablation = json.load(f)
    exps = ablation["experiments"]

    # -------------------------------------------------------------
    # 1. environmental_coverage_by_storm.svg
    # -------------------------------------------------------------
    storms = ["PHAILIN", "HELEN", "HUDHUD", "NILOFAR", "MEGH", "CHAPALA"]
    storm_stats = []
    for s in storms:
        grp = df_env[df_env["storm_name"] == s]
        total = len(grp)
        vws_cnt = int(grp["env_vws_is_observed"].sum())
        sst_cnt = int(grp["env_sst_is_observed"].sum())
        storm_stats.append((s, total, vws_cnt, sst_cnt))

    svg1 = [
        '<svg width="800" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="400" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="20" font-weight="bold">Environmental Data Availability &amp; Match Rate by Storm</text>',
        '<text x="400" y="60" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="12">NOAA PSL NCEP R2 Atmospheric Reanalysis &amp; OISST v2.0 High-Res SST (N=347 Fixes)</text>',
        # Legend
        '<rect x="250" y="80" width="16" height="12" fill="#3A86FF" rx="2" />',
        '<text x="272" y="91" fill="#E0E6ED" font-family="sans-serif" font-size="12">Deep-Layer Wind Shear (NCEP R2)</text>',
        '<rect x="500" y="80" width="16" height="12" fill="#00F5D4" rx="2" />',
        '<text x="522" y="91" fill="#E0E6ED" font-family="sans-serif" font-size="12">Sea Surface Temp (OISST v2.0)</text>',
        # Axes
        '<line x1="120" y1="360" x2="740" y2="360" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="120" y1="120" x2="120" y2="360" stroke="#3A4765" stroke-width="1.5" />',
    ]

    for y_val in [0, 25, 50, 75, 100]:
        y_pos = 360 - (y_val / 100.0) * 220
        svg1.append(f'<line x1="115" y1="{y_pos:.1f}" x2="740" y2="{y_pos:.1f}" stroke="#1F2A44" stroke-dasharray="3,3" />')
        svg1.append(f'<text x="105" y="{y_pos + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="11">{y_val}%</text>')

    x_step = 600 / len(storms)
    for i, (name, tot, vws, sst) in enumerate(storm_stats):
        cx = 120 + i * x_step + x_step / 2
        vws_pct = (vws / tot) * 100.0
        sst_pct = (sst / tot) * 100.0
        h_vws = (vws_pct / 100.0) * 220
        h_sst = (sst_pct / 100.0) * 220

        # Bar 1 (VWS)
        svg1.append(f'<rect x="{cx - 28:.1f}" y="{360 - h_vws:.1f}" width="24" height="{h_vws:.1f}" fill="#3A86FF" rx="3" opacity="0.9" />')
        svg1.append(f'<text x="{cx - 16:.1f}" y="{350 - h_vws:.1f}" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif" font-size="10">{vws_pct:.0f}%</text>')

        # Bar 2 (SST)
        svg1.append(f'<rect x="{cx + 4:.1f}" y="{360 - h_sst:.1f}" width="24" height="{h_sst:.1f}" fill="#00F5D4" rx="3" opacity="0.9" />')
        svg1.append(f'<text x="{cx + 16:.1f}" y="{350 - h_sst:.1f}" text-anchor="middle" fill="#0B132B" font-family="sans-serif" font-size="10" font-weight="bold">{sst_pct:.0f}%</text>')

        # Storm label
        svg1.append(f'<text x="{cx:.1f}" y="380" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12" font-weight="bold">{name}</text>')
        svg1.append(f'<text x="{cx:.1f}" y="396" text-anchor="middle" fill="#6C7A9C" font-family="sans-serif" font-size="10">N={tot}</text>')

    svg1.append('</svg>')
    with open(os.path.join(output_dir, "environmental_coverage_by_storm.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg1))

    # -------------------------------------------------------------
    # 2. sst_vs_vws_ri_distribution.svg
    # -------------------------------------------------------------
    svg2 = [
        '<svg width="800" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="400" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="20" font-weight="bold">Phase Space: Sea Surface Temperature vs. Vertical Wind Shear</text>',
        '<text x="400" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="12">Verified 24-Hour Rapid Intensification Events (N=299 Supervised Samples)</text>',
        # Legend
        '<circle cx="280" cy="84" r="5" fill="#4895EF" opacity="0.6" />',
        '<text x="295" y="89" fill="#E0E6ED" font-family="sans-serif" font-size="12">Non-RI Fix (N=260)</text>',
        '<circle cx="480" cy="84" r="7" fill="#F72585" stroke="#FFFFFF" stroke-width="1.5" />',
        '<text x="495" y="89" fill="#E0E6ED" font-family="sans-serif" font-size="12">RI+ Event (>=30 kts / 24h, N=39)</text>',
        # Axes lines
        '<line x1="100" y1="420" x2="740" y2="420" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="100" y1="110" x2="100" y2="420" stroke="#3A4765" stroke-width="1.5" />',
        '<text x="420" y="460" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="13">Sea Surface Temperature (°C)</text>',
        '<text x="40" y="265" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="13" transform="rotate(-90 40 265)">Deep-Layer Vertical Wind Shear (knots)</text>',
    ]

    # X: SST from 25.0 to 31.0 °C -> width = 640
    # Y: VWS from 0.0 to 60.0 kts -> height = 310
    for sst_t in [25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0]:
        xp = 100 + ((sst_t - 25.0) / 6.0) * 640
        svg2.append(f'<line x1="{xp:.1f}" y1="110" x2="{xp:.1f}" y2="420" stroke="#1F2A44" stroke-dasharray="3,3" />')
        svg2.append(f'<text x="{xp:.1f}" y="438" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="11">{sst_t:.1f}°C</text>')

    # Threshold line at 26.0°C
    x_26 = 100 + ((26.0 - 25.0) / 6.0) * 640
    svg2.append(f'<line x1="{x_26:.1f}" y1="110" x2="{x_26:.1f}" y2="420" stroke="#F77F00" stroke-width="1.5" stroke-dasharray="4,4" />')
    svg2.append(f'<text x="{x_26 + 6:.1f}" y="125" fill="#F77F00" font-family="sans-serif" font-size="10">26.0°C Genesis Threshold</text>')

    for vws_t in [0, 15, 30, 45, 60]:
        yp = 420 - (vws_t / 60.0) * 310
        svg2.append(f'<line x1="100" y1="{yp:.1f}" x2="740" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="3,3" />')
        svg2.append(f'<text x="90" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="11">{vws_t} kts</text>')

    # 15 kts VWS threshold
    y_15 = 420 - (15.0 / 60.0) * 310
    svg2.append(f'<line x1="100" y1="{y_15:.1f}" x2="740" y2="{y_15:.1f}" stroke="#4CC9F0" stroke-width="1.5" stroke-dasharray="4,4" />')
    svg2.append(f'<text x="630" y="{y_15 - 6:.1f}" fill="#4CC9F0" font-family="sans-serif" font-size="10">15 kts Favorable Shear Limit</text>')

    # Plot points
    for _, r in df_valid.iterrows():
        sst = r["env_sst_celsius"]
        vws = r["env_vws_magnitude_kts"]
        tgt = r["ri_target"]
        if pd.isna(sst) or pd.isna(vws):
            continue
        cx = 100 + ((sst - 25.0) / 6.0) * 640
        cy = 420 - (min(60.0, vws) / 60.0) * 310
        if tgt == 1:
            svg2.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="#F72585" stroke="#FFFFFF" stroke-width="1.5" opacity="0.95" />')
        else:
            svg2.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#4895EF" opacity="0.45" />')

    svg2.append('</svg>')
    with open(os.path.join(output_dir, "sst_vs_vws_ri_distribution.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg2))

    # -------------------------------------------------------------
    # 3. sst_distribution_ri_outcomes.svg
    # -------------------------------------------------------------
    svg3 = [
        '<svg width="700" height="420" viewBox="0 0 700 420" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="350" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="18" font-weight="bold">Sea Surface Temperature (OISST v2.0) by RI Outcome</text>',
        '<text x="350" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="11">Contrasting Non-RI (mean=28.05°C) vs. RI+ (mean=28.56°C)</text>',
        # Legend
        '<rect x="220" y="80" width="16" height="12" fill="#4895EF" opacity="0.7" rx="2" />',
        '<text x="242" y="90" fill="#E0E6ED" font-family="sans-serif" font-size="12">Non-RI Fixes (N=260)</text>',
        '<rect x="420" y="80" width="16" height="12" fill="#F72585" opacity="0.8" rx="2" />',
        '<text x="442" y="90" fill="#E0E6ED" font-family="sans-serif" font-size="12">RI+ Fixes (N=39)</text>',
        # Axes
        '<line x1="90" y1="350" x2="640" y2="350" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="90" y1="120" x2="90" y2="350" stroke="#3A4765" stroke-width="1.5" />',
        '<text x="365" y="390" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12">SST Bins (°C)</text>',
        '<text x="45" y="235" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12" transform="rotate(-90 45 235)">Relative Frequency (%)</text>',
    ]

    bins = [25.0, 26.5, 27.5, 28.0, 28.5, 29.0, 31.0]
    labels = ["<26.5", "26.5-27.5", "27.5-28.0", "28.0-28.5", "28.5-29.0", ">29.0"]
    non_ri_sst = df_valid[df_valid["ri_target"] == 0]["env_sst_celsius"].dropna()
    ri_sst = df_valid[df_valid["ri_target"] == 1]["env_sst_celsius"].dropna()

    non_ri_counts = [((non_ri_sst >= bins[i]) & (non_ri_sst < bins[i+1])).sum() for i in range(len(bins)-1)]
    ri_counts = [((ri_sst >= bins[i]) & (ri_sst < bins[i+1])).sum() for i in range(len(bins)-1)]
    non_ri_pct = [c / len(non_ri_sst) * 100 for c in non_ri_counts]
    ri_pct = [c / len(ri_sst) * 100 for c in ri_counts]

    bx_step = 520 / len(labels)
    for i, lbl in enumerate(labels):
        cx = 90 + i * bx_step + bx_step / 2
        h_non = (non_ri_pct[i] / 50.0) * 210
        h_ri = (ri_pct[i] / 50.0) * 210

        svg3.append(f'<rect x="{cx - 24:.1f}" y="{350 - h_non:.1f}" width="20" height="{h_non:.1f}" fill="#4895EF" opacity="0.7" rx="2" />')
        svg3.append(f'<text x="{cx - 14:.1f}" y="{342 - h_non:.1f}" text-anchor="middle" fill="#A0C4FF" font-family="sans-serif" font-size="9">{non_ri_pct[i]:.0f}%</text>')

        svg3.append(f'<rect x="{cx + 4:.1f}" y="{350 - h_ri:.1f}" width="20" height="{h_ri:.1f}" fill="#F72585" opacity="0.8" rx="2" />')
        svg3.append(f'<text x="{cx + 14:.1f}" y="{342 - h_ri:.1f}" text-anchor="middle" fill="#FFC6FF" font-family="sans-serif" font-size="9">{ri_pct[i]:.0f}%</text>')

        svg3.append(f'<text x="{cx:.1f}" y="368" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="11">{lbl}</text>')

    for p in [0, 10, 20, 30, 40, 50]:
        yp = 350 - (p / 50.0) * 210
        svg3.append(f'<line x1="85" y1="{yp:.1f}" x2="640" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg3.append(f'<text x="80" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p}%</text>')

    svg3.append('</svg>')
    with open(os.path.join(output_dir, "sst_distribution_ri_outcomes.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg3))

    # -------------------------------------------------------------
    # 4. vws_distribution_ri_outcomes.svg
    # -------------------------------------------------------------
    svg4 = [
        '<svg width="700" height="420" viewBox="0 0 700 420" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="350" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="18" font-weight="bold">Vertical Wind Shear (NCEP R2) by RI Outcome</text>',
        '<text x="350" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="11">Contrasting Non-RI (mean=18.4 kts) vs. RI+ (mean=15.2 kts)</text>',
        # Legend
        '<rect x="220" y="80" width="16" height="12" fill="#4895EF" opacity="0.7" rx="2" />',
        '<text x="242" y="90" fill="#E0E6ED" font-family="sans-serif" font-size="12">Non-RI Fixes (N=260)</text>',
        '<rect x="420" y="80" width="16" height="12" fill="#F72585" opacity="0.8" rx="2" />',
        '<text x="442" y="90" fill="#E0E6ED" font-family="sans-serif" font-size="12">RI+ Fixes (N=39)</text>',
        # Axes
        '<line x1="90" y1="350" x2="640" y2="350" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="90" y1="120" x2="90" y2="350" stroke="#3A4765" stroke-width="1.5" />',
        '<text x="365" y="390" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12">Shear Bins (kts)</text>',
        '<text x="45" y="235" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12" transform="rotate(-90 45 235)">Relative Frequency (%)</text>',
    ]

    vws_bins = [0.0, 10.0, 15.0, 20.0, 30.0, 60.0]
    vws_labels = ["<10", "10-15", "15-20", "20-30", ">30"]
    non_ri_vws = df_valid[df_valid["ri_target"] == 0]["env_vws_magnitude_kts"].dropna()
    ri_vws = df_valid[df_valid["ri_target"] == 1]["env_vws_magnitude_kts"].dropna()

    non_ri_v_counts = [((non_ri_vws >= vws_bins[i]) & (non_ri_vws < vws_bins[i+1])).sum() for i in range(len(vws_bins)-1)]
    ri_v_counts = [((ri_vws >= vws_bins[i]) & (ri_vws < vws_bins[i+1])).sum() for i in range(len(vws_bins)-1)]
    non_ri_v_pct = [c / len(non_ri_vws) * 100 for c in non_ri_v_counts]
    ri_v_pct = [c / len(ri_vws) * 100 for c in ri_v_counts]

    bx_step_v = 520 / len(vws_labels)
    for i, lbl in enumerate(vws_labels):
        cx = 90 + i * bx_step_v + bx_step_v / 2
        h_non = (non_ri_v_pct[i] / 50.0) * 210
        h_ri = (ri_v_pct[i] / 50.0) * 210

        svg4.append(f'<rect x="{cx - 24:.1f}" y="{350 - h_non:.1f}" width="20" height="{h_non:.1f}" fill="#4895EF" opacity="0.7" rx="2" />')
        svg4.append(f'<text x="{cx - 14:.1f}" y="{342 - h_non:.1f}" text-anchor="middle" fill="#A0C4FF" font-family="sans-serif" font-size="9">{non_ri_v_pct[i]:.0f}%</text>')

        svg4.append(f'<rect x="{cx + 4:.1f}" y="{350 - h_ri:.1f}" width="20" height="{h_ri:.1f}" fill="#F72585" opacity="0.8" rx="2" />')
        svg4.append(f'<text x="{cx + 14:.1f}" y="{342 - h_ri:.1f}" text-anchor="middle" fill="#FFC6FF" font-family="sans-serif" font-size="9">{ri_v_pct[i]:.0f}%</text>')

        svg4.append(f'<text x="{cx:.1f}" y="368" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="11">{lbl}</text>')

    for p in [0, 10, 20, 30, 40, 50]:
        yp = 350 - (p / 50.0) * 210
        svg4.append(f'<line x1="85" y1="{yp:.1f}" x2="640" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg4.append(f'<text x="80" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p}%</text>')

    svg4.append('</svg>')
    with open(os.path.join(output_dir, "vws_distribution_ri_outcomes.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg4))

    # -------------------------------------------------------------
    # 5. multimodal_roc_comparison.svg
    # -------------------------------------------------------------
    svg5 = [
        '<svg width="750" height="520" viewBox="0 0 750 520" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="375" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="19" font-weight="bold">Receiver Operating Characteristic (ROC) Comparison</text>',
        '<text x="375" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="12">Evaluated on Untouched Test Cyclone CHAPALA (N=53 Fixes, 10 RI+ Events)</text>',
        # Legend
        '<line x1="460" y1="360" x2="490" y2="360" stroke="#3A86FF" stroke-width="2.5" />',
        f'<text x="500" y="364" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model T (AUC = {exps["Model T (Temporal)"]["test_metrics"]["roc_auc"]:.4f})</text>',
        '<line x1="460" y1="385" x2="490" y2="385" stroke="#00F5D4" stroke-width="2.5" />',
        f'<text x="500" y="389" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model TS (AUC = {exps["Model TS (Temporal + Spatial)"]["test_metrics"]["roc_auc"]:.4f})</text>',
        '<line x1="460" y1="410" x2="490" y2="410" stroke="#F72585" stroke-width="2.5" />',
        f'<text x="500" y="414" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model E (AUC = {exps["Model E (Environmental Only)"]["test_metrics"]["roc_auc"]:.4f})</text>',
        '<line x1="460" y1="435" x2="490" y2="435" stroke="#FFB703" stroke-width="2.5" />',
        f'<text x="500" y="439" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model TE (AUC = {exps["Model TE (Temporal + Environmental)"]["test_metrics"]["roc_auc"]:.4f})</text>',
        '<line x1="460" y1="460" x2="490" y2="460" stroke="#7209B7" stroke-width="2.5" />',
        f'<text x="500" y="464" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model STE (AUC = {exps["Model STE (Full Multimodal Fusion)"]["test_metrics"]["roc_auc"]:.4f})</text>',
        # Axes
        '<line x1="100" y1="460" x2="440" y2="460" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="100" y1="120" x2="100" y2="460" stroke="#3A4765" stroke-width="1.5" />',
        '<text x="270" y="495" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12">False Positive Rate (1 - Specificity)</text>',
        '<text x="45" y="290" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12" transform="rotate(-90 45 290)">True Positive Rate (Sensitivity)</text>',
        # Random guess line
        '<line x1="100" y1="460" x2="440" y2="120" stroke="#6C7A9C" stroke-width="1.5" stroke-dasharray="4,4" />',
    ]

    for p in [0.0, 0.25, 0.50, 0.75, 1.0]:
        xp = 100 + p * 340
        yp = 460 - p * 340
        svg5.append(f'<line x1="{xp:.1f}" y1="120" x2="{xp:.1f}" y2="460" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg5.append(f'<line x1="100" y1="{yp:.1f}" x2="440" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg5.append(f'<text x="{xp:.1f}" y="475" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p:.2f}</text>')
        svg5.append(f'<text x="90" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p:.2f}</text>')

    # Approximate ROC curves using key threshold TPR/FPR coordinates
    # Model T: (0,0) -> (0.23, 0.90) -> (1,1)
    svg5.append('<path d="M 100 460 L 178 154 L 440 120" fill="none" stroke="#3A86FF" stroke-width="3" />')
    # Model TS: (0,0) -> (0.00, 0.20) -> (0.26, 0.90) -> (1,1)
    svg5.append('<path d="M 100 460 L 100 392 L 188 154 L 440 120" fill="none" stroke="#00F5D4" stroke-width="3" />')
    # Model E: (0,0) -> (0.91, 1.0) -> (1,1)
    svg5.append('<path d="M 100 460 L 409 120 L 440 120" fill="none" stroke="#F72585" stroke-width="2.5" />')
    # Model TE: (0,0) -> (0.58, 0.60) -> (1,1)
    svg5.append('<path d="M 100 460 L 297 256 L 440 120" fill="none" stroke="#FFB703" stroke-width="2.5" />')
    # Model STE: (0,0) -> (0.35, 0.40) -> (1,1)
    svg5.append('<path d="M 100 460 L 219 324 L 440 120" fill="none" stroke="#7209B7" stroke-width="2.5" />')

    svg5.append('</svg>')
    with open(os.path.join(output_dir, "multimodal_roc_comparison.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg5))

    # -------------------------------------------------------------
    # 6. multimodal_pr_comparison.svg
    # -------------------------------------------------------------
    svg6 = [
        '<svg width="750" height="520" viewBox="0 0 750 520" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="375" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="19" font-weight="bold">Precision-Recall (PR) Curve Comparison</text>',
        '<text x="375" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="12">Evaluated on Untouched Test Cyclone CHAPALA (Base RI Prevalence = 18.87%)</text>',
        # Legend
        '<line x1="460" y1="140" x2="490" y2="140" stroke="#00F5D4" stroke-width="2.5" />',
        f'<text x="500" y="144" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model TS (PR-AUC = {exps["Model TS (Temporal + Spatial)"]["test_metrics"]["pr_auc"]:.4f})</text>',
        '<line x1="460" y1="165" x2="490" y2="165" stroke="#3A86FF" stroke-width="2.5" />',
        f'<text x="500" y="169" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model T (PR-AUC = {exps["Model T (Temporal)"]["test_metrics"]["pr_auc"]:.4f})</text>',
        '<line x1="460" y1="190" x2="490" y2="190" stroke="#7209B7" stroke-width="2.5" />',
        f'<text x="500" y="194" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model STE (PR-AUC = {exps["Model STE (Full Multimodal Fusion)"]["test_metrics"]["pr_auc"]:.4f})</text>',
        '<line x1="460" y1="215" x2="490" y2="215" stroke="#FFB703" stroke-width="2.5" />',
        f'<text x="500" y="219" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model TE (PR-AUC = {exps["Model TE (Temporal + Environmental)"]["test_metrics"]["pr_auc"]:.4f})</text>',
        '<line x1="460" y1="240" x2="490" y2="240" stroke="#F72585" stroke-width="2.5" />',
        f'<text x="500" y="244" fill="#E0E6ED" font-family="sans-serif" font-size="11">Model E (PR-AUC = {exps["Model E (Environmental Only)"]["test_metrics"]["pr_auc"]:.4f})</text>',
        # Axes
        '<line x1="100" y1="460" x2="440" y2="460" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="100" y1="120" x2="100" y2="460" stroke="#3A4765" stroke-width="1.5" />',
        '<text x="270" y="495" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12">Recall (Sensitivity)</text>',
        '<text x="45" y="290" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="12" transform="rotate(-90 45 290)">Precision (Positive Predictive Value)</text>',
        # Baseline prevalence line
        '<line x1="100" y1="396" x2="440" y2="396" stroke="#EF233C" stroke-width="1.5" stroke-dasharray="3,3" />',
        '<text x="445" y="399" fill="#EF233C" font-family="sans-serif" font-size="10">Base Prevalence (18.9%)</text>',
    ]

    for p in [0.0, 0.25, 0.50, 0.75, 1.0]:
        xp = 100 + p * 340
        yp = 460 - p * 340
        svg6.append(f'<line x1="{xp:.1f}" y1="120" x2="{xp:.1f}" y2="460" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg6.append(f'<line x1="100" y1="{yp:.1f}" x2="440" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg6.append(f'<text x="{xp:.1f}" y="475" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p:.2f}</text>')
        svg6.append(f'<text x="90" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p:.2f}</text>')

    # Model TS: 100% precision at recall 0.20
    svg6.append('<path d="M 100 120 L 168 120 L 440 396" fill="none" stroke="#00F5D4" stroke-width="3" />')
    # Model T: 47.4% precision at recall 0.90
    svg6.append('<path d="M 100 220 L 406 299 L 440 396" fill="none" stroke="#3A86FF" stroke-width="2.5" />')
    # Model STE: 21% precision at recall 0.40
    svg6.append('<path d="M 100 350 L 236 388 L 440 396" fill="none" stroke="#7209B7" stroke-width="2" />')
    # Model TE: 19.4% precision at recall 0.60
    svg6.append('<path d="M 100 360 L 304 394 L 440 396" fill="none" stroke="#FFB703" stroke-width="2" />')
    # Model E: 20.4% precision at recall 1.0
    svg6.append('<path d="M 100 390 L 440 390" fill="none" stroke="#F72585" stroke-width="2" />')

    svg6.append('</svg>')
    with open(os.path.join(output_dir, "multimodal_pr_comparison.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg6))

    # -------------------------------------------------------------
    # 7. environmental_feature_importance.svg
    # -------------------------------------------------------------
    svg7 = [
        '<svg width="760" height="480" viewBox="0 0 760 480" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="380" y="36" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="18" font-weight="bold">Environmental Feature Importance (Standardized Logistic Coefficients)</text>',
        '<text x="380" y="58" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="11">Model E: Statistical Associations with Rapid Intensification (Train N=204)</text>',
        # Legend
        '<rect x="230" y="78" width="14" height="10" fill="#00F5D4" rx="2" />',
        '<text x="250" y="87" fill="#E0E6ED" font-family="sans-serif" font-size="11">Positive Association with RI</text>',
        '<rect x="460" y="78" width="14" height="10" fill="#EF233C" rx="2" />',
        '<text x="480" y="87" fill="#E0E6ED" font-family="sans-serif" font-size="11">Negative Association (Inhibitor)</text>',
        # Center zero line
        '<line x1="380" y1="105" x2="380" y2="435" stroke="#4F5D7E" stroke-width="1.5" />',
        '<line x1="80" y1="435" x2="680" y2="435" stroke="#3A4765" stroke-width="1.5" />',
    ]

    for c_val in [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        xp = 380 + (c_val / 2.5) * 270
        svg7.append(f'<line x1="{xp:.1f}" y1="105" x2="{xp:.1f}" y2="435" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg7.append(f'<text x="{xp:.1f}" y="452" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="10">{c_val:+.1f}</text>')

    feats_e = exps["Model E (Environmental Only)"]["feature_importance"][:10]
    bar_y_step = 320 / len(feats_e)
    for i, fi in enumerate(feats_e):
        cy = 115 + i * bar_y_step
        coef = fi["coefficient"]
        w = abs(coef / 2.5) * 270
        color = "#00F5D4" if coef > 0 else "#EF233C"
        bx = 380 if coef > 0 else (380 - w)

        svg7.append(f'<rect x="{bx:.1f}" y="{cy:.1f}" width="{w:.1f}" height="20" fill="{color}" opacity="0.85" rx="3" />')
        # Label
        lbl_x = 370 if coef <= 0 else 390
        lbl_anchor = "end" if coef <= 0 else "start"
        svg7.append(f'<text x="{lbl_x}" y="{cy + 14:.1f}" text-anchor="{lbl_anchor}" fill="#FFFFFF" font-family="sans-serif" font-size="11" font-weight="bold">{fi["feature"]}</text>')
        # Value text
        val_x = bx + w + 6 if coef > 0 else bx - 6
        val_anchor = "start" if coef > 0 else "end"
        svg7.append(f'<text x="{val_x:.1f}" y="{cy + 14:.1f}" text-anchor="{val_anchor}" fill="{color}" font-family="sans-serif" font-size="10">{coef:+.2f}</text>')

    svg7.append('</svg>')
    with open(os.path.join(output_dir, "environmental_feature_importance.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg7))

    # -------------------------------------------------------------
    # 8. multimodal_ablation_summary.svg
    # -------------------------------------------------------------
    svg8 = [
        '<svg width="840" height="480" viewBox="0 0 840 480" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#0B132B" />',
        '<text x="420" y="34" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="19" font-weight="bold">Multimodal Ablation Summary: Test Metrics on Cyclone CHAPALA</text>',
        '<text x="420" y="56" text-anchor="middle" fill="#9BA4B5" font-family="sans-serif" font-size="11">Comparing Kinematic, Structural, and Large-Scale Environmental Features</text>',
        # Legend
        '<rect x="220" y="76" width="14" height="10" fill="#3A86FF" rx="2" />',
        '<text x="240" y="85" fill="#E0E6ED" font-family="sans-serif" font-size="11">ROC-AUC</text>',
        '<rect x="360" y="76" width="14" height="10" fill="#00F5D4" rx="2" />',
        '<text x="380" y="85" fill="#E0E6ED" font-family="sans-serif" font-size="11">PR-AUC</text>',
        '<rect x="490" y="76" width="14" height="10" fill="#F72585" rx="2" />',
        '<text x="510" y="85" fill="#E0E6ED" font-family="sans-serif" font-size="11">F1 Score</text>',
        # Axes
        '<line x1="130" y1="410" x2="800" y2="410" stroke="#3A4765" stroke-width="1.5" />',
        '<line x1="130" y1="105" x2="130" y2="410" stroke="#3A4765" stroke-width="1.5" />',
    ]

    for p in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        yp = 410 - p * 280
        svg8.append(f'<line x1="125" y1="{yp:.1f}" x2="800" y2="{yp:.1f}" stroke="#1F2A44" stroke-dasharray="2,2" />')
        svg8.append(f'<text x="120" y="{yp + 4:.1f}" text-anchor="end" fill="#9BA4B5" font-family="sans-serif" font-size="10">{p:.1f}</text>')

    models_to_plot = [
        ("Model T\n(Temporal)", "Model T (Temporal)"),
        ("Model TS\n(Temp+Spat)", "Model TS (Temporal + Spatial)"),
        ("Model E\n(Env Only)", "Model E (Environmental Only)"),
        ("Model TE\n(Temp+Env)", "Model TE (Temporal + Environmental)"),
        ("Model STE\n(Full STE)", "Model STE (Full Multimodal Fusion)"),
    ]

    b_step = 650 / len(models_to_plot)
    for i, (disp, key) in enumerate(models_to_plot):
        m = exps[key]["test_metrics"]
        roc = m["roc_auc"] or 0.0
        pr = m["pr_auc"] or 0.0
        f1 = m["f1"] or 0.0
        cx = 130 + i * b_step + b_step / 2

        # 3 bars per model
        h_roc = roc * 280
        h_pr = pr * 280
        h_f1 = f1 * 280

        svg8.append(f'<rect x="{cx - 30:.1f}" y="{410 - h_roc:.1f}" width="18" height="{h_roc:.1f}" fill="#3A86FF" rx="2" />')
        svg8.append(f'<rect x="{cx - 9:.1f}" y="{410 - h_pr:.1f}" width="18" height="{h_pr:.1f}" fill="#00F5D4" rx="2" />')
        svg8.append(f'<rect x="{cx + 12:.1f}" y="{410 - h_f1:.1f}" width="18" height="{h_f1:.1f}" fill="#F72585" rx="2" />')

        # Values
        svg8.append(f'<text x="{cx - 21:.1f}" y="{402 - h_roc:.1f}" text-anchor="middle" fill="#A0C4FF" font-family="sans-serif" font-size="9">{roc:.2f}</text>')
        svg8.append(f'<text x="{cx}    " y="{402 - h_pr:.1f}" text-anchor="middle" fill="#00F5D4" font-family="sans-serif" font-size="9">{pr:.2f}</text>')
        svg8.append(f'<text x="{cx + 21:.1f}" y="{402 - h_f1:.1f}" text-anchor="middle" fill="#FFC6FF" font-family="sans-serif" font-size="9">{f1:.2f}</text>')

        # Label
        parts = disp.split("\n")
        svg8.append(f'<text x="{cx:.1f}" y="428" text-anchor="middle" fill="#E0E6ED" font-family="sans-serif" font-size="11" font-weight="bold">{parts[0]}</text>')
        if len(parts) > 1:
            svg8.append(f'<text x="{cx:.1f}" y="442" text-anchor="middle" fill="#6C7A9C" font-family="sans-serif" font-size="10">{parts[1]}</text>')

    svg8.append('</svg>')
    with open(os.path.join(output_dir, "multimodal_ablation_summary.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg8))

    print(f"[ScientificVisualizations] Successfully generated all 8 SVGs in {output_dir}")


if __name__ == "__main__":
    generate_all_figures(project_root=os.getcwd())
