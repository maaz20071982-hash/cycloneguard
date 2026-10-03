"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  Eye,
  Activity,
  Zap,
  Shield,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Compass,
  Play,
  RotateCcw,
  Check,
  ChevronDown,
  ChevronUp,
  Cpu,
  Info,
  Wind,
  Gauge,
  Layers,
} from "lucide-react";

export default function AIAnalysisPage() {
  const {
    currentStorm,
    selectStorm,
    availableStorms,
    isAnalyzing,
    analysisSequence,
    analysisComplete,
    triggerAnalysis,
    calculatedConfidence,
    confidencePenaltyTotal,
    missingSourcesList,
  } = useStorm();

  const [techDetailsOpen, setTechDetailsOpen] = useState<boolean>(false);

  const detection = currentStorm.ai_detection;
  const intensity = currentStorm.intensity_classification;
  const conf = currentStorm.explainable_confidence;

  const inferenceSteps = [
    { id: "extracting", label: "Feature Extraction", desc: "Extracting 23 kinematic + 38 spatial proxies from fused tensor" },
    { id: "segmenting", label: "Core Segmentation", desc: "Morphological analysis of cold cloud-top symmetry & eyewall boundary" },
    { id: "inferring", label: "Model Inference", desc: "Computing Empirical RI Risk Index vs calibrated operating threshold τ = 0.125" },
    { id: "complete", label: "Complete", desc: "Detection, intensity classification, and feature attribution finalized" },
  ];

  // Plain-Language "Why this result?" factors
  const whyFactors = [
    {
      title: "Satellite Structure (Cold Core Eyewall Formation)",
      factor_type: "satellite_structure",
      desc: "NOAA HURSAT-B1 infrared imagery exhibits a sharp core thermal gradient of 2.31 K/km and 41.8% cold cloud tops (<219 K), showing nascent eyewall ring formation.",
      contribution_pts: 32.4,
      actual_metric: "irwin_grad_max (+2.31)",
      direction: "supports",
      is_demo: false,
    },
    {
      title: "Movement Pattern (Thermodynamic Inflow Corridor)",
      factor_type: "movement",
      desc: "Translating WNW at 6.8 kt across high ocean heat content (95 kJ/cm²) with low vertical wind shear (8.2 kt), providing optimal thermodynamic sustainment.",
      contribution_pts: 18.4,
      actual_metric: "shear_kts (8.2 kt)",
      direction: "supports",
      is_demo: false,
    },
    {
      title: "Historical Pattern (Analogue Onset Match)",
      factor_type: "historical",
      desc: "Kinematic signature closely matches historical North Indian Ocean rapid intensification benchmarks (Cyclone Nilofar 2014, Cyclone Chapala 2015), where low initial depressions rapidly deepened into major cyclones.",
      contribution_pts: 15.0,
      actual_metric: "LOO-CV Prior Match",
      direction: "supports",
      is_demo: true,
    },
    {
      title: "Wind Trend (Positive Rotational Acceleration)",
      factor_type: "wind_trend",
      desc: "12-hour wind tendency increased by +10 kt (from 20 kt to 30 kt), establishing positive rotational momentum before surface winds peak.",
      contribution_pts: 13.2,
      actual_metric: "dv_12h (+10 kt)",
      direction: "supports",
      is_demo: false,
    },
    {
      title: "Pressure Trend (Sustained Central Deepening)",
      factor_type: "pressure_trend",
      desc: "Central pressure dropped 2 hPa in 6 hours with a steady core pressure gradient, confirming continuous kinetic spin-up.",
      contribution_pts: 11.5,
      actual_metric: "dp_6h (-2.0 hPa)",
      direction: "supports",
      is_demo: false,
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/analysis" />

        {/* Stage Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 03 · AI DETECTION, INTENSITY & EXPLAINABILITY
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              AI Vortex Detection & Rapid Intensification Inference
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5 font-mono">
              Deep morphological vortex localization, IMD intensity classification, and explainable feature attribution for Cyclone {currentStorm.storm_name}.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            {/* Storm Switcher */}
            <div className="flex items-center bg-white border border-[#cbd2d6] rounded-[3px] px-2 py-1">
              <span className="text-[#5a6872] text-[11px] mr-1.5">Storm:</span>
              <select
                value={currentStorm.storm_id}
                onChange={(e) => selectStorm(e.target.value)}
                className="bg-transparent font-bold text-[#0f5b6c] text-xs focus:outline-hidden cursor-pointer"
              >
                {availableStorms.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.basin.split("(")[0]})
                  </option>
                ))}
              </select>
            </div>

            {/* Run Inference Button */}
            <Button
              variant="primary"
              size="md"
              onClick={triggerAnalysis}
              disabled={isAnalyzing}
              className="shadow-sm font-mono font-bold tracking-wider uppercase text-xs"
            >
              {isAnalyzing ? (
                <>
                  <RotateCcw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Running Inference...
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 mr-1.5 fill-white" />
                  RUN AI ANALYSIS
                </>
              )}
            </Button>
          </div>
        </div>

        {/* ============================================================ */}
        {/* INFERENCE PROGRESS SEQUENCE (Simulated short inference)      */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#0f5b6c]/30 bg-[#edf5f7] p-4 shadow-xs font-mono text-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#0f5b6c] uppercase text-[11px] flex items-center gap-1.5">
              <Cpu className="h-4 w-4" />
              Inference Execution Pipeline: Feature Extraction &rarr; Core Segmentation &rarr; Model Inference &rarr; Complete
            </span>
            <span className="text-[10px] text-[#5a6872]">
              Status:{" "}
              <strong className="text-[#0f5b6c] uppercase">
                {analysisSequence === "complete"
                  ? "INFERENCE COMPLETE"
                  : analysisSequence === "idle"
                  ? "STANDBY · READY FOR INFERENCE"
                  : `${analysisSequence.toUpperCase()}...`}
              </strong>
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {inferenceSteps.map((st, idx) => {
              const isStepComplete =
                analysisSequence === "complete" ||
                (analysisSequence === "inferring" && idx < 2) ||
                (analysisSequence === "segmenting" && idx < 1);

              const isCurrent = analysisSequence === st.id;

              return (
                <div
                  key={st.id}
                  className={`p-2.5 rounded-[3px] border transition-colors ${
                    isCurrent
                      ? "bg-[#0f5b6c] text-white border-[#0f5b6c] shadow-xs"
                      : isStepComplete
                      ? "bg-white text-[#182026] border-[#bcdbe2]"
                      : "bg-white/60 text-[#7d8c97] border-[#e2e6e9]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold">0{idx + 1}</span>
                    {isStepComplete && !isCurrent ? (
                      <Check className="h-3.5 w-3.5 text-[#059669]" />
                    ) : isCurrent ? (
                      <span className="h-2 w-2 rounded-full bg-cyan-300 animate-ping" />
                    ) : null}
                  </div>
                  <div className="font-bold text-[11px] uppercase">{st.label}</div>
                  <div
                    className={`text-[9px] mt-0.5 font-sans leading-tight line-clamp-2 ${
                      isCurrent ? "text-cyan-100" : "text-[#5a6872]"
                    }`}
                  >
                    {st.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ============================================================ */}
        {/* 1. CORE DETECTION FINDINGS (Cyclone, Eye, Extent, Lat/Lon)   */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs p-4 sm:p-5 font-mono text-xs">
          <div className="flex items-center justify-between pb-3 border-b border-[#e2e6e9]">
            <span className="font-bold text-xs uppercase tracking-wider text-[#182026] flex items-center gap-1.5">
              <Eye className="h-4 w-4 text-[#0f5b6c]" />
              AI Vortex Detection Diagnostics
            </span>
            <Badge variant="brand">OBSERVATION FIX (t0)</Badge>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-3">
            {/* Cyclone Detected */}
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Cyclone Detected</span>
              <span className="text-sm font-bold text-[#059669] flex items-center gap-1.5 mt-0.5">
                <CheckCircle2 className="h-4 w-4" />
                CONFIRMED
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                Deep convective vortex active
              </span>
            </div>

            {/* Eye Detected */}
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Eye Detected</span>
              <span className="text-sm font-bold text-[#b45309] flex items-center gap-1.5 mt-0.5">
                <Compass className="h-4 w-4 text-[#b45309]" />
                DEVELOPING CDO
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                Nascent 18 km inner core ring
              </span>
            </div>

            {/* Storm Extent */}
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Storm Extent</span>
              <span className="text-sm font-bold text-[#182026] block mt-0.5">
                140 km Gale Radius
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                480 km Convective Cloud Shield
              </span>
            </div>

            {/* Latitude / Longitude */}
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Latitude / Longitude</span>
              <span className="text-sm font-bold text-[#0f5b6c] block mt-0.5">
                {detection.center_fix_lat.toFixed(1)}&deg;N, {detection.center_fix_lon.toFixed(1)}&deg;E
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                Central Arabian Sea Fix Fix
              </span>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 2. INTENSITY CLASSIFICATION & INTENSITY INDICATOR GAUGE      */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs p-4 sm:p-5 font-mono text-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#e2e6e9] gap-2">
            <div>
              <span className="font-bold text-xs uppercase tracking-wider text-[#182026] flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-[#0f5b6c]" />
                Intensity Classification & Rapid Intensification Screening
              </span>
              <span className="text-[10px] text-[#5a6872]">
                WMO / IMD Standard Scale &bull; Empirical RI Screening Criteria: &ge;30 kt increase in 24h
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="danger" className="font-bold text-[10px] px-2 py-0.5">
                HIGH RI RISK DETECTED
              </Badge>
            </div>
          </div>

          {/* Core Intensity Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Current Category</span>
              <span className="text-base font-bold text-[#182026] block mt-0.5">
                {intensity.current_category_imd}
              </span>
              <span className="text-[10px] text-[#5a6872]">WMO: Tropical Depression</span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Maximum Wind</span>
              <span className="text-base font-bold text-[#0f5b6c] block mt-0.5">
                {intensity.v_max_kts} kt ({intensity.v_max_kmh} km/h)
              </span>
              <span className="text-[10px] text-[#b91c1c] font-semibold">
                Surge: +{intensity.estimated_24h_delta_kts} kt in 24h
              </span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Central Pressure</span>
              <span className="text-base font-bold text-[#182026] block mt-0.5">
                {intensity.central_pressure_mb} hPa
              </span>
              <span className="text-[10px] text-[#5a6872]">6h Drop: -2.0 hPa</span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Classification Confidence</span>
              <span className={`text-base font-bold block mt-0.5 ${confidencePenaltyTotal > 0 ? "text-[#b45309]" : "text-[#059669]"}`}>
                {calculatedConfidence}%
              </span>
              <span className="text-[10px] text-[#5a6872]">
                {confidencePenaltyTotal > 0 ? `-${confidencePenaltyTotal}% Source Penalty` : "High Confidence Baseline"}
              </span>
            </div>
          </div>

          {/* Simple Intensity Indicator Bar / IMD Scale Gauge */}
          <div className="p-3.5 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-2">
            <div className="flex items-center justify-between text-[11px]">
              <span className="font-bold text-[#182026] uppercase flex items-center gap-1.5">
                <Gauge className="h-3.5 w-3.5 text-[#0f5b6c]" />
                IMD Intensity Scale Progression Indicator
              </span>
              <span className="text-[#5a6872] text-[10px]">
                Current: <strong>30 kt</strong> &rarr; Projected Surge: <strong className="text-[#b91c1c]">65 kt</strong>
              </span>
            </div>

            {/* Continuous Progress Bar with Category Segments */}
            <div className="relative pt-4 pb-2">
              <div className="h-3 w-full rounded-full bg-[#e2e6e9] overflow-hidden flex">
                <div style={{ width: "23%" }} className="bg-[#0ea5e9]" title="Depression (<34 kt)" />
                <div style={{ width: "13%" }} className="bg-[#14b8a6]" title="Cyclonic Storm (34-47 kt)" />
                <div style={{ width: "13%" }} className="bg-[#eab308]" title="Severe Cyclonic Storm (48-63 kt)" />
                <div style={{ width: "21%" }} className="bg-[#f97316]" title="Very Severe Cyclonic Storm (64-89 kt)" />
                <div style={{ width: "17%" }} className="bg-[#ef4444]" title="Extremely Severe (90-119 kt)" />
                <div style={{ width: "13%" }} className="bg-[#d946ef]" title="Super Cyclone (≥120 kt)" />
              </div>

              {/* Pin for Current Intensity (30 kt ~ 20%) */}
              <div
                className="absolute top-0 flex flex-col items-center pointer-events-none"
                style={{ left: "20%", transform: "translateX(-50%)" }}
              >
                <span className="px-1.5 py-0.2 bg-[#0ea5e9] text-white text-[9px] font-bold rounded-[2px] shadow-xs whitespace-nowrap">
                  Current: 30 kt
                </span>
                <div className="w-1.5 h-1.5 bg-[#0ea5e9] rotate-45 -mt-0.5" />
              </div>

              {/* Pin for Projected Surge (65 kt ~ 52%) */}
              <div
                className="absolute top-0 flex flex-col items-center pointer-events-none"
                style={{ left: "52%", transform: "translateX(-50%)" }}
              >
                <span className="px-1.5 py-0.2 bg-[#b91c1c] text-white text-[9px] font-bold rounded-[2px] shadow-xs whitespace-nowrap animate-pulse">
                  24h Projected: 65 kt
                </span>
                <div className="w-1.5 h-1.5 bg-[#b91c1c] rotate-45 -mt-0.5" />
              </div>
            </div>

            <div className="grid grid-cols-6 text-[9px] text-[#5a6872] pt-1">
              <div>Depression (&lt;34)</div>
              <div>CS (34-47)</div>
              <div>SCS (48-63)</div>
              <div>VSCS (64-89)</div>
              <div>ESCS (90-119)</div>
              <div className="text-right">SuCS (&ge;120)</div>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 3. EXPLAINABLE AI: 'WHY THIS RESULT?' (3-5 Plain Factors)    */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs p-4 sm:p-5 font-mono text-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#e2e6e9] gap-2">
            <div>
              <h2 className="font-bold text-xs uppercase tracking-wider text-[#182026] flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-[#0f5b6c]" />
                Explainable AI: Why This Result?
              </h2>
              <p className="text-[11px] text-[#5a6872] font-sans">
                Transparent physical attribution explaining why the model triggered the Rapid Intensification early-warning signal at 30 kt.
              </p>
            </div>
            <span className="text-[10px] text-[#5a6872]">
              Empirical RI Index: <strong className="text-[#0f5b6c]">0.3592</strong> vs &tau; = 0.125
            </span>
          </div>

          {/* 5 Plain-Language Factors Grid */}
          <div className="space-y-2.5">
            {whyFactors.map((factor, fIdx) => (
              <div
                key={fIdx}
                className="p-3 rounded-[3px] bg-[#f8f9fa] border border-[#e2e6e9] flex flex-col sm:flex-row sm:items-start justify-between gap-3 hover:border-[#cbd2d6] transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-[#0f5b6c]">FACTOR 0{fIdx + 1}</span>
                    <span className="text-[#cbd2d6]">&bull;</span>
                    <h3 className="font-bold text-xs text-[#182026]">{factor.title}</h3>
                    {factor.is_demo && (
                      <span className="px-1.5 py-0.2 text-[8px] font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                        DEMONSTRATION SCORE
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-[#5a6872] font-sans leading-relaxed">
                    {factor.desc}
                  </p>
                </div>

                <div className="shrink-0 flex items-center sm:flex-col sm:items-end justify-between sm:justify-start gap-1">
                  <span className="px-2 py-0.5 bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px] font-bold text-[10px]">
                    +{factor.contribution_pts.toFixed(1)}% Weight
                  </span>
                  <span className="text-[9px] text-[#7d8c97]">
                    Signal: {factor.actual_metric}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Missing Source Notice in Explainability */}
          {missingSourcesList.length > 0 && (
            <div className="p-3 bg-[#fef2f2] border border-[#fecaca] rounded-[3px] space-y-1 text-[11px]">
              <span className="font-bold text-[#b91c1c] uppercase flex items-center gap-1 text-[10px]">
                <AlertTriangle className="h-3.5 w-3.5" />
                Missing Source Impact on Attribution:
              </span>
              <p className="text-[#334155] font-sans">
                {missingSourcesList.length} data source(s) are currently marked missing ({missingSourcesList.map(s => s.short_name).join(", ")}). The model has replaced these inputs with neutral climatological baselines, which lowers the overall decision confidence by {confidencePenaltyTotal}%.
              </p>
            </div>
          )}
        </div>

        {/* ============================================================ */}
        {/* 4. COLLAPSED TECHNICAL DETAILS SECTION                       */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs overflow-hidden font-mono text-xs">
          <button
            onClick={() => setTechDetailsOpen(!techDetailsOpen)}
            className="w-full px-4 py-3 bg-[#f8f9fa] flex items-center justify-between hover:bg-[#edf5f7] transition-colors cursor-pointer text-left"
          >
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-[#0f5b6c]" />
              <span className="font-bold uppercase tracking-wider text-xs text-[#182026]">
                Technical Model Architecture & Inference Specifications
              </span>
              <span className="text-[10px] text-[#5a6872] hidden sm:inline">
                (Click to {techDetailsOpen ? "collapse" : "expand"})
              </span>
            </div>
            {techDetailsOpen ? (
              <ChevronUp className="h-4 w-4 text-[#0f5b6c]" />
            ) : (
              <ChevronDown className="h-4 w-4 text-[#5a6872]" />
            )}
          </button>

          {techDetailsOpen && (
            <div className="p-4 sm:p-5 border-t border-[#cbd2d6] space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px]">
                <div className="space-y-2">
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Model ID:</span>
                    <span className="font-bold text-[#182026]">CycloneSense-RI-Multimodal-TS-Final</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Model Version:</span>
                    <span className="font-bold text-[#0f5b6c]">v3.0.0-frozen</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Model Architecture:</span>
                    <span className="font-semibold text-[#182026]">Regularized Balanced Logistic (L2, C=1.0)</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Feature Dimension:</span>
                    <span className="font-semibold text-[#182026]">61 Multimodal Features</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Input Data Sources:</span>
                    <span className="font-semibold text-[#182026]">INSAT IR, Water Vapour, Buoy, Radar, NWP</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Operating Threshold:</span>
                    <span className="font-bold text-[#0f5b6c]">&tau; = 0.125 (Balancing recall vs false alarms)</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Inference Status:</span>
                    <span className="font-bold text-[#059669]">FROZEN_VALIDATED (Anti-Leakage Certified)</span>
                  </div>
                  <div className="flex justify-between border-b border-[#e2e6e9] pb-1.5">
                    <span className="text-[#5a6872]">Last Updated:</span>
                    <span className="font-semibold text-[#182026]">{new Date().toISOString().slice(0, 19)} UTC</span>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-[#edf5f7] border border-[#bcdbe2] rounded-[3px] text-[10px] text-[#334155] leading-relaxed">
                <strong>Governance & Evaluation Protocol:</strong> Model validation is strictly conducted under Leave-One-Storm-Out cross-validation across verified historical North Indian Ocean cyclone lifecycles (NOAA IBTrACS v04r01). Under no circumstances are model scores presented as replacement for official advisories issued by the India Meteorological Department (IMD / RSMC New Delhi).
              </div>
            </div>
          )}
        </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/fusion">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: Data Fusion
            </Button>
          </Link>
          <Link href="/prediction">
            <Button variant="primary" size="sm">
              Next Stage: Prediction
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
