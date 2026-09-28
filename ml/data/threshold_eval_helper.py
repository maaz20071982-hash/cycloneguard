import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix, brier_score_loss

def analyze_thresholds(y_true, y_probs, thresholds=None):
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 19)
    results = []
    best_th = 0.5
    best_f1 = -1.0
    for th in thresholds:
        y_pred = (y_probs >= th).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f = f1_score(y_true, y_pred, zero_division=0)
        acc = accuracy_score(y_true, y_pred)
        results.append({
            "threshold": round(float(th), 3),
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1": round(float(f), 4),
            "accuracy": round(float(acc), 4),
        })
        if f > best_f1:
            best_f1 = f
            best_th = th
    return best_th, best_f1, results

def evaluate_at_threshold(y_true, y_probs, threshold):
    y_pred = (y_probs >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    brier = brier_score_loss(y_true, y_probs)
    return {
        "threshold": round(float(threshold), 3),
        "accuracy": round(float(acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "brier": round(float(brier), 4),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
    }
