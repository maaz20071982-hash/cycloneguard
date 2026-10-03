"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { CycloneMap, MapTrackPoint } from "@/components/ui/CycloneMap";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  MapPin,
  Users,
  Waves,
  Building,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Shield,
  CheckCircle2,
  Play,
  Pause,
  RotateCcw,
  Sliders,
  Anchor,
  Activity,
  Layers,
  Info,
} from "lucide-react";

// 0 to 72h Timeline Steps in 6h increments
const TIMELINE_STEPS = [
  { hour: 0, lat: 13.1, lon: 64.6, wind_kts: 30, wind_kmh: 55, cat: "Depression (D)", phase: "Genesis & Formation in Central Arabian Sea" },
  { hour: 6, lat: 13.3, lon: 63.8, wind_kts: 35, wind_kmh: 65, cat: "Deep Depression (DD)", phase: "Early Spin-up, Heading Westward" },
  { hour: 12, lat: 13.6, lon: 62.9, wind_kts: 45, wind_kmh: 83, cat: "Cyclonic Storm (CS)", phase: "Gale-Force Wind Field Broadening" },
  { hour: 18, lat: 13.8, lon: 62.0, wind_kts: 55, wind_kmh: 102, cat: "Cyclonic Storm (CS)", phase: "Onset of Rapid Intensification (RI)" },
  { hour: 24, lat: 14.1, lon: 61.2, wind_kts: 65, wind_kmh: 120, cat: "Severe Cyclonic Storm (SCS)", phase: "Eyewall Pin-Hole Developing" },
  { hour: 30, lat: 14.3, lon: 60.2, wind_kts: 78, wind_kmh: 145, cat: "Very Severe Cyclonic Storm (VSCS)", phase: "Strong Inner Core Contracting" },
  { hour: 36, lat: 14.4, lon: 59.2, wind_kts: 90, wind_kmh: 165, cat: "Very Severe Cyclonic Storm (VSCS)", phase: "Hurricane-Force Core Broadening" },
  { hour: 42, lat: 14.3, lon: 58.1, wind_kts: 102, wind_kmh: 190, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "Entering Socotra Thermal Channel" },
  { hour: 48, lat: 14.2, lon: 57.0, wind_kts: 115, wind_kmh: 215, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "Peak Intensity (Cat 4 Equivalent)" },
  { hour: 54, lat: 14.1, lon: 56.1, wind_kts: 112, wind_kmh: 208, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "Approaching Gulf of Aden Corridor" },
  { hour: 60, lat: 14.0, lon: 55.2, wind_kts: 110, wind_kmh: 204, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "Coastal Surge Waves Building" },
  { hour: 66, lat: 14.0, lon: 54.4, wind_kts: 108, wind_kmh: 200, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "North of Socotra; Outer Bands Raking Coast" },
  { hour: 72, lat: 13.9, lon: 53.8, wind_kts: 105, wind_kmh: 195, cat: "Extremely Severe Cyclonic Storm (ESCS)", phase: "Critical Threat to Hadramaut / Al Mukalla" },
];

