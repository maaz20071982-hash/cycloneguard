import React from "react";
import { cn } from "@/lib/utils";

export interface MetricProps {
  label: string;
  value: React.ReactNode;
  unit?: string;
  trend?: string;
  trendDirection?: "increasing" | "decreasing" | "steady" | "neutral";
  trendLabel?: string;
  detail?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function Metric({
  label,
  value,
  unit,
  trend,
  trendDirection = "neutral",
  trendLabel,
  detail,
  className,
  size = "md",
}: MetricProps) {
  const displayDetail = detail || trendLabel;
  const trendColors = {
    increasing: "text-amber-400",
    decreasing: "text-emerald-400",
    steady: "text-slate-400",
    neutral: "text-slate-400",
  };

  const valueSizes = {
    sm: "text-xl",
    md: "text-2xl sm:text-3xl",
    lg: "text-3xl sm:text-4xl",
  };

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="text-xs font-sans font-medium text-slate-400">
        {label}
      </div>
      <div className="flex items-baseline gap-2 font-tabular">
        <span className={cn("font-bold tracking-tight text-white font-sans", valueSizes[size])}>
          {value}
        </span>
        {unit && (
          <span className="text-xs font-mono font-medium text-slate-400">
            {unit}
          </span>
        )}
      </div>
      {(trend || displayDetail) && (
        <div className="flex items-center gap-2 text-xs font-sans">
          {trend && (
            <span className={cn("font-semibold", trendColors[trendDirection])}>
              {trendDirection === "increasing" && "↑ "}
              {trendDirection === "decreasing" && "↓ "}
              {trendDirection === "steady" && "→ "}
              {trend}
            </span>
          )}
          {displayDetail && <span className="text-slate-400">{displayDetail}</span>}
        </div>
      )}
    </div>
  );
}
