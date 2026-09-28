"use client";

import React from "react";
import { AttributionItem } from "@/lib/api/cyclones";
import { Sparkles, Info, ShieldAlert, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface ModelFeatureAttributionPanelProps {
  topSupporting: AttributionItem[];
  topSuppressing: AttributionItem[];
  method?: string;
  disclaimer?: string;
  className?: string;
}

export function ModelFeatureAttributionPanel({
  topSupporting,
  topSuppressing,
  method = "Standardized Linear Coefficient Weighting",
  disclaimer = "Attributions describe statistical model behavior within the regularized linear decision space, not physical meteorological causality.",
  className = "",
}: ModelFeatureAttributionPanelProps) {
  // Find maximum contribution magnitude for scaling contribution bars
  const allItems = [...topSupporting, ...topSuppressing];
  const maxMag = Math.max(0.01, ...allItems.map((i) => i.contribution_magnitude || Math.abs(i.attribution_score) || 0));

  return (
    <div className={`border border-[#e2e6e9] bg-[#ffffff] p-5 rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-4 ${className}`}>
      {/* Header with strictly honest scientific nomenclature */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#e2e6e9]">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[#0f5b6c]" />
            <h3 className="text-sm font-bold tracking-tight text-[#182026] font-mono uppercase">
              Model Feature Attribution
            </h3>
          </div>
          <p className="text-[11px] text-[#5f6b7c] mt-0.5">
            Statistical contribution of standardized multimodal features to the empirical risk score.
          </p>
        </div>

        <span className="bg-[#edf5f7] border border-[#0f5b6c]/30 text-[#0f5b6c] text-[10px] font-mono font-semibold px-2 py-1 rounded-[3px] shrink-0">
          Method: {method}
        </span>
      </div>

      {/* Two Column Grid: Supporting vs Suppressing */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Supporting Features (Positive contribution to risk index) */}
        <div className="space-y-3 p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
            <div className="flex items-center gap-1.5">
              <ArrowUpRight className="h-4 w-4 text-[#cf1322]" />
              <span className="text-xs font-bold font-mono uppercase text-[#182026]">
                Top Supporting Features
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#cf1322] font-semibold">
              Supports RI Escalation
            </span>
          </div>

          {topSupporting.length === 0 ? (
            <div className="text-xs text-[#5f6b7c] font-mono py-4 text-center">
              No features exhibited positive contribution for this fix.
            </div>
          ) : (
            <div className="space-y-2.5">
              {topSupporting.map((item) => {
                const mag = item.contribution_magnitude || Math.abs(item.attribution_score);
                const pct = Math.min(100, Math.round((mag / maxMag) * 100));

                return (
                  <div key={item.feature_name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-[#182026] text-[11px] truncate max-w-[220px]" title={item.display_name}>
                        {item.display_name}
                      </span>
                      <span className="text-[#cf1322] font-semibold text-[11px]">
                        +{item.attribution_score.toFixed(3)}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-[#e2e6e9] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#cf1322] h-full rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#5f6b7c] font-mono">
                      <span className="truncate max-w-[200px]" title={item.feature_name}>
                        {item.feature_name}
                      </span>
                      <span className="italic text-[#8a9ba8]">contributed to score</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Top Suppressing Features (Negative contribution / dampens risk index) */}
        <div className="space-y-3 p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
          <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
            <div className="flex items-center gap-1.5">
              <ArrowDownRight className="h-4 w-4 text-[#389e0d]" />
              <span className="text-xs font-bold font-mono uppercase text-[#182026]">
                Top Suppressing Features
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#389e0d] font-semibold">
              Dampens RI Risk
            </span>
          </div>

          {topSuppressing.length === 0 ? (
            <div className="text-xs text-[#5f6b7c] font-mono py-4 text-center">
              No dampening features active for this fix.
            </div>
          ) : (
            <div className="space-y-2.5">
              {topSuppressing.map((item) => {
                const mag = item.contribution_magnitude || Math.abs(item.attribution_score);
                const pct = Math.min(100, Math.round((mag / maxMag) * 100));

                return (
                  <div key={item.feature_name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-[#182026] text-[11px] truncate max-w-[220px]" title={item.display_name}>
                        {item.display_name}
                      </span>
                      <span className="text-[#389e0d] font-semibold text-[11px]">
                        {item.attribution_score.toFixed(3)}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-[#e2e6e9] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#389e0d] h-full rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#5f6b7c] font-mono">
                      <span className="truncate max-w-[200px]" title={item.feature_name}>
                        {item.feature_name}
                      </span>
                      <span className="italic text-[#8a9ba8]">dampened score</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Mandatory Non-Causality Scientific Advisory */}
      <div className="p-3 bg-[#edf5f7] border border-[#0f5b6c]/30 rounded-[3px] text-xs flex items-start gap-2.5">
        <Info className="h-4 w-4 text-[#0f5b6c] shrink-0 mt-0.5" />
        <div className="space-y-1 text-[#182026]">
          <span className="font-bold font-mono text-[10px] uppercase text-[#0f5b6c] block">
            Scientific Attribution Notice
          </span>
          <p className="text-[11px] leading-relaxed">
            {disclaimer}
          </p>
          <p className="text-[10px] text-[#5f6b7c] font-mono">
            Features describe statistical model association in the 61-feature normalized vector space. This does NOT imply physical thermodynamic causation.
          </p>
        </div>
      </div>
    </div>
  );
}
