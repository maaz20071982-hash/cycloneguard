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
    increasing: "text-[#b45309]",
    decreasing: "text-[#1b7a4f]",
    steady: "text-[#5a6872]",
    neutral: "text-[#5a6872]",
  };

  const valueSizes = {
    sm: "text-xl",
    md: "text-2xl sm:text-3xl",
    lg: "text-3xl sm:text-4xl",
  };

  return (
    <div className={cn("space-y-1", className)}>
      <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#5a6872]">
        {label}
      </div>
      <div className="flex items-baseline gap-1.5 font-tabular">
        <span className={cn("font-bold tracking-tight text-[#182026]", valueSizes[size])}>
          {value}
        </span>
        {unit && (
          <span className="text-xs font-mono font-medium text-[#7d8c97] uppercase">
            {unit}
          </span>
        )}
      </div>
      {(trend || displayDetail) && (
        <div className="flex items-center gap-2 text-[11px] font-mono">
          {trend && (
            <span className={cn("font-semibold", trendColors[trendDirection])}>
              {trendDirection === "increasing" && "↑ "}
              {trendDirection === "decreasing" && "↓ "}
              {trendDirection === "steady" && "→ "}
              {trend}
            </span>
          )}
          {displayDetail && <span className="text-[#7d8c97]">{displayDetail}</span>}
        </div>
      )}
    </div>
  );
}
