"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { CycloneMap, MapTrackPoint } from "@/components/ui/CycloneMap";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  Wind,
  Compass,
  MapPin,
  Clock,
  ArrowRight,
  ArrowLeft,
  Navigation,
  Shield,
  TrendingUp,
  AlertTriangle,
  Info,
  CheckCircle2,
  HelpCircle,
} from "lucide-react";

export default function PredictionPage() {
  const { currentStorm, selectStorm, availableStorms } = useStorm();
  const pred = currentStorm.track_landfall_prediction;
  const landfall = pred.landfall_prediction;
  const [selectedHorizon, setSelectedHorizon] = useState<number | null>(null);

  // Filter forecast points to standard milestones: +12h, +24h, +36h, +48h, +72h (plus +6h if available)
  const milestoneHorizons = [6, 12, 24, 36, 48, 72];
  const milestoneCards = pred.forecast_points.filter((p) =>
    milestoneHorizons.includes(p.horizon_hours)
  );

  // Map forecast points for Leaflet
  const forecastMapPoints: MapTrackPoint[] = pred.forecast_points.map((p) => ({
    lat: p.latitude,
    lon: p.longitude,
    time: p.valid_time_utc,
    intensity_kts: p.wind_speed_kts,
    intensity_kmh: p.wind_speed_kmh,
    pressure_mb: p.central_pressure_mb,
    category: p.category,
    agency_grade: "CycloneSense AI Ensemble",
  }));

  // Historical best-track leading to t0
  const pastMapPoints: MapTrackPoint[] = [
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

  const landfallMarkers = [
    {
      lat: 14.1,
      lon: 49.0,
      label: "LANDFALL TARGET (~130h)",
      sublabel: landfall.predicted_landfall_sector,
      type: "landfall" as const,
    },
  ];

  // Wind speed trajectory data points for SVG chart
  const chartPoints = [
    { horizon: 0, kts: currentStorm.observation_data.current_wind_kts, label: "t0" },
    ...pred.forecast_points.map((p) => ({
      horizon: p.horizon_hours,
      kts: p.wind_speed_kts,
      label: `+${p.horizon_hours}h`,
      cat: p.category,
    })),
  ];

  const maxChartKts = 140;
  const chartWidth = 620;
  const chartHeight = 170;
  const padLeft = 40;
  const padRight = 30;
  const padTop = 20;
  const padBottom = 30;

  const innerW = chartWidth - padLeft - padRight;
  const innerH = chartHeight - padTop - padBottom;

  const getX = (horizon: number) => {
    const maxH = 72;
    return padLeft + (Math.min(horizon, maxH) / maxH) * innerW;
  };

  const getY = (kts: number) => {
    return padTop + innerH - (kts / maxChartKts) * innerH;
  };

  // Build SVG path
  const svgPathD = chartPoints.reduce((acc, pt, i) => {
    const x = getX(pt.horizon);
    const y = getY(pt.kts);
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, "");

  // Area fill under line
  const svgAreaD = `${svgPathD} L ${getX(72)} ${padTop + innerH} L ${getX(0)} ${padTop + innerH} Z`;

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/prediction" />

        {/* Stage Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 04 · KINEMATIC TRACK & LANDFALL PREDICTION
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              Forward Trajectory & Landfall Prediction
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5">
              Multi-horizon forecast vectors (+12h to +72h), widening uncertainty cone, intensity trajectory, and explainable landfall window for Cyclone {currentStorm.storm_name}.
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

        {/* Estimated Landfall Highlight Banner */}
        <div className="rounded-[4px] border-2 border-[#b91c1c] bg-white p-5 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-[#fee2e2] text-[#b91c1c] border border-[#fecaca] rounded-[2px] flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  ESTIMATED LANDFALL TARGET
                </span>
                <span className="text-[10px] font-mono text-[#5a6872]">
                  Lead Time: ~{landfall.lead_time_hours}h (&plusmn;{landfall.confidence_window_hours}h Window)
                </span>
              </div>
              <h2 className="text-lg sm:text-xl font-bold font-mono text-[#182026]">
                {landfall.predicted_landfall_sector}
              </h2>
              <p className="text-xs text-[#5a6872] font-mono">
                Projected Arrival Window: <strong className="text-[#182026]">Nov 03, 00:00 - 06:00 UTC</strong> · Intensity: <strong className="text-[#b91c1c]">{landfall.expected_intensity_at_landfall_kts} kt</strong> ({landfall.expected_category_at_landfall})
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right font-mono">
                <span className="text-[10px] text-[#5a6872] uppercase block">Landfall Confidence</span>
                <span className="text-2xl font-bold text-[#0f5b6c]">
                  {landfall.confidence_score_pct || 78}%
                </span>
                <span className="text-[10px] text-[#1b7a4f] block font-semibold">HIGH STEERING AGREEMENT</span>
              </div>
            </div>
          </div>

          {/* 'Why?' Explanation based on movement, observations and historical trajectory */}
          <div className="pt-4 space-y-3 font-mono text-xs">
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase text-[#0f5b6c]">
              <HelpCircle className="h-4 w-4" />
              Why This Landfall Prediction? (Physical Trajectory Explainability)
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5">
                <div className="text-[11px] font-bold text-[#182026] flex items-center gap-1.5">
                  <Navigation className="h-3.5 w-3.5 text-[#0f5b6c]" />
                  1. Movement & Steering Ridge
                </div>
                <p className="text-[11px] text-[#5a6872] leading-relaxed">
                  {landfall.why_explanation?.movement_reason ||
                    "A deep mid-tropospheric subtropical anticyclone over the Arabian Peninsula maintains an unbroken westerly steering flow along 14°N, blocking recurvature northwards toward Gujarat or Oman."}
                </p>
              </div>

              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5">
                <div className="text-[11px] font-bold text-[#182026] flex items-center gap-1.5">
                  <Wind className="h-3.5 w-3.5 text-[#0f5b6c]" />
                  2. Observations & Thermodynamics
                </div>
                <p className="text-[11px] text-[#5a6872] leading-relaxed">
                  {landfall.why_explanation?.observations_reason ||
                    "High ocean heat content (95 kJ/cm²) coupled with anomalous low vertical wind shear (8.2 kt) funnels the system through the thermal channel east of Socotra toward Yemen."}
                </p>
              </div>

              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5">
                <div className="text-[11px] font-bold text-[#182026] flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-[#0f5b6c]" />
                  3. Historical Trajectory Analogue
                </div>
                <p className="text-[11px] text-[#5a6872] leading-relaxed">
                  {landfall.why_explanation?.historical_analogue_reason ||
                    "Kinematic and climatological match with historical October-November westward Arabian Sea super-storms (Chapala 2015, Megh 2015) constrained into the Gulf of Aden corridor."}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Forecast Milestones Cards: +12h, +24h, +36h, +48h, +72h */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#182026] font-mono">
                Multi-Horizon Forecast Milestones (+12h, +24h, +36h, +48h, +72h)
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <span className="text-[11px] font-mono text-[#5a6872]">
              Select card to highlight coordinate vector
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {milestoneCards.map((fc) => {
              const isSelected = selectedHorizon === fc.horizon_hours;
              const isPeak = fc.wind_speed_kts >= 110;

              return (
                <div
                  key={fc.horizon_hours}
                  onClick={() => setSelectedHorizon(isSelected ? null : fc.horizon_hours)}
                  className={`p-3.5 rounded-[4px] border font-mono transition-all cursor-pointer ${
                    isSelected
                      ? "bg-[#edf5f7] border-[#0f5b6c] shadow-sm ring-1 ring-[#0f5b6c]"
                      : isPeak
                      ? "bg-[#fef8ee] border-[#fde68a] hover:border-[#b45309]"
                      : "bg-white border-[#cbd2d6] hover:border-[#0f5b6c] shadow-xs"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-0.5 text-xs font-bold bg-[#0f5b6c] text-white rounded-[2px]">
                      +{fc.horizon_hours}h
                    </span>
                    <span className="text-[10px] text-[#5a6872]">
                      {fc.valid_time_utc.replace("T", " ").slice(5, 16)} UTC
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-[10px] text-[#5a6872] uppercase block">Expected Position</span>
                      <span className="font-bold text-[#182026]">
                        {fc.latitude.toFixed(1)}°N, {fc.longitude.toFixed(1)}°E
                      </span>
                      <span className="text-[10px] text-[#5a6872] block">
                        {fc.forward_speed_kts} kt @ {fc.bearing_deg}°
                      </span>
                    </div>

                    <div>
                      <span className="text-[10px] text-[#5a6872] uppercase block">Wind / Intensity</span>
                      <div className="flex items-baseline gap-1">
                        <span className={`text-base font-bold ${isPeak ? "text-[#b91c1c]" : "text-[#0f5b6c]"}`}>
                          {fc.wind_speed_kts} kt
                        </span>
                        <span className="text-[10px] text-[#5a6872]">
                          ({fc.wind_speed_kmh} km/h)
                        </span>
                      </div>
                      <span className="text-[10px] text-[#5a6872] block truncate">
                        {fc.category}
                      </span>
                    </div>

                    <div className="pt-2 border-t border-[#e2e6e9]">
                      <div className="flex items-center justify-between text-[10px] mb-1">
                        <span className="text-[#5a6872] uppercase">Confidence</span>
                        <span className="font-bold text-[#182026]">
                          {fc.confidence_pct || 80}%
                        </span>
                      </div>
                      <div className="w-full bg-[#e2e6e9] h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-[#0f5b6c] h-full rounded-full"
                          style={{ width: `${fc.confidence_pct || 80}%` }}
                        />
                      </div>
                      <span className="text-[9px] text-[#5a6872] block mt-1">
                        Cone: &plusmn;{fc.cone_radius_km} km
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Map Visualization & Wind Speed Chart Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Map Column (7 Cols) */}
          <div className="lg:col-span-7 rounded-[4px] border border-[#cbd2d6] bg-white overflow-hidden shadow-xs">
            <div className="px-4 py-2.5 bg-[#f8f9fa] border-b border-[#cbd2d6] flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#182026] font-mono flex items-center gap-1.5">
                <Compass className="h-3.5 w-3.5 text-[#0f5b6c]" />
                Forecast Path & Widening Uncertainty Cone
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>

            <div className="h-[440px] w-full">
              <CycloneMap
                center={[14.0, 59.0]}
                zoom={5}
                tracks={pastMapPoints}
                forecastPath={forecastMapPoints}
                markers={landfallMarkers}
                title={`Cyclone ${currentStorm.storm_name} Forecast Envelope`}
                subtitle="Solid track: Past fix | Dashed cyan: AI forecast | Translucent polygon: Widening cone"
                height="440px"
                windLayers={true}
                riskLayers={true}
              />
            </div>

            <div className="p-3 bg-[#f8f9fa] border-t border-[#cbd2d6] text-[11px] font-mono text-[#5a6872] flex flex-wrap items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-[#f59e0b] inline-block" /> Solid: Best Track Past
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 border-t-2 border-dashed border-[#38bdf8] inline-block" /> Dashed Cyan: AI Forecast Path
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-2 bg-[#38bdf8]/30 border border-[#0284c7] inline-block rounded-xs" /> Uncertainty Cone Envelope
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#b91c1c] border border-white inline-block" /> Landfall Target Pin
              </span>
            </div>
          </div>

          {/* Wind Speed Chart & Technical Trajectory Column (5 Cols) */}
          <div className="lg:col-span-5 space-y-4">
            {/* Simple Wind Speed Chart */}
            <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-4 shadow-xs font-mono">
              <div className="flex items-center justify-between pb-2 border-b border-[#e2e6e9] mb-3">
                <div className="flex items-center gap-1.5">
                  <TrendingUp className="h-4 w-4 text-[#0f5b6c]" />
                  <span className="text-xs font-bold uppercase text-[#182026]">
                    Projected Wind Speed Trajectory
                  </span>
                </div>
                <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                  DEMO / SIMULATION
                </span>
              </div>

              {/* Responsive SVG Chart */}
              <div className="w-full overflow-hidden">
                <svg
                  viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                  className="w-full h-auto text-xs"
                >
                  {/* Grid Lines */}
                  {[34, 64, 100].map((thr) => {
                    const y = getY(thr);
                    return (
                      <g key={thr}>
                        <line
                          x1={padLeft}
                          y1={y}
                          x2={chartWidth - padRight}
                          y2={y}
                          stroke="#e2e6e9"
                          strokeDasharray="4 4"
                          strokeWidth="1"
                        />
                        <text
                          x={padLeft - 6}
                          y={y + 3}
                          textAnchor="end"
                          fill="#94a3b8"
                          fontSize="9"
                          fontFamily="monospace"
                        >
                          {thr}kt
                        </text>
                      </g>
                    );
                  })}

                  {/* Rapid Intensification Shading Box (+12h to +36h) */}
                  <rect
                    x={getX(12)}
                    y={padTop}
                    width={getX(36) - getX(12)}
                    height={innerH}
                    fill="#fee2e2"
                    fillOpacity="0.4"
                  />
                  <text
                    x={(getX(12) + getX(36)) / 2}
                    y={padTop + 14}
                    textAnchor="middle"
                    fill="#b91c1c"
                    fontSize="9"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    RAPID INTENSIFICATION (+45 kt surge)
                  </text>

                  {/* Area fill */}
                  <path d={svgAreaD} fill="#0f5b6c" fillOpacity="0.12" />

                  {/* Curve Path */}
                  <path
                    d={svgPathD}
                    fill="none"
                    stroke="#0f5b6c"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />

                  {/* Data Dots & Labels */}
                  {chartPoints.map((pt, idx) => {
                    const x = getX(pt.horizon);
                    const y = getY(pt.kts);
                    return (
                      <g key={idx}>
                        <circle
                          cx={x}
                          cy={y}
                          r="4"
                          fill="#0f5b6c"
                          stroke="#ffffff"
                          strokeWidth="2"
                        />
                        <text
                          x={x}
                          y={y - 8}
                          textAnchor="middle"
                          fill="#182026"
                          fontSize="10"
                          fontWeight="bold"
                          fontFamily="monospace"
                        >
                          {pt.kts}
                        </text>
                        {/* X-axis label */}
                        <text
                          x={x}
                          y={padTop + innerH + 16}
                          textAnchor="middle"
                          fill="#5a6872"
                          fontSize="9"
                          fontFamily="monospace"
                        >
                          {pt.label}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>

              <div className="flex items-center justify-between text-[10px] text-[#5a6872] pt-2 border-t border-[#e2e6e9] mt-2">
                <span>Thresholds: 34kt (Gale) · 64kt (Cat 1) · 100kt (Cat 3)</span>
                <span className="text-[#b91c1c] font-bold">Peak: 115 kt (+48h)</span>
              </div>
            </div>

            {/* Timestep Table Preview */}
            <div className="rounded-[4px] border border-[#cbd2d6] bg-white overflow-hidden shadow-xs">
              <div className="px-3.5 py-2 bg-[#f8f9fa] border-b border-[#cbd2d6] flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-[#182026] font-mono">
                  Vector Coordinate Matrix
                </span>
                <span className="text-[10px] font-mono text-[#5a6872]">WMO Standard</span>
              </div>

              <div className="max-h-[175px] overflow-y-auto">
                <table className="w-full text-left text-[11px] font-mono border-collapse">
                  <thead>
                    <tr className="bg-[#f1f3f4] text-[#5a6872] border-b border-[#e2e6e9]">
                      <th className="py-1 px-2.5 font-semibold">T+</th>
                      <th className="py-1 px-2.5 font-semibold">Lat, Lon</th>
                      <th className="py-1 px-2.5 font-semibold">Vmax</th>
                      <th className="py-1 px-2.5 font-semibold">Category</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#e2e6e9]">
                    {pred.forecast_points.map((fp, idx) => (
                      <tr key={idx} className="hover:bg-[#f8f9fa]">
                        <td className="py-1 px-2.5 font-bold text-[#0f5b6c]">+{fp.horizon_hours}h</td>
                        <td className="py-1 px-2.5 text-[#5a6872]">{fp.latitude.toFixed(1)}°N, {fp.longitude.toFixed(1)}°E</td>
                        <td className="py-1 px-2.5 font-bold text-[#182026]">{fp.wind_speed_kts} kt</td>
                        <td className="py-1 px-2.5 text-[#0f5b6c] truncate max-w-[130px]">{fp.category}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/analysis">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: AI Analysis
            </Button>
          </Link>
          <Link href="/risk">
            <Button variant="primary" size="sm">
              Next Stage: Risk & Impact
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