export default function RiskImpactPage() {
  const { currentStorm, selectStorm, availableStorms } = useStorm();
  const risk = currentStorm.gis_risk_impact;
  const pred = currentStorm.track_landfall_prediction;

  // Selected district for detail card
  const [selectedDistrictIdx, setSelectedDistrictIdx] = useState<number>(0);
  const activeDistrict = risk.exposed_districts[selectedDistrictIdx] || risk.exposed_districts[0];

  // 4 Layer Toggles
  const [showPopulation, setShowPopulation] = useState<boolean>(true);
  const [showInfrastructure, setShowInfrastructure] = useState<boolean>(true);
  const [showMaritime, setShowMaritime] = useState<boolean>(true);
  const [showRiskZones, setShowRiskZones] = useState<boolean>(true);

  // 0-72h Time Slider (in index 0 to 12)
  const [sliderIndex, setSliderIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const currentStep = TIMELINE_STEPS[sliderIndex];

  // Play/Pause animation timer
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setSliderIndex((prev) => {
          if (prev >= TIMELINE_STEPS.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1500);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying]);

  // Total population at risk
  const totalPopAtRisk = risk.exposed_districts.reduce(
    (acc, d) => acc + d.simulated_population_at_risk,
    0
  );

  // Dynamic past track up to slider position
  const dynamicTracks: MapTrackPoint[] = TIMELINE_STEPS.slice(0, sliderIndex + 1).map((s) => ({
    lat: s.lat,
    lon: s.lon,
    time: `+${s.hour}h`,
    intensity_kts: s.wind_kts,
    intensity_kmh: s.wind_kmh,
    category: s.cat,
  }));

  // Remaining forecast points from slider position onward
  const dynamicForecastPath: MapTrackPoint[] = TIMELINE_STEPS.slice(sliderIndex).map((s) => ({
    lat: s.lat,
    lon: s.lon,
    time: `+${s.hour}h`,
    intensity_kts: s.wind_kts,
    intensity_kmh: s.wind_kmh,
    category: s.cat,
  }));

  // Dynamic map markers based on toggles
  const mapMarkers: Array<{ lat: number; lon: number; label: string; sublabel?: string; type?: "landfall" | "center" | "station" }> = [
    // Current storm position fix
    {
      lat: currentStep.lat,
      lon: currentStep.lon,
      label: `+${currentStep.hour}h FIX: ${currentStep.wind_kts} KT`,
      sublabel: currentStep.cat,
      type: "center",
    },
    // Landfall Target
    {
      lat: 14.1,
      lon: 49.0,
      label: "LANDFALL TARGET (~130h)",
      sublabel: pred.landfall_prediction.predicted_landfall_sector,
      type: "landfall",
    },
  ];

  // If Risk Zones toggle is active, show the 4 coastal zone pins
  if (showRiskZones) {
    mapMarkers.push(
      { lat: 14.53, lon: 49.13, label: "RED: Al Mukalla (Critical)", sublabel: "Surge 3.2m · Gusts 145 km/h", type: "station" },
      { lat: 14.75, lon: 49.60, label: "ORANGE: Ash Shihr (High)", sublabel: "Surge 2.6m · Gusts 120 km/h", type: "station" },
      { lat: 12.65, lon: 54.02, label: "YELLOW: Socotra (Moderate)", sublabel: "Surge 1.8m · Gusts 95 km/h", type: "station" },
      { lat: 17.01, lon: 54.09, label: "GREEN: Salalah (Low/Advisory)", sublabel: "Surge 0.8m · Gusts 60 km/h", type: "station" }
    );
  }

  // If Infrastructure toggle is active
  if (showInfrastructure) {
    mapMarkers.push(
      { lat: 14.66, lon: 49.37, label: "Riyan Airport (Watch)", sublabel: "Flood Staging Active", type: "station" }
    );
  }

  // If Fishing/Maritime toggle is active
  if (showMaritime) {
    mapMarkers.push(
      { lat: 13.5, lon: 51.5, label: "MARITIME EXCLUSION CORRIDOR", sublabel: "All Small Crafts & Fishing Suspended", type: "station" }
    );
  }

  const getRiskBadgeColor = (color: string) => {
    switch (color) {
      case "Red":
        return "bg-[#fee2e2] text-[#b91c1c] border-[#fecaca]";
      case "Orange":
        return "bg-[#ffedd5] text-[#c2410c] border-[#fed7aa]";
      case "Yellow":
        return "bg-[#fef9c3] text-[#a16207] border-[#fef08a]";
      case "Green":
        return "bg-[#dcfce7] text-[#15803d] border-[#bbf7d0]";
      default:
        return "bg-[#f1f3f4] text-[#5a6872] border-[#cbd2d6]";
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/risk" />

        {/* Stage Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 05 · GIS RISK & IMPACT ASSESSMENT
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              Coastal Risk Zones & Hazard Exposure
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5">
              4-tier coastal risk zones (Green/Yellow/Orange/Red), 0–72h forecast progression slider, and actionable district impact directives for Cyclone {currentStorm.storm_name}.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-[#5a6872]">Target Storm:</span>
            <select
              value={currentStorm.storm_id}
              onChange={(e) => selectStorm(e.target.value)}
              className="bg-white border border-[#cbd2d6] text-[#182026] text-xs font-mono px-2 py-1 rounded-[3px]"
            >
              {availableStorms.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.basin.split("(")[0]})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 4-Tier Coastal Risk Zones Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono">
          {risk.exposed_districts.map((d, idx) => {
            const isSelected = selectedDistrictIdx === idx;
            const badgeClass = getRiskBadgeColor(d.risk_color);

            return (
              <div
                key={idx}
                onClick={() => setSelectedDistrictIdx(idx)}
                className={`p-3.5 rounded-[4px] border transition-all cursor-pointer ${
                  isSelected
                    ? "bg-[#edf5f7] border-[#0f5b6c] shadow-sm ring-1 ring-[#0f5b6c]"
                    : "bg-white border-[#cbd2d6] hover:border-[#0f5b6c] shadow-xs"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-0.5 text-[10px] font-bold border rounded-[2px] ${badgeClass}`}>
                    {d.risk_color.toUpperCase()} · {d.risk_level}
                  </span>
                  <span className="text-[10px] text-[#5a6872]">
                    {d.distance_from_eye_km} km to eye
                  </span>
                </div>

                <div className="font-bold text-xs text-[#182026] line-clamp-1">
                  {d.district_name}
                </div>
                <div className="text-[10px] text-[#5a6872] mb-2 truncate">
                  {d.state_or_province}
                </div>

                <div className="grid grid-cols-2 gap-1 text-[10px] pt-2 border-t border-[#e2e6e9]">
                  <div>
                    <span className="text-[#5a6872] block">Population:</span>
                    <span className="font-bold text-[#182026]">{d.simulated_population_at_risk.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-[#5a6872] block">Storm Surge:</span>
                    <span className="font-bold text-[#0f5b6c]">{d.surge_height_meters} m</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Interactive 0–72h Time Slider & Hazard Progression Bar */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-4 shadow-xs font-mono space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e2e6e9] pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="h-4 w-4 text-[#0f5b6c]" />
              <span className="text-xs font-bold uppercase text-[#182026]">
                0–72h Forecast Time Slider (6h Steps)
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                DYNAMIC SYNCHRONIZATION
              </span>
            </div>

            {/* Play/Pause & Reset Controls */}
            <div className="flex items-center gap-2">
              <Button
                variant={isPlaying ? "danger" : "primary"}
                size="sm"
                onClick={() => setIsPlaying(!isPlaying)}
                className="h-7 text-xs px-2.5"
              >
                {isPlaying ? (
                  <>
                    <Pause className="h-3.5 w-3.5 mr-1" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-3.5 w-3.5 mr-1" />
                    Play Track
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsPlaying(false);
                  setSliderIndex(0);
                }}
                className="h-7 text-xs px-2"
                title="Reset to 0h"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>

          {/* Slider Input with Tick Milestones */}
          <div className="space-y-1.5 pt-1">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-[#0f5b6c] flex items-center gap-1.5">
                <span className="px-2 py-0.5 bg-[#0f5b6c] text-white rounded-[2px]">
                  T+{currentStep.hour}h
                </span>
                <span>{currentStep.cat}</span>
              </span>
              <span className="text-sm font-bold text-[#b91c1c]">
                {currentStep.wind_kts} kt ({currentStep.wind_kmh} km/h)
              </span>
            </div>

            <input
              type="range"
              min="0"
              max={TIMELINE_STEPS.length - 1}
              step="1"
              value={sliderIndex}
              onChange={(e) => {
                setIsPlaying(false);
                setSliderIndex(parseInt(e.target.value, 10));
              }}
              className="w-full accent-[#0f5b6c] h-2 bg-[#e2e6e9] rounded-lg cursor-pointer"
            />

            <div className="flex justify-between text-[10px] text-[#5a6872] px-0.5">
              {TIMELINE_STEPS.map((s, idx) => (
                <span
                  key={s.hour}
                  onClick={() => {
                    setIsPlaying(false);
                    setSliderIndex(idx);
                  }}
                  className={`cursor-pointer transition-colors ${
                    sliderIndex === idx ? "font-bold text-[#0f5b6c]" : "hover:text-[#182026]"
                  }`}
                >
                  +{s.hour}h
                </span>
              ))}
            </div>
          </div>

          {/* Synchronized Status Card */}
          <div className="p-2.5 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
            <div>
              <span className="text-[10px] text-[#5a6872] uppercase block">Current Phase & Threat Profile</span>
              <span className="font-bold text-[#182026]">{currentStep.phase}</span>
            </div>
            <div className="text-right sm:text-right">
              <span className="text-[10px] text-[#5a6872] uppercase block">Position Fix</span>
              <span className="font-mono text-[#0f5b6c] font-bold">
                {currentStep.lat.toFixed(1)}°N, {currentStep.lon.toFixed(1)}°E
              </span>
            </div>
          </div>
        </div>

        {/* Layer Toggles & Map Container */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white overflow-hidden shadow-xs font-mono">
          {/* Header with Layer Toggles */}
          <div className="px-4 py-3 bg-[#f8f9fa] border-b border-[#cbd2d6] flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase text-[#182026]">
              <Layers className="h-4 w-4 text-[#0f5b6c]" />
              Corridor Hazard Map & GIS Layers
            </div>

            {/* 4 Feature Toggles: Population, Infrastructure, Fishing/Maritime, Risk Zone */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <button
                onClick={() => setShowRiskZones(!showRiskZones)}
                className={`px-2.5 py-1 rounded-[3px] border text-[11px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                  showRiskZones
                    ? "bg-[#0f5b6c] text-white border-[#0f5b6c]"
                    : "bg-white text-[#5a6872] border-[#cbd2d6] hover:border-[#0f5b6c]"
                }`}
              >
                <Shield className="h-3 w-3" />
                Risk Zones
              </button>

              <button
                onClick={() => setShowPopulation(!showPopulation)}
                className={`px-2.5 py-1 rounded-[3px] border text-[11px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                  showPopulation
                    ? "bg-[#0f5b6c] text-white border-[#0f5b6c]"
                    : "bg-white text-[#5a6872] border-[#cbd2d6] hover:border-[#0f5b6c]"
                }`}
              >
                <Users className="h-3 w-3" />
                Population
              </button>

              <button
                onClick={() => setShowInfrastructure(!showInfrastructure)}
                className={`px-2.5 py-1 rounded-[3px] border text-[11px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                  showInfrastructure
                    ? "bg-[#0f5b6c] text-white border-[#0f5b6c]"
                    : "bg-white text-[#5a6872] border-[#cbd2d6] hover:border-[#0f5b6c]"
                }`}
              >
                <Building className="h-3 w-3" />
                Infrastructure
              </button>

              <button
                onClick={() => setShowMaritime(!showMaritime)}
                className={`px-2.5 py-1 rounded-[3px] border text-[11px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                  showMaritime
                    ? "bg-[#0f5b6c] text-white border-[#0f5b6c]"
                    : "bg-white text-[#5a6872] border-[#cbd2d6] hover:border-[#0f5b6c]"
                }`}
              >
                <Anchor className="h-3 w-3" />
                Fishing/Maritime
              </button>
            </div>
          </div>

          {/* Uncluttered Leaflet Map */}
          <div className="h-[460px] w-full">
            <CycloneMap
              center={[currentStep.lat, currentStep.lon]}
              zoom={5}
              tracks={dynamicTracks}
              forecastPath={dynamicForecastPath}
              markers={mapMarkers}
              title={`Cyclone ${currentStorm.storm_name} Corridor & Coastal Exposure`}
              subtitle={`T+${currentStep.hour}h position fix: ${currentStep.wind_kts} kt · Corridor radius: 140km`}
              height="460px"
              windLayers={true}
              riskLayers={true}
            />
          </div>

          {/* Clean Legend */}
          <div className="p-3 bg-[#f8f9fa] border-t border-[#cbd2d6] text-[11px] text-[#5a6872] flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-4">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#b91c1c] inline-block" /> Red: Critical Landfall Zone
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#f97316] inline-block" /> Orange: High Exposure
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#eab308] inline-block" /> Yellow: Moderate Coastal Swell
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#22c55e] inline-block" /> Green: Low / Advisory Only
              </span>
            </div>
            <span className="text-[10px] text-[#0f5b6c] font-bold">
              Map automatically centers on active storm fix
            </span>
          </div>
        </div>

        {/* Selected District/Area Card: Risk Level, Plain-Language Reasons, People Exposed, Shelters, Key Actions */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-5 shadow-xs font-mono space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#e2e6e9] gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-xs font-bold border rounded-[2px] ${getRiskBadgeColor(activeDistrict.risk_color)}`}>
                  {activeDistrict.risk_color.toUpperCase()} ZONE · {activeDistrict.risk_level}
                </span>
                <span className="text-xs text-[#5a6872]">
                  Distance from Eye: <strong className="text-[#182026]">{activeDistrict.distance_from_eye_km} km</strong>
                </span>
              </div>
              <h2 className="text-lg sm:text-xl font-bold text-[#182026] mt-1">
                {activeDistrict.district_name}
              </h2>
              <span className="text-xs text-[#5a6872]">{activeDistrict.state_or_province}</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-1.5 py-0.5 text-[10px] font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                {activeDistrict.simulation_label || "DEMO / SIMULATION"}
              </span>
            </div>
          </div>

          {/* Exposure Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">People Exposed</span>
              <span className="text-base font-bold text-[#b91c1c]">
                {activeDistrict.simulated_population_at_risk.toLocaleString()}
              </span>
              <span className="text-[10px] text-[#5a6872] block">Vulnerable coastal strip</span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Peak Wind Gust</span>
              <span className="text-base font-bold text-[#b45309]">
                {activeDistrict.peak_wind_gust_kmh} km/h
              </span>
              <span className="text-[10px] text-[#5a6872] block">Structural impact hazard</span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Storm Surge Height</span>
              <span className="text-base font-bold text-[#0f5b6c]">
                {activeDistrict.surge_height_meters} meters
              </span>
              <span className="text-[10px] text-[#5a6872] block">Inundation threat</span>
            </div>

            <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
              <span className="text-[10px] text-[#5a6872] uppercase block">Evacuation Shelters</span>
              <span className="text-base font-bold text-[#1b7a4f]">
                {activeDistrict.evacuation_shelters_active} Operational
              </span>
              <span className="text-[10px] text-[#5a6872] block">Designated relief points</span>
            </div>
          </div>

          {/* Plain-Language Reasons */}
          <div className="p-3.5 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5 text-xs">
            <div className="flex items-center gap-1.5 font-bold uppercase text-[#0f5b6c]">
              <Info className="h-4 w-4" />
              Plain-Language Impact Rationale
            </div>
            <p className="text-[#182026] leading-relaxed">
              {activeDistrict.plain_language_reasons}
            </p>
          </div>

          {/* Key Recommended Actions (Checklist) */}
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-1.5 font-bold uppercase text-[#b91c1c]">
              <CheckCircle2 className="h-4 w-4" />
              Key Operational Actions & Directives
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {activeDistrict.key_recommended_actions.map((act, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded-[3px] bg-white border border-[#cbd2d6] flex items-start gap-2 shadow-xs"
                >
                  <span className="w-5 h-5 rounded-full bg-[#0f5b6c] text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-[#182026] text-[11px] leading-tight">
                    {act}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/prediction">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: Prediction
            </Button>
          </Link>
          <Link href="/alerts">
            <Button variant="primary" size="sm">
              Next Stage: Targeted Alerts
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
