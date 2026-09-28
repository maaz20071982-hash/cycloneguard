"use client";

import React from "react";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Clock, Navigation, Compass, AlertCircle } from "lucide-react";
import { CycloneForecast, ForecastHorizon } from "@/types";

export interface ForecastTimelineProps {
  forecast?: CycloneForecast | null;
  className?: string;
}

export function ForecastTimeline({ forecast, className = "" }: ForecastTimelineProps) {
  const isAvailable = forecast?.status === "available" && forecast?.horizons && forecast.horizons.length > 0;

  const standardHorizons: Array<{ hour: 12 | 24 | 36 | 48; label: string; period: string }> = [
    { hour: 12, label: "+12h Horizon", period: "Short-Range Nowcasting" },
    { hour: 24, label: "+24h Horizon", period: "Primary RI Warning Window" },
    { hour: 36, label: "+36h Horizon", period: "Intermediate Lead Time" },
    { hour: 48, label: "+48h Horizon", period: "Extended Track Projection" },
  ];

  return (
    <Panel className={className}>
      <PanelHeader
        title="Multi-Horizon Forecast Trajectory Timeline"
        subtitle="Forward trajectory, intensity progression, and cone uncertainty across 12h to 48h horizons"
      />

      <div className="p-5 space-y-5">
        {!isAvailable ? (
          <div>
            {/* Top State Notification */}
            <div className="p-3 border border-[#cbd2d6] bg-[#f8f9fa] rounded-[3px] text-xs flex items-center justify-between mb-4">
              <div>
                <span className="font-bold text-[#182026] uppercase font-mono mr-2">
                  Forecast Unavailable
                </span>
                <span className="text-[#5f6b7c]">
                  Multi-lead trajectory predictions and track cone uncertainties will calculate upon neural model deployment in Sprint 4.
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#5f6b7c] shrink-0 hidden sm:inline">
                ZERO INVENTED NUMBERS RULE
              </span>
            </div>

            {/* Vertical Tree Visual Structure: NOW -> 12h -> 24h -> 36h -> 48h */}
            <div className="relative pl-6 sm:pl-8 space-y-4 before:absolute before:left-3 sm:before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#cbd2d6]">
              {/* NOW Node */}
              <div className="relative flex items-center gap-3">
                <span className="absolute -left-6 sm:-left-8 flex h-5 w-5 items-center justify-center rounded-full bg-[#0f5b6c] text-white text-[10px] font-bold">
                  ●
                </span>
                <div className="border border-[#0f5b6c] bg-[#edf5f7] px-3 py-1.5 rounded-[3px] text-xs font-mono font-semibold text-[#0f5b6c] flex items-center gap-2">
                  <Clock className="h-3 w-3" />
                  <span>NOW (t = 0h)</span>
                  <span className="text-[10px] text-[#5f6b7c] font-normal">• Initialized at Observation Time</span>
                </div>
              </div>

              {/* 12h, 24h, 36h, 48h Horizon Nodes */}
              {standardHorizons.map((h) => (
                <div key={h.hour} className="relative flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px] gap-2">
                  <span className="absolute -left-6 sm:-left-8 flex h-4 w-4 items-center justify-center rounded-full bg-[#eaedef] border border-[#cbd2d6] text-[8px] text-[#5f6b7c]">
                    ○
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold font-mono text-[#182026]">
                        {h.label}
                      </span>
                      <span className="text-[10px] text-[#5f6b7c] font-mono">
                        ({h.period})
                      </span>
                    </div>
                    <span className="text-[11px] text-[#5f6b7c] block mt-0.5">
                      Standby for ensemble spatiotemporal forecast engine
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-mono shrink-0">
                    <span className="px-2 py-0.5 bg-[#f8f9fa] border border-[#e2e6e9] text-[#5f6b7c] text-[11px] rounded-[2px]">
                      Vmax: — kt
                    </span>
                    <span className="px-2 py-0.5 bg-[#f8f9fa] border border-[#e2e6e9] text-[#5f6b7c] text-[11px] rounded-[2px]">
                      Cone: — km
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {forecast?.horizons.map((h) => (
              <div key={h.hour} className="p-3 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px] flex justify-between items-center text-xs">
                <div>
                  <span className="font-bold font-mono text-[#182026]">+{h.hour}h Horizon</span>
                  <span className="text-[11px] text-[#5f6b7c] ml-2">Lat: {h.lat?.toFixed(1)}° / Lon: {h.lon?.toFixed(1)}°</span>
                </div>
                <div className="font-mono font-bold text-[#0f5b6c]">
                  {h.vmax_kmh} km/h
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Panel>
  );
}
