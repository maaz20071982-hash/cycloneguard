"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  Compass,
  Wind,
  CloudRain,
  Eye,
  Satellite,
  Maximize2,
  Layers,
  MapPin,
  AlertCircle,
  Globe,
  Sun,
  Moon,
  Info,
} from "lucide-react";
import type { MapTrackPoint, StormTrackGroup } from "./map/LeafletMap";

export type { MapTrackPoint, StormTrackGroup };

// Dynamically import Leaflet map with SSR disabled
const LeafletMap = dynamic(
  () => import("./map/LeafletMap").then((mod) => mod.LeafletMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[460px] bg-[#0b1520] flex flex-col items-center justify-center p-6 text-center space-y-3">
        <div className="relative flex items-center justify-center h-12 w-12 rounded-full bg-slate-900 border border-teal-500/40">
          <div className="absolute inset-0 rounded-full bg-teal-500/20 animate-ping" />
          <Satellite className="h-6 w-6 text-teal-400" />
        </div>
        <div className="text-xs font-mono text-slate-300 uppercase tracking-widest font-semibold">
          Initializing Meteorological Map Canvas...
        </div>
        <p className="text-[11px] text-slate-400 font-mono">
          Loading Esri & OpenStreetMap GIS tiles, projection matrices, and track vectors
        </p>
      </div>
    ),
  }
);

export interface CycloneMapProps {
  center?: [number, number]; // [lat, lon]
  zoom?: number;
  tracks?: MapTrackPoint[];
  multiStormTracks?: StormTrackGroup[];
  activeStormId?: string;
  onSelectStorm?: (stormId: string) => void;
  selectedTime?: string;
  markers?: Array<{ lat: number; lon: number; label: string; icon?: React.ReactNode }>;
  windLayers?: boolean;
  riskLayers?: boolean;
  rainfallLayers?: boolean;
  satelliteLayers?: boolean;
  forecastPath?: MapTrackPoint[];
  title?: string;
  subtitle?: string;
  basin?: string;
  isDemo?: boolean;
  height?: string | number;
  className?: string;
  onLayerChange?: (layers: Record<string, boolean>) => void;
}

