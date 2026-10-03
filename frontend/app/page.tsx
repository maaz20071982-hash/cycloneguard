"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { CycloneMap, MapTrackPoint } from "@/components/ui/CycloneMap";
import { useStorm } from "@/lib/storm-context";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  Compass,
  Wind,
  Layers,
  Eye,
  Activity,
  MapPin,
  AlertTriangle,
  Shield,
  ArrowRight,
  Play,
  RotateCcw,
  CheckCircle2,
  Clock,
  Navigation,
  Database,
  Satellite,
  Waves,
  ChevronRight,
  TrendingUp,
  Info,
} from "lucide-react";

export default function MainDashboardPage() {
  const {
    currentStorm,
    selectStorm,
    availableStorms,
    calculatedConfidence,
    confidencePenaltyTotal,
  } = useStorm();
  const [selectedTime, setSelectedTime] = useState<string>(currentStorm.observation_time_utc);

  // Sync selected time when storm changes
  useEffect(() => {
    setSelectedTime(currentStorm.observation_time_utc);
  }, [currentStorm]);

  // Forecast points from centralized storm store
  const forecastMapPoints: MapTrackPoint[] = currentStorm.track_landfall_prediction.forecast_points.map((p) => ({
    lat: p.latitude,
    lon: p.longitude,
    time: p.valid_time_utc,
    intensity_kts: p.wind_speed_kts,
    intensity_kmh: p.wind_speed_kmh,
    pressure_mb: p.central_pressure_mb,
    category: p.category,
    agency_grade: "CycloneSense AI Ensemble",
  }));

  // Past track points leading up to t0 observation fix
  const pastMapPoints: MapTrackPoint[] = [
    {
      lat: currentStorm.observation_data.latitude - 1.2,
      lon: currentStorm.observation_data.longitude + 2.0,
      time: "2015-10-28T06:00:00Z",
      intensity_kts: 25,
      intensity_kmh: 46,
      pressure_mb: 1003,
      category: "Depression",
    },
    {
      lat: currentStorm.observation_data.latitude - 0.5,
      lon: currentStorm.observation_data.longitude + 0.9,
      time: "2015-10-28T12:00:00Z",
      intensity_kts: 30,
      intensity_kmh: 55,
      pressure_mb: 1001,
      category: "Depression",
    },
    {
      lat: currentStorm.observation_data.latitude,
      lon: currentStorm.observation_data.longitude,
      time: currentStorm.observation_time_utc,
      intensity_kts: currentStorm.observation_data.current_wind_kts,
      intensity_kmh: currentStorm.observation_data.current_wind_kmh,
      pressure_mb: currentStorm.observation_data.central_pressure_mb,
      category: currentStorm.intensity_classification.current_category_imd,
    },
  ];

  // Landfall Marker for map
  const landfallMarkers = [
    {
      lat: 14.1,
      lon: 49.0,
      label: "LANDFALL TARGET (~130h)",
      sublabel: currentStorm.track_landfall_prediction.landfall_prediction.predicted_landfall_sector,
      type: "landfall" as const,
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#080d16] text-slate-100 font-sans">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* ============================================================ */}
        {/* 1. TOP HEADER & TITLE: CYCLONESENSE — CYCLONE INTELLIGENCE    */}
        {/* ============================================================ */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-cyan-400">
                Smart India Hackathon 2026 · Problem SIH26070
              </span>
              <span className="text-slate-600">•</span>
              <span className="px-2.5 py-0.5 text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 rounded-full">
                DEMO / SIMULATION
              </span>
              <span className="text-slate-600">•</span>
              <StatusBadge status="operational" label="Inference Engine Active" />
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              CycloneSense — Cyclone Intelligence
            </h1>

            <p className="text-xs sm:text-sm text-slate-400 mt-1.5 font-normal">
              Multi-Source Satellite Intelligence &bull; North Indian Ocean Basin Surveillance &bull; Anti-Data-Leakage Certified
            </p>
          </div>

          {/* Quick Storm Selector & View Switcher */}
          <div className="flex flex-wrap items-center gap-2.5 self-start md:self-auto text-xs">
            <div className="flex items-center bg-slate-900/80 border border-slate-700/80 rounded-lg px-3 py-1.5 shadow-sm">
              <span className="text-slate-400 text-xs mr-2 font-medium">Active Vortex:</span>
              <select
                value={currentStorm.storm_id}
                onChange={(e) => selectStorm(e.target.value)}
                className="bg-transparent font-semibold text-cyan-300 text-xs focus:outline-none cursor-pointer border-none p-0"
              >
                {availableStorms.map((s) => (
                  <option key={s.id} value={s.id} className="bg-slate-900 text-slate-100">
                    {s.name} ({s.basin.split("(")[0]})
                  </option>
                ))}
              </select>
            </div>

            <Link href="/demo">
              <Button size="sm" variant="primary" className="shadow-md">
                <Play className="h-3.5 w-3.5 mr-1.5 fill-white" />
                9-Stage Flow
              </Button>
            </Link>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 2. COMPACT KPI ROW (4 Mandatory Metrics)                     */}
        {/* ============================================================ */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 text-xs">
          {/* KPI 1: Active Cyclones */}
          <div className="p-4 bg-[#0e1726]/80 rounded-xl border border-slate-800/80 shadow-md backdrop-blur-md hover:border-cyan-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold text-slate-300">Active Cyclones</span>
              <span className="px-2 py-0.5 text-[10px] font-medium bg-cyan-950/70 text-cyan-300 border border-cyan-800/50 rounded-full">
                NIO BASIN
              </span>
            </div>
            <div className="mt-2">
              <div className="text-2xl sm:text-3xl font-bold text-cyan-400">3 Systems</div>
              <div className="text-xs text-slate-400 mt-1 truncate">
                1 Evaluation ({currentStorm.storm_name}) + 2 Historical
              </div>
            </div>
          </div>

          {/* KPI 2: Highest Intensity */}
          <div className="p-4 bg-[#0e1726]/80 rounded-xl border border-slate-800/80 shadow-md backdrop-blur-md hover:border-rose-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold text-slate-300">Highest Intensity</span>
              <span className="px-2 py-0.5 text-[10px] font-medium bg-rose-950/70 text-rose-300 border border-rose-800/50 rounded-full">
                PEAK VMAX
              </span>
            </div>
            <div className="mt-2">
              <div className="text-2xl sm:text-3xl font-bold text-rose-400">115 kt</div>
              <div className="text-xs text-slate-400 mt-1 truncate">
                213 km/h &bull; Ext. Severe (Cat 4 Equiv.)
              </div>
            </div>
          </div>

          {/* KPI 3: Next Landfall */}
          <div className="p-4 bg-[#0e1726]/80 rounded-xl border border-slate-800/80 shadow-md backdrop-blur-md hover:border-amber-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold text-slate-300">Next Landfall</span>
              <span className="px-2 py-0.5 text-[10px] font-medium bg-amber-950/70 text-amber-300 border border-amber-800/50 rounded-full">
                SIMULATED
              </span>
            </div>
            <div className="mt-2">
              <div className="text-2xl sm:text-3xl font-bold text-amber-400">~130h</div>
              <div className="text-xs text-slate-400 mt-1 truncate">
                Hadramaut Coast (Al Mukalla)
              </div>
            </div>
          </div>

          {/* KPI 4: Prediction Confidence */}
          <div className="p-4 bg-[#0e1726]/80 rounded-xl border border-slate-800/80 shadow-md backdrop-blur-md hover:border-emerald-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold text-slate-300">Prediction Confidence</span>
              <span className="px-2 py-0.5 text-[10px] font-medium bg-emerald-950/70 text-emerald-300 border border-emerald-800/50 rounded-full">
                HIGH CONF
              </span>
            </div>
            <div className="mt-2">
              <div className="text-2xl sm:text-3xl font-bold text-emerald-400">{calculatedConfidence}%</div>
              <div className="text-xs text-slate-400 mt-1 truncate">
                {confidencePenaltyTotal > 0
                  ? `-${confidencePenaltyTotal}% Source Degradation Penalty`
                  : `Empirical RI: ${currentStorm.explainable_confidence.empirical_ri_risk_index} vs τ=0.125`}
              </div>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 3. MINIMUM NAVIGATION FOR JUDGE FLOW                         */}
        {/* ============================================================ */}
        <JudgeFlowNav currentPath="/" />

        {/* ============================================================ */}
        {/* 4. CURRENT ACTIVE CYCLONE SUMMARY CARD                       */}
        {/* ============================================================ */}
        <div className="rounded-xl border border-slate-800/80 bg-[#0e1726]/80 backdrop-blur-md shadow-lg p-5 text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 border-b border-slate-800/80 gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25">
                <span className="text-xl">🌀</span>
              </div>
              <div>
                <div className="flex items-center gap-2.5">
                  <span className="text-base font-bold text-white font-sans">
                    Cyclone {currentStorm.storm_name}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    ({currentStorm.storm_id})
                  </span>
                  <Badge variant="cyan">TARGET EVALUATION</Badge>
                </div>
                <span className="text-xs text-cyan-400 mt-0.5 block">
                  {currentStorm.basin_name} &bull; Fix Time: <span className="font-mono">{currentStorm.observation_time_utc.replace("T", " ").slice(0, 16)} UTC</span>
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="px-3 py-1 bg-cyan-950/60 text-cyan-300 border border-cyan-800/50 rounded-lg font-medium">
                RI Risk Index: <span className="font-mono font-bold">{currentStorm.explainable_confidence.empirical_ri_risk_index}</span>
              </span>
              <span className="px-3 py-1 bg-rose-950/60 text-rose-300 border border-rose-800/50 rounded-lg font-bold">
                HIGH RI RISK
              </span>
            </div>
          </div>

          {/* Required Fields Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-4">
            {/* Category */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Current Category</span>
              <span className="font-bold text-white text-xs block mt-1">
                {currentStorm.intensity_classification.current_category_imd}
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">WMO: Tropical Depression</span>
            </div>

            {/* Wind Speed */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Current Wind Speed</span>
              <span className="font-bold text-cyan-400 text-xs block mt-1 font-mono">
                {currentStorm.observation_data.current_wind_kts} kt ({currentStorm.observation_data.current_wind_kmh} km/h)
              </span>
              <span className="text-[10px] text-rose-400 font-semibold block mt-0.5">
                Surge: +{currentStorm.intensity_classification.estimated_24h_delta_kts} kt/24h
              </span>
            </div>

            {/* Position */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Vortex Position</span>
              <span className="font-bold text-white text-xs block mt-1 font-mono">
                {currentStorm.observation_data.latitude.toFixed(1)}°N, {currentStorm.observation_data.longitude.toFixed(1)}°E
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Central Arabian Sea</span>
            </div>

            {/* Movement Direction */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Movement Direction</span>
              <span className="font-bold text-white text-xs block mt-1 flex items-center gap-1.5 font-mono">
                <Navigation className="h-3 w-3 text-cyan-400 rotate-[-45deg]" />
                WNW (285°) at 6.8 kt
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Forward Translation</span>
            </div>

            {/* Landfall Window */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Est. Landfall Window</span>
              <span className="font-bold text-amber-400 text-xs block mt-1 font-mono">
                Nov 03, 04:00 UTC
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">
                Lead Time: ~{currentStorm.track_landfall_prediction.landfall_prediction.lead_time_hours}h (±12h)
              </span>
            </div>

            {/* Confidence */}
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block font-medium">Prediction Confidence</span>
              <span className="font-bold text-emerald-400 text-xs block mt-1 font-mono">
                {calculatedConfidence}% (τ = 0.125)
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">
                {confidencePenaltyTotal > 0 ? `-${confidencePenaltyTotal}% Sensor Penalty` : "High Confidence"}
              </span>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 5. INTERACTIVE MAP: THE VISUAL FOCUS                         */}
        {/* ============================================================ */}
        <div className="rounded-xl border border-slate-800/80 bg-[#0e1726]/80 overflow-hidden shadow-xl backdrop-blur-md">
          <div className="px-5 py-3.5 bg-slate-900/90 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <Compass className="h-4.5 w-4.5 text-cyan-400" />
              <div>
                <span className="text-sm font-bold tracking-tight text-white font-sans">
                  North Indian Ocean Basin Surveillance GIS
                </span>
                <span className="text-slate-400 text-xs ml-2 hidden md:inline">
                  (Arabian Sea, Bay of Bengal & Coastline)
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 text-xs">
              <span className="px-2.5 py-0.5 text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full">
                DEMO / SIMULATION
              </span>
              <span className="text-slate-400 text-xs">
                Target: <span className="text-cyan-400 font-semibold">{currentStorm.storm_name}</span>
              </span>
            </div>
          </div>

          {/* Centerpiece Map Canvas */}
          <div className="h-[520px] w-full relative">
            <CycloneMap
              center={[14.5, 68.0]}
              zoom={5}
              tracks={pastMapPoints}
              forecastPath={forecastMapPoints}
              markers={landfallMarkers}
              title={`Cyclone ${currentStorm.storm_name} Interactive Surveillance Basin`}
              subtitle="Center Marker &bull; Past Track &bull; AI Forecast Track &bull; Uncertainty Envelope &bull; Landfall Sector"
              height="520px"
              windLayers={true}
              riskLayers={true}
            />
          </div>

          {/* Map Footer Operational Note */}
          <div className="px-5 py-2.5 bg-slate-900/70 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-3">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-500" />
                <span>Observed Past Track</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-sky-400" />
                <span>AI Forecast Track</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-sky-400/30 border border-sky-400" />
                <span>Uncertainty Corridor</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span>🎯</span>
                <span>Landfall Target (~130h)</span>
              </span>
            </div>

            <div className="text-[11px] text-slate-500">
              WGS84 Projection &bull; 100% Free GIS Tiles &bull; Zero API Key Dependency
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 6. FAST JUDGE FLOW CALLOUT BANNER                            */}
        {/* ============================================================ */}
        <div className="p-5 rounded-xl border border-cyan-500/25 bg-gradient-to-r from-cyan-950/30 via-slate-900/60 to-blue-950/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs shadow-md">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <span className="font-bold text-sm text-cyan-300">
                Ready to review the complete 7-stage disaster management flow?
              </span>
              <Badge variant="cyan">JUDGE SPEEDWALK</Badge>
            </div>
            <p className="text-slate-300 text-xs">
              Step through Observation Fusion &rarr; AI Detection &rarr; Prediction &rarr; GIS Risk &rarr; Alerts &rarr; Authorized Sign-Off.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            <Link href="/fusion">
              <Button size="sm" variant="primary">
                Begin Walkthrough: Data Fusion
                <ArrowRight className="h-3.5 w-3.5 ml-1.5" />
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="sm" variant="outline">
                All-in-One 9-Stage View
              </Button>
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
