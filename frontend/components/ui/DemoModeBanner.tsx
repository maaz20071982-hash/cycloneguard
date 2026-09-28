"use client";

import React from "react";
import { AlertCircle, FlaskConical } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

export interface DemoModeBannerProps {
  stormName?: string;
  sourceDataset?: string;
  className?: string;
}

export function DemoModeBanner({
  stormName,
  sourceDataset = "Historical Reanalysis Simulation / Synthetic Benchmark",
  className = "",
}: DemoModeBannerProps) {
  return (
    <div
      className={`border border-[#b45309]/30 bg-[#fef8ee] p-3 text-xs text-[#b45309] rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 select-none ${className}`}
      role="alert"
    >
      <div className="flex items-center gap-2">
        <FlaskConical className="h-4 w-4 shrink-0 text-[#b45309]" />
        <div>
          <span className="font-bold tracking-wider uppercase font-mono mr-1.5">
            Demonstration Data
          </span>
          <span className="text-[11px] text-[#92400e]">
            {stormName ? `Displaying benchmark reference case for ${stormName}.` : "Displaying benchmark reference case."} This is simulated/reanalysis data for interface demonstration and evaluation, NOT a live operational advisory.
          </span>
        </div>
      </div>
      <div className="shrink-0 flex items-center gap-2">
        <Badge variant="warning" className="text-[10px]">
          DEMO MODE
        </Badge>
        <span className="text-[10px] font-mono text-[#92400e] hidden md:inline">
          {sourceDataset}
        </span>
      </div>
    </div>
  );
}
