"use client";

import React from "react";
import { TimelineObservation } from "@/lib/api/cyclones";
import { Badge } from "@/components/ui/Badge";
import { Clock, Navigation, Wind, Activity, Satellite, CheckCircle2 } from "lucide-react";

interface CycloneTimelineProps {
  timeline: TimelineObservation[];
  selectedObservationTime: string;
  onSelectObservation: (obsTime: string) => void;
  className?: string;
}

export function CycloneTimeline({
  timeline,
  selectedObservationTime,
  onSelectObservation,
  className = "",
}: CycloneTimelineProps) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-[#5f6b7c] font-mono border border-dashed border-[#e2e6e9] bg-[#f8f9fa] rounded-[4px]">
        No historical observations loaded for this timeline.
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between pb-2 border-b border-[#e2e6e9]">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-[#0f5b6c]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#182026] font-mono">
            Historical Observation Timeline ({timeline.length} Fixes)
          </h3>
        </div>
        <span className="text-[11px] text-[#5f6b7c] font-mono">
          Select an observation to inspect what the model saw
        </span>
      </div>

      {/* Horizontal / Card Scroll Strip */}
      <div className="overflow-x-auto pb-3 pt-1 scrollbar-thin">
        <div className="flex gap-2.5 min-w-max">
          {timeline.map((obs) => {
            const isSelected = obs.observation_time === selectedObservationTime;
            const isAboveTau = obs.ri_risk_index !== null && obs.ri_risk_index !== undefined && obs.ri_risk_index >= obs.operating_threshold;
            const formattedTime = obs.observation_time.replace("T", " ").replace(":00Z", "Z");

            return (
              <button
                key={obs.observation_time}
                type="button"
                onClick={() => onSelectObservation(obs.observation_time)}
                className={`text-left p-3 rounded-[4px] border transition-all w-52 shrink-0 ${
                  isSelected
                    ? "border-[#0f5b6c] bg-[#edf5f7] shadow-[0_2px_4px_rgba(15,91,108,0.15)] ring-1 ring-[#0f5b6c]"
                    : "border-[#e2e6e9] bg-[#ffffff] hover:border-[#b0bac5] hover:bg-[#fbfcfc]"
                }`}
              >
                {/* Header: Timestamp & Canonical Badge */}
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <span className="font-mono font-bold text-xs text-[#182026]">
                    {formattedTime}
                  </span>
                  {obs.is_canonical && (
                    <span className="bg-[#0f5b6c] text-[#ffffff] text-[9px] font-mono px-1 py-0.5 rounded-[2px] uppercase">
                      Target Fix
                    </span>
                  )}
                </div>

                {/* Position & Wind */}
                <div className="space-y-1 text-[11px] font-mono text-[#5f6b7c] mb-2">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1">
                      <Navigation className="h-3 w-3 text-[#5f6b7c]" />
                      Coords:
                    </span>
                    <span className="text-[#182026] font-semibold">
                      {obs.latitude}°N, {obs.longitude}°E
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1">
                      <Wind className="h-3 w-3 text-[#5f6b7c]" />
                      Current Vmax:
                    </span>
                    <span className="text-[#182026] font-bold">
                      {obs.current_wind_kts} kt
                    </span>
                  </div>
                </div>

                {/* Model Empirical Risk Score Badge */}
                <div className="pt-2 border-t border-[#e2e6e9] flex items-center justify-between">
                  <span className="text-[10px] uppercase font-mono text-[#5f6b7c]">
                    RI Risk Index:
                  </span>
                  {obs.ri_risk_index !== null && obs.ri_risk_index !== undefined ? (
                    <span
                      className={`text-[11px] font-mono font-bold px-1.5 py-0.5 rounded-[2px] ${
                        isAboveTau
                          ? "bg-[#fff1f0] text-[#cf1322] border border-[#ffa39e]"
                          : "bg-[#f6ffed] text-[#389e0d] border border-[#b7eb8f]"
                      }`}
                    >
                      {obs.ri_risk_index.toFixed(3)}
                    </span>
                  ) : (
                    <span className="text-[10px] text-[#8a9ba8] font-mono">—</span>
                  )}
                </div>

                {/* Satellite Channel Availability */}
                <div className="mt-2 flex items-center gap-1">
                  <Satellite className="h-3 w-3 text-[#5f6b7c] shrink-0" />
                  <div className="flex gap-1 text-[9px] font-mono">
                    <span
                      className={`px-1 py-0.2 rounded-[2px] ${
                        obs.has_irwin ? "bg-[#e2e6e9] text-[#182026]" : "bg-transparent text-[#8a9ba8]"
                      }`}
                      title={obs.has_irwin ? "IRWIN Available" : "IRWIN Unavailable"}
                    >
                      IR
                    </span>
                    <span
                      className={`px-1 py-0.2 rounded-[2px] ${
                        obs.has_irwvp ? "bg-[#e2e6e9] text-[#182026]" : "bg-transparent text-[#8a9ba8]"
                      }`}
                      title={obs.has_irwvp ? "IRWVP Available" : "IRWVP Unavailable"}
                    >
                      WV
                    </span>
                    <span
                      className={`px-1 py-0.2 rounded-[2px] ${
                        obs.has_vschn ? "bg-[#e2e6e9] text-[#182026]" : "bg-transparent text-[#8a9ba8]"
                      }`}
                      title={obs.has_vschn ? "VSCHN Available" : "VSCHN Night/Unilluminated"}
                    >
                      VIS
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
