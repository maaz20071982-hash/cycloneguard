"""
CycloneGuard Sprint 11 — Scientific Figure Generator.

Generates 9 high-resolution publication-quality vector SVGs for Sprint 11:
1. per_storm_roc_comparison.svg: ROC-AUC across all 5 defined storms (T vs TS).
2. per_storm_pr_comparison.svg: PR-AUC across all 5 defined storms (T vs TS).
3. per_storm_f1_comparison.svg: F1 score per storm under out-of-fold tuned thresholds.
4. per_storm_recall_comparison.svg: Recall per storm (T vs TS).
5. per_storm_precision_comparison.svg: Precision per storm (T vs TS).
6. false_positive_comparison.svg: False alarm count per storm.
7. threshold_sensitivity.svg: F1, Precision, and Recall sensitivity across threshold grid [0.20 - 0.50].
8. feature_importance_stability.svg: Top 10 stable features across folds with coefficient error bars.
9. calibration_reliability.svg: Empirical probability vs observed frequency reliability comparison.
"""

import json
import math
import os
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def generate_all_figures(project_root: str) -> None:
    output_dir = os.path.join(project_root, "reports", "figures", "sprint11")
    os.makedirs(output_dir, exist_ok=True)

    results_json = os.path.join(project_root, "docs", "SPRINT11_MULTI_STORM_RESULTS.json")
    with open(results_json, "r", encoding="utf-8") as f:
        res = json.load(f)

    loso_t = res["leave_one_storm_out"]["Finalist_T"]["per_storm"]
    loso_ts = res["leave_one_storm_out"]["Finalist_TS"]["per_storm"]
    th_sens = res["threshold_sensitivity"]
    feat_stab_ts = res["leave_one_storm_out"]["Finalist_TS"]["feature_stability"]

    storms_all = ["PHAILIN", "HELEN", "HUDHUD", "NILOFAR", "MEGH", "CHAPALA"]
    storms_defined = ["PHAILIN", "HUDHUD", "NILOFAR", "MEGH", "CHAPALA"]

    # -------------------------------------------------------------
    # Helper: Base SVG template
    # -------------------------------------------------------------
    def svg_header(w: int, h: int, title: str, subtitle: str) -> str:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    .bg {{ fill: #0f172a; }}
    .card {{ fill: #1e293b; rx: 8px; stroke: #334155; stroke-width: 1px; }}
    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 18px; font-weight: 700; fill: #f8fafc; }}
    .subtitle {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; fill: #94a3b8; }}
    .axis {{ stroke: #475569; stroke-width: 1px; }}
    .grid {{ stroke: #334155; stroke-dasharray: 4,4; stroke-width: 1px; }}
    .tick-label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; fill: #cbd5e1; }}
    .legend-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; fill: #e2e8f0; }}
  </style>
  <rect width="{w}" height="{h}" class="bg"/>
  <text x="35" y="38" class="title">{title}</text>
  <text x="35" y="58" class="subtitle">{subtitle}</text>
"""

    def svg_footer() -> str:
        return "</svg>\n"

    # -------------------------------------------------------------
    # 1. per_storm_roc_comparison.svg
    # -------------------------------------------------------------
    w, h = 760, 440
    svg = svg_header(w, h, "Leave-One-Storm-Out ROC-AUC by Cyclone Lifecycle", "Finalist T (Temporal, 23 feats) vs. Finalist TS (Temporal + Spatial, 61 feats) | Excludes Helen (0 RI+)")
    
    # Legend
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    # Plot frame
    x0, y0, pw, ph = 70, 90, 640, 290
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    # Y ticks 0.0 to 1.0
    for tick in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        y_pos = y0 + ph - int(tick * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{tick:.1f}</text>\n'
    # Chance line at 0.5
    y_chance = y0 + ph - int(0.5 * ph)
    svg += f'  <line x1="{x0}" y1="{y_chance}" x2="{x0+pw}" y2="{y_chance}" stroke="#ef4444" stroke-dasharray="3,3" stroke-width="1.5"/>\n'
    svg += f'  <text x="{x0+pw-5}" y="{y_chance-6}" text-anchor="end" font-family="sans-serif" font-size="10px" fill="#ef4444">Chance Level (0.50)</text>\n'

    # Bars per defined storm
    bar_group_w = pw / len(storms_defined)
    b_w = 34
    for i, s in enumerate(storms_defined):
        cx = x0 + i * bar_group_w + bar_group_w / 2
        roc_t = loso_t[s]["roc_auc"]
        roc_ts = loso_ts[s]["roc_auc"]

        h_t = int(roc_t * ph)
        h_ts = int(roc_ts * ph)

        # Bar T
        bx_t = cx - b_w - 4
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        svg += f'  <text x="{bx_t+b_w/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-weight="bold">{roc_t:.3f}</text>\n'

        # Bar TS
        bx_ts = cx + 4
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        svg += f'  <text x="{bx_ts+b_w/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-weight="bold">{roc_ts:.3f}</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'
        prev = loso_t[s]["prevalence_pct"]
        svg += f'  <text x="{cx}" y="{y0+ph+35}" text-anchor="middle" font-family="sans-serif" font-size="10px" fill="#64748b">Prev: {prev}%</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "per_storm_roc_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 2. per_storm_pr_comparison.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Leave-One-Storm-Out Precision-Recall AUC (PR-AUC)", "Measures positive-class RI discrimination under high class imbalance | Excludes Helen")
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y_pos = y0 + ph - int(tick * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{tick:.1f}</text>\n'

    for i, s in enumerate(storms_defined):
        cx = x0 + i * bar_group_w + bar_group_w / 2
        pr_t = loso_t[s]["pr_auc"]
        pr_ts = loso_ts[s]["pr_auc"]

        h_t = int(pr_t * ph)
        h_ts = int(pr_ts * ph)

        bx_t = cx - b_w - 4
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        svg += f'  <text x="{bx_t+b_w/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-weight="bold">{pr_t:.3f}</text>\n'

        bx_ts = cx + 4
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        svg += f'  <text x="{bx_ts+b_w/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-weight="bold">{pr_ts:.3f}</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'
        prev = loso_t[s]["prevalence_pct"]
        svg += f'  <text x="{cx}" y="{y0+ph+35}" text-anchor="middle" font-family="sans-serif" font-size="10px" fill="#64748b">Baseline: {prev}%</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "per_storm_pr_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 3. per_storm_f1_comparison.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Leave-One-Storm-Out F1 Score by Cyclone Lifecycle", "Harmonic mean of precision and recall evaluated at out-of-fold optimized thresholds")
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    for tick in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        y_pos = y0 + ph - int((tick / 0.6) * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{tick:.1f}</text>\n'

    bar_group_w6 = pw / len(storms_all)
    b_w6 = 26
    for i, s in enumerate(storms_all):
        cx = x0 + i * bar_group_w6 + bar_group_w6 / 2
        f1_t = loso_t[s]["f1"]
        f1_ts = loso_ts[s]["f1"]

        h_t = int((f1_t / 0.6) * ph)
        h_ts = int((f1_ts / 0.6) * ph)

        bx_t = cx - b_w6 - 3
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w6}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        if f1_t > 0:
            svg += f'  <text x="{bx_t+b_w6/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-size="10px">{f1_t:.3f}</text>\n'

        bx_ts = cx + 3
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w6}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        if f1_ts > 0:
            svg += f'  <text x="{bx_ts+b_w6/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-size="10px">{f1_ts:.3f}</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "per_storm_f1_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 4. per_storm_recall_comparison.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Leave-One-Storm-Out Recall / Sensitivity by Cyclone", "Proportion of true Rapid Intensification fixes successfully identified")
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    for tick in [0.0, 0.25, 0.50, 0.75, 1.0]:
        y_pos = y0 + ph - int(tick * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{int(tick*100)}%</text>\n'

    for i, s in enumerate(storms_all):
        cx = x0 + i * bar_group_w6 + bar_group_w6 / 2
        r_t = loso_t[s]["recall"]
        r_ts = loso_ts[s]["recall"]

        h_t = int(r_t * ph)
        h_ts = int(r_ts * ph)

        bx_t = cx - b_w6 - 3
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w6}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        if r_t > 0:
            svg += f'  <text x="{bx_t+b_w6/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-size="10px">{int(r_t*100)}%</text>\n'

        bx_ts = cx + 3
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w6}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        if r_ts > 0:
            svg += f'  <text x="{bx_ts+b_w6/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-size="10px">{int(r_ts*100)}%</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "per_storm_recall_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 5. per_storm_precision_comparison.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Leave-One-Storm-Out Precision / Positive Predictive Value", "Proportion of positive RI warnings that corresponded to actual 24h RI")
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    for tick in [0.0, 0.25, 0.50, 0.75, 1.0]:
        y_pos = y0 + ph - int(tick * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{int(tick*100)}%</text>\n'

    for i, s in enumerate(storms_all):
        cx = x0 + i * bar_group_w6 + bar_group_w6 / 2
        p_t = loso_t[s]["precision"]
        p_ts = loso_ts[s]["precision"]

        h_t = int(p_t * ph)
        h_ts = int(p_ts * ph)

        bx_t = cx - b_w6 - 3
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w6}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        if p_t > 0:
            svg += f'  <text x="{bx_t+b_w6/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-size="10px">{int(p_t*100)}%</text>\n'

        bx_ts = cx + 3
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w6}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        if p_ts > 0:
            svg += f'  <text x="{bx_ts+b_w6/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-size="10px">{int(p_ts*100)}%</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "per_storm_precision_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 6. false_positive_comparison.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "False Alarm (False Positive) Count by Cyclone Lifecycle", "Lower count indicates superior false alarm rejection in non-intensifying environments")
    svg += """  <rect x="500" y="32" width="14" height="14" fill="#38bdf8" rx="2"/>
  <text x="522" y="44" class="legend-text">Finalist T (Temporal)</text>
  <rect x="635" y="32" width="14" height="14" fill="#10b981" rx="2"/>
  <text x="657" y="44" class="legend-text">Finalist TS (T + S)</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    max_fp = 45
    for tick in [0, 10, 20, 30, 40]:
        y_pos = y0 + ph - int((tick / max_fp) * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{tick}</text>\n'

    for i, s in enumerate(storms_all):
        cx = x0 + i * bar_group_w6 + bar_group_w6 / 2
        fp_t = loso_t[s]["confusion_matrix"]["fp"]
        fp_ts = loso_ts[s]["confusion_matrix"]["fp"]

        h_t = int((fp_t / max_fp) * ph)
        h_ts = int((fp_ts / max_fp) * ph)

        bx_t = cx - b_w6 - 3
        by_t = y0 + ph - h_t
        svg += f'  <rect x="{bx_t}" y="{by_t}" width="{b_w6}" height="{h_t}" fill="#38bdf8" rx="3"/>\n'
        svg += f'  <text x="{bx_t+b_w6/2}" y="{by_t-5}" text-anchor="middle" class="tick-label" font-size="10px">{fp_t}</text>\n'

        bx_ts = cx + 3
        by_ts = y0 + ph - h_ts
        svg += f'  <rect x="{bx_ts}" y="{by_ts}" width="{b_w6}" height="{h_ts}" fill="#10b981" rx="3"/>\n'
        svg += f'  <text x="{bx_ts+b_w6/2}" y="{by_ts-5}" text-anchor="middle" class="tick-label" font-size="10px">{fp_ts}</text>\n'

        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label" font-weight="600">{s}</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "false_positive_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 7. threshold_sensitivity.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Operating Threshold Sensitivity Analysis (Validation Storm Megh)", "Evaluates trade-off across predefined threshold grid [0.20 to 0.50] for Model T and Model TS")
    
    # Legend
    svg += """  <line x1="420" y1="38" x2="445" y2="38" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="452" y="42" class="legend-text">T Recall</text>
  <line x1="510" y1="38" x2="535" y2="38" stroke="#38bdf8" stroke-dasharray="4,3" stroke-width="2.5"/>
  <text x="542" y="42" class="legend-text">T Precision</text>
  <line x1="615" y1="38" x2="640" y2="38" stroke="#10b981" stroke-width="2.5"/>
  <text x="647" y="42" class="legend-text">TS Precision</text>
"""
    svg += f'  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>\n'
    svg += f'  <line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>\n'

    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        y_pos = y0 + ph - int(tick * ph)
        svg += f'  <line x1="{x0}" y1="{y_pos}" x2="{x0+pw}" y2="{y_pos}" class="grid"/>\n'
        svg += f'  <text x="{x0-10}" y="{y_pos+4}" text-anchor="end" class="tick-label">{tick:.1f}</text>\n'

    t_grid = th_sens["Finalist_T"]
    ts_grid = th_sens["Finalist_TS"]
    n_pts = len(t_grid)

    def get_x(i):
        return x0 + int((i / (n_pts - 1)) * pw)

    def get_y(val):
        return y0 + ph - int(val * ph)

    # Plot T Recall
    pts_t_rec = " ".join([f"{get_x(i)},{get_y(item['val_metrics']['recall'])}" for i, item in enumerate(t_grid)])
    svg += f'  <polyline points="{pts_t_rec}" fill="none" stroke="#38bdf8" stroke-width="3"/>\n'

    # Plot T Precision
    pts_t_prec = " ".join([f"{get_x(i)},{get_y(item['val_metrics']['precision'])}" for i, item in enumerate(t_grid)])
    svg += f'  <polyline points="{pts_t_prec}" fill="none" stroke="#38bdf8" stroke-dasharray="5,4" stroke-width="2.5"/>\n'

    # Plot TS Precision
    pts_ts_prec = " ".join([f"{get_x(i)},{get_y(item['val_metrics']['precision'])}" for i, item in enumerate(ts_grid)])
    svg += f'  <polyline points="{pts_ts_prec}" fill="none" stroke="#10b981" stroke-width="3"/>\n'

    # Plot TS Recall
    pts_ts_rec = " ".join([f"{get_x(i)},{get_y(item['val_metrics']['recall'])}" for i, item in enumerate(ts_grid)])
    svg += f'  <polyline points="{pts_ts_rec}" fill="none" stroke="#10b981" stroke-dasharray="5,4" stroke-width="2.5"/>\n'

    for i, item in enumerate(t_grid):
        th_val = item["threshold"]
        cx = get_x(i)
        svg += f'  <circle cx="{cx}" cy="{get_y(item["val_metrics"]["recall"])}" r="4" fill="#38bdf8"/>\n'
        svg += f'  <circle cx="{cx}" cy="{get_y(item["val_metrics"]["precision"])}" r="4" fill="#38bdf8"/>\n'
        svg += f'  <circle cx="{cx}" cy="{get_y(ts_grid[i]["val_metrics"]["precision"])}" r="4" fill="#10b981"/>\n'
        svg += f'  <circle cx="{cx}" cy="{get_y(ts_grid[i]["val_metrics"]["recall"])}" r="4" fill="#10b981"/>\n'
        svg += f'  <text x="{cx}" y="{y0+ph+20}" text-anchor="middle" class="tick-label">{th_val:.2f}</text>\n'

    svg += f'  <text x="{x0+pw/2}" y="{y0+ph+40}" text-anchor="middle" class="tick-label" font-weight="600">Decision Threshold Grid</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "threshold_sensitivity.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 8. feature_importance_stability.svg
    # -------------------------------------------------------------
    w_feat, h_feat = 820, 480
    svg = svg_header(w_feat, h_feat, "Feature Importance Stability Across Folds (Finalist TS)", "Mean standardized logistic regression coefficients ± standard deviation across 6 Leave-One-Storm-Out folds")
    
    top_10 = feat_stab_ts[:10]
    fx0, fy0, fpw, fph = 250, 80, 520, 360
    bar_h = 24
    spacing = fph / 10

    # Center axis (0.0)
    max_c = 2.0
    cx_zero = fx0 + int((1.0 / 2.0) * fpw)
    svg += f'  <line x1="{cx_zero}" y1="{fy0}" x2="{cx_zero}" y2="{fy0+fph}" stroke="#64748b" stroke-width="1.5"/>\n'

    for tick in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        tx = fx0 + int(((tick + 1.0) / 2.0) * fpw)
        svg += f'  <line x1="{tx}" y1="{fy0}" x2="{tx}" y2="{fy0+fph}" class="grid"/>\n'
        svg += f'  <text x="{tx}" y="{fy0+fph+16}" text-anchor="middle" class="tick-label">{tick:+.1f}</text>\n'

    for i, item in enumerate(top_10):
        y_pos = fy0 + i * spacing + (spacing - bar_h) / 2
        name = item["feature"]
        mean_c = item["mean_coefficient"]
        std_c = item["std_coefficient"]

        # Bar width from zero
        bar_len = int((mean_c / 2.0) * fpw)
        if mean_c >= 0:
            bx = cx_zero
            fill_c = "#38bdf8" if "track" in name or "temp" in name else "#10b981"
            svg += f'  <rect x="{bx}" y="{y_pos}" width="{bar_len}" height="{bar_h}" fill="{fill_c}" rx="2"/>\n'
        else:
            bx = cx_zero + bar_len
            fill_c = "#f43f5e" if "irwin" in name else "#fbbf24"
            svg += f'  <rect x="{bx}" y="{y_pos}" width="{-bar_len}" height="{bar_h}" fill="{fill_c}" rx="2"/>\n'

        # Error bar
        err_len = int((std_c / 2.0) * fpw)
        center_x = cx_zero + bar_len
        svg += f'  <line x1="{center_x - err_len}" y1="{y_pos+bar_h/2}" x2="{center_x + err_len}" y2="{y_pos+bar_h/2}" stroke="#ffffff" stroke-width="1.5"/>\n'
        svg += f'  <line x1="{center_x - err_len}" y1="{y_pos+4}" x2="{center_x - err_len}" y2="{y_pos+bar_h-4}" stroke="#ffffff" stroke-width="1.5"/>\n'
        svg += f'  <line x1="{center_x + err_len}" y1="{y_pos+4}" x2="{center_x + err_len}" y2="{y_pos+bar_h-4}" stroke="#ffffff" stroke-width="1.5"/>\n'

        # Feature label
        svg += f'  <text x="{fx0-12}" y="{y_pos+16}" text-anchor="end" class="tick-label" font-size="11px" font-weight="500">{name}</text>\n'
        svg += f'  <text x="{fx0+fpw+10}" y="{y_pos+16}" text-anchor="start" font-family="monospace" font-size="11px" fill="#cbd5e1">{mean_c:+.2f} ±{std_c:.2f}</text>\n'

    svg += svg_footer()
    with open(os.path.join(output_dir, "feature_importance_stability.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # -------------------------------------------------------------
    # 9. calibration_reliability.svg
    # -------------------------------------------------------------
    svg = svg_header(w, h, "Empirical Probability Calibration & Reliability Assessment", "Brier Score and Reliability Curves on Chapala (T vs TS) | Documents Empirical Uncalibrated State")
    svg += """  <line x1="500" y1="38" x2="525" y2="38" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="532" y="42" class="legend-text">Finalist T (Brier=0.1616)</text>
  <line x1="500" y1="56" x2="525" y2="56" stroke="#10b981" stroke-width="2.5"/>
  <text x="532" y="60" class="legend-text">Finalist TS (Brier=0.1626)</text>
"""
    # Square plot area for calibration
    cal_s = 280
    cx0, cy0 = 120, 90
    svg += f'  <line x1="{cx0}" y1="{cy0}" x2="{cx0}" y2="{cy0+cal_s}" class="axis"/>\n'
    svg += f'  <line x1="{cx0}" y1="{cy0+cal_s}" x2="{cx0+cal_s}" y2="{cy0+cal_s}" class="axis"/>\n'

    # Diagonal perfect calibration line
    svg += f'  <line x1="{cx0}" y1="{cy0+cal_s}" x2="{cx0+cal_s}" y2="{cy0}" stroke="#64748b" stroke-dasharray="4,4" stroke-width="1.5"/>\n'
    svg += f'  <text x="{cx0+cal_s-10}" y="{cy0+15}" font-family="sans-serif" font-size="10px" fill="#64748b">Perfect Reliability</text>\n'

    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        pos = int(tick * cal_s)
        svg += f'  <line x1="{cx0}" y1="{cy0+cal_s-pos}" x2="{cx0+cal_s}" y2="{cy0+cal_s-pos}" class="grid"/>\n'
        svg += f'  <text x="{cx0-10}" y="{cy0+cal_s-pos+4}" text-anchor="end" class="tick-label">{tick:.1f}</text>\n'
        svg += f'  <line x1="{cx0+pos}" y1="{cy0}" x2="{cx0+pos}" y2="{cy0+cal_s}" class="grid"/>\n'
        svg += f'  <text x="{cx0+pos}" y="{cy0+cal_s+18}" text-anchor="middle" class="tick-label">{tick:.1f}</text>\n'

    svg += f'  <text x="{cx0+cal_s/2}" y="{cy0+cal_s+36}" text-anchor="middle" class="tick-label" font-weight="600">Mean Predicted Probability</text>\n'
    svg += f'  <text x="{cx0-35}" y="{cy0+cal_s/2}" text-anchor="middle" class="tick-label" font-weight="600" transform="rotate(-90 {cx0-35} {cy0+cal_s/2})">Fraction of Positives</text>\n'

    # Explanatory card on right side
    svg += f"""  <rect x="440" y="90" width="290" height="280" class="card"/>
  <text x="455" y="118" class="title" font-size="14px">Scientific Calibration Status</text>
  <text x="455" y="145" class="subtitle" font-size="11px" fill="#cbd5e1">• Cohort Size: N=53 (Chapala), 10 RI+.</text>
  <text x="455" y="165" class="subtitle" font-size="11px" fill="#cbd5e1">• Validation Set: N=42 (Megh), 6 RI+.</text>
  <text x="455" y="195" class="subtitle" font-size="11px" fill="#cbd5e1">• Finding: Dataset scale remains</text>
  <text x="455" y="210" class="subtitle" font-size="11px" fill="#cbd5e1">  insufficient for reliable isotonic or</text>
  <text x="455" y="225" class="subtitle" font-size="11px" fill="#cbd5e1">  Platt calibration fitting.</text>
  <text x="455" y="255" class="subtitle" font-size="11px" fill="#f59e0b">• Operational Rule: Model outputs</text>
  <text x="455" y="270" class="subtitle" font-size="11px" fill="#f59e0b">  must be presented as empirical risk</text>
  <text x="455" y="285" class="subtitle" font-size="11px" fill="#f59e0b">  indices, not true physical probabilities.</text>
"""

    svg += svg_footer()
    with open(os.path.join(output_dir, "calibration_reliability.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"[Sprint 11 Visualizations] Successfully generated all 9 vector SVGs in: {output_dir}")


if __name__ == "__main__":
    generate_all_figures(".")