export function CycloneMap({
  center = [15.0, 75.0],
  zoom = 4,
  tracks = [],
  multiStormTracks = [],
  activeStormId: externalActiveStormId,
  onSelectStorm,
  selectedTime,
  windLayers = true,
  riskLayers = true,
  rainfallLayers = false,
  satelliteLayers = false,
  forecastPath = [],
  title = "Tropical Cyclone Monitoring Basin",
  subtitle = "Interactive Geographic Centerpiece · Best-Track Observation & Forecast Cones",
  basin = "North Indian Ocean & West Pacific",
  isDemo = false,
  height = "520px",
  className = "",
  onLayerChange,
}: CycloneMapProps) {
  const [internalActiveStormId, setInternalActiveStormId] = useState<string | undefined>(externalActiveStormId);
  const activeStormId = externalActiveStormId !== undefined ? externalActiveStormId : internalActiveStormId;

  const [basemap, setBasemap] = useState<"dark" | "satellite" | "ocean" | "osm">("dark");
  const [showWindRadii, setShowWindRadii] = useState<boolean>(windLayers);
  const [showRiskCone, setShowRiskCone] = useState<boolean>(riskLayers);
  const [showTracks, setShowTracks] = useState<boolean>(true);
  const [showLegend, setShowLegend] = useState<boolean>(true);

  // Sync external activeStormId if provided
  useEffect(() => {
    if (externalActiveStormId !== undefined) {
      setInternalActiveStormId(externalActiveStormId);
    }
  }, [externalActiveStormId]);

  const handleSelectStorm = (stormId: string) => {
    const next = activeStormId === stormId ? undefined : stormId;
    setInternalActiveStormId(next);
    if (onSelectStorm) onSelectStorm(stormId);
  };

  const totalPoints = (tracks.length > 0 ? tracks.length : 0) +
    multiStormTracks.reduce((acc, s) => acc + (s.points?.length || 0), 0);

  const hasAnyData = totalPoints > 0 || isDemo;

  // Active point for wind radii: either latest point of selected storm or single track
  let activePointForRadii: MapTrackPoint | undefined;
  if (tracks.length > 0) {
    activePointForRadii = tracks[tracks.length - 1];
  } else if (multiStormTracks.length > 0) {
    const storm = activeStormId
      ? multiStormTracks.find((s) => s.id === activeStormId)
      : multiStormTracks[0];
    if (storm && storm.points && storm.points.length > 0) {
      activePointForRadii = storm.points[storm.points.length - 1];
    }
  }

  const windRadiiConfig = activePointForRadii
    ? {
        lat: activePointForRadii.lat,
        lon: activePointForRadii.lon,
        r34_nm: 120,
        r50_nm: activePointForRadii.intensity_kts && activePointForRadii.intensity_kts >= 50 ? 60 : 0,
        r64_nm: activePointForRadii.intensity_kts && activePointForRadii.intensity_kts >= 64 ? 30 : 0,
      }
    : undefined;

  return (
    <div className={cn("border border-[#cbd2d6] bg-[#0b1520] rounded-[4px] shadow-[0_2px_8px_rgba(0,0,0,0.12)] overflow-hidden flex flex-col", className)}>
      {/* Top Map Operational Control Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between px-4 py-2.5 bg-[#182026] border-b border-slate-700/80 gap-2.5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono flex items-center gap-1.5">
              <Compass className="h-3.5 w-3.5 text-teal-400" />
              {title}
            </span>
            <span className="text-[11px] text-slate-400 font-mono hidden md:inline">
              ({basin})
            </span>
          </div>
          {subtitle && (
            <div className="text-[10px] text-slate-400 mt-0.5 font-normal">
              {subtitle}
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          {/* Basemap Switcher (100% Free, Zero API Keys) */}
          <div className="flex items-center bg-slate-900 border border-slate-700 rounded-[3px] p-0.5">
            <button
              onClick={() => setBasemap("dark")}
              className={cn(
                "px-2 py-0.5 text-[10px] rounded-[2px] transition-colors cursor-pointer",
                basemap === "dark"
                  ? "bg-slate-700 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-white"
              )}
              title="Dark Radar Basemap (Esri World Dark Gray Base)"
            >
              Dark
            </button>
            <button
              onClick={() => setBasemap("satellite")}
              className={cn(
                "px-2 py-0.5 text-[10px] rounded-[2px] transition-colors cursor-pointer",
                basemap === "satellite"
                  ? "bg-slate-700 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-white"
              )}
              title="Esri World Satellite Imagery"
            >
              Satellite
            </button>
            <button
              onClick={() => setBasemap("ocean")}
              className={cn(
                "px-2 py-0.5 text-[10px] rounded-[2px] transition-colors cursor-pointer",
                basemap === "ocean"
                  ? "bg-slate-700 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-white"
              )}
              title="Maritime Oceanic Bathymetry (Esri Oceans)"
            >
              Oceans
            </button>
            <button
              onClick={() => setBasemap("osm")}
              className={cn(
                "px-2 py-0.5 text-[10px] rounded-[2px] transition-colors cursor-pointer",
                basemap === "osm"
                  ? "bg-slate-700 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-white"
              )}
              title="OpenStreetMap Standard Global Tiles"
            >
              OSM
            </button>
          </div>

          {/* Feed Status */}
          <StatusBadge
            status={hasAnyData ? "operational" : "standby"}
            label={hasAnyData ? (multiStormTracks.length > 0 ? `${multiStormTracks.length} STORMS MAPPED` : "LIVE TRACK ACTIVE") : "STANDBY"}
          />
        </div>
      </div>

      {/* Multi-Storm Quick Filter Tabs (If multi-storm mode) */}
      {multiStormTracks.length > 0 && (
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0f172a] border-b border-slate-800 overflow-x-auto text-[11px] font-mono scrollbar-none">
          <span className="text-[10px] text-slate-400 uppercase tracking-widest mr-1 shrink-0 font-semibold">
            Track Filter:
          </span>
          <button
            onClick={() => setInternalActiveStormId(undefined)}
            className={cn(
              "px-2 py-0.5 rounded-[2px] cursor-pointer whitespace-nowrap transition-colors",
              !activeStormId
                ? "bg-teal-600 text-white font-bold shadow-xs"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            )}
          >
            ALL VORTICES ({multiStormTracks.length})
          </button>
          {multiStormTracks.map((storm) => {
            const isSelected = activeStormId === storm.id;
            return (
              <button
                key={storm.id}
                onClick={() => handleSelectStorm(storm.id)}
                className={cn(
                  "flex items-center gap-1 px-2 py-0.5 rounded-[2px] cursor-pointer whitespace-nowrap transition-colors",
                  isSelected
                    ? "bg-[#0f5b6c] text-white font-bold border border-teal-400/50 shadow-xs"
                    : "bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700"
                )}
              >
                <span>🌀</span>
                <span>{storm.name}</span>
                {storm.peak_intensity_kts && (
                  <span className="text-[9px] text-amber-300 font-normal">
                    ({storm.peak_intensity_kts}kt)
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Main Meteorological Map Canvas with guaranteed height */}
      <div
        className="relative flex-1 w-full min-h-[380px] bg-[#0b1520]"
        style={{
          minHeight: "380px",
          height: typeof height === "number" ? `${height}px` : (height && height !== "100%" ? height : undefined),
        }}
      >
        <LeafletMap
          center={center}
          zoom={zoom}
          tracks={tracks}
          multiStormTracks={multiStormTracks}
          activeStormId={activeStormId}
          onSelectStorm={handleSelectStorm}
          selectedPointTime={selectedTime}
          windRadii={windRadiiConfig}
          forecastPath={forecastPath}
          showWindRadii={showWindRadii}
          showForecastCone={showRiskCone}
          showTrackPoints={showTracks}
          basemap={basemap}
          height="100%"
        />

        {/* Floating Layer Controls (Bottom-Right) */}
        <div className="absolute bottom-3 right-3 z-[500] flex flex-wrap gap-1 bg-[#182026]/95 border border-slate-700 p-1.5 rounded-[3px] text-xs font-mono shadow-xl backdrop-blur-xs">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest px-2 py-1 flex items-center gap-1 font-semibold border-r border-slate-700 mr-0.5">
            <Layers className="h-3 w-3 text-teal-400" />
            Layers
          </div>

          {/* Track Layer Toggle */}
          <button
            onClick={() => setShowTracks((prev) => !prev)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 text-[11px] rounded-[2px] transition-colors cursor-pointer",
              showTracks
                ? "bg-[#0f5b6c] text-white font-semibold"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            )}
            title="Toggle best-track observations"
          >
            <Compass className="h-3.5 w-3.5" />
            <span>Track</span>
          </button>

          {/* Wind Radii Layer Toggle */}
          <button
            onClick={() => setShowWindRadii((prev) => !prev)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 text-[11px] rounded-[2px] transition-colors cursor-pointer",
              showWindRadii
                ? "bg-[#0f5b6c] text-white font-semibold"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            )}
            title="Toggle R34/R50/R64 wind radii"
          >
            <Wind className="h-3.5 w-3.5" />
            <span>Wind Radii</span>
          </button>

          {/* Forecast / RI Cone Layer Toggle */}
          <button
            onClick={() => setShowRiskCone((prev) => !prev)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 text-[11px] rounded-[2px] transition-colors cursor-pointer",
              showRiskCone
                ? "bg-[#0f5b6c] text-white font-semibold"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            )}
            title="Toggle projected RI risk cone"
          >
            <Eye className="h-3.5 w-3.5" />
            <span>RI Cone</span>
          </button>

          {/* Satellite Imagery Basemap Toggle */}
          <button
            onClick={() => setBasemap((prev) => (prev === "satellite" ? "dark" : "satellite"))}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 text-[11px] rounded-[2px] transition-colors cursor-pointer",
              basemap === "satellite"
                ? "bg-[#0f5b6c] text-white font-semibold"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            )}
            title="Toggle satellite Earth imagery"
          >
            <Satellite className="h-3.5 w-3.5" />
            <span>Satellite</span>
          </button>
        </div>

        {/* Intensity Legend (Bottom-Left above coordinates) */}
        {showLegend && (
          <div className="absolute bottom-11 left-2.5 z-[500] bg-[#182026]/95 border border-slate-700/80 p-2 rounded-[3px] text-[10px] font-mono text-slate-300 shadow-lg backdrop-blur-xs max-w-xs hidden sm:block">
            <div className="flex items-center justify-between border-b border-slate-700 pb-1 mb-1.5">
              <span className="text-teal-400 font-bold uppercase tracking-wider text-[9px]">
                WMO / IMD Intensity Scale
              </span>
              <button
                onClick={() => setShowLegend(false)}
                className="text-slate-500 hover:text-slate-300 text-[10px] cursor-pointer"
                title="Hide Legend"
              >
                &times;
              </button>
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[10px]">
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#0ea5e9]" />
                <span>Depression (&lt;34 kt)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#14b8a6]" />
                <span>Cyclonic (34-47 kt)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#eab308]" />
                <span>Severe (48-63 kt)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#f97316]" />
                <span>Very Severe (64-89)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#ef4444]" />
                <span>Ext. Severe (90-119)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#d946ef]" />
                <span>Super Cyclone (≥120)</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
