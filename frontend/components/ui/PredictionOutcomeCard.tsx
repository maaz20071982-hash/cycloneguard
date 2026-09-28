"use client";

import React from "react";
import { WhatTheModelSawData, HistoricalOutcome } from "@/lib/api/cyclones";
import { Eye, CheckCircle2, XCircle, AlertTriangle, ShieldCheck, ArrowRight, Gauge, Wind, Clock } from "lucide-react";

interface PredictionOutcomeCardProps {
  whatTheModelSaw: WhatTheModelSawData;
  historicalOutcome: HistoricalOutcome;
  className?: string;
}

export function PredictionOutcomeCard({
  whatTheModelSaw,
  historicalOutcome,
  className = "",
}: PredictionOutcomeCardProps) {
  const modelScore = whatTheModelSaw.model_score;
  const isElevated = modelScore.ri_flag;
  const riOccurred = historicalOutcome.ri_occurred;

  // Comparison evaluation: did model signal align with historical outcome?
  const isMatch = (isElevated && riOccurred) || (!isElevated && !riOccurred);

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* ======================================================== */}
        {/* SECTION A: WHAT THE MODEL SAW (Observation Time t0)      */}
        {/* ======================================================== */}
        <div className="border border-[#0f5b6c]/40 bg-[#ffffff] rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden flex flex-col justify-between">
          <div>
            {/* Header */}
            <div className="bg-[#edf5f7] border-b border-[#0f5b6c]/20 p-3.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-[#0f5b6c]" />
                <span className="font-mono font-bold text-xs uppercase tracking-wider text-[#0f5b6c]">
                  Section A: What the Model Saw
                </span>
              </div>
              <span className="text-[10px] font-mono bg-[#ffffff] border border-[#0f5b6c]/30 text-[#0f5b6c] px-2 py-0.5 rounded-[2px]">
                Observation Time (t₀)
              </span>
            </div>

            {/* Content */}
            <div className="p-4 space-y-4">
              <div className="flex items-baseline justify-between border-b border-[#e2e6e9] pb-3">
                <div>
                  <span className="text-[10px] text-[#5f6b7c] font-mono uppercase block">
                    Fix Timestamp
                  </span>
                  <span className="text-sm font-bold text-[#182026] font-mono">
                    {whatTheModelSaw.observation_time_utc.replace("T", " ")}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-[#5f6b7c] font-mono uppercase block">
                    Vortex Center
                  </span>
                  <span className="text-xs font-mono text-[#182026]">
                    {whatTheModelSaw.latitude}°N, {whatTheModelSaw.longitude}°E
                  </span>
                </div>
              </div>

              {/* Observed Inputs Summary */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">Current Wind (V0)</span>
                  <span className="text-base font-bold text-[#182026]">
                    {whatTheModelSaw.temporal_indicators.current_wind_kts} kt
                  </span>
                </div>
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">Central Pressure (P0)</span>
                  <span className="text-base font-bold text-[#182026]">
                    {whatTheModelSaw.temporal_indicators.central_pressure_mb ?? "—"} hPa
                  </span>
                </div>
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">HURSAT-B1 Satellite</span>
                  <span className="text-xs font-bold text-[#0f5b6c] truncate block">
                    {whatTheModelSaw.satellite_evidence.channels_available.join(" + ")}
                  </span>
                </div>
                <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">Multimodal Features</span>
                  <span className="text-xs font-bold text-[#182026]">
                    61 Inputs (23 TS + 38 Spatial)
                  </span>
                </div>
              </div>

              {/* Model Output at Observation Time */}
              <div className="p-3 border border-[#cbd2d6] bg-[#f8f9fa] rounded-[3px] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-[#5f6b7c]">
                    Empirical RI Risk Index:
                  </span>
                  <span className={`text-base font-mono font-bold px-2 py-0.5 rounded-[2px] ${
                    isElevated ? "bg-[#fff1f0] text-[#cf1322] border border-[#ffa39e]" : "bg-[#f6ffed] text-[#389e0d] border border-[#b7eb8f]"
                  }`}>
                    {modelScore.ri_risk_index.toFixed(4)}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#5f6b7c]">Operating Threshold:</span>
                  <span className="text-[#182026] font-semibold">τ = {modelScore.operating_threshold}</span>
                </div>

                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#5f6b7c]">Decision Category:</span>
                  <span className={`font-bold ${isElevated ? "text-[#cf1322]" : "text-[#389e0d]"}`}>
                    {modelScore.risk_category}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="px-4 py-2.5 bg-[#f8f9fa] border-t border-[#e2e6e9] text-[10px] text-[#5f6b7c] font-mono">
            Model: {modelScore.model_name} ({modelScore.model_version})
          </div>
        </div>

        {/* ======================================================== */}
        {/* SECTION B: WHAT HAPPENED AFTERWARD (Historical Outcome)  */}
        {/* ======================================================== */}
        <div className="border-2 border-[#b45309] bg-[#ffffff] rounded-[4px] shadow-[0_2px_6px_rgba(180,83,9,0.12)] overflow-hidden flex flex-col justify-between">
          <div>
            {/* Header with explicit separation label */}
            <div className="bg-[#fef3c7] border-b border-[#f59e0b]/40 p-3.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-[#b45309]" />
                <span className="font-mono font-bold text-xs uppercase tracking-wider text-[#b45309]">
                  Section B: Historical 24h Outcome
                </span>
              </div>
              <span className="text-[10px] font-mono bg-[#b45309] text-[#ffffff] px-2 py-0.5 rounded-[2px] font-bold">
                GROUND TRUTH (t₀ + 24h)
              </span>
            </div>

            {/* Prominent Non-Lookahead Warning */}
            <div className="bg-[#fffbeb] border-b border-[#fef3c7] p-2.5 text-center">
              <span className="text-[10px] font-mono font-bold text-[#b45309] uppercase tracking-wide">
                HISTORICAL OUTCOME — NOT USED AS MODEL INPUT
              </span>
            </div>

            {/* Content */}
            <div className="p-4 space-y-4">
              <div className="flex items-baseline justify-between border-b border-[#e2e6e9] pb-3">
                <div>
                  <span className="text-[10px] text-[#5f6b7c] font-mono uppercase block">
                    Verification Time (t₀ + 24h)
                  </span>
                  <span className="text-sm font-bold text-[#182026] font-mono">
                    {historicalOutcome.verification_time_24h.replace("T", " ")}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-[#5f6b7c] font-mono uppercase block">
                    WMO RI Threshold
                  </span>
                  <span className="text-xs font-mono font-semibold text-[#182026]">
                    ΔV ≥ 30 kt / 24h
                  </span>
                </div>
              </div>

              {/* Observed Ground Truth Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-3 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">Future Intensity (V24)</span>
                  <span className="text-xl font-bold text-[#182026]">
                    {historicalOutcome.observed_future_wind_kts} kt
                  </span>
                  <span className="text-[9px] text-[#5f6b7c] block mt-0.5">
                    at t₀ + 24 hours
                  </span>
                </div>

                <div className="p-3 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px]">
                  <span className="block text-[9px] text-[#5f6b7c]">Observed 24h Change (ΔV24)</span>
                  <span className={`text-xl font-bold ${
                    historicalOutcome.observed_delta_v_24h >= 30 ? "text-[#cf1322]" : "text-[#182026]"
                  }`}>
                    {historicalOutcome.observed_delta_v_24h >= 0 ? "+" : ""}
                    {historicalOutcome.observed_delta_v_24h} kt
                  </span>
                  <span className="text-[9px] text-[#5f6b7c] block mt-0.5">
                    net 24h intensification
                  </span>
                </div>
              </div>

              {/* RI Ground Truth Result Card */}
              <div className={`p-3.5 border rounded-[3px] flex items-center justify-between ${
                riOccurred ? "border-[#ffa39e] bg-[#fff1f0]" : "border-[#b7eb8f] bg-[#f6ffed]"
              }`}>
                <div>
                  <span className="text-[10px] uppercase font-mono font-bold text-[#5f6b7c] block">
                    Actual Reanalysis Ground Truth
                  </span>
                  <span className={`text-base font-bold font-mono ${riOccurred ? "text-[#cf1322]" : "text-[#389e0d]"}`}>
                    {riOccurred ? "RAPID INTENSIFICATION OCCURRED (RI+)" : "NO RAPID INTENSIFICATION (RI-)"}
                  </span>
                </div>
                {riOccurred ? (
                  <AlertTriangle className="h-6 w-6 text-[#cf1322] shrink-0" />
                ) : (
                  <ShieldCheck className="h-6 w-6 text-[#389e0d] shrink-0" />
                )}
              </div>
            </div>
          </div>

          {/* Verification Disclaimer */}
          <div className="px-4 py-2.5 bg-[#fef3c7]/60 border-t border-[#f59e0b]/30 text-[10px] text-[#7d5a00] font-mono leading-relaxed">
            {historicalOutcome.disclaimer}
          </div>
        </div>
      </div>

      {/* Synthesis Evaluation Banner */}
      <div className={`p-3.5 border rounded-[4px] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono ${
        isMatch ? "bg-[#f6ffed] border-[#b7eb8f] text-[#274916]" : "bg-[#fffbe6] border-[#ffe58f] text-[#874d00]"
      }`}>
        <div className="flex items-center gap-2">
          {isMatch ? (
            <CheckCircle2 className="h-5 w-5 text-[#389e0d] shrink-0" />
          ) : (
            <AlertTriangle className="h-5 w-5 text-[#d48806] shrink-0" />
          )}
          <div>
            <span className="font-bold uppercase text-[11px] block">
              {isMatch ? "Scientific Verification: Model Signal Aligned with Outcome" : "Scientific Verification: Divergent Empirical Signal"}
            </span>
            <span className="text-[11px] opacity-90">
              {isElevated && riOccurred
                ? `Model risk index ${modelScore.ri_risk_index.toFixed(4)} exceeded operating threshold (τ = 0.125), identifying the observed +${historicalOutcome.observed_delta_v_24h} kt escalation.`
                : !isElevated && !riOccurred
                ? `Model risk index ${modelScore.ri_risk_index.toFixed(4)} stayed below operating threshold (τ = 0.125), correctly indicating non-RI baseline (ΔV = +${historicalOutcome.observed_delta_v_24h} kt).`
                : isElevated && !riOccurred
                ? `Model risk index ${modelScore.ri_risk_index.toFixed(4)} flagged elevated risk, but observed ΔV was ${historicalOutcome.observed_delta_v_24h} kt.`
                : `Model risk index ${modelScore.ri_risk_index.toFixed(4)} was below threshold, but historical storm intensified by +${historicalOutcome.observed_delta_v_24h} kt.`}
            </span>
          </div>
        </div>
        <span className="text-[10px] uppercase font-bold px-2 py-1 bg-[#ffffff] border border-current rounded shrink-0">
          Historical Benchmark Reanalysis
        </span>
      </div>
    </div>
  );
}
