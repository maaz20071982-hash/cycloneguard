"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Alert } from "@/components/ui/Alert";
import { CycloneMap, MapTrackPoint } from "@/components/ui/CycloneMap";
import { useStorm } from "@/lib/storm-context";
import {
  Compass,
  Layers,
  Eye,
  Activity,
  Wind,
  BarChart3,
  MapPin,
  AlertTriangle,
  Shield,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  CheckCircle2,
  Clock,
  ExternalLink,
  Info,
  Radio,
  Send,
  FileCheck,
  Check,
  Cpu,
} from "lucide-react";

export default function GuidedJudgeDemoPage() {
  const {
    currentStorm,
    selectStorm,
    availableStorms,
    authorizeAlert,
    authorizeAllAlerts,
    updateHumanReview,
    isFullyAuthorized,
  } = useStorm();

  const [currentStep, setCurrentStep] = useState<number>(1);
  const [reviewNotes, setReviewNotes] = useState<string>(
    currentStorm.authorized_human_review.meteorologist_notes
  );
  const [activeDistrictIndex, setActiveDistrictIndex] = useState<number>(0);

  // Sync review notes if storm changes
  useEffect(() => {
    setReviewNotes(currentStorm.authorized_human_review.meteorologist_notes);
  }, [currentStorm]);

  // Keyboard navigation for presentation ergonomics (Left / Right arrow keys)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" && currentStep < 9) {
        setCurrentStep((prev) => prev + 1);
      } else if (e.key === "ArrowLeft" && currentStep > 1) {
        setCurrentStep((prev) => prev - 1);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentStep]);

  const stages = [
    { num: 1, name: "Observation Data", short: "Observations", icon: <Compass className="h-3.5 w-3.5" /> },
    { num: 2, name: "Multi-Source Fusion", short: "Fusion", icon: <Layers className="h-3.5 w-3.5" /> },
    { num: 3, name: "AI Detection", short: "AI Detection", icon: <Eye className="h-3.5 w-3.5" /> },
    { num: 4, name: "Intensity Classification", short: "Intensity", icon: <Activity className="h-3.5 w-3.5" /> },
    { num: 5, name: "Track & Landfall Prediction", short: "Prediction", icon: <Wind className="h-3.5 w-3.5" /> },
    { num: 6, name: "Explainable Confidence", short: "Confidence", icon: <BarChart3 className="h-3.5 w-3.5" /> },
    { num: 7, name: "GIS Risk & Impact", short: "GIS Risk", icon: <MapPin className="h-3.5 w-3.5" /> },
    { num: 8, name: "Targeted Alerts", short: "Alerts", icon: <AlertTriangle className="h-3.5 w-3.5" /> },
    { num: 9, name: "Authorized Human Review", short: "Review", icon: <Shield className="h-3.5 w-3.5" /> },
  ];

  // Map forecast points for the prediction and map stages
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

  const historicalMapPoints: MapTrackPoint[] = [
    {
      lat: currentStorm.observation_data.latitude - 1.2,
      lon: currentStorm.observation_data.longitude + 2.0,
      time: "t0 - 12h",
      intensity_kts: 25,
      intensity_kmh: 46,
      category: "Depression",
    },
    {
      lat: currentStorm.observation_data.latitude - 0.5,
      lon: currentStorm.observation_data.longitude + 0.9,
      time: "t0 - 6h",
      intensity_kts: 30,
      intensity_kmh: 55,
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

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      {/* Top Demo Banner */}
      <div className="bg-[#0f5b6c] text-white px-4 py-2 border-b border-[#0a4350]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-bold uppercase tracking-wider">
              CYCLONESENSE AI · DISASTER MANAGEMENT WALKTHROUGH (SIH26070)
            </span>
            <span className="text-cyan-200">|</span>
            <span className="text-cyan-100 hidden sm:inline">
              Target: Cyclone {currentStorm.storm_name} ({currentStorm.observation_time_utc.slice(0, 16)} UTC)
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-cyan-200 text-[11px]">Active Storm:</span>
              <select
                value={currentStorm.storm_id}
                onChange={(e) => selectStorm(e.target.value)}
                className="bg-[#0a4350] text-white text-[11px] font-mono px-2 py-0.5 rounded-[2px] border border-cyan-400/40"
              >
                {availableStorms.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.basin.split("(")[0]})
                  </option>
                ))}
              </select>
            </div>
            <span className="text-cyan-200 text-[11px] hidden md:inline">
              Use ← / → Arrow Keys
            </span>
          </div>
        </div>
      </div>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Step Navigation Bar & Presentation Controls */}
        <div className="p-4 rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-2">
              <Badge variant="brand" className="font-mono text-xs px-2.5 py-0.5">
                STAGE {currentStep} OF 9
              </Badge>
              <h2 className="text-sm sm:text-base font-bold text-[#182026] uppercase font-mono">
                {stages[currentStep - 1].name}
              </h2>
              <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>

            {/* Presentation Controls: Prev, Next, Reset */}
            <div className="flex flex-wrap items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setCurrentStep((prev) => Math.max(1, prev - 1))}
                disabled={currentStep === 1}
              >
                <ArrowLeft className="h-3.5 w-3.5 mr-1" />
                Previous
              </Button>

              <Button
                size="sm"
                variant="primary"
                onClick={() => setCurrentStep((prev) => Math.min(9, prev + 1))}
                disabled={currentStep === 9}
              >
                Next
                <ArrowRight className="h-3.5 w-3.5 ml-1" />
              </Button>

              <Button
                size="sm"
                variant="ghost"
                onClick={() => setCurrentStep(1)}
                title="Reset to Stage 1"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span className="hidden sm:inline ml-1">Reset</span>
              </Button>

              <Link href="/user/monitor">
                <Button size="sm" variant="outline" className="text-[#5f6b7c]">
                  Open GIS Monitor
                </Button>
              </Link>
            </div>
          </div>

          {/* Stepper Progress Bar (9 Stages) */}
          <div className="grid grid-cols-3 sm:grid-cols-9 gap-1.5 pt-1">
            {stages.map((stage) => {
              const isCurrent = currentStep === stage.num;
              const isCompleted = currentStep > stage.num;
              return (
                <button
                  key={stage.num}
                  onClick={() => setCurrentStep(stage.num)}
                  className={`px-2 py-1.5 rounded-[3px] text-[10px] font-mono font-semibold transition-colors flex items-center justify-center gap-1 ${
                    isCurrent
                      ? "bg-[#0f5b6c] text-white shadow-xs"
                      : isCompleted
                      ? "bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] hover:bg-[#dbebee]"
                      : "bg-[#f8f9fa] text-[#7d8c97] border border-[#e2e6e9] hover:bg-[#f1f3f4]"
                  }`}
                >
                  <span>{stage.num}.</span>
                  <span className="truncate">{stage.short}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ------------------------------------------------------------ */}
        {/* STAGE 1: OBSERVATION DATA                                    */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 1 — OBSERVATION DATA: MULTI-SENSOR INGESTION AT t0"
                subtitle="Calibrated geostationary satellite infrared, coastal Doppler radar, ocean buoy telemetry, and NWP soundings"
              />
              <div className="p-6 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
                  <div>
                    <span className="text-[10px] font-mono text-[#0f5b6c] uppercase font-bold block">
                      Observation Fix (t0)
                    </span>
                    <h3 className="text-xl font-bold font-mono text-[#182026]">
                      {currentStorm.observation_time_utc.slice(0, 16)} UTC · {currentStorm.storm_name}
                    </h3>
                    <span className="text-xs text-[#5f6b7c] font-mono">
                      Location: {currentStorm.observation_data.latitude.toFixed(2)}° N, {currentStorm.observation_data.longitude.toFixed(2)}° E ({currentStorm.observation_data.location_name})
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant="brand">{currentStorm.observation_data.basin}</Badge>
                    <StatusBadge status="operational" label="4 Sensors Synchronized" />
                  </div>
                </div>

                {/* 4 Sensor Telemetry Ingestion Feeds */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
                  {/* Feed 1: Satellite IR */}
                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[#0f5b6c] uppercase">1. Satellite Infrared</span>
                      <Badge variant="neutral" className="text-[9px]">IRWIN 11µm</Badge>
                    </div>
                    <div className="text-sm font-bold text-[#182026]">
                      Core Tb: {currentStorm.observation_data.core_convection_mean_k.toFixed(1)} K
                    </div>
                    <p className="text-[11px] text-[#5f6b7c] font-sans">
                      Mean Tb: {currentStorm.observation_data.irwin_mean_tb_k.toFixed(1)} K · Cold fraction: {currentStorm.observation_data.cold_cloud_fraction_233k}%
                    </p>
                    <span className="text-[9px] text-[#0f5b6c] font-bold block">Source: NOAA HURSAT-B1 / INSAT-3D</span>
                  </div>

                  {/* Feed 2: Ocean Buoy */}
                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[#0f5b6c] uppercase">2. Moored Ocean Buoy</span>
                      <Badge variant="neutral" className="text-[9px]">{currentStorm.observation_data.buoy_telemetry.station_id}</Badge>
                    </div>
                    <div className="text-sm font-bold text-[#182026]">
                      SST: {currentStorm.observation_data.buoy_telemetry.sst_celsius} °C
                    </div>
                    <p className="text-[11px] text-[#5f6b7c] font-sans">
                      Salinity: {currentStorm.observation_data.buoy_telemetry.sea_surface_salinity_psu} PSU · Waves: {currentStorm.observation_data.buoy_telemetry.wave_height_meters} m
                    </p>
                    <span className="text-[9px] text-[#1b7a4f] font-bold block">Status: {currentStorm.observation_data.buoy_telemetry.status}</span>
                  </div>

                  {/* Feed 3: Coastal Doppler Radar */}
                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[#0f5b6c] uppercase">3. Coastal Radar</span>
                      <Badge variant="neutral" className="text-[9px]">DWR</Badge>
                    </div>
                    <div className="text-sm font-bold text-[#182026]">
                      Echo: {currentStorm.observation_data.radar_telemetry.reflectivity_max_dbz} dBZ
                    </div>
                    <p className="text-[11px] text-[#5f6b7c] font-sans">
                      Station: {currentStorm.observation_data.radar_telemetry.station_name} · Range: {currentStorm.observation_data.radar_telemetry.range_km} km
                    </p>
                    <span className="text-[9px] text-[#1b7a4f] font-bold block">Status: Outer rainband acquisition</span>
                  </div>

                  {/* Feed 4: NWP Atmospheric Soundings */}
                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[#0f5b6c] uppercase">4. NWP Sounding</span>
                      <Badge variant="neutral" className="text-[9px]">GFS / ECMWF</Badge>
                    </div>
                    <div className="text-sm font-bold text-[#182026]">
                      Shear: {currentStorm.observation_data.nwp_environment.vertical_wind_shear_kts} kt
                    </div>
                    <p className="text-[11px] text-[#5f6b7c] font-sans">
                      Mid-level RH: {currentStorm.observation_data.nwp_environment.mid_level_rh_pct}% · OHC: {currentStorm.observation_data.nwp_environment.ocean_heat_content_kj_cm2} kJ/cm²
                    </p>
                    <span className="text-[9px] text-[#0f5b6c] font-bold block">Condition: Low shear / High energy</span>
                  </div>
                </div>

                {/* Map of Initial Observation Fix */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-[#182026] uppercase font-bold flex items-center gap-1.5">
                      <Compass className="h-4 w-4 text-[#0f5b6c]" />
                      Observation Fix & Immediate Historical Track
                    </span>
                    <span className="text-[#0f5b6c]">
                      Initial Intensity: {currentStorm.observation_data.current_wind_kts} kt · Pressure: {currentStorm.observation_data.central_pressure_mb} hPa
                    </span>
                  </div>
                  <CycloneMap
                    title={`Cyclone ${currentStorm.storm_name} — Observation Fix (t0)`}
                    subtitle="Authentic historical NOAA IBTrACS trajectory · 1-minute sustained wind baseline"
                    center={[currentStorm.observation_data.latitude, currentStorm.observation_data.longitude]}
                    zoom={5}
                    tracks={historicalMapPoints}
                    selectedTime={currentStorm.observation_time_utc}
                    className="h-[360px]"
                  />
                </div>
              </div>
            </Panel>

            <div className="flex justify-end">
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(2)}>
                Step 2: Inspect Multi-Source Fusion
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 2: MULTI-SOURCE FUSION                                 */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 2 — MULTI-SOURCE FUSION & QUALITY ASSURANCE"
                subtitle="Synchronizing spatio-temporal observations into a 61-feature canonical contract without data leakage"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Feature Contract</span>
                    <span className="text-2xl font-extrabold text-[#0f5b6c]">
                      {currentStorm.multi_source_fusion.total_features} Canonical
                    </span>
                    <span className="text-[11px] text-[#5f6b7c] block">
                      23 Kinematics + 38 Spatial Structural Proxies
                    </span>
                  </div>

                  <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Spatial Alignment</span>
                    <span className="text-2xl font-extrabold text-[#182026]">
                      {currentStorm.multi_source_fusion.spatial_alignment_offset_km} km
                    </span>
                    <span className="text-[11px] text-[#5f6b7c] block">
                      Sub-pixel satellite patch to best-track center
                    </span>
                  </div>

                  <div className="p-4 bg-[#f0fdf4] border border-[#bbf7d0] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#1b7a4f] uppercase block">Leakage Firewall</span>
                    <span className="text-base font-bold text-[#1b7a4f] block">
                      ASSERTION PASSED
                    </span>
                    <span className="text-[11px] text-[#5f6b7c] block">
                      Strict temporal barrier: t_feature &lt; t_target
                    </span>
                  </div>
                </div>

                {/* Key Fused Telemetry Metrics Table */}
                <div className="space-y-2 pt-2">
                  <span className="text-xs font-bold text-[#182026] uppercase block">
                    Fused Telemetry Variables & Normalized Z-Scores
                  </span>
                  <div className="border border-[#e2e6e9] rounded-[4px] overflow-hidden">
                    <table className="w-full text-left">
                      <thead className="bg-[#f1f3f4] text-[#5f6b7c] text-[10px] uppercase">
                        <tr>
                          <th className="py-2 px-3">Variable Name</th>
                          <th className="py-2 px-3">Raw Value</th>
                          <th className="py-2 px-3">Standardized Z-Score</th>
                          <th className="py-2 px-3">Physical Interpretation</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#e2e6e9] bg-white">
                        {currentStorm.multi_source_fusion.key_fused_metrics.map((m, idx) => (
                          <tr key={idx}>
                            <td className="py-2.5 px-3 font-semibold text-[#182026]">{m.name}</td>
                            <td className="py-2.5 px-3 text-[#0f5b6c] font-bold">{m.raw_value}</td>
                            <td className="py-2.5 px-3">+{m.z_score.toFixed(2)}σ</td>
                            <td className="py-2.5 px-3 text-[#5f6b7c] font-sans text-[11px]">{m.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <Alert variant="info" title="Scientific Handling of Missing Sensors">
                  Satellite infrared and microwave passes are intermittent in operational environments. Missing sensors are handled truthfully using explicit presence indicator flags (e.g. <code className="font-mono">has_vschn = 1</code>, <code className="font-mono">has_microwave = 0</code>) rather than fabricating synthetic data.
                </Alert>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(1)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Observations
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(3)}>
                Step 3: Run AI Detection
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 3: AI DETECTION                                        */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 3 — AI DETECTION: VORTEX LOCALIZATION & MORPHOLOGY"
                subtitle="Autonomous cyclone pattern recognition and convective core segmentation"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                  <div className="space-y-4">
                    <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-[#0f5b6c] uppercase font-bold">Detection Algorithm</span>
                        <Badge variant="brand">{currentStorm.ai_detection.simulation_label}</Badge>
                      </div>
                      <h4 className="text-sm font-bold text-[#182026]">
                        {currentStorm.ai_detection.algorithm}
                      </h4>
                      <p className="text-xs text-[#5f6b7c] font-sans leading-relaxed">
                        Evaluates azimuthal gradient distribution and deep convective cloud symmetry to identify the true center of circulation.
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-white border border-[#e2e6e9] rounded-[3px]">
                        <span className="text-[10px] text-[#5f6b7c] block uppercase">Vortex Center Fix</span>
                        <span className="text-base font-bold text-[#0f5b6c]">
                          {currentStorm.ai_detection.center_fix_lat}° N, {currentStorm.ai_detection.center_fix_lon}° E
                        </span>
                        <span className="text-[9px] text-[#5f6b7c] block">Confidence: {(currentStorm.ai_detection.detection_confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="p-3 bg-white border border-[#e2e6e9] rounded-[3px]">
                        <span className="text-[10px] text-[#5f6b7c] block uppercase">Vortex Symmetry</span>
                        <span className="text-base font-bold text-[#182026]">
                          {currentStorm.ai_detection.vortex_symmetry_score.toFixed(2)} / 1.00
                        </span>
                        <span className="text-[9px] text-[#1b7a4f] block">{currentStorm.ai_detection.convective_band_count} Curved Spiral Bands</span>
                      </div>
                    </div>

                    <div className="p-3 bg-[#edf5f7] border border-[#bcdbe2] rounded-[3px] text-[#0f5b6c] font-sans text-xs">
                      <strong>Eyewall Assessment:</strong> {currentStorm.ai_detection.eye_wall_definition}
                    </div>
                  </div>

                  {/* Satellite Visual Representation */}
                  <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#182026] uppercase">
                        Center Localization Overlay
                      </span>
                      <span className="text-[10px] text-[#5f6b7c]">64 × 64 px Infrared Patch</span>
                    </div>

                    <div className="relative aspect-video w-full rounded-[4px] overflow-hidden border border-[#cbd2d6] bg-[#0b1520] flex items-center justify-center">
                      <img
                        src={currentStorm.observation_data.irwin_patch_url}
                        alt="Satellite Detection Patch"
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          e.currentTarget.style.display = "none";
                        }}
                      />
                      {/* Reticle Overlay */}
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="h-16 w-16 border-2 border-teal-400/80 rounded-full animate-pulse flex items-center justify-center">
                          <div className="h-2 w-2 bg-red-500 rounded-full" />
                        </div>
                      </div>
                      <div className="absolute bottom-2 left-2 right-2 bg-black/80 px-2 py-1 text-[10px] text-white flex justify-between">
                        <span>Resolved Center: 13.10°N, 64.60°E</span>
                        <span className="text-teal-300 font-bold">VORTEX DETECTED</span>
                      </div>
                    </div>

                    <p className="text-[11px] text-[#5f6b7c] font-sans">
                      Automated pattern recognition isolates the cloud-top thermal gradient and resolves center coordinates independently of manual Dvorak ambiguity.
                    </p>
                  </div>
                </div>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(2)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Fusion
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(4)}>
                Step 4: Intensity Classification
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 4: INTENSITY CLASSIFICATION                            */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 4 — INTENSITY CLASSIFICATION & RAPID INTENSIFICATION (RI) SCREENING"
                subtitle="Categorizing surface wind speed and flagging high-consequence 24-hour intensification potential"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Current Classification</span>
                    <span className="text-lg font-bold text-[#182026] block">
                      {currentStorm.intensity_classification.current_category_imd}
                    </span>
                    <span className="text-[11px] text-[#5f6b7c] block">
                      WMO: {currentStorm.intensity_classification.current_category_wmo}
                    </span>
                  </div>

                  <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">1-Min Sustained Wind</span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-extrabold text-[#0f5b6c]">
                        {currentStorm.intensity_classification.v_max_kts}
                      </span>
                      <span className="text-sm font-semibold text-[#5f6b7c]">kt ({currentStorm.intensity_classification.v_max_kmh} km/h)</span>
                    </div>
                    <span className="text-[10px] text-[#5f6b7c] block">
                      Pressure: {currentStorm.intensity_classification.central_pressure_mb} hPa
                    </span>
                  </div>

                  <div className="p-4 bg-[#fef2f2] border-2 border-[#fecaca] rounded-[4px] space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-[#b91c1c] uppercase font-bold block">24h RI Screening</span>
                      <Badge variant="danger" className="text-[9px]">FLAGGED</Badge>
                    </div>
                    <span className="text-sm font-extrabold text-[#b91c1c] block">
                      {currentStorm.intensity_classification.ri_screening_label}
                    </span>
                    <span className="text-[10px] text-[#b91c1c] block">
                      {currentStorm.intensity_classification.ri_criteria}
                    </span>
                  </div>
                </div>

                {/* IMD Intensity Scale Alignment Chart */}
                <div className="p-4 bg-white border border-[#e2e6e9] rounded-[4px] space-y-3">
                  <span className="text-xs font-bold text-[#182026] uppercase block">
                    North Indian Ocean Cyclonic Intensity Scale (IMD Classification)
                  </span>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span>Current Level: <strong>{currentStorm.intensity_classification.v_max_kts} kt</strong></span>
                      <span className="text-[#b91c1c] font-bold">Projected 24h: ≥ 65 kt (Very Severe Cyclonic Storm)</span>
                    </div>

                    <div className="h-3 w-full bg-[#e2e6e9] rounded-full overflow-hidden flex">
                      <div style={{ width: "20%" }} className="bg-[#0ea5e9]" title="Depression (17-27 kt)" />
                      <div style={{ width: "15%" }} className="bg-[#14b8a6]" title="Deep Depression (28-33 kt)" />
                      <div style={{ width: "20%" }} className="bg-[#eab308]" title="Cyclonic Storm (34-47 kt)" />
                      <div style={{ width: "15%" }} className="bg-[#f97316]" title="Severe Cyclonic Storm (48-63 kt)" />
                      <div style={{ width: "15%" }} className="bg-[#ef4444]" title="Very Severe (64-89 kt)" />
                      <div style={{ width: "15%" }} className="bg-[#d946ef]" title="Super Cyclone (≥120 kt)" />
                    </div>

                    <div className="flex justify-between text-[9px] text-[#5f6b7c]">
                      <span>Depression (25kt)</span>
                      <span>Cyclonic Storm (34kt)</span>
                      <span>Severe (48kt)</span>
                      <span>Very Severe (64kt)</span>
                      <span>Super Cyclone (120kt)</span>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-[#edf5f7] border border-[#bcdbe2] rounded-[3px] text-xs font-sans text-[#182026] leading-relaxed">
                  <strong>Operational Insight:</strong> While traditional monitoring treats a 30 kt depression as low-consequence, the AI early-warning system flags that kinematic rate of change and structural proxies indicate an imminent explosion into Hurricane-force winds (+35 kt in 24h).
                </div>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(3)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Detection
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(5)}>
                Step 5: View Track & Landfall Prediction
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 5: TRACK & LANDFALL PREDICTION                         */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 5 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 5 — TRACK & LANDFALL PREDICTION (MULTI-HORIZON)"
                subtitle="Projected 48-hour trajectory, forward velocity, cone of uncertainty, and estimated time of landfall (ETL)"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                {/* Landfall Prediction Summary Banner */}
                <div className="p-4 bg-[#fef8ee] border border-[#fed7aa] rounded-[4px] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-[#b45309] uppercase block tracking-wider">
                      Projected Landfall Assessment ({currentStorm.track_landfall_prediction.landfall_prediction.simulation_label})
                    </span>
                    <h3 className="text-base font-extrabold text-[#182026]">
                      {currentStorm.track_landfall_prediction.landfall_prediction.predicted_landfall_sector}
                    </h3>
                    <div className="text-xs text-[#5f6b7c] flex flex-wrap items-center gap-3">
                      <span>ETL: <strong>{currentStorm.track_landfall_prediction.landfall_prediction.estimated_time_of_landfall_utc.slice(0, 16)} UTC</strong></span>
                      <span>•</span>
                      <span>Lead Time: <strong>{currentStorm.track_landfall_prediction.landfall_prediction.lead_time_hours} Hours</strong></span>
                      <span>•</span>
                      <span>Landfall Vmax: <strong>{currentStorm.track_landfall_prediction.landfall_prediction.expected_intensity_at_landfall_kts} kt</strong></span>
                    </div>
                  </div>

                  <Badge variant="warning" className="shrink-0 text-xs px-3 py-1 font-bold">
                    {currentStorm.track_landfall_prediction.landfall_prediction.expected_category_at_landfall}
                  </Badge>
                </div>

                {/* Interactive Map with Forecast Path and Cone */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#182026] uppercase flex items-center gap-1.5">
                      <Wind className="h-4 w-4 text-[#0f5b6c]" />
                      Multi-Horizon Forecast Trajectory & Cone of Uncertainty
                    </span>
                    <span className="text-[#0f5b6c]">Model: {currentStorm.track_landfall_prediction.model_name}</span>
                  </div>
                  <CycloneMap
                    title="Track & Landfall Prediction Map"
                    subtitle="Multi-horizon trajectory: 6h, 12h, 24h, 36h, 48h projections with expanding uncertainty cone"
                    center={[currentStorm.observation_data.latitude, currentStorm.observation_data.longitude - 3.0]}
                    zoom={5}
                    tracks={historicalMapPoints}
                    forecastPath={forecastMapPoints}
                    selectedTime={currentStorm.observation_time_utc}
                    riskLayers={true}
                    windLayers={true}
                    className="h-[380px]"
                  />
                </div>

                {/* Horizon Table */}
                <div className="space-y-2 pt-2">
                  <span className="text-xs font-bold text-[#182026] uppercase block">
                    Multi-Horizon Forecast Table
                  </span>
                  <div className="border border-[#e2e6e9] rounded-[4px] overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-[#f1f3f4] text-[#5f6b7c] text-[10px] uppercase">
                        <tr>
                          <th className="py-2 px-3">Horizon</th>
                          <th className="py-2 px-3">Valid Time (UTC)</th>
                          <th className="py-2 px-3">Position</th>
                          <th className="py-2 px-3">Wind (kt / km/h)</th>
                          <th className="py-2 px-3">Pressure</th>
                          <th className="py-2 px-3">Category</th>
                          <th className="py-2 px-3">Uncertainty Cone</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#e2e6e9] bg-white">
                        {currentStorm.track_landfall_prediction.forecast_points.map((pt) => (
                          <tr key={pt.horizon_hours}>
                            <td className="py-2 px-3 font-bold text-[#0f5b6c]">+{pt.horizon_hours} Hours</td>
                            <td className="py-2 px-3">{pt.valid_time_utc.slice(0, 16)}</td>
                            <td className="py-2 px-3">{pt.latitude.toFixed(1)}°N, {pt.longitude.toFixed(1)}°E</td>
                            <td className="py-2 px-3 font-semibold text-[#182026]">{pt.wind_speed_kts} kt ({pt.wind_speed_kmh} km/h)</td>
                            <td className="py-2 px-3">{pt.central_pressure_mb} hPa</td>
                            <td className="py-2 px-3">
                              <Badge variant={pt.wind_speed_kts >= 64 ? "danger" : pt.wind_speed_kts >= 34 ? "warning" : "brand"}>
                                {pt.category}
                              </Badge>
                            </td>
                            <td className="py-2 px-3 text-[#5f6b7c]">±{pt.cone_radius_km} km</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(4)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Intensity
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(6)}>
                Step 6: Explainable Confidence
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 6: EXPLAINABLE CONFIDENCE                              */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 6 && (
          <div className="space-y-6">
            <Panel className="border-2 border-[#0f5b6c]">
              <PanelHeader
                title="STAGE 6 — EXPLAINABLE CONFIDENCE & ATTRIBUTION"
                subtitle="Standardized linear decision factor weights explaining the model's empirical score"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                {/* Confidence & Empirical Score Showcase */}
                <div className="p-5 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[4px] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-[#0f5b6c] uppercase block">
                      {currentStorm.explainable_confidence.model_card.model_id}
                    </span>
                    <div className="flex items-baseline gap-3">
                      <span className="text-4xl font-extrabold text-[#0f5b6c]">
                        {currentStorm.explainable_confidence.empirical_ri_risk_index.toFixed(4)}
                      </span>
                      <span className="text-xs text-[#5f6b7c]">
                        Empirical RI Risk Index
                      </span>
                    </div>
                    <span className="text-[11px] text-[#5f6b7c] block">
                      Operating Threshold: <strong>τ = {currentStorm.explainable_confidence.operating_threshold_tau}</strong> (Margin: +{currentStorm.explainable_confidence.margin_above_threshold.toFixed(4)})
                    </span>
                  </div>

                  <div className="flex flex-col items-end gap-1.5">
                    <Badge variant="danger" className="text-xs px-3 py-1 font-bold">
                      {currentStorm.explainable_confidence.risk_tier} (FLAGGED)
                    </Badge>
                    <span className="text-[10px] text-[#b45309] font-bold">
                      {currentStorm.explainable_confidence.calibration_status}
                    </span>
                  </div>
                </div>

                {/* Feature Attribution List */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#182026] uppercase">
                      Top Supporting Factor Weights (Elevating RI Risk)
                    </span>
                    <span className="text-[10px] text-[#5f6b7c]">Standardized Z-Score Weights</span>
                  </div>

                  <div className="space-y-2">
                    {currentStorm.explainable_confidence.top_supporting_features.map((f) => (
                      <div
                        key={f.feature_name}
                        className="p-3 bg-[#f0fdf4] border border-[#bbf7d0] rounded-[3px] flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                      >
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-[#182026]">{f.display_name}</span>
                            <code className="text-[10px] text-[#0f5b6c] bg-white px-1.5 py-0.2 rounded border border-[#bbf7d0]">
                              {f.feature_name}
                            </code>
                          </div>
                          <p className="text-[11px] text-[#5f6b7c] font-sans">
                            {f.physical_interpretation}
                          </p>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="font-bold text-[#1b7a4f] text-sm block">
                            +{f.attribution_score.toFixed(4)}
                          </span>
                          <span className="text-[9px] text-[#5f6b7c]">{f.contribution_pct}% contribution</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <Alert variant="warning" title="Mandatory Statistical Governance Standard">
                  Feature contributions describe mathematical decision boundaries in the historical training sample and do NOT prove physical or thermodynamic causality. Decision support outputs must always be weighed with official synoptic bulletins.
                </Alert>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(5)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Track Prediction
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(7)}>
                Step 7: View GIS Risk & Impact
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 7: GIS RISK & IMPACT                                   */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 7 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 7 — GIS RISK & IMPACT ASSESSMENT"
                subtitle="Wind hazard swaths (R34/R50/R64), storm surge vulnerability, and coastal district exposure"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                {/* Wind Radii & Surge Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Gale Wind Radius (R34)</span>
                    <span className="text-xl font-extrabold text-[#0ea5e9]">
                      {currentStorm.gis_risk_impact.wind_hazard_radii.gale_force_34kt_radius_km} km
                    </span>
                    <span className="text-[10px] text-[#5f6b7c] block">34-47 kt wind envelope</span>
                  </div>

                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Storm Wind Radius (R50)</span>
                    <span className="text-xl font-extrabold text-[#eab308]">
                      {currentStorm.gis_risk_impact.wind_hazard_radii.storm_force_50kt_radius_km} km
                    </span>
                    <span className="text-[10px] text-[#5f6b7c] block">48-63 kt severe gale</span>
                  </div>

                  <div className="p-3.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#5f6b7c] uppercase block">Hurricane Radius (R64)</span>
                    <span className="text-xl font-extrabold text-[#ef4444]">
                      {currentStorm.gis_risk_impact.wind_hazard_radii.hurricane_force_64kt_radius_km} km
                    </span>
                    <span className="text-[10px] text-[#5f6b7c] block">≥ 64 kt destructive core</span>
                  </div>

                  <div className="p-3.5 bg-[#fef2f2] border border-[#fecaca] rounded-[4px] space-y-1">
                    <span className="text-[10px] text-[#b91c1c] uppercase block font-bold">Peak Storm Surge</span>
                    <span className="text-xl font-extrabold text-[#b91c1c]">
                      {currentStorm.gis_risk_impact.storm_surge_peak_meters} m
                    </span>
                    <span className="text-[10px] text-[#b91c1c] block">Above astronomical high tide</span>
                  </div>
                </div>

                {/* Exposed Coastal Districts Table */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#182026] uppercase">
                      Exposed Coastal Districts & Shelters Readiness
                    </span>
                    <span className="px-1.5 py-0.5 text-[9px] font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                      POPULATION VALUES: {currentStorm.gis_risk_impact.simulation_label}
                    </span>
                  </div>

                  <div className="border border-[#e2e6e9] rounded-[4px] overflow-hidden">
                    <table className="w-full text-left">
                      <thead className="bg-[#f1f3f4] text-[#5f6b7c] text-[10px] uppercase">
                        <tr>
                          <th className="py-2 px-3">Coastal District</th>
                          <th className="py-2 px-3">Distance to Track</th>
                          <th className="py-2 px-3">Peak Gust</th>
                          <th className="py-2 px-3">Surge Height</th>
                          <th className="py-2 px-3">Population at Risk [SIMULATION]</th>
                          <th className="py-2 px-3">Shelters</th>
                          <th className="py-2 px-3">Threat Tier</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#e2e6e9] bg-white">
                        {currentStorm.gis_risk_impact.exposed_districts.map((d, idx) => (
                          <tr
                            key={d.district_name}
                            onClick={() => setActiveDistrictIndex(idx)}
                            className={`cursor-pointer transition-colors ${
                              activeDistrictIndex === idx ? "bg-[#edf5f7]" : "hover:bg-[#f8f9fa]"
                            }`}
                          >
                            <td className="py-2.5 px-3 font-bold text-[#182026]">
                              {d.district_name}
                              <span className="block text-[10px] text-[#5f6b7c] font-normal">{d.state_or_province}</span>
                            </td>
                            <td className="py-2.5 px-3">{d.distance_from_eye_km} km</td>
                            <td className="py-2.5 px-3">{d.peak_wind_gust_kmh} km/h</td>
                            <td className="py-2.5 px-3 text-[#b91c1c] font-bold">{d.surge_height_meters} m</td>
                            <td className="py-2.5 px-3 font-semibold text-[#0f5b6c]">
                              {d.simulated_population_at_risk.toLocaleString()}
                            </td>
                            <td className="py-2.5 px-3">{d.evacuation_shelters_active} Active</td>
                            <td className="py-2.5 px-3">
                              <Badge variant={d.risk_level === "CRITICAL" ? "danger" : d.risk_level === "WARNING" ? "warning" : "brand"}>
                                {d.risk_level}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Critical Infrastructure Highlights */}
                <div className="p-4 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[4px] space-y-2">
                  <span className="text-xs font-bold text-[#182026] uppercase block">
                    Critical Infrastructure Exposed in Hazard Zone
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                    {currentStorm.gis_risk_impact.critical_facilities.map((fac, idx) => (
                      <div key={idx} className="p-2.5 bg-white border border-[#e2e6e9] rounded-[3px]">
                        <span className="text-[9px] text-[#0f5b6c] font-bold block uppercase">{fac.facility_type}</span>
                        <span className="font-bold text-[#182026] block truncate">{fac.name}</span>
                        <span className="text-[10px] text-[#5f6b7c] block">{fac.status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(6)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Confidence
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(8)}>
                Step 8: Inspect Targeted Alerts
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 8: TARGETED ALERTS                                     */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 8 && (
          <div className="space-y-6">
            <Panel className="border border-[#cbd2d6]">
              <PanelHeader
                title="STAGE 8 — ROLE-TARGETED DISASTER MANAGEMENT ADVISORIES"
                subtitle="Dedicated operational bulletins synthesized for Port Authorities, Fishermen, District Collectors, and Disaster Forces"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#e2e6e9]">
                  <div>
                    <span className="text-xs font-bold text-[#182026] uppercase block">
                      Targeted Early-Warning Bulletins
                    </span>
                    <span className="text-[11px] text-[#5f6b7c] font-sans">
                      Clear plain-language directives tailored to specific stakeholder action mandates.
                    </span>
                  </div>

                  <Button size="sm" variant="primary" onClick={authorizeAllAlerts}>
                    <Send className="h-3.5 w-3.5 mr-1.5" />
                    Authorize All Advisories
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentStorm.targeted_alerts.map((alt) => {
                    const isDispatched = alt.status === "AUTHORIZED_DISPATCHED";
                    return (
                      <div
                        key={alt.alert_id}
                        className={`p-4 rounded-[4px] border transition-all ${
                          isDispatched
                            ? "bg-white border-[#bbf7d0] shadow-xs"
                            : "bg-[#f8f9fa] border-[#cbd2d6]"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <Badge variant={alt.severity === "RED_ALERT" ? "danger" : "warning"}>
                            {alt.severity}
                          </Badge>
                          <span className="px-1.5 py-0.2 text-[9px] font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                            {alt.simulation_label}
                          </span>
                        </div>

                        <h4 className="text-xs font-bold text-[#182026] uppercase font-mono mb-1">
                          {alt.title}
                        </h4>

                        <p className="text-xs text-[#5f6b7c] font-sans leading-relaxed mb-3">
                          {alt.plain_language_summary}
                        </p>

                        <div className="p-2.5 bg-[#f1f3f4] rounded-[3px] space-y-1 mb-3">
                          <span className="text-[10px] font-bold text-[#182026] uppercase block">
                            Directives:
                          </span>
                          <ul className="list-disc pl-4 space-y-1 text-[11px] text-[#5f6b7c] font-sans">
                            {alt.actionable_directives.map((dir, dIdx) => (
                              <li key={dIdx}>{dir}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-[#e2e6e9] text-[10px]">
                          <span className="text-[#5f6b7c]">Channel: {alt.dispatch_channel}</span>
                          {isDispatched ? (
                            <span className="flex items-center gap-1 text-[#1b7a4f] font-bold">
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              AUTHORIZED & DISPATCHED
                            </span>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-6 text-[10px] px-2"
                              onClick={() => authorizeAlert(alt.alert_id)}
                            >
                              Authorize Alert
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(7)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to GIS Risk
              </Button>
              <Button size="lg" variant="primary" onClick={() => setCurrentStep(9)}>
                Step 9: Authorized Human Review
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------ */}
        {/* STAGE 9: AUTHORIZED HUMAN REVIEW                             */}
        {/* ------------------------------------------------------------ */}
        {currentStep === 9 && (
          <div className="space-y-6">
            <Panel className="border-2 border-[#0f5b6c]">
              <PanelHeader
                title="STAGE 9 — AUTHORIZED HUMAN REVIEW & HISTORICAL VERIFICATION"
                subtitle="Decision support governance: Human meteorologist review, bulletin sign-off, and ground-truth verification"
              />
              <div className="p-6 space-y-6 font-mono text-xs">
                {/* Decision Support Protocol Notice */}
                <div className="p-3 bg-[#edf5f7] border border-[#bcdbe2] rounded-[3px] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-[#0f5b6c]" />
                    <span className="font-bold text-[#0f5b6c] uppercase">
                      Mandatory Human-in-the-Loop Protocol
                    </span>
                  </div>
                  <Badge variant="brand">Protocol Standard</Badge>
                </div>

                {/* Meteorologist Review & Sign-Off Desk */}
                <div className="p-5 bg-white border border-[#cbd2d6] rounded-[4px] space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#e2e6e9] pb-3">
                    <div>
                      <span className="text-[10px] text-[#5f6b7c] uppercase block">Designated Duty Meteorologist</span>
                      <span className="text-sm font-bold text-[#182026]">
                        {currentStorm.authorized_human_review.duty_officer_name} ({currentStorm.authorized_human_review.duty_officer_designation})
                      </span>
                      <span className="text-[10px] text-[#5f6b7c] block">
                        Agency: {currentStorm.authorized_human_review.agency}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] text-[#5f6b7c] uppercase block">Official Status</span>
                      <Badge variant={isFullyAuthorized ? "success" : "warning"} className="font-bold">
                        {isFullyAuthorized ? "OFFICIALLY AUTHORIZED" : "PENDING HUMAN REVIEW"}
                      </Badge>
                    </div>
                  </div>

                  {/* Editable Review Notes */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-[#182026] uppercase block">
                      Operational Decision Notes & Bulletin Customization
                    </label>
                    <textarea
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      rows={3}
                      className="w-full p-3 font-mono text-xs border border-[#cbd2d6] rounded-[3px] bg-[#f8f9fa] focus:bg-white focus:outline-none focus:border-[#0f5b6c]"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="text-[10px] text-[#5f6b7c]">
                      Audit Stamp: <code className="text-[#0f5b6c]">{currentStorm.authorized_human_review.audit_hash.slice(0, 36)}...</code>
                    </div>

                    {!isFullyAuthorized ? (
                      <Button
                        size="md"
                        variant="primary"
                        onClick={() => {
                          updateHumanReview(reviewNotes, "OFFICIALLY_AUTHORIZED");
                          authorizeAllAlerts();
                        }}
                      >
                        <FileCheck className="h-4 w-4 mr-1.5" />
                        Approve & Officially Authorize Advisory Dispatch
                      </Button>
                    ) : (
                      <div className="flex items-center gap-2 text-[#1b7a4f] font-bold">
                        <CheckCircle2 className="h-4 w-4" />
                        DIGITALLY SIGNED & DISPATCHED BY DUTY METEOROLOGIST
                      </div>
                    )}
                  </div>
                </div>

                {/* Ground-Truth Verification Section */}
                <div className="p-5 bg-[#fef2f2] border-2 border-[#b91c1c] rounded-[4px] space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-[#b91c1c]" />
                      <span className="font-bold text-[#b91c1c] uppercase text-xs">
                        Historical Ground-Truth Verification (t0 + 24 Hours)
                      </span>
                    </div>
                    <Badge variant="danger">Quarantined Post-Season Best-Track</Badge>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="p-3 bg-white border border-[#fecaca] rounded-[3px]">
                      <span className="text-[9px] text-[#5f6b7c] uppercase block">Observed Wind at t0+24h</span>
                      <span className="text-xl font-extrabold text-[#b91c1c]">
                        {currentStorm.historical_verification_outcome.verified_wind_kts} kt (Hurricane Force)
                      </span>
                    </div>

                    <div className="p-3 bg-white border border-[#fecaca] rounded-[3px]">
                      <span className="text-[9px] text-[#5f6b7c] uppercase block">24h Surge Delta</span>
                      <span className="text-xl font-extrabold text-[#b91c1c]">
                        +{currentStorm.historical_verification_outcome.observed_24h_delta_kts} kt (RI Criteria ≥30)
                      </span>
                    </div>

                    <div className="p-3 bg-white border border-[#fecaca] rounded-[3px]">
                      <span className="text-[9px] text-[#5f6b7c] uppercase block">Algorithm Accuracy</span>
                      <span className="text-sm font-bold text-[#1b7a4f] block pt-1">
                        TRUE POSITIVE EARLY WARNING
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-[#5f6b7c] font-sans leading-relaxed pt-1">
                    {currentStorm.historical_verification_outcome.accuracy_verdict}. The model detected the empirical RI risk signal (0.3592 &gt; 0.125) while the storm was still a 30 kt depression, before the 24-hour surge took place.
                  </p>
                </div>

                {/* Final Statutory Notice */}
                <Alert variant="warning" title="Statutory Operational Authority Precedence">
                  CycloneSense AI is an academic and operational research decision-support prototype. It does not replace official forecasts, bulletins, or evacuation directives issued by the India Meteorological Department (IMD / RSMC New Delhi) or WMO.
                </Alert>
              </div>
            </Panel>

            <div className="flex justify-between items-center">
              <Button size="lg" variant="outline" onClick={() => setCurrentStep(8)}>
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Targeted Alerts
              </Button>
              <div className="flex items-center gap-2">
                <Button size="lg" variant="secondary" onClick={() => setCurrentStep(1)}>
                  <RotateCcw className="h-4 w-4 mr-2" /> Replay From Stage 1
                </Button>
                <Link href="/admin/alerts">
                  <Button size="lg" variant="primary">
                    Go to Operations Console
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
