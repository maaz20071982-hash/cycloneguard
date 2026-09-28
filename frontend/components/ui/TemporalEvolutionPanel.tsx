"use client";

import React from "react";
import { TemporalIndicators } from "@/lib/api/cyclones";
import { Wind, Gauge, Compass, History, TrendingUp, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface TemporalEvolutionPanelProps {
  indicators: TemporalIndicators;
  rawFeatures?: Record<string, number>;
  className?: string;
}

export function TemporalEvolutionPanel({
  indicators,
  rawFeatures = {},
  className = "",
}: TemporalEvolutionPanelProps) {
  const dv6 = indicators.wind_change_6h_kts ?? rawFeatures["temp_delta_wind_6h_val"];
  const dv12 = indicators.wind_change_12h_kts ?? rawFeatures["temp_delta_wind_12h_val"];
  const mslp = indicators.central_pressure_mb ?? rawFeatures["track_pressure_val"];
  const dp6 = indicators.pressure_drop_6h_mb ?? rawFeatures["temp_delta_pressure_6h_val"];
  const vtrans = indicators.translation_speed_kts ?? rawFeatures["track_translation_speed_kts_val"];
  const bearing = indicators.translation_bearing_deg ?? rawFeatures["track_translation_bearing_deg_val"];
  const heading = indicators.translation_heading ?? "—";
  const accel = rawFeatures["temp_wind_change_rate_per_hour_val"];

  return (
    <div className={`border border-[#e2e6e9] bg-[#ffffff] p-5 rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-4 ${className}`}>
      {/* Header with mandatory attribution label */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#e2e6e9]">
        <div>
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-[#0f5b6c]" />
            <h3 className="text-sm font-bold tracking-tight text-[#182026] font-mono uppercase">
              Temporal Evolution & Kinematics
            </h3>
          </div>
          <p className="text-[11px] text-[#5f6b7c] mt-0.5">
            Prior observational indicators extracted from best-track time-series history at observation time.
          </p>
        </div>

        <span className="bg-[#edf5f7] border border-[#0f5b6c]/30 text-[#0f5b6c] text-[10px] font-mono font-semibold px-2 py-1 rounded-[3px] shrink-0">
          Derived from observation history
        </span>
      </div>

      {/* Grid of Verified Indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* 1. Current Intensity Vmax */}
        <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between text-xs text-[#5f6b7c] mb-1">
            <span className="font-mono text-[10px] uppercase">Current Intensity (V0)</span>
            <Wind className="h-3.5 w-3.5 text-[#0f5b6c]" />
          </div>
          <div className="text-lg font-bold text-[#182026] font-mono">
            {indicators.current_wind_kts} <span className="text-xs font-normal text-[#5f6b7c]">kt</span>
          </div>
          <div className="text-[10px] text-[#5f6b7c] mt-1 font-mono">
            Feature: track_wind_speed_val
          </div>
        </div>

        {/* 2. Prior 6h Wind Change */}
        <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between text-xs text-[#5f6b7c] mb-1">
            <span className="font-mono text-[10px] uppercase">6h Wind Change (ΔV6)</span>
            {dv6 !== undefined && dv6 > 0 ? (
              <ArrowUpRight className="h-3.5 w-3.5 text-[#cf1322]" />
            ) : dv6 !== undefined && dv6 < 0 ? (
              <ArrowDownRight className="h-3.5 w-3.5 text-[#389e0d]" />
            ) : (
              <Minus className="h-3.5 w-3.5 text-[#5f6b7c]" />
            )}
          </div>
          <div className="text-lg font-bold text-[#182026] font-mono">
            {dv6 !== undefined ? `${dv6 > 0 ? "+" : ""}${dv6}` : "—"}{" "}
            <span className="text-xs font-normal text-[#5f6b7c]">kt / 6h</span>
          </div>
          <div className="text-[10px] text-[#5f6b7c] mt-1 font-mono">
            Feature: temp_delta_wind_6h_val
          </div>
        </div>

        {/* 3. Prior 12h Wind Change */}
        <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between text-xs text-[#5f6b7c] mb-1">
            <span className="font-mono text-[10px] uppercase">12h Wind Change (ΔV12)</span>
            {dv12 !== undefined && dv12 > 0 ? (
              <ArrowUpRight className="h-3.5 w-3.5 text-[#cf1322]" />
            ) : dv12 !== undefined && dv12 < 0 ? (
              <ArrowDownRight className="h-3.5 w-3.5 text-[#389e0d]" />
            ) : (
              <Minus className="h-3.5 w-3.5 text-[#5f6b7c]" />
            )}
          </div>
          <div className="text-lg font-bold text-[#182026] font-mono">
            {dv12 !== undefined ? `${dv12 > 0 ? "+" : ""}${dv12}` : "—"}{" "}
            <span className="text-xs font-normal text-[#5f6b7c]">kt / 12h</span>
          </div>
          <div className="text-[10px] text-[#5f6b7c] mt-1 font-mono">
            Feature: temp_delta_wind_12h_val
          </div>
        </div>

        {/* 4. Central Pressure */}
        <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between text-xs text-[#5f6b7c] mb-1">
            <span className="font-mono text-[10px] uppercase">Central Pressure (MSLP)</span>
            <Gauge className="h-3.5 w-3.5 text-[#0f5b6c]" />
          </div>
          <div className="text-lg font-bold text-[#182026] font-mono">
            {mslp !== undefined && mslp !== null ? mslp : "—"}{" "}
            <span className="text-xs font-normal text-[#5f6b7c]">hPa</span>
          </div>
          <div className="text-[10px] text-[#5f6b7c] mt-1 font-mono">
            Feature: track_pressure_val
          </div>
        </div>
      </div>

      {/* Second Row: Motion & Acceleration Indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        {/* Translation Speed & Heading */}
        <div className="p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px]">
          <div className="flex items-center gap-1.5 text-xs text-[#5f6b7c] mb-1">
            <Compass className="h-3.5 w-3.5 text-[#0f5b6c]" />
            <span className="font-mono text-[10px] uppercase font-bold">Vortex Translation</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-[#182026] font-mono">
              {vtrans !== undefined ? vtrans : "—"} kt
            </span>
            <span className="text-xs font-mono text-[#5f6b7c]">
              bearing {bearing !== undefined ? `${bearing}°` : "—"} ({heading})
            </span>
          </div>
          <span className="text-[10px] text-[#8a9ba8] font-mono block mt-1">
            Features: track_translation_speed_kts_val, bearing
          </span>
        </div>

        {/* Pressure Tendency */}
        <div className="p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px]">
          <div className="flex items-center gap-1.5 text-xs text-[#5f6b7c] mb-1">
            <Gauge className="h-3.5 w-3.5 text-[#0f5b6c]" />
            <span className="font-mono text-[10px] uppercase font-bold">6h Pressure Tendency</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-[#182026] font-mono">
              {dp6 !== undefined ? `${dp6 > 0 ? "+" : ""}${dp6} hPa` : "0.0 hPa"}
            </span>
            <span className="text-xs font-mono text-[#5f6b7c]">
              {dp6 && dp6 < 0 ? "Deepening" : "Steady"}
            </span>
          </div>
          <span className="text-[10px] text-[#8a9ba8] font-mono block mt-1">
            Feature: temp_delta_pressure_6h_val
          </span>
        </div>

        {/* Intensification Acceleration */}
        <div className="p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px]">
          <div className="flex items-center gap-1.5 text-xs text-[#5f6b7c] mb-1">
            <TrendingUp className="h-3.5 w-3.5 text-[#0f5b6c]" />
            <span className="font-mono text-[10px] uppercase font-bold">Rate of Change</span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-[#182026] font-mono">
              {accel !== undefined ? `${accel} kt/hr` : "0.0 kt/hr"}
            </span>
            <span className="text-xs font-mono text-[#5f6b7c]">Instantaneous</span>
          </div>
          <span className="text-[10px] text-[#8a9ba8] font-mono block mt-1">
            Feature: temp_wind_change_rate_per_hour_val
          </span>
        </div>
      </div>
    </div>
  );
}
