"use client";

import React, { useEffect, useState } from "react";
import { AdminLayout } from "@/components/layout/AdminLayout";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { Alert } from "@/components/ui/Alert";
import { ModelStatusCard } from "@/components/ui/ModelStatusCard";
import { SystemStatus } from "@/components/ui/SystemStatus";
import { Modal } from "@/components/ui/Modal";
import { LoadingSpinner } from "@/components/ui/Loading";
import { fetchAdminModels } from "@/lib/api/admin";
import { AdminModel } from "@/types";
import { Cpu, RefreshCw, Layers, LayoutGrid, ListFilter, ShieldCheck, Lock, CheckCircle2 } from "lucide-react";

export default function AdminModelsPage() {
  const [models, setModels] = useState<AdminModel[]>([]);
  const [finalFrozenModel, setFinalFrozenModel] = useState<any | null>(null);
  const [spatialModelS, setSpatialModelS] = useState<any | null>(null);
  const [combinedModelST, setCombinedModelST] = useState<any | null>(null);
  const [environmentalModelE, setEnvironmentalModelE] = useState<any | null>(null);
  const [multimodalModelSTE, setMultimodalModelSTE] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [activeModalModel, setActiveModalModel] = useState<AdminModel | null>(null);

  const loadModels = async () => {
    setIsLoading(true);
    try {
      const res = await fetchAdminModels();
      setModels(res.models);
      setFinalFrozenModel(res.final_frozen_model || null);
      setSpatialModelS(res.spatial_model_s || null);
      setCombinedModelST(res.combined_model_st || null);
      setEnvironmentalModelE(res.environmental_model_e || null);
      setMultimodalModelSTE(res.multimodal_model_ste || null);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Breadcrumb */}
        <Breadcrumb
          items={[
            { label: "Admin Console", href: "/admin/dashboard" },
            { label: "Models" },
          ]}
        />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-3 border-b border-[#e2e6e9]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Certified Model Registry & Benchmark Validation
              </span>
              <Badge variant="brand">Sprint 14 Certified Production Model Card</Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
              <Cpu className="h-5 w-5 text-[#0f5b6c]" />
              Model Management Registry
            </h1>
            <p className="text-xs text-[#5f6b7c] mt-0.5">
              Production frozen intelligence card (CycloneGuard-RI-Multimodal-TS-Final) and out-of-fold validation benchmark archives.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="border border-[#e2e6e9] rounded-[3px] p-0.5 bg-[#f8f9fa] flex items-center">
              <button
                onClick={() => setViewMode("cards")}
                className={`p-1.5 rounded-[2px] text-xs ${
                  viewMode === "cards" ? "bg-white text-[#0f5b6c] shadow-xs font-semibold" : "text-[#5f6b7c]"
                }`}
                title="Cards View"
              >
                <LayoutGrid className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-[2px] text-xs ${
                  viewMode === "table" ? "bg-white text-[#0f5b6c] shadow-xs font-semibold" : "text-[#5f6b7c]"
                }`}
                title="Table View"
              >
                <ListFilter className="h-3.5 w-3.5" />
              </button>
            </div>

            <Button size="sm" variant="outline" onClick={loadModels} isLoading={isLoading}>
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Refresh Registry
            </Button>
          </div>
        </div>

        {/* Sprint 11 Frozen Production Model Panel */}
        <Panel className="border-2 border-[#0f5b6c] shadow-sm">
          <PanelHeader
            title="Official Certified Model Card: CycloneGuard-RI-Multimodal-TS-Final"
            subtitle="Final certified research baseline combining Temporal Kinematics & HURSAT Satellite Spatial Structure. Multi-storm validated across 6 unique historical cyclones."
          />
          <div className="p-4 space-y-4 font-mono text-xs">
            {/* Phase 9: Official 11-Field Model Card Grid */}
            <div className="p-4 bg-[#f8fafc] border-2 border-[#0f5b6c] rounded-[4px] space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-[#cbd5e1] gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base text-[#0f5b6c]">
                    CycloneGuard-RI-Multimodal-TS-Final
                  </span>
                  <Badge variant="brand">v3.0.0-frozen</Badge>
                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#0f5b6c] bg-[#e0f2fe] px-2 py-0.5 rounded-[2px] border border-[#bae6fd]">
                    <Lock className="w-3 h-3" /> MODEL FROZEN
                  </span>
                </div>
                <div className="text-[11px] text-[#475569]">
                  Classification: <span className="font-bold text-[#0f5b6c]">CLASSIFICATION C</span>
                </div>
              </div>

              {/* 11 Key-Value Pairs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 text-[11px]">
                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">MODEL</span>
                  <span className="font-bold text-[#0f5b6c] break-all">CycloneGuard-RI-Multimodal-TS-Final</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">VERSION</span>
                  <span className="font-bold text-[#182026]">v3.0.0-frozen</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">MODEL TYPE</span>
                  <span className="font-semibold text-[#182026]">Regularized Balanced Logistic Regression</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">FEATURES</span>
                  <span className="font-bold text-[#182026]">61 Total Features</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">TEMPORAL</span>
                  <span className="font-semibold text-[#182026]">23 Features (Kinematic & Pressure)</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">SATELLITE STRUCTURAL</span>
                  <span className="font-semibold text-[#182026]">38 Features (HURSAT Spatial IR)</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">ENVIRONMENTAL</span>
                  <span className="font-bold text-[#dc2626]">Excluded from final model</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">OUTPUT</span>
                  <span className="font-bold text-[#0f5b6c]">Empirical RI Risk Index</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">THRESHOLD</span>
                  <span className="font-bold text-[#0f5b6c]">τ = 0.125 (Operating Decision Threshold)</span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px] sm:col-span-2">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">DATASET</span>
                  <span className="font-semibold text-[#182026]">
                    6 historical North Indian Ocean cyclone lifecycles (299 supervised observations, 39 RI+ events)
                  </span>
                </div>

                <div className="p-2.5 bg-white border border-[#e2e8f0] rounded-[3px]">
                  <span className="block text-[9px] uppercase tracking-wider text-[#64748b] font-bold">STATUS</span>
                  <span className="font-bold text-[#0284c7]">Research prototype</span>
                </div>
              </div>

              {/* Explicit Limitation Banner */}
              <div className="p-2.5 bg-[#fef2f2] border border-[#fecaca] rounded-[3px] text-[#991b1b] text-[11px] flex items-center justify-between">
                <span>
                  <strong>LIMITATION:</strong> Not calibrated for autonomous operational warning. Official meteorological warnings remain authoritative.
                </span>
                <Badge variant="danger" className="text-[10px] shrink-0">RESEARCH ONLY</Badge>
              </div>
            </div>

            {/* Side-by-side: Multi-Storm Generalization vs Primary Benchmark */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Box 1: Multi-Storm Out-of-Storm Generalization (LOSO) */}
              <div className="p-4 border border-[#cbd2d6] bg-[#ffffff] rounded-[4px] space-y-3">
                <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                  <div>
                    <span className="font-bold text-sm text-[#182026]">Multi-Storm Out-of-Fold Generalization</span>
                    <span className="block text-[10px] text-[#5f6b7c]">Leave-One-Storm-Out (LOSO) across 6 Historical Cyclones</span>
                  </div>
                  <Badge variant="neutral" className="text-[10px]">CROSS-STORM</Badge>
                </div>
                <p className="text-[11px] text-[#475569] leading-relaxed">
                  Evaluated across all 6 verified storms (Phailin, Helen, Hudhud, Nilofar, Megh, Chapala; N=299 supervised samples, 39 RI+). Zero test-storm data leakage.
                </p>
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Mean ROC-AUC</span>
                    <span className="font-bold text-[#0f5b6c] text-xs">0.6997 ± 0.117</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Mean PR-AUC</span>
                    <span className="font-bold text-[#0f5b6c] text-xs">0.3832 ± 0.302</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Mean Accuracy</span>
                    <span className="font-bold text-[#182026] text-xs">55.68% ± 22.4%</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Median ROC-AUC</span>
                    <span className="font-bold text-[#182026] text-xs">0.6959</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Median PR-AUC</span>
                    <span className="font-bold text-[#182026] text-xs">0.2468</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Variance vs Model T</span>
                    <span className="font-bold text-[#16a34a] text-xs">-32.7% Std</span>
                  </div>
                </div>
                <div className="text-[10px] text-[#5f6b7c] italic">
                  * Note: Helen contains 0 RI+ events; ROC-AUC is mathematically undefined and recorded as Undefined without 0-imputation.
                </div>
              </div>

              {/* Box 2: Held-out Benchmark Test Storm (Chapala) */}
              <div className="p-4 border border-[#cbd2d6] bg-[#ffffff] rounded-[4px] space-y-3">
                <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                  <div>
                    <span className="font-bold text-sm text-[#182026]">Held-Out Test Storm Benchmark</span>
                    <span className="block text-[10px] text-[#5f6b7c]">Untouched Evaluation on CHAPALA (2015, N=53, 10 RI+)</span>
                  </div>
                  <Badge variant="success" className="text-[10px]">TEST BENCHMARK</Badge>
                </div>
                <p className="text-[11px] text-[#475569] leading-relaxed">
                  Evaluated strictly once at operating threshold 0.125 frozen from validation storm Megh. Imputer & scaler fitted on train only.
                </p>
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Test ROC-AUC</span>
                    <span className="font-bold text-[#182026] text-xs">0.7349</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Test PR-AUC</span>
                    <span className="font-bold text-[#182026] text-xs">0.6109</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Precision</span>
                    <span className="font-bold text-[#16a34a] text-xs">100.0% (2/2)</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Recall</span>
                    <span className="font-bold text-[#182026] text-xs">20.0% (2/10)</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">False Positives</span>
                    <span className="font-bold text-[#16a34a] text-xs">0 FP</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-[#5f6b7c]">Brier Score</span>
                    <span className="font-bold text-[#182026] text-xs">0.1626</span>
                  </div>
                </div>
                <div className="text-[10px] text-[#5f6b7c]">
                  Companion Model T (Temporal 23 feats): ROC 0.8279, PR 0.4011, Recall 90%, Precision 47.4%, FP 10.
                </div>
              </div>
            </div>

            {/* Architecture Rationale & Scientific Disclaimers */}
            <div className="p-3 bg-[#f8fafc] border border-[#e2e8f0] rounded-[3px] space-y-2 text-[11px] text-[#475569]">
              <div className="font-bold text-[#182026] flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-[#16a34a]" /> Finalist Architecture Rationale & Trade-off:
              </div>
              <p>
                <strong>Finalist TS</strong> was selected as the frozen production model because incorporating geostationary infrared cloud core symmetry and temperature gradient metrics stabilizes cross-storm generalization (reducing cross-storm ROC standard deviation from 0.1743 to 0.1173) and completely eliminates false alarms on the held-out test storm (0 false positives vs. 10 in Model T).
              </p>
              <div className="pt-1 border-t border-[#e2e8f0] flex flex-col md:flex-row gap-2 justify-between text-[10px] text-[#64748b]">
                <span>• Environmental Features: Strictly Excluded (Sprint 10 Classification B: Coarse 2.5° reanalysis diluted predictive signals).</span>
                <span>• Probabilities: Uncalibrated empirical risk indices (Validation N=42 insufficient for Platt calibration).</span>
              </div>
            </div>
          </div>
        </Panel>

        {/* Sprint 9 Evaluated Research Baselines Panel */}
        <Panel>
          <PanelHeader
            title="Sprint 9 Evaluated Research Baselines (Strict Storm-Wise Protocol)"
            subtitle="Empirical models evaluated on untouched test storm CHAPALA (2015, N=53, 10 RI+). Zero synthetic metrics."
          />
          <div className="p-4 grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs font-mono">
            {/* Model S */}
            <div className="p-4 border border-[#cbd2d6] bg-[#ffffff] rounded-[4px] space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <div>
                  <span className="font-bold text-sm text-[#182026]">Model S (Satellite Spatial Baseline)</span>
                  <span className="block text-[10px] text-[#5f6b7c]">CycloneGuard-RI-Spatial-v2</span>
                </div>
                <Badge variant="neutral" className="text-[10px]">SPATIAL ONLY</Badge>
              </div>

              <div className="space-y-1 text-[11px]">
                <div><span className="text-[#5f6b7c]">Model Type:</span> <span className="text-[#182026]">Regularized Logistic Regression (L2)</span></div>
                <div><span className="text-[#5f6b7c]">Feature Family:</span> <span className="text-[#182026]">38 Spatial Satellite Proxies (Families A-E)</span></div>
                <div><span className="text-[#5f6b7c]">Training Dataset:</span> <span className="text-[#182026]">NOAA HURSAT-B1 (4 NIO storms: PHAILIN, HELEN, HUDHUD, NILOFAR)</span></div>
                <div><span className="text-[#5f6b7c]">Untouched Test Storm:</span> <span className="font-bold text-[#0f5b6c]">CHAPALA (N=53, 10 RI+)</span></div>
                <div><span className="text-[#5f6b7c]">Decision Threshold:</span> <span className="font-bold text-[#182026]">0.275 (Validation-selected on MEGH)</span></div>
                <div><span className="text-[#5f6b7c]">Calibration:</span> <span className="text-[#7d5a00]">Uncalibrated (Validation cohort N=42 with 6 positives is insufficient for statistically reliable calibration)</span></div>
              </div>

              {/* Metrics Grid */}
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">ROC-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.4488</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">PR-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.1777</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">F1 Score</span>
                  <span className="font-bold text-[#182026] text-xs">0.3333</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Recall</span>
                  <span className="font-bold text-[#182026] text-xs">60.0%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Precision</span>
                  <span className="font-bold text-[#182026] text-xs">23.1%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Accuracy</span>
                  <span className="font-bold text-[#182026] text-xs">54.7%</span>
                </div>
              </div>

              <div className="p-2 bg-[#fef9e7] border border-[#f5d996] rounded-[2px] text-[10px] text-[#7d5a00]">
                <strong>Scientific Finding:</strong> Pure spatial features underperform temporal kinematics out-of-storm due to baseline brightness temperature drift between storms.
              </div>
            </div>

            {/* Model ST */}
            <div className="p-4 border border-[#0f5b6c] bg-[#ffffff] rounded-[4px] space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <div>
                  <span className="font-bold text-sm text-[#0f5b6c]">Model ST (Temporal + Spatial Baseline)</span>
                  <span className="block text-[10px] text-[#5f6b7c]">CycloneGuard-RI-Combined-v2</span>
                </div>
                <Badge variant="brand" className="text-[10px]">COMBINED FUSION</Badge>
              </div>

              <div className="space-y-1 text-[11px]">
                <div><span className="text-[#5f6b7c]">Model Type:</span> <span className="text-[#182026]">Regularized Logistic Regression (L2)</span></div>
                <div><span className="text-[#5f6b7c]">Feature Family:</span> <span className="text-[#182026]">Temporal Kinematics (23) + Spatial Proxies (38) = 61 Feats</span></div>
                <div><span className="text-[#5f6b7c]">Training Dataset:</span> <span className="text-[#182026]">NOAA IBTrACS + HURSAT-B1 (4 NIO storms)</span></div>
                <div><span className="text-[#5f6b7c]">Untouched Test Storm:</span> <span className="font-bold text-[#0f5b6c]">CHAPALA (N=53, 10 RI+)</span></div>
                <div><span className="text-[#5f6b7c]">Decision Threshold:</span> <span className="font-bold text-[#182026]">0.400 (Validation-selected on MEGH)</span></div>
                <div><span className="text-[#5f6b7c]">Calibration:</span> <span className="text-[#7d5a00]">Uncalibrated (Validation cohort N=42 with 6 positives is insufficient for statistically reliable calibration)</span></div>
              </div>

              {/* Metrics Grid */}
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">ROC-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.7279</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">PR-AUC</span>
                  <span className="font-bold text-[#0f5b6c] text-xs">0.4086</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">F1 Score</span>
                  <span className="font-bold text-[#182026] text-xs">0.4706</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Recall</span>
                  <span className="font-bold text-[#182026] text-xs">40.0%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Precision</span>
                  <span className="font-bold text-[#0f5b6c] text-xs">57.1%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Accuracy</span>
                  <span className="font-bold text-[#0f5b6c] text-xs">83.0%</span>
                </div>
              </div>

              <div className="p-2 bg-[#e1f0f5] border border-[#b2d7e5] rounded-[2px] text-[10px] text-[#0f5b6c]">
                <strong>Scientific Finding:</strong> Adding spatial features to temporal kinematics sharply suppresses false alarms (14 down to 3) and achieves the highest PR-AUC (0.4086) and lowest Brier score (0.1356).
              </div>
            </div>

            {/* Model E */}
            <div className="p-4 border border-[#e2e6e9] bg-[#ffffff] rounded-[4px] space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <div>
                  <span className="font-bold text-sm text-[#182026]">Model E (Environmental Baseline)</span>
                  <span className="block text-[10px] text-[#5f6b7c]">CycloneGuard-RI-Environmental-v3</span>
                </div>
                <Badge variant="neutral" className="text-[10px]">SPRINT 10 REANALYSIS</Badge>
              </div>

              <div className="space-y-1 text-[11px]">
                <div><span className="text-[#5f6b7c]">Model Type:</span> <span className="text-[#182026]">Regularized Logistic Regression (L2)</span></div>
                <div><span className="text-[#5f6b7c]">Feature Family:</span> <span className="text-[#182026]">NCEP R2 Winds/RH + OISST v2.0 (13 Feats)</span></div>
                <div><span className="text-[#5f6b7c]">Training Dataset:</span> <span className="text-[#182026]">NOAA PSL Reanalysis (4 NIO storms, N=204)</span></div>
                <div><span className="text-[#5f6b7c]">Untouched Test Storm:</span> <span className="font-bold text-[#182026]">CHAPALA (N=53, 10 RI+)</span></div>
                <div><span className="text-[#5f6b7c]">Decision Threshold:</span> <span className="font-bold text-[#182026]">0.400 (Validation-selected on MEGH)</span></div>
                <div><span className="text-[#5f6b7c]">Calibration:</span> <span className="text-[#7d5a00]">Uncalibrated (Validation cohort N=42 insufficient for Platt/Isotonic)</span></div>
              </div>

              {/* Metrics Grid */}
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">ROC-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.3581</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">PR-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.1582</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">F1 Score</span>
                  <span className="font-bold text-[#182026] text-xs">0.3390</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Recall</span>
                  <span className="font-bold text-[#182026] text-xs">100.0%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Precision</span>
                  <span className="font-bold text-[#182026] text-xs">20.4%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Accuracy</span>
                  <span className="font-bold text-[#182026] text-xs">26.4%</span>
                </div>
              </div>

              <div className="p-2 bg-[#fef9e7] border border-[#f5d996] rounded-[2px] text-[10px] text-[#7d5a00]">
                <strong>Scientific Finding:</strong> Standalone coarse-grid (2.5°) environmental fields yield low out-of-storm discrimination and over-predict RI without kinematic/structural constraints (FP=39).
              </div>
            </div>

            {/* Model STE */}
            <div className="p-4 border border-[#7209B7] bg-[#ffffff] rounded-[4px] space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <div>
                  <span className="font-bold text-sm text-[#7209B7]">Model STE (Multimodal Fusion)</span>
                  <span className="block text-[10px] text-[#5f6b7c]">CycloneGuard-RI-Multimodal-STE-v3</span>
                </div>
                <Badge variant="warning" className="text-[10px]">FULL MULTIMODAL</Badge>
              </div>

              <div className="space-y-1 text-[11px]">
                <div><span className="text-[#5f6b7c]">Model Type:</span> <span className="text-[#182026]">Regularized Logistic Regression (L2)</span></div>
                <div><span className="text-[#5f6b7c]">Feature Family:</span> <span className="text-[#182026]">Temporal (23) + Spatial (38) + Environmental (13) = 74 Feats</span></div>
                <div><span className="text-[#5f6b7c]">Training Dataset:</span> <span className="text-[#182026]">IBTrACS + HURSAT + NCEP R2 + OISST (4 NIO storms)</span></div>
                <div><span className="text-[#5f6b7c]">Untouched Test Storm:</span> <span className="font-bold text-[#7209B7]">CHAPALA (N=53, 10 RI+)</span></div>
                <div><span className="text-[#5f6b7c]">Decision Threshold:</span> <span className="font-bold text-[#182026]">0.400 (Validation-selected on MEGH)</span></div>
                <div><span className="text-[#5f6b7c]">Calibration:</span> <span className="text-[#7d5a00]">Uncalibrated (Scientific Classification B: No incremental signal)</span></div>
              </div>

              {/* Metrics Grid */}
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] grid grid-cols-3 gap-2 text-center">
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">ROC-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.5070</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">PR-AUC</span>
                  <span className="font-bold text-[#182026] text-xs">0.2333</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">F1 Score</span>
                  <span className="font-bold text-[#182026] text-xs">0.2759</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Recall</span>
                  <span className="font-bold text-[#182026] text-xs">40.0%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Precision</span>
                  <span className="font-bold text-[#182026] text-xs">21.1%</span>
                </div>
                <div>
                  <span className="block text-[9px] text-[#5f6b7c]">Accuracy</span>
                  <span className="font-bold text-[#182026] text-xs">60.4%</span>
                </div>
              </div>

              <div className="p-2 bg-[#f8f9fa] border border-[#cbd2d6] rounded-[2px] text-[10px] text-[#5f6b7c]">
                <strong>Scientific Finding:</strong> Adding 13 coarse environmental features to Model ST dilutes the sharp kinematic/spatial signal (PR-AUC drops from 0.6109 to 0.2333). Confirms Classification B.
              </div>
            </div>
          </div>
        </Panel>

        {/* Scientific Honesty Alert */}
        <Alert variant="info" title="Scientific Honesty & Registry Status">
          Under strict CycloneGuard operational principles, all neural models are flagged as <strong>Not deployed</strong>. Zero synthetic accuracy, F1, or MAE metrics are fabricated. Model training and benchmark evaluations begin in subsequent phases.
        </Alert>

        {isLoading ? (
          <div className="flex justify-center p-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : viewMode === "cards" ? (
          /* Cards Grid View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {models.map((m) => (
              <ModelStatusCard
                key={m.model_name}
                model={m}
                onAction={() => setActiveModalModel(m)}
              />
            ))}
          </div>
        ) : (
          /* Table View */
          <Panel>
            <PanelHeader
              title="Registered PyTorch Architectures"
              subtitle="Computer vision and recurrent spatiotemporal network models"
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Model Name</TableHead>
                  <TableHead>Target Objective</TableHead>
                  <TableHead>Framework</TableHead>
                  <TableHead>Deployment Status</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {models.map((m) => (
                  <TableRow key={m.model_name}>
                    <TableCell className="font-semibold text-[#182026]">
                      <div className="flex items-center gap-2">
                        <Layers className="h-4 w-4 text-[#0f5b6c] shrink-0" />
                        <div>
                          <span className="block">{m.model_name}</span>
                          <span className="text-[10px] text-[#5f6b7c] font-mono">{m.framework}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-[#5f6b7c] text-xs max-w-xs truncate">{m.target}</TableCell>
                    <TableCell className="text-[#182026] font-mono text-xs">{m.framework}</TableCell>
                    <TableCell>
                      <SystemStatus status={m.status} size="sm" />
                    </TableCell>
                    <TableCell className="text-[#5f6b7c] font-mono text-xs">{m.version}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 text-[11px] px-2"
                        onClick={() => setActiveModalModel(m)}
                      >
                        Inspect
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Panel>
        )}

        {/* Model Inspect Modal */}
        {activeModalModel && (
          <Modal
            isOpen={true}
            onClose={() => setActiveModalModel(null)}
            title={`Architecture Specs: ${activeModalModel.model_name}`}
          >
            <div className="space-y-4 text-xs font-mono">
              <div className="p-3 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] space-y-1.5">
                <div>
                  <span className="text-[#5f6b7c]">Target Objective: </span>
                  <span className="text-[#182026] font-sans font-semibold">{activeModalModel.target}</span>
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Framework: </span>
                  <span className="text-[#182026]">{activeModalModel.framework}</span>
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Version: </span>
                  <span className="text-[#182026]">{activeModalModel.version}</span>
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Deployment Status: </span>
                  <SystemStatus status={activeModalModel.status} size="sm" />
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Training Dataset: </span>
                  <span className="text-[#182026]">{activeModalModel.dataset}</span>
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Dataset Version: </span>
                  <span className="text-[#182026]">{activeModalModel.dataset_version || "—"}</span>
                </div>
                <div>
                  <span className="text-[#5f6b7c]">Evaluation Metrics: </span>
                  {activeModalModel.metrics ? (
                    <div className="mt-1 p-2 bg-[#ffffff] border border-[#e2e6e9] rounded-[2px] grid grid-cols-2 gap-1.5 font-mono text-[11px]">
                      <div>ROC-AUC: <span className="font-bold text-[#182026]">{activeModalModel.metrics.roc_auc !== undefined ? activeModalModel.metrics.roc_auc.toFixed(4) : "—"}</span></div>
                      <div>PR-AUC: <span className="font-bold text-[#182026]">{activeModalModel.metrics.pr_auc !== undefined ? activeModalModel.metrics.pr_auc.toFixed(4) : "—"}</span></div>
                      <div>F1 Score: <span className="font-bold text-[#182026]">{activeModalModel.metrics.f1 !== undefined ? activeModalModel.metrics.f1.toFixed(4) : "—"}</span></div>
                      <div>Recall: <span className="font-bold text-[#182026]">{activeModalModel.metrics.recall !== undefined ? (activeModalModel.metrics.recall * 100).toFixed(1) + "%" : "—"}</span></div>
                      <div>Precision: <span className="font-bold text-[#182026]">{activeModalModel.metrics.precision !== undefined ? (activeModalModel.metrics.precision * 100).toFixed(1) + "%" : "—"}</span></div>
                      <div>Accuracy: <span className="font-bold text-[#182026]">{activeModalModel.metrics.accuracy !== undefined ? (activeModalModel.metrics.accuracy * 100).toFixed(1) + "%" : "—"}</span></div>
                      <div>Brier Score: <span className="font-bold text-[#182026]">{activeModalModel.metrics.brier_score !== undefined ? activeModalModel.metrics.brier_score.toFixed(4) : "—"}</span></div>
                      <div>Threshold: <span className="font-bold text-[#0f5b6c]">{activeModalModel.metrics.threshold !== undefined ? activeModalModel.metrics.threshold : "—"}</span></div>
                    </div>
                  ) : (
                    <span className="text-[#182026]">—</span>
                  )}
                </div>

                {activeModalModel.evaluation && (
                  <>
                    {activeModalModel.evaluation.feature_family && (
                      <div>
                        <span className="text-[#5f6b7c]">Feature Family: </span>
                        <span className="text-[#182026]">{activeModalModel.evaluation.feature_family}</span>
                      </div>
                    )}
                    {activeModalModel.evaluation.test_storm && (
                      <div>
                        <span className="text-[#5f6b7c]">Untouched Test Storm: </span>
                        <span className="font-bold text-[#0f5b6c]">{activeModalModel.evaluation.test_storm}</span>
                      </div>
                    )}
                    {activeModalModel.evaluation.calibration_status && (
                      <div>
                        <span className="text-[#5f6b7c]">Calibration Status: </span>
                        <span className="text-[#182026]">{activeModalModel.evaluation.calibration_status}</span>
                      </div>
                    )}
                    {activeModalModel.evaluation.limitations && activeModalModel.evaluation.limitations.length > 0 && (
                      <div className="pt-1">
                        <span className="text-[#5f6b7c] block mb-1">Documented Limitations:</span>
                        <ul className="list-disc pl-4 space-y-0.5 text-[10px] text-[#5f6b7c]">
                          {activeModalModel.evaluation.limitations.map((lim: string, idx: number) => (
                            <li key={idx}>{lim}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="p-3 border border-[#cbd2d6] bg-[#f1f3f4] rounded-[3px]">
                <span className="font-bold text-[#182026] block mb-1">Security & Integrity Notice:</span>
                <p className="text-[#5f6b7c] leading-relaxed">
                  Internal filesystem paths, weight check-sums, and serialized weights are isolated from client-facing responses. Checkpoint loading is restricted to verified TorchScript artifacts.
                </p>
              </div>

              <div className="flex justify-end pt-2">
                <Button size="sm" variant="primary" onClick={() => setActiveModalModel(null)}>
                  Close
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </AdminLayout>
  );
}
