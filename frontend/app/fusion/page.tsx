"use client";

import React from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import {
  Layers,
  Database,
  Radio,
  Satellite,
  ShieldCheck,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Activity,
  AlertTriangle,
  Play,
  RotateCcw,
  Check,
  HelpCircle,
  Cpu,
} from "lucide-react";

export default function DataFusionPage() {
  const {
    currentStorm,
    selectStorm,
    availableStorms,
    observationSources,
    setSourceStatus,
    isFusing,
    fusionSequence,
    fusionComplete,
    triggerFusion,
    missingSourcesList,
    calculatedConfidence,
    confidencePenaltyTotal,
  } = useStorm();

  const fusion = currentStorm.multi_source_fusion;
  const activeSourcesCount = observationSources.filter((s) => s.status !== "Missing").length;
  const totalSourcesCount = observationSources.length;
  const dataCoveragePct = Number(((activeSourcesCount / totalSourcesCount) * 100).toFixed(1));

  const sequenceSteps = [
    { id: "receiving", label: "Receiving", desc: "Streaming raw satellite, buoy, and radar telemetric packets" },
    { id: "validating", label: "Validating", desc: "Verifying checksums and asserting temporal order at t0" },
    { id: "aligning", label: "Aligning", desc: "Re-projecting to WGS84 Mercator grid (±1.4 km sub-pixel match)" },
    { id: "fusing", label: "Fusing", desc: "Concatenating 23 kinematic + 38 spatial proxies with zero leakage" },
    { id: "complete", label: "Complete", desc: "61-feature multimodal observation tensor locked for inference" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/fusion" />

        {/* Stage Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 02 · MULTI-SOURCE OBSERVATION FUSION
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              6-Channel Multi-Source Observation Fusion
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5 font-mono">
              Integrating calibrated radiometry, ocean buoys, Doppler radar, and historical baselines for Cyclone {currentStorm.storm_name}.
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

            {/* Fuse Button */}
            <Button
              variant="primary"
              size="md"
              onClick={triggerFusion}
              disabled={isFusing}
              className="shadow-sm font-mono font-bold tracking-wider uppercase text-xs"
            >
              {isFusing ? (
                <>
                  <RotateCcw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Fusing Sensors...
                </>
              ) : (
                <>
                  <Layers className="h-3.5 w-3.5 mr-1.5" />
                  FUSE OBSERVATIONS
                </>
              )}
            </Button>
          </div>
        </div>

        {/* ============================================================ */}
        {/* PROGRESS SEQUENCE: Receiving → Validating → Aligning → Fusing → Complete */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#0f5b6c]/30 bg-[#edf5f7] p-4 shadow-xs font-mono text-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#0f5b6c] uppercase text-[11px] flex items-center gap-1.5">
              <Activity className="h-4 w-4" />
              Pipeline Fusion Sequence: Receiving &rarr; Validating &rarr; Aligning &rarr; Fusing &rarr; Complete
            </span>
            <span className="text-[10px] text-[#5a6872]">
              Status:{" "}
              <strong className="text-[#0f5b6c] uppercase">
                {fusionSequence === "complete"
                  ? "FUSION COMPLETED"
                  : fusionSequence === "idle"
                  ? "STANDBY · READY TO FUSE"
                  : `${fusionSequence.toUpperCase()}...`}
              </strong>
            </span>
          </div>

            {/* Visual Stepper */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {sequenceSteps.map((st, sIdx) => {
                const isStepComplete =
                  fusionSequence === "complete" ||
                  (fusionSequence === "fusing" && sIdx < 3) ||
                  (fusionSequence === "aligning" && sIdx < 2) ||
                  (fusionSequence === "validating" && sIdx < 1);

                const isCurrent = fusionSequence === st.id;

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
                      <span className="text-[10px] font-bold">0{sIdx + 1}</span>
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
        {/* FINAL FUSION SUMMARY (Sources Integrated, Data Coverage, Status) */}
        {/* ============================================================ */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs p-4 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#e2e6e9] gap-2">
            <span className="font-bold text-xs uppercase tracking-wider text-[#182026] flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-[#0f5b6c]" />
              Observation Tensor Summary & Anti-Leakage Audit
            </span>
            <span className="text-[10px] text-[#5a6872]">
              Strict Causal Cutoff: {currentStorm.observation_time_utc.replace("T", " ").slice(0, 16)} UTC
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-3">
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Sources Integrated</span>
              <span className="text-xl font-bold text-[#0f5b6c]">
                {activeSourcesCount} / {totalSourcesCount}
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                {totalSourcesCount - activeSourcesCount === 0
                  ? "All 6 Channels Active"
                  : `${totalSourcesCount - activeSourcesCount} Channel Missing`}
              </span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Data Coverage</span>
              <span className={`text-xl font-bold ${dataCoveragePct < 85 ? "text-[#b45309]" : "text-[#1b7a4f]"}`}>
                {dataCoveragePct}%
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                Spatial-Temporal Completeness
              </span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Fusion Status</span>
              <div className="mt-1">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-[2px] bg-[#ecfdf5] text-[#059669] border border-[#a7f3d0] font-bold text-[10px]">
                  <CheckCircle2 className="h-3 w-3" />
                  {fusionComplete ? "FUSION_COMPLETE" : "READY_FOR_FUSION"}
                </span>
              </div>
              <span className="text-[9px] text-[#5a6872] block mt-1">
                Zero Forward-Looking Leakage
              </span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Downstream Confidence</span>
              <span className={`text-xl font-bold ${confidencePenaltyTotal > 0 ? "text-[#b45309]" : "text-[#059669]"}`}>
                {calculatedConfidence}%
              </span>
              <span className="text-[10px] text-[#5a6872] block mt-0.5">
                {confidencePenaltyTotal > 0
                  ? `-${confidencePenaltyTotal}% Penalty Applied`
                  : "Nominal Model Baseline"}
              </span>
            </div>
          </div>

          {/* Missing Source Downstream Explanation Banner */}
          {missingSourcesList.length > 0 && (
            <div className="mt-3 p-3 bg-[#fef2f2] border border-[#fecaca] rounded-[3px] space-y-1.5">
              <div className="flex items-center gap-1.5 text-[#b91c1c] font-bold text-xs">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>Impact of Missing Data Sources on Model Confidence:</span>
              </div>
              <ul className="space-y-1 text-[11px] text-[#334155] font-sans pl-1">
                {missingSourcesList.map((ms) => (
                  <li key={ms.id} className="flex items-start gap-1.5">
                    <span className="text-[#b91c1c] font-bold shrink-0">&bull;</span>
                    <span>
                      <strong className="text-[#182026] font-mono">{ms.short_name}:</strong>{" "}
                      {ms.missing_impact_text}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* ============================================================ */}
        {/* 6 MANDATORY SOURCE CARDS                                     */}
        {/* ============================================================ */}
        <div className="space-y-3 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider text-[#182026]">
                Observation Sources & Telemetry Ingestion (6 Channels)
              </h2>
              <p className="text-[11px] text-[#5a6872]">
                Inspect status and click badges to simulate sensor dropouts and test explainable confidence impact.
              </p>
            </div>
            <span className="text-[10px] text-[#5a6872]">
              Interactive Simulation Toggle
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {observationSources.map((source) => {
              const isAvailable = source.status === "Available";
              const isDemo = source.status === "Demo";
              const isMissing = source.status === "Missing";

              return (
                <div
                  key={source.id}
                  className={`p-4 rounded-[4px] border bg-white shadow-xs flex flex-col justify-between space-y-3 transition-colors ${
                    isMissing
                      ? "border-[#fca5a5] bg-[#fffbfb]"
                      : isDemo
                      ? "border-[#fed7aa]"
                      : "border-[#cbd2d6]"
                  }`}
                >
                  <div className="space-y-2">
                    {/* Top Row: Name and Status Badge */}
                    <div className="flex items-start justify-between gap-2 border-b border-[#e2e6e9] pb-2">
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px] font-bold uppercase text-[#0f5b6c]">
                            {source.category}
                          </span>
                          <span className="text-[#cbd2d6]">&bull;</span>
                          <span className="text-[10px] text-[#5a6872]">{source.resolution}</span>
                        </div>
                        <h3 className="font-bold text-xs text-[#182026] mt-0.5 leading-tight">
                          {source.short_name}
                        </h3>
                      </div>

                      {/* Status Tag */}
                      <span
                        className={`px-2 py-0.5 rounded-[2px] font-bold text-[10px] uppercase whitespace-nowrap ${
                          isAvailable
                            ? "bg-[#ecfdf5] text-[#059669] border border-[#a7f3d0]"
                            : isDemo
                            ? "bg-[#fef3c7] text-[#b45309] border border-[#fde68a]"
                            : "bg-[#fee2e2] text-[#b91c1c] border border-[#fecaca]"
                        }`}
                      >
                        {source.status}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-[11px] text-[#5a6872] font-sans leading-relaxed">
                      {source.description}
                    </p>

                    {/* Metric & Latency */}
                    <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] text-[10px] space-y-1">
                      <div className="flex justify-between">
                        <span className="text-[#5a6872]">Telemetry Latency:</span>
                        <span className="font-semibold text-[#182026]">{source.latency_minutes} min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#5a6872]">Quality Diagnostic:</span>
                        <span className="font-semibold text-[#0f5b6c]">{source.quality_metric}</span>
                      </div>
                    </div>

                    {/* Missing Impact Notice (Only if marked Missing) */}
                    {isMissing && (
                      <div className="p-2 rounded-[2px] bg-[#fef2f2] border border-[#fecaca] text-[10px] text-[#b91c1c]">
                        <strong>Confidence Impact:</strong> {source.missing_impact_text}
                      </div>
                    )}
                  </div>

                  {/* Interactive Status Switcher */}
                  <div className="pt-2 border-t border-[#e2e6e9] flex items-center justify-between text-[10px]">
                    <span className="text-[#5a6872]">Simulate Sensor:</span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setSourceStatus(source.id, "Available")}
                        className={`px-1.5 py-0.5 rounded-[2px] cursor-pointer transition-colors ${
                          isAvailable
                            ? "bg-[#059669] text-white font-bold"
                            : "bg-[#f1f3f4] text-[#5a6872] hover:bg-[#e2e6e9]"
                        }`}
                      >
                        Avail
                      </button>
                      <button
                        onClick={() => setSourceStatus(source.id, "Demo")}
                        className={`px-1.5 py-0.5 rounded-[2px] cursor-pointer transition-colors ${
                          isDemo
                            ? "bg-[#b45309] text-white font-bold"
                            : "bg-[#f1f3f4] text-[#5a6872] hover:bg-[#e2e6e9]"
                        }`}
                      >
                        Demo
                      </button>
                      <button
                        onClick={() => setSourceStatus(source.id, "Missing")}
                        className={`px-1.5 py-0.5 rounded-[2px] cursor-pointer transition-colors ${
                          isMissing
                            ? "bg-[#b91c1c] text-white font-bold"
                            : "bg-[#f1f3f4] text-[#5a6872] hover:bg-[#e2e6e9]"
                        }`}
                      >
                        Missing
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: Dashboard
            </Button>
          </Link>
          <Link href="/analysis">
            <Button variant="primary" size="sm">
              Next Stage: AI Analysis
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
