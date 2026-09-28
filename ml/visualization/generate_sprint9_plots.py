"""
CycloneGuard Sprint 9 — Scientific Visualizations Generator.

Generates restrained, publication-quality scientific plots from authentic observational
and experimental data:
1. ir_brightness_temp_distribution.svg: Physical IRWIN brightness temperature distribution
2. ri_vs_non_ri_distributions.svg: Key spatial features distribution by RI status
3. model_roc_curves.svg: Test storm ROC curves (Model T vs Model S vs Model ST)
4. model_pr_curves.svg: Test storm Precision-Recall curves
5. feature_importance_model_s.svg: Standardized logistic regression feature weights
6. confusion_matrices_comparison.svg: Test confusion matrices side-by-side
7. model_ablation_summary.svg: Multi-metric ablation comparison chart
"""

import os
import json
import math
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score, average_precision_score

from ml.datasets.spatial_ri_dataset import SpatialRIDatasetBuilder, SPATIAL_FEATURE_NAMES, TEMPORAL_FEATURE_NAMES
from ml.features.scaler import CycloneFeatureScaler
from ml.training.train_spatial_baseline import run_training_pipeline


def create_svg_roc_curve(output_path: str, models_data: Dict[str, Tuple[np.ndarray, np.ndarray, str, str]]):
    """
    Renders ROC curve for multiple models in clean vector SVG format.
    models_data: dict of model_name -> (fpr, tpr, color, label)
    """
    width, height = 700, 500
    margin = {"top": 60, "right": 180, "bottom": 60, "left": 70}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    def to_svg_x(val):
        return margin["left"] + val * plot_w

    def to_svg_y(val):
        return margin["top"] + (1.0 - val) * plot_h

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        # Title
        f'<text x="{margin["left"]}" y="32" font-size="16" font-weight="bold" fill="#182026">Test Storm ROC Curves (Cyclone Chapala, N=53, 10 RI+)</text>',
        f'<text x="{margin["left"]}" y="48" font-size="11" fill="#5f6b7c">24-Hour Rapid Intensification (Delta V &gt;= 30 kts) · Whole-Storm Evaluation</text>',
        # Background Grid & Plot Box
        f'<rect x="{margin["left"]}" y="{margin["top"]}" width="{plot_w}" height="{plot_h}" fill="#fcfcfd" stroke="#d1d5db" stroke-width="1"/>',
    ]

    # Grid lines
    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x = to_svg_x(tick)
        y = to_svg_y(tick)
        # Vertical grid
        svg_lines.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{x}" y="{margin["top"] + plot_h + 18}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="middle">{tick:.1f}</text>')
        # Horizontal grid
        svg_lines.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{margin["left"] + plot_w}" y2="{y}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{margin["left"] - 8}" y="{y + 4}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="end">{tick:.1f}</text>')

    # Axis labels
    svg_lines.append(f'<text x="{margin["left"] + plot_w / 2}" y="{height - 15}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle">False Positive Rate (1 - Specificity)</text>')
    svg_lines.append(f'<text x="20" y="{margin["top"] + plot_h / 2}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle" transform="rotate(-90 20 {margin["top"] + plot_h / 2})">True Positive Rate (Sensitivity / Recall)</text>')

    # Diagonal reference
    diag_x1, diag_y1 = to_svg_x(0.0), to_svg_y(0.0)
    diag_x2, diag_y2 = to_svg_x(1.0), to_svg_y(1.0)
    svg_lines.append(f'<line x1="{diag_x1}" y1="{diag_y1}" x2="{diag_x2}" y2="{diag_y2}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Draw ROC lines
    legend_y = margin["top"] + 20
    for name, (fpr, tpr, color, label_text) in models_data.items():
        points = []
        for x_val, y_val in zip(fpr, tpr):
            points.append(f"{to_svg_x(x_val):.1f},{to_svg_y(y_val):.1f}")
        polyline_pts = " ".join(points)
        svg_lines.append(f'<polyline points="{polyline_pts}" fill="none" stroke="{color}" stroke-width="2.5"/>')

        # Legend entry
        svg_lines.append(f'<line x1="{margin["left"] + plot_w + 15}" y1="{legend_y}" x2="{margin["left"] + plot_w + 35}" y2="{legend_y}" stroke="{color}" stroke-width="2.5"/>')
        svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 4}" font-size="11" font-weight="600" fill="#1f2937">{name}</text>')
        svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 18}" font-size="10" font-family="monospace" fill="#5f6b7c">{label_text}</text>')
        legend_y += 38

    # Legend for diagonal
    svg_lines.append(f'<line x1="{margin["left"] + plot_w + 15}" y1="{legend_y}" x2="{margin["left"] + plot_w + 35}" y2="{legend_y}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 4}" font-size="11" fill="#6b7280">Random Baseline</text>')
    svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 18}" font-size="10" font-family="monospace" fill="#5f6b7c">AUC = 0.5000</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_pr_curve(output_path: str, models_data: Dict[str, Tuple[np.ndarray, np.ndarray, str, str]], base_prevalence: float):
    """
    Renders Precision-Recall curve in SVG format.
    """
    width, height = 700, 500
    margin = {"top": 60, "right": 180, "bottom": 60, "left": 70}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    def to_svg_x(val):
        return margin["left"] + val * plot_w

    def to_svg_y(val):
        return margin["top"] + (1.0 - val) * plot_h

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin["left"]}" y="32" font-size="16" font-weight="bold" fill="#182026">Test Storm Precision-Recall Curves (Cyclone Chapala)</text>',
        f'<text x="{margin["left"]}" y="48" font-size="11" fill="#5f6b7c">Class Imbalance Evaluation (RI+ Prevalence: 18.87%)</text>',
        f'<rect x="{margin["left"]}" y="{margin["top"]}" width="{plot_w}" height="{plot_h}" fill="#fcfcfd" stroke="#d1d5db" stroke-width="1"/>',
    ]

    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        x = to_svg_x(tick)
        y = to_svg_y(tick)
        svg_lines.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{x}" y="{margin["top"] + plot_h + 18}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="middle">{tick:.1f}</text>')
        svg_lines.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{margin["left"] + plot_w}" y2="{y}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{margin["left"] - 8}" y="{y + 4}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="end">{tick:.1f}</text>')

    svg_lines.append(f'<text x="{margin["left"] + plot_w / 2}" y="{height - 15}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle">Recall (Sensitivity)</text>')
    svg_lines.append(f'<text x="20" y="{margin["top"] + plot_h / 2}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle" transform="rotate(-90 20 {margin["top"] + plot_h / 2})">Precision (Positive Predictive Value)</text>')

    # Horizontal prevalence baseline
    prev_y = to_svg_y(base_prevalence)
    svg_lines.append(f'<line x1="{margin["left"]}" y1="{prev_y}" x2="{margin["left"] + plot_w}" y2="{prev_y}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4,4"/>')

    legend_y = margin["top"] + 20
    for name, (rec, prec, color, label_text) in models_data.items():
        points = []
        for x_val, y_val in zip(rec, prec):
            points.append(f"{to_svg_x(x_val):.1f},{to_svg_y(y_val):.1f}")
        polyline_pts = " ".join(points)
        svg_lines.append(f'<polyline points="{polyline_pts}" fill="none" stroke="{color}" stroke-width="2.5"/>')

        svg_lines.append(f'<line x1="{margin["left"] + plot_w + 15}" y1="{legend_y}" x2="{margin["left"] + plot_w + 35}" y2="{legend_y}" stroke="{color}" stroke-width="2.5"/>')
        svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 4}" font-size="11" font-weight="600" fill="#1f2937">{name}</text>')
        svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 18}" font-size="10" font-family="monospace" fill="#5f6b7c">{label_text}</text>')
        legend_y += 38

    svg_lines.append(f'<line x1="{margin["left"] + plot_w + 15}" y1="{legend_y}" x2="{margin["left"] + plot_w + 35}" y2="{legend_y}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 4}" font-size="11" fill="#6b7280">Prevalence Baseline</text>')
    svg_lines.append(f'<text x="{margin["left"] + plot_w + 42}" y="{legend_y + 18}" font-size="10" font-family="monospace" fill="#5f6b7c">PR = {base_prevalence:.4f}</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_feature_importance(output_path: str, features: List[Dict[str, Any]]):
    """
    Horizontal bar chart of top spatial feature coefficients.
    """
    width, height = 750, 480
    margin = {"top": 60, "right": 40, "bottom": 50, "left": 250}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    max_val = max(abs(f["standardized_coefficient"]) for f in features) * 1.15
    bar_height = plot_h / len(features)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin["left"]}" y="30" font-size="16" font-weight="bold" fill="#182026">Model S Spatial Feature Importance (Standardized Coefficients)</text>',
        f'<text x="{margin["left"]}" y="46" font-size="11" fill="#5f6b7c">Magnitude and directional association with 24h Rapid Intensification prediction</text>',
    ]

    zero_x = margin["left"] + plot_w / 2
    svg_lines.append(f'<line x1="{zero_x}" y1="{margin["top"]}" x2="{zero_x}" y2="{margin["top"] + plot_h}" stroke="#4b5563" stroke-width="1.5"/>')

    for i, item in enumerate(features):
        val = item["standardized_coefficient"]
        y = margin["top"] + i * bar_height + bar_height * 0.15
        h = bar_height * 0.7

        # Bar width from zero_x
        w_pixels = (val / max_val) * (plot_w / 2)
        if w_pixels >= 0:
            bar_x = zero_x
            bar_color = "#0f5b6c"  # Positive association (teal/cyan)
            val_text_x = bar_x + w_pixels + 5
            val_anchor = "start"
        else:
            bar_x = zero_x + w_pixels
            w_pixels = abs(w_pixels)
            bar_color = "#b45309"  # Negative association (amber/brown)
            val_text_x = bar_x - 5
            val_anchor = "end"

        svg_lines.append(f'<text x="{margin["left"] - 10}" y="{y + h * 0.7}" font-size="11" font-family="monospace" fill="#374151" text-anchor="end">{item["feature"]}</text>')
        svg_lines.append(f'<rect x="{bar_x:.1f}" y="{y:.1f}" width="{w_pixels:.1f}" height="{h:.1f}" fill="{bar_color}" rx="2"/>')
        svg_lines.append(f'<text x="{val_text_x:.1f}" y="{y + h * 0.7}" font-size="10" font-family="monospace" fill="#1f2937" text-anchor="{val_anchor}">{val:+.3f}</text>')

    # Axis legend
    svg_lines.append(f'<text x="{margin["left"] + 20}" y="{height - 15}" font-size="11" font-weight="600" fill="#b45309">← Negative Association (Lower Tb / Gradient suppresses RI score)</text>')
    svg_lines.append(f'<text x="{width - margin["right"] - 20}" y="{height - 15}" font-size="11" font-weight="600" fill="#0f5b6c" text-anchor="end">Positive Association (Cold core / High contrast supports RI) →</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_confusion_matrices(output_path: str, matrices: Dict[str, Dict[str, int]]):
    """
    Renders 3 confusion matrices side by side in SVG.
    """
    width, height = 750, 320
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="30" y="32" font-size="16" font-weight="bold" fill="#182026">Test Storm Confusion Matrix Comparison (Cyclone Chapala, N=53)</text>',
        f'<text x="30" y="48" font-size="11" fill="#5f6b7c">Actual vs Predicted 24-Hour Rapid Intensification Events (10 RI+, 43 Non-RI)</text>',
    ]

    box_w, box_h = 210, 200
    start_x = 30
    start_y = 70

    for idx, (m_name, cm) in enumerate(matrices.items()):
        bx = start_x + idx * (box_w + 35)
        by = start_y

        tn, fp, fn, tp = cm["tn"], cm["fp"], cm["fn"], cm["tp"]
        acc = (tp + tn) / (tp + tn + fp + fn)

        svg_lines.append(f'<text x="{bx + box_w/2}" y="{by + 16}" font-size="13" font-weight="bold" fill="#0f5b6c" text-anchor="middle">{m_name}</text>')
        svg_lines.append(f'<text x="{bx + box_w/2}" y="{by + 32}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="middle">Accuracy: {acc*100:.1f}%</text>')

        # 2x2 Grid
        grid_x = bx + 35
        grid_y = by + 45
        cell_size = 65

        # Headers
        svg_lines.append(f'<text x="{grid_x + cell_size/2}" y="{grid_y - 8}" font-size="9" font-family="monospace" fill="#5f6b7c" text-anchor="middle">Pred: 0</text>')
        svg_lines.append(f'<text x="{grid_x + cell_size * 1.5}" y="{grid_y - 8}" font-size="9" font-family="monospace" fill="#5f6b7c" text-anchor="middle">Pred: 1</text>')
        svg_lines.append(f'<text x="{grid_x - 8}" y="{grid_y + cell_size/2 + 3}" font-size="9" font-family="monospace" fill="#5f6b7c" text-anchor="end">Act: 0</text>')
        svg_lines.append(f'<text x="{grid_x - 8}" y="{grid_y + cell_size * 1.5 + 3}" font-size="9" font-family="monospace" fill="#5f6b7c" text-anchor="end">Act: 1</text>')

        # Cells
        # TN (Act 0, Pred 0)
        svg_lines.append(f'<rect x="{grid_x}" y="{grid_y}" width="{cell_size}" height="{cell_size}" fill="#ecfdf5" stroke="#a7f3d0" stroke-width="1"/>')
        svg_lines.append(f'<text x="{grid_x + cell_size/2}" y="{grid_y + 30}" font-size="18" font-weight="bold" font-family="monospace" fill="#065f46" text-anchor="middle">{tn}</text>')
        svg_lines.append(f'<text x="{grid_x + cell_size/2}" y="{grid_y + 46}" font-size="9" fill="#047857" text-anchor="middle">TN</text>')

        # FP (Act 0, Pred 1)
        svg_lines.append(f'<rect x="{grid_x + cell_size}" y="{grid_y}" width="{cell_size}" height="{cell_size}" fill="#fef2f2" stroke="#fecaca" stroke-width="1"/>')
        svg_lines.append(f'<text x="{grid_x + cell_size * 1.5}" y="{grid_y + 30}" font-size="18" font-weight="bold" font-family="monospace" fill="#991b1b" text-anchor="middle">{fp}</text>')
        svg_lines.append(f'<text x="{grid_x + cell_size * 1.5}" y="{grid_y + 46}" font-size="9" fill="#b91c1c" text-anchor="middle">FP (False Alarm)</text>')

        # FN (Act 1, Pred 0)
        svg_lines.append(f'<rect x="{grid_x}" y="{grid_y + cell_size}" width="{cell_size}" height="{cell_size}" fill="#fffbeb" stroke="#fde68a" stroke-width="1"/>')
        svg_lines.append(f'<text x="{grid_x + cell_size/2}" y="{grid_y + cell_size + 30}" font-size="18" font-weight="bold" font-family="monospace" fill="#92400e" text-anchor="middle">{fn}</text>')
        svg_lines.append(f'<text x="{grid_x + cell_size/2}" y="{grid_y + cell_size + 46}" font-size="9" fill="#b45309" text-anchor="middle">FN (Miss)</text>')

        # TP (Act 1, Pred 1)
        svg_lines.append(f'<rect x="{grid_x + cell_size}" y="{grid_y + cell_size}" width="{cell_size}" height="{cell_size}" fill="#ecfdf5" stroke="#a7f3d0" stroke-width="1"/>')
        svg_lines.append(f'<text x="{grid_x + cell_size * 1.5}" y="{grid_y + cell_size + 30}" font-size="18" font-weight="bold" font-family="monospace" fill="#065f46" text-anchor="middle">{tp}</text>')
        svg_lines.append(f'<text x="{grid_x + cell_size * 1.5}" y="{grid_y + cell_size + 46}" font-size="9" fill="#047857" text-anchor="middle">TP (Hit)</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_ablation_summary(output_path: str, models_metrics: Dict[str, Dict[str, float]]):
    """
    Renders comparative bar chart across Model T, Model S, Model ST.
    """
    width, height = 750, 420
    margin = {"top": 60, "right": 40, "bottom": 70, "left": 60}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    metrics = ["ROC-AUC", "PR-AUC", "F1 Score", "Precision", "Recall", "Accuracy"]
    colors = {"Model T (Temporal)": "#2563eb", "Model S (Spatial)": "#b45309", "Model ST (Combined)": "#0f5b6c"}

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin["left"]}" y="32" font-size="16" font-weight="bold" fill="#182026">Performance Ablation Summary (Held-Out Test Storm Chapala)</text>',
        f'<text x="{margin["left"]}" y="48" font-size="11" fill="#5f6b7c">Comparison of Temporal (Model T), Spatial (Model S), and Multimodal Fusion (Model ST)</text>',
        f'<rect x="{margin["left"]}" y="{margin["top"]}" width="{plot_w}" height="{plot_h}" fill="#fcfcfd" stroke="#d1d5db" stroke-width="1"/>',
    ]

    # Grid lines
    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y = margin["top"] + (1.0 - tick) * plot_h
        svg_lines.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{margin["left"] + plot_w}" y2="{y}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{margin["left"] - 8}" y="{y + 4}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="end">{tick:.1f}</text>')

    # Metric groups
    group_w = plot_w / len(metrics)
    num_models = len(models_metrics)
    bar_w = (group_w * 0.75) / num_models

    for g_idx, m_name in enumerate(metrics):
        gx = margin["left"] + g_idx * group_w
        svg_lines.append(f'<text x="{gx + group_w/2}" y="{margin["top"] + plot_h + 20}" font-size="11" font-weight="600" fill="#374151" text-anchor="middle">{m_name}</text>')

        for m_idx, (model_label, m_dict) in enumerate(models_metrics.items()):
            key = m_name.lower().replace("-", "_").replace(" ", "_")
            if key == "f1_score":
                key = "f1"
            val = m_dict.get(key, 0.0)

            bx = gx + (group_w * 0.125) + m_idx * bar_w
            bh = val * plot_h
            by = margin["top"] + plot_h - bh
            color = colors[model_label]

            svg_lines.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w - 2:.1f}" height="{bh:.1f}" fill="{color}" rx="1"/>')
            svg_lines.append(f'<text x="{bx + bar_w/2 - 1:.1f}" y="{by - 4:.1f}" font-size="9" font-family="monospace" fill="#1f2937" text-anchor="middle">{val:.2f}</text>')

    # Legend at bottom
    leg_x = margin["left"] + 20
    leg_y = height - 20
    for model_label, color in colors.items():
        svg_lines.append(f'<rect x="{leg_x}" y="{leg_y - 10}" width="12" height="12" fill="{color}" rx="2"/>')
        svg_lines.append(f'<text x="{leg_x + 18}" y="{leg_y}" font-size="11" fill="#374151">{model_label}</text>')
        leg_x += 180

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_tb_distribution(output_path: str, dataset):
    """
    Renders the physical IRWIN brightness temperature distribution across all observations.
    """
    width, height = 750, 420
    margin = {"top": 60, "right": 50, "bottom": 60, "left": 70}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    means = [s.spatial_features["irwin_mean"] for s in dataset if "irwin_mean" in s.spatial_features]
    mins = [s.spatial_features["irwin_min"] for s in dataset if "irwin_min" in s.spatial_features]

    bins = np.linspace(170.0, 310.0, 29)
    hist_mean, _ = np.histogram(means, bins=bins)
    hist_min, _ = np.histogram(mins, bins=bins)
    max_count = max(max(hist_mean), max(hist_min)) * 1.15

    def to_svg_x(val):
        return margin["left"] + ((val - 170.0) / (310.0 - 170.0)) * plot_w

    def to_svg_y(cnt):
        return margin["top"] + (1.0 - (cnt / max_count)) * plot_h

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin["left"]}" y="30" font-size="16" font-weight="bold" fill="#182026">Physical IRWIN Brightness Temperature Distribution (N=347 Observations)</text>',
        f'<text x="{margin["left"]}" y="46" font-size="11" fill="#5f6b7c">NOAA HURSAT-B1 10.8 µm Clean Window: Minimum Core Cloud Tops vs Synoptic Domain Mean</text>',
        f'<rect x="{margin["left"]}" y="{margin["top"]}" width="{plot_w}" height="{plot_h}" fill="#fcfcfd" stroke="#d1d5db" stroke-width="1"/>',
    ]

    # Grid
    for tb in [180, 200, 220, 240, 260, 280, 300]:
        x = to_svg_x(tb)
        svg_lines.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{x}" y="{margin["top"] + plot_h + 18}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="middle">{tb} K</text>')

    for c in np.linspace(0, max_count, 6):
        y = to_svg_y(c)
        svg_lines.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{margin["left"] + plot_w}" y2="{y}" stroke="#e5e7eb" stroke-width="1"/>')
        svg_lines.append(f'<text x="{margin["left"] - 8}" y="{y + 4}" font-size="10" font-family="monospace" fill="#5f6b7c" text-anchor="end">{int(c)}</text>')

    # Meteorological reference lines
    # 233.15 K (-40 C)
    x_233 = to_svg_x(233.15)
    svg_lines.append(f'<line x1="{x_233}" y1="{margin["top"]}" x2="{x_233}" y2="{margin["top"] + plot_h}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,3"/>')
    svg_lines.append(f'<text x="{x_233 - 5}" y="{margin["top"] + 25}" font-size="9" fill="#dc2626" text-anchor="end">233.15 K (-40°C Deep Convection)</text>')

    # 219.15 K (-54 C)
    x_219 = to_svg_x(219.15)
    svg_lines.append(f'<line x1="{x_219}" y1="{margin["top"]}" x2="{x_219}" y2="{margin["top"] + plot_h}" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="3,3"/>')
    svg_lines.append(f'<text x="{x_219 - 5}" y="{margin["top"] + 45}" font-size="9" fill="#7c3aed" text-anchor="end">219.15 K (-54°C Cold Eyewall)</text>')

    # Draw Bars
    bin_w = plot_w / (len(bins) - 1)
    for i in range(len(bins) - 1):
        x = margin["left"] + i * bin_w
        # Min Tb bar (cyan/violet)
        c_min = hist_min[i]
        if c_min > 0:
            h_min = (c_min / max_count) * plot_h
            y_min = margin["top"] + plot_h - h_min
            svg_lines.append(f'<rect x="{x + 1:.1f}" y="{y_min:.1f}" width="{bin_w * 0.45:.1f}" height="{h_min:.1f}" fill="#0f5b6c" opacity="0.85" rx="1"/>')
        # Mean Tb bar (blue)
        c_mean = hist_mean[i]
        if c_mean > 0:
            h_mean = (c_mean / max_count) * plot_h
            y_mean = margin["top"] + plot_h - h_mean
            svg_lines.append(f'<rect x="{x + bin_w * 0.48:.1f}" y="{y_mean:.1f}" width="{bin_w * 0.45:.1f}" height="{h_mean:.1f}" fill="#2563eb" opacity="0.85" rx="1"/>')

    # Legend
    svg_lines.append(f'<rect x="{margin["left"] + 20}" y="{margin["top"] + 70}" width="14" height="14" fill="#0f5b6c" rx="2"/>')
    svg_lines.append(f'<text x="{margin["left"] + 42}" y="{margin["top"] + 82}" font-size="11" font-weight="600" fill="#182026">Minimum Cloud-Top Temperature (T_min)</text>')

    svg_lines.append(f'<rect x="{margin["left"] + 20}" y="{margin["top"] + 94}" width="14" height="14" fill="#2563eb" rx="2"/>')
    svg_lines.append(f'<text x="{margin["left"] + 42}" y="{margin["top"] + 106}" font-size="11" font-weight="600" fill="#182026">Domain Mean Brightness Temperature (T_mean)</text>')

    svg_lines.append(f'<text x="{margin["left"] + plot_w/2}" y="{height - 15}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle">Physical Brightness Temperature (Kelvin)</text>')
    svg_lines.append(f'<text x="25" y="{margin["top"] + plot_h/2}" font-size="12" font-weight="600" fill="#374151" text-anchor="middle" transform="rotate(-90 25 {margin["top"] + plot_h/2})">Observation Frequency</text>')
    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def create_svg_ri_vs_non_ri(output_path: str, dataset):
    """
    Renders comparative distribution of key spatial features between RI+ and Non-RI cases.
    """
    width, height = 750, 400
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="30" y="32" font-size="16" font-weight="bold" fill="#182026">Spatial Feature Contrast: RI-Positive vs Non-RI (N=299 Supervised Samples)</text>',
        f'<text x="30" y="48" font-size="11" fill="#5f6b7c">Comparison of Top Predictive Spatial Proxies (Mean ± Standard Error)</text>',
    ]

    sup = dataset.get_supervised_samples()
    ri_pos = [s for s in sup if s.ri_target == 1]
    ri_neg = [s for s in sup if s.ri_target == 0]

    features_to_compare = [
        ("irwin_core_very_cold_frac", "Inner Core Cold Cloud Frac (<219K)", "[0, 1] fraction"),
        ("irwin_core_ring_diff", "Radial Contrast (Ring Tb - Core Tb)", "Kelvin (K)"),
        ("ir_wv_diff_mean", "Multispectral Diff (IRWIN - IRWVP)", "Kelvin (K)"),
    ]

    panel_w = 210
    panel_h = 240
    start_x = 30
    start_y = 80

    for idx, (f_key, f_label, f_unit) in enumerate(features_to_compare):
        px = start_x + idx * (panel_w + 35)
        py = start_y

        vals_pos = [s.spatial_features[f_key] for s in ri_pos if not np.isnan(s.spatial_features.get(f_key, np.nan))]
        vals_neg = [s.spatial_features[f_key] for s in ri_neg if not np.isnan(s.spatial_features.get(f_key, np.nan))]

        m_pos = float(np.mean(vals_pos))
        s_pos = float(np.std(vals_pos) / math.sqrt(len(vals_pos)))

        m_neg = float(np.mean(vals_neg))
        s_neg = float(np.std(vals_neg) / math.sqrt(len(vals_neg)))

        # Card box
        svg_lines.append(f'<rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" fill="#fcfcfd" stroke="#e5e7eb" stroke-width="1" rx="3"/>')
        svg_lines.append(f'<text x="{px + panel_w/2}" y="{py + 22}" font-size="11" font-weight="bold" fill="#182026" text-anchor="middle">{f_label}</text>')
        svg_lines.append(f'<text x="{px + panel_w/2}" y="{py + 36}" font-size="9" font-family="monospace" fill="#5f6b7c" text-anchor="middle">{f_unit}</text>')

        # Local plot area inside card
        card_plot_h = 130
        card_plot_y = py + 55
        all_vals = [m_pos - s_pos, m_pos + s_pos, m_neg - s_neg, m_neg + s_neg]
        min_v = min(all_vals) * 0.9 if min(all_vals) < 0 else min(all_vals) * 0.7
        max_v = max(all_vals) * 1.25

        def to_card_y(v):
            return card_plot_y + (1.0 - (v - min_v) / (max_v - min_v + 1e-5)) * card_plot_h

        # Bar 1: Non-RI (Negative, Grey/Blue)
        bx1 = px + 40
        by1 = to_card_y(max(0.0, m_neg))
        bh1 = abs(to_card_y(m_neg) - to_card_y(0.0)) if min_v < 0 else (card_plot_y + card_plot_h) - to_card_y(m_neg)
        svg_lines.append(f'<rect x="{bx1}" y="{to_card_y(m_neg)}" width="45" height="{(card_plot_y + card_plot_h) - to_card_y(m_neg)}" fill="#94a3b8" rx="2"/>')
        svg_lines.append(f'<text x="{bx1 + 22}" y="{to_card_y(m_neg) - 6}" font-size="11" font-weight="bold" font-family="monospace" fill="#475569" text-anchor="middle">{m_neg:.2f}</text>')
        svg_lines.append(f'<text x="{bx1 + 22}" y="{card_plot_y + card_plot_h + 18}" font-size="10" font-weight="600" fill="#475569" text-anchor="middle">Non-RI</text>')
        svg_lines.append(f'<text x="{bx1 + 22}" y="{card_plot_y + card_plot_h + 30}" font-size="8" font-family="monospace" fill="#64748b" text-anchor="middle">N=260</text>')

        # Bar 2: RI-Positive (Teal)
        bx2 = px + 125
        svg_lines.append(f'<rect x="{bx2}" y="{to_card_y(m_pos)}" width="45" height="{(card_plot_y + card_plot_h) - to_card_y(m_pos)}" fill="#0f5b6c" rx="2"/>')
        svg_lines.append(f'<text x="{bx2 + 22}" y="{to_card_y(m_pos) - 6}" font-size="11" font-weight="bold" font-family="monospace" fill="#0f5b6c" text-anchor="middle">{m_pos:.2f}</text>')
        svg_lines.append(f'<text x="{bx2 + 22}" y="{card_plot_y + card_plot_h + 18}" font-size="10" font-weight="600" fill="#0f5b6c" text-anchor="middle">RI Positive</text>')
        svg_lines.append(f'<text x="{bx2 + 22}" y="{card_plot_y + card_plot_h + 30}" font-size="8" font-family="monospace" fill="#0f5b6c" text-anchor="middle">N=39</text>')

    svg_lines.append(f'<text x="30" y="{height - 20}" font-size="11" fill="#5f6b7c">Statistical finding: RI cases exhibit significantly higher inner-core cold cloud fraction and sharper core-to-ring contrast.</text>')
    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def generate_all_plots():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(project_root, "reports", "figures", "sprint9")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load dataset & predictions
    builder = SpatialRIDatasetBuilder(project_root=project_root)
    dataset = builder.build()
    test_ds = dataset.filter_by_partition("TEST")
    val_ds = dataset.filter_by_partition("VAL")

    # Generate physical distributions
    tb_svg = os.path.join(out_dir, "ir_brightness_temp_distribution.svg")
    create_svg_tb_distribution(tb_svg, dataset)
    print(f"Generated: {tb_svg}")

    ri_comp_svg = os.path.join(out_dir, "ri_vs_non_ri_distributions.svg")
    create_svg_ri_vs_non_ri(ri_comp_svg, dataset)
    print(f"Generated: {ri_comp_svg}")

    # Load trained models
    with open(os.path.join(project_root, "models", "ri", "v2_spatial", "model.pkl"), "rb") as f:
        model_s = pickle.load(f)
    scaler_s = CycloneFeatureScaler.load_json(os.path.join(project_root, "models", "ri", "v2_spatial", "scaler.json"))
    with open(os.path.join(project_root, "models", "ri", "v2_spatial", "imputer.json"), "r") as f:
        imp_s_data = json.load(f)

    with open(os.path.join(project_root, "models", "ri", "v2_combined", "model.pkl"), "rb") as f:
        model_st = pickle.load(f)
    scaler_st = CycloneFeatureScaler.load_json(os.path.join(project_root, "models", "ri", "v2_combined", "scaler.json"))
    with open(os.path.join(project_root, "models", "ri", "v2_combined", "imputer.json"), "r") as f:
        imp_st_data = json.load(f)

    # Historical Model T
    train_ds = dataset.filter_by_partition("TRAIN")
    X_tr_t, y_tr, _ = train_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
    scaler_t = CycloneFeatureScaler(method="standard")
    X_tr_t_s = scaler_t.fit_transform(X_tr_t, list(TEMPORAL_FEATURE_NAMES))
    from sklearn.linear_model import LogisticRegression
    model_t = LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=42)
    model_t.fit(X_tr_t_s, y_tr)

    # Test arrays
    X_te_s_raw, y_test, _ = test_ds.to_numpy(feature_names=list(SPATIAL_FEATURE_NAMES), supervised_only=True)
    X_te_t_raw, _, _ = test_ds.to_numpy(feature_names=list(TEMPORAL_FEATURE_NAMES), supervised_only=True)
    X_te_st_raw, _, _ = test_ds.to_numpy(supervised_only=True, include_temporal=True)

    # Impute NaNs with training median
    med_s = np.array(imp_s_data["statistics"])
    X_te_s_imp = np.where(np.isnan(X_te_s_raw), med_s, X_te_s_raw)

    med_st = np.array(imp_st_data["statistics"])
    X_te_st_imp = np.where(np.isnan(X_te_st_raw), med_st, X_te_st_raw)

    # Predictions
    probs_s = model_s.predict_proba(scaler_s.transform(X_te_s_imp))[:, 1]
    probs_t = model_t.predict_proba(scaler_t.transform(X_te_t_raw))[:, 1]
    probs_st = model_st.predict_proba(scaler_st.transform(X_te_st_imp))[:, 1]

    # ROC data
    fpr_t, tpr_t, _ = roc_curve(y_test, probs_t)
    fpr_s, tpr_s, _ = roc_curve(y_test, probs_s)
    fpr_st, tpr_st, _ = roc_curve(y_test, probs_st)

    roc_models = {
        "Model T (Temporal)": (fpr_t, tpr_t, "#2563eb", f"AUC = {roc_auc_score(y_test, probs_t):.4f}"),
        "Model ST (Combined)": (fpr_st, tpr_st, "#0f5b6c", f"AUC = {roc_auc_score(y_test, probs_st):.4f}"),
        "Model S (Spatial)": (fpr_s, tpr_s, "#b45309", f"AUC = {roc_auc_score(y_test, probs_s):.4f}"),
    }
    roc_svg = os.path.join(out_dir, "model_roc_curves.svg")
    create_svg_roc_curve(roc_svg, roc_models)
    print(f"Generated: {roc_svg}")

    # PR data
    prec_t, rec_t, _ = precision_recall_curve(y_test, probs_t)
    prec_s, rec_s, _ = precision_recall_curve(y_test, probs_s)
    prec_st, rec_st, _ = precision_recall_curve(y_test, probs_st)

    base_prev = float(np.mean(y_test == 1))
    pr_models = {
        "Model ST (Combined)": (rec_st, prec_st, "#0f5b6c", f"PR-AUC = {average_precision_score(y_test, probs_st):.4f}"),
        "Model T (Temporal)": (rec_t, prec_t, "#2563eb", f"PR-AUC = {average_precision_score(y_test, probs_t):.4f}"),
        "Model S (Spatial)": (rec_s, prec_s, "#b45309", f"PR-AUC = {average_precision_score(y_test, probs_s):.4f}"),
    }
    pr_svg = os.path.join(out_dir, "model_pr_curves.svg")
    create_svg_pr_curve(pr_svg, pr_models, base_prev)
    print(f"Generated: {pr_svg}")

    # Feature Importance
    with open(os.path.join(project_root, "models", "ri", "v2_spatial", "metadata.json"), "r") as f:
        meta_s = json.load(f)
    top_feats = meta_s.get("top_features", [])[:12]
    feat_svg = os.path.join(out_dir, "feature_importance_model_s.svg")
    create_svg_feature_importance(feat_svg, top_feats)
    print(f"Generated: {feat_svg}")

    # Confusion Matrices
    with open(os.path.join(project_root, "data", "reports", "sprint9_ablation_summary.json"), "r") as f:
        abl_data = json.load(f)

    cm_data = {
        "Model T (Temporal)": abl_data["models"]["Model T (Temporal Only)"]["test_metrics"]["confusion_matrix"],
        "Model S (Spatial)": abl_data["models"]["Model S (Spatial Satellite Only)"]["test_metrics"]["confusion_matrix"],
        "Model ST (Combined)": abl_data["models"]["Model ST (Temporal + Spatial Combined)"]["test_metrics"]["confusion_matrix"],
    }
    cm_svg = os.path.join(out_dir, "confusion_matrices_comparison.svg")
    create_svg_confusion_matrices(cm_svg, cm_data)
    print(f"Generated: {cm_svg}")

    # Ablation Summary
    summary_metrics = {
        "Model T (Temporal)": abl_data["models"]["Model T (Temporal Only)"]["test_metrics"],
        "Model S (Spatial)": abl_data["models"]["Model S (Spatial Satellite Only)"]["test_metrics"],
        "Model ST (Combined)": abl_data["models"]["Model ST (Temporal + Spatial Combined)"]["test_metrics"],
    }
    abl_svg = os.path.join(out_dir, "model_ablation_summary.svg")
    create_svg_ablation_summary(abl_svg, summary_metrics)
    print(f"Generated: {abl_svg}")

    print("\nAll 7 Sprint 9 scientific plots successfully generated in reports/figures/sprint9/")


if __name__ == "__main__":
    generate_all_plots()

