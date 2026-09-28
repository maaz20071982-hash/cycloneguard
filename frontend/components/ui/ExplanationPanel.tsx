"use client";

import React from "react";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { DataRow } from "@/components/ui/DataRow";
import { Eye, Sparkles, Layers, ShieldCheck } from "lucide-react";
import { Explanation } from "@/types";

export interface ExplanationPanelProps {
  explanation?: Explanation | null;
  className?: string;
}

export function ExplanationPanel({ explanation, className = "" }: ExplanationPanelProps) {
  const isAvailable = explanation?.is_available || false;

  return (
    <Panel className={className}>
      <PanelHeader
        title="Model Feature Attribution & Decision Factors"
        subtitle="Standardized linear feature attribution (feature value × standardized coefficient) isolating drivers of empirical RI risk"
      />

      <div className="p-5">
        {!isAvailable ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Visual Attribution Canvas Placeholder */}
            <div className="md:col-span-1 min-h-[220px] border border-dashed border-[#e2e6e9] bg-[#f8f9fa] flex flex-col items-center justify-center p-5 text-center rounded-[3px]">
              <div className="h-10 w-10 rounded-full bg-[#edf5f7] text-[#0f5b6c] flex items-center justify-center mb-2">
                <Eye className="h-5 w-5" />
              </div>
              <span className="text-xs font-bold text-[#182026] uppercase font-mono tracking-wider">
                Attribution Standby
              </span>
              <span className="text-[11px] text-[#5f6b7c] mt-1 leading-relaxed">
                Feature attribution weights will populate when an observation evaluation is conducted.
              </span>
              <div className="mt-3 text-[10px] font-mono text-[#0f5b6c]">
                STANDARDIZED LINEAR ATTRIBUTION
              </div>
            </div>

            {/* Explanation Summary & Factor Architecture */}
            <div className="md:col-span-2 space-y-3">
              <div className="p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px]">
                <h4 className="text-xs font-bold text-[#182026] uppercase font-mono tracking-wider mb-1 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-[#0f5b6c]" />
                  Attribution Status
                </h4>
                <p className="text-xs text-[#5f6b7c] leading-relaxed">
                  Feature attribution is computed directly from the frozen regularized logistic regression model weights.
                </p>
                <p className="text-[11px] text-[#5f6b7c] mt-1">
                  CycloneGuard delivers statistical model feature contributions rather than claiming physical causation.
                </p>
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                  Top Evaluated Feature Families (61-Feature Multimodal Model)
                </span>
                <DataRow
                  label="Temporal Pressure Drop (6h / 12h)"
                  value="Rapid central pressure drop signal"
                />
                <DataRow
                  label="Kinematic Wind Acceleration"
                  value="Recent 6h / 12h intensity change rate"
                />
                <DataRow
                  label="HURSAT Cold Core Symmetry"
                  value="Inner 100km IR brightness temperature"
                />
                <DataRow
                  label="Convective Fraction (< 233 K)"
                  value="Deep convective areal coverage"
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-xs text-[#182026] font-medium">{explanation?.summary}</p>
            <div className="space-y-2">
              {explanation?.features.map((f) => (
                <DataRow
                  key={f.name}
                  label={f.name}
                  value={`${(f.importance * 100).toFixed(0)}% contribution — ${f.description}`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </Panel>
  );
}
