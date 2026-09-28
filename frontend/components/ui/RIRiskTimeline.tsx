"use client";

import React, { useState } from "react";
import { TimelineObservation } from "@/lib/api/cyclones";
import { Activity, AlertTriangle, ShieldCheck } from "lucide-react";

interface RIRiskTimelineProps {
  timeline: TimelineObservation[];
  selectedObservationTime: string;
  onSelectObservation: (obsTime: string) => void;
  className?: string;
}

export function RIRiskTimeline({
  timeline,
  selectedObservationTime,
  onSelectObservation,
  className = "",
}: RIRiskTimelineProps) {
  const [hoveredPoint, setHoveredPoint] = useState<TimelineObservation | null>(null);

  if (!timeline || timeline.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-[#5f6b7c] font-mono border border-dashed border-[#e2e6e9] bg-[#f8f9fa] rounded-[4px]">
        No observations available for RI evolution chart.
      </div>
    );
  }

  // Filter out any observations missing the risk index
  const validPoints = timeline.filter((t) => t.ri_risk_index !== null && t.ri_risk_index !== undefined);
  if (validPoints.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-[#5f6b7c] font-mono border border-dashed border-[#e2e6e9] bg-[#f8f9fa] rounded-[4px]">
        Empirical RI Risk Index has not been evaluated for these observations.
      </div>
    );
  }

  // Chart layout dimensions
  const width = 800;
  const height = 240;
  const padding = { top: 25, right: 30, bottom: 40, left: 50 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  // Values and scaling
  const tau = 0.125;
  const maxScore = Math.max(0.5, ...validPoints.map((p) => p.ri_risk_index || 0));
  const minScore = 0.0;

  const getY = (score: number) => {
    const ratio = (score - minScore) / (maxScore - minScore);
    return padding.top + plotHeight - ratio * plotHeight;
  };

  const getX = (index: number) => {
    if (validPoints.length === 1) return padding.left + plotWidth / 2;
    return padding.left + (index / (validPoints.length - 1)) * plotWidth;
  };

  const tauY = getY(tau);

  // Build SVG path
  const linePath = validPoints
    .map((p, idx) => {
      const x = getX(idx);
      const y = getY(p.ri_risk_index || 0);
      return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");

  // Y-axis grid ticks
  const yTicks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5].filter((v) => v <= maxScore);

  return (
    <div className={`border border-[#e2e6e9] bg-[#ffffff] p-5 rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-4 ${className}`}>
      {/* Title & Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#e2e6e9]">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#0f5b6c]" />
            <h3 className="text-sm font-bold tracking-tight text-[#182026] font-mono uppercase">
              Empirical RI Risk Index Evolution
            </h3>
          </div>
          <p className="text-[11px] text-[#5f6b7c] mt-0.5">
            Model risk index trajectory across storm lifecycle relative to frozen operating threshold.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#389e0d]" />
            <span className="text-[#5f6b7c]">Below τ (&lt; 0.125)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#cf1322]" />
            <span className="text-[#5f6b7c]">Elevated RI Risk (≥ 0.125)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-5 border-t-2 border-dashed border-[#cf1322]" />
            <span className="text-[#182026] font-semibold">τ = 0.125</span>
          </div>
        </div>
      </div>

      {/* SVG Plot */}
      <div className="relative w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto min-w-[600px] select-none"
        >
          {/* Background Gradient / Shading for Elevated Risk Zone */}
          <rect
            x={padding.left}
            y={padding.top}
            width={plotWidth}
            height={tauY - padding.top}
            fill="#fff1f0"
            fillOpacity={0.4}
          />
          <rect
            x={padding.left}
            y={tauY}
            width={plotWidth}
            height={padding.top + plotHeight - tauY}
            fill="#f6ffed"
            fillOpacity={0.2}
          />

          {/* Grid lines (horizontal) */}
          {yTicks.map((tick) => {
            const y = getY(tick);
            return (
              <g key={tick}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={padding.left + plotWidth}
                  y2={y}
                  stroke="#e2e6e9"
                  strokeDasharray="3 3"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[10px] font-mono fill-[#8a9ba8]"
                >
                  {tick.toFixed(2)}
                </text>
              </g>
            );
          })}

          {/* Operating Threshold τ = 0.125 Line */}
          <line
            x1={padding.left}
            y1={tauY}
            x2={padding.left + plotWidth}
            y2={tauY}
            stroke="#cf1322"
            strokeWidth={1.5}
            strokeDasharray="6 4"
          />
          <text
            x={padding.left + plotWidth - 4}
            y={tauY - 6}
            textAnchor="end"
            className="text-[10px] font-mono font-bold fill-[#cf1322]"
          >
            FROZEN OPERATING THRESHOLD: τ = 0.125
          </text>

          {/* Connective Line Path */}
          <path
            d={linePath}
            fill="none"
            stroke="#0f5b6c"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Data Points */}
          {validPoints.map((point, idx) => {
            const x = getX(idx);
            const score = point.ri_risk_index || 0;
            const y = getY(score);
            const isAbove = score >= tau;
            const isSelected = point.observation_time === selectedObservationTime;

            return (
              <g
                key={point.observation_time}
                className="cursor-pointer"
                onClick={() => onSelectObservation(point.observation_time)}
                onMouseEnter={() => setHoveredPoint(point)}
                onMouseLeave={() => setHoveredPoint(null)}
              >
                {/* Outer Ring if Selected */}
                {isSelected && (
                  <circle
                    cx={x}
                    cy={y}
                    r={8}
                    fill="none"
                    stroke="#0f5b6c"
                    strokeWidth={2.5}
                    className="animate-pulse"
                  />
                )}

                {/* Point Marker */}
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 5 : 3.5}
                  fill={isAbove ? "#cf1322" : "#389e0d"}
                  stroke="#ffffff"
                  strokeWidth={1.5}
                />
              </g>
            );
          })}

          {/* X Axis Baseline */}
          <line
            x1={padding.left}
            y1={padding.top + plotHeight}
            x2={padding.left + plotWidth}
            y2={padding.top + plotHeight}
            stroke="#b0bac5"
            strokeWidth={1}
          />

          {/* X Axis Time Labels (Sampled to avoid overlapping) */}
          {validPoints.map((point, idx) => {
            // Show every Nth label or endpoints
            const step = Math.max(1, Math.floor(validPoints.length / 6));
            if (idx % step !== 0 && idx !== validPoints.length - 1) return null;

            const x = getX(idx);
            const timeLabel = point.observation_time.replace("T", " ").replace(":00Z", "Z").slice(5);

            return (
              <text
                key={point.observation_time}
                x={x}
                y={padding.top + plotHeight + 18}
                textAnchor="middle"
                className="text-[9px] font-mono fill-[#5f6b7c]"
              >
                {timeLabel}
              </text>
            );
          })}
        </svg>

        {/* Hover / Active Tooltip Overlay */}
        {(hoveredPoint || selectedObservationTime) && (
          <div className="mt-2 text-xs font-mono flex items-center justify-between bg-[#f8f9fa] border border-[#e2e6e9] px-3 py-1.5 rounded-[3px]">
            {(() => {
              const active = hoveredPoint || validPoints.find((p) => p.observation_time === selectedObservationTime);
              if (!active) return null;
              const isAbove = (active.ri_risk_index || 0) >= tau;
              return (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-[#5f6b7c]">Fix:</span>
                    <span className="font-bold text-[#182026]">
                      {active.observation_time.replace("T", " ")}
                    </span>
                    <span className="text-[#5f6b7c]">|</span>
                    <span className="text-[#5f6b7c]">Vmax:</span>
                    <span className="font-bold text-[#182026]">{active.current_wind_kts} kt</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[#5f6b7c]">Empirical RI Risk Index:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded-[2px] ${isAbove ? "bg-[#fff1f0] text-[#cf1322]" : "bg-[#f6ffed] text-[#389e0d]"}`}>
                      {(active.ri_risk_index || 0).toFixed(4)}
                    </span>
                    <span className="text-[10px] text-[#5f6b7c]">
                      ({isAbove ? "Elevated Risk ≥ 0.125" : "Low Risk < 0.125"})
                    </span>
                  </div>
                </>
              );
            })()}
          </div>
        )}
      </div>

      <div className="text-[11px] text-[#5f6b7c] flex items-center justify-between border-t border-[#e2e6e9] pt-2">
        <span>X axis: Observation time UTC · Y axis: Empirical RI Risk Index</span>
        <span className="font-mono text-[#0f5b6c] font-semibold">Strictly Empirical Index · Not a Calibrated Probability</span>
      </div>
    </div>
  );
}
