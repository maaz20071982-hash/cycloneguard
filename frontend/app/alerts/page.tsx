"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  AlertTriangle,
  Ship,
  Anchor,
  Radio,
  Building2,
  CheckCircle2,
  Send,
  ArrowRight,
  ArrowLeft,
  Clock,
  Shield,
  Users,
  Compass,
  MapPin,
  Home,
  Check,
  RotateCcw,
  Sparkles,
  Info,
  SlidersHorizontal,
} from "lucide-react";

export default function AlertsPage() {
  const { currentStorm, selectStorm, availableStorms, authorizeAlert, authorizeAllAlerts } = useStorm();
  const alerts = currentStorm.targeted_alerts;
  const risk = currentStorm.gis_risk_impact;

  // Active Audience Tab: "public" | "fishermen" | "officials"
  const [activeAudience, setActiveAudience] = useState<"public" | "fishermen" | "officials">("public");

  // Public Location Selector
  const [selectedPublicLocation, setSelectedPublicLocation] = useState<number>(0);
  const activeLocation = risk.exposed_districts[selectedPublicLocation] || risk.exposed_districts[0];

  // Generate Targeted Alert State
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generationNotice, setGenerationNotice] = useState<string | null>(null);

  const handleGenerateAlert = () => {
    setIsGenerating(true);
    setGenerationNotice("Ingesting GIS risk state & demographic exposure vectors...");
    setTimeout(() => {
      setGenerationNotice("Synthesizing tailored multi-stakeholder operational directives...");
    }, 600);
    setTimeout(() => {
      setIsGenerating(false);
      setGenerationNotice("Targeted alerts successfully generated for Public, Fishermen, and Disaster Officials!");
      setTimeout(() => setGenerationNotice(null), 4000);
    }, 1200);
  };

  // Demo Shelters for Public View
  const DEMO_SHELTERS = [
    {
      name: "Hadramaut Designated Secondary School #4",
      distance: "0.8 km inland",
      elevation: "Elevated Ridge (+24m MSL)",
      capacity: 1200,
      facilities: "Potable Water Tank, Backup Generator, First Aid Staging",
      status: "OPEN & MANNED",
    },
    {
      name: "Ibn Sina Hospital Civil Defense Relief Compound",
      distance: "1.5 km inland",
      elevation: "High Ground (+35m MSL)",
      capacity: 850,
      facilities: "Emergency Surgical Ward, Medical Tents, Satellite Comms",
      status: "OPEN & MANNED",
    },
    {
      name: "Al Mukalla Municipal Sports Complex Shelter Hall",
      distance: "2.1 km inland",
      elevation: "Inland Plateau (+40m MSL)",
      capacity: 2500,
      facilities: "Food Distribution Hub, Communal Kitchen, Armed Guard",
      status: "OPEN & MANNED",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/alerts" />

        {/* Stage Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 06 · TARGETED STAKEHOLDER DIRECTIVES
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              Role-Targeted Disaster Alert Center
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5">
              Multi-audience plain-language operational directives customized for Public Residents, Marine Fishermen, and Administrative Officials for Cyclone {currentStorm.storm_name}.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            {/* Generate Targeted Alert Button */}
            <Button
              size="sm"
              variant="primary"
              onClick={handleGenerateAlert}
              disabled={isGenerating}
              className="bg-[#0f5b6c] hover:bg-[#0c4a57] text-white"
            >
              {isGenerating ? (
                <>
                  <RotateCcw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Generating Directives...
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                  GENERATE TARGETED ALERT
                </>
              )}
            </Button>

            <Button
              size="sm"
              variant="outline"
              onClick={authorizeAllAlerts}
              className="text-[#0f5b6c] border-[#0f5b6c]"
            >
              <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
              Authorize All
            </Button>
          </div>
        </div>

        {/* Generation Feedback Notice */}
        {generationNotice && (
          <div className="p-3 bg-[#edf5f7] border border-[#0f5b6c] text-[#0f5b6c] rounded-[4px] font-mono text-xs flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-[#0f5b6c]" />
            <span>{generationNotice}</span>
          </div>
        )}

        {/* Audience Tab Navigation: Public / Fishermen / Officials */}
        <div className="flex items-center gap-2 border-b border-[#cbd2d6] pb-1 font-mono text-xs">
          <button
            onClick={() => setActiveAudience("public")}
            className={`px-4 py-2 font-bold uppercase transition-all flex items-center gap-2 border-b-2 cursor-pointer ${
              activeAudience === "public"
                ? "border-[#0f5b6c] text-[#0f5b6c] bg-white rounded-t-[4px]"
                : "border-transparent text-[#5a6872] hover:text-[#182026]"
            }`}
          >
            <Users className="h-4 w-4" />
            1. Public View (Citizens)
          </button>

          <button
            onClick={() => setActiveAudience("fishermen")}
            className={`px-4 py-2 font-bold uppercase transition-all flex items-center gap-2 border-b-2 cursor-pointer ${
              activeAudience === "fishermen"
                ? "border-[#0f5b6c] text-[#0f5b6c] bg-white rounded-t-[4px]"
                : "border-transparent text-[#5a6872] hover:text-[#182026]"
            }`}
          >
            <Anchor className="h-4 w-4" />
            2. Fisherman Mode (Marine)
          </button>

          <button
            onClick={() => setActiveAudience("officials")}
            className={`px-4 py-2 font-bold uppercase transition-all flex items-center gap-2 border-b-2 cursor-pointer ${
              activeAudience === "officials"
                ? "border-[#0f5b6c] text-[#0f5b6c] bg-white rounded-t-[4px]"
                : "border-transparent text-[#5a6872] hover:text-[#182026]"
            }`}
          >
            <Shield className="h-4 w-4" />
            3. Disaster Officials (Authorities)
          </button>
        </div>

        {/* ========================================================================= */}
        {/* 1. PUBLIC VIEW: "Am I in danger?" / Large Risk / Plain Reasons / Shelters */}
        {/* ========================================================================= */}
        <div className={activeAudience === "public" ? "space-y-6 font-mono" : "hidden"}>
            {/* Location Selector Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-white rounded-[4px] border border-[#cbd2d6] shadow-xs gap-3">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-[#0f5b6c]" />
                <span className="text-xs font-bold uppercase text-[#182026]">
                  Select Your Coastal District / Town:
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs">
                {risk.exposed_districts.map((d, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedPublicLocation(idx)}
                    className={`px-3 py-1.5 rounded-[3px] border transition-all cursor-pointer ${
                      selectedPublicLocation === idx
                        ? "bg-[#0f5b6c] text-white border-[#0f5b6c] font-bold"
                        : "bg-[#f8f9fa] text-[#5a6872] border-[#cbd2d6] hover:border-[#0f5b6c]"
                    }`}
                  >
                    {d.district_name.split(" ")[0]} ({d.risk_color})
                  </button>
                ))}
              </div>
            </div>

            {/* "Am I in danger?" Result Card */}
            <div
              className={`p-6 rounded-[4px] border-2 bg-white shadow-xs space-y-4 ${
                activeLocation.risk_color === "Red"
                  ? "border-[#b91c1c]"
                  : activeLocation.risk_color === "Orange"
                  ? "border-[#f97316]"
                  : activeLocation.risk_color === "Yellow"
                  ? "border-[#eab308]"
                  : "border-[#22c55e]"
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#e2e6e9] pb-4">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#5a6872] uppercase block">
                    Citizen Safety Inquiry: &ldquo;Am I in danger?&rdquo; · {activeLocation.district_name}
                  </span>
                  <div className="text-xl sm:text-2xl font-bold font-mono tracking-tight">
                    {activeLocation.risk_color === "Red" && (
                      <span className="text-[#b91c1c] flex items-center gap-2">
                        🔴 YES — IMMINENT SEVERE DANGER: DIRECT EYEWALL & SURGE THREAT
                      </span>
                    )}
                    {activeLocation.risk_color === "Orange" && (
                      <span className="text-[#c2410c] flex items-center gap-2">
                        🟠 YES — HIGH DANGER: DAMAGING WINDS & SEAWATER FLOODING
                      </span>
                    )}
                    {activeLocation.risk_color === "Yellow" && (
                      <span className="text-[#a16207] flex items-center gap-2">
                        🟡 CAUTION — MODERATE THREAT: HEAVY SWELL & GALE GUSTS
                      </span>
                    )}
                    {activeLocation.risk_color === "Green" && (
                      <span className="text-[#15803d] flex items-center gap-2">
                        🟢 LOW DANGER — MINIMAL STRUCTURAL THREAT (ADVISORY ONLY)
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-[#5a6872] uppercase block">Assigned Risk Tier</span>
                  <span
                    className={`inline-block px-3 py-1 text-sm font-bold rounded-[3px] border ${
                      activeLocation.risk_color === "Red"
                        ? "bg-[#fee2e2] text-[#b91c1c] border-[#fecaca]"
                        : activeLocation.risk_color === "Orange"
                        ? "bg-[#ffedd5] text-[#c2410c] border-[#fed7aa]"
                        : activeLocation.risk_color === "Yellow"
                        ? "bg-[#fef9c3] text-[#a16207] border-[#fef08a]"
                        : "bg-[#dcfce7] text-[#15803d] border-[#bbf7d0]"
                    }`}
                  >
                    {activeLocation.risk_color.toUpperCase()} ZONE · {activeLocation.risk_level}
                  </span>
                </div>
              </div>

              {/* One Plain-Language Explanation */}
              <div className="p-4 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5 text-xs">
                <span className="text-[10px] font-bold text-[#0f5b6c] uppercase block">
                  Plain-Language Public Summary:
                </span>
                <p className="text-sm font-sans text-[#182026] leading-relaxed">
                  Extremely Severe Cyclone {currentStorm.storm_name} is moving directly along the coastal corridor, located {activeLocation.distance_from_eye_km} km from your area. Expect {activeLocation.peak_wind_gust_kmh} km/h violent wind gusts, destructive seawater surges up to {activeLocation.surge_height_meters} meters, and flash-flooding downpours. Low-lying areas and beachfront properties will be submerged.
                </p>
              </div>

              {/* 3 Clear Action Steps */}
              <div className="space-y-2 text-xs">
                <span className="text-[11px] font-bold text-[#182026] uppercase flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-[#b91c1c]" />
                  3 Immediate Safety Actions You Must Take Now:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3 bg-white rounded-[3px] border border-[#cbd2d6] space-y-1">
                    <span className="px-2 py-0.5 bg-[#b91c1c] text-white text-[10px] font-bold rounded-[2px]">
                      STEP 1: EVACUATE
                    </span>
                    <p className="text-[11px] text-[#182026] font-sans leading-tight mt-1">
                      If living within 1.5 km of shoreline or in non-masonry housing, relocate immediately to designated concrete multi-story shelters before gale-force winds begin.
                    </p>
                  </div>

                  <div className="p-3 bg-white rounded-[3px] border border-[#cbd2d6] space-y-1">
                    <span className="px-2 py-0.5 bg-[#0f5b6c] text-white text-[10px] font-bold rounded-[2px]">
                      STEP 2: STOCK UP
                    </span>
                    <p className="text-[11px] text-[#182026] font-sans leading-tight mt-1">
                      Secure loose roofing sheets. Store at least 3 days of clean potable water (5L/person/day), dry ration foods, torches, powerbanks, and critical prescription medicines.
                    </p>
                  </div>

                  <div className="p-3 bg-white rounded-[3px] border border-[#cbd2d6] space-y-1">
                    <span className="px-2 py-0.5 bg-[#0f5b6c] text-white text-[10px] font-bold rounded-[2px]">
                      STEP 3: STAY INDOORS
                    </span>
                    <p className="text-[11px] text-[#182026] font-sans leading-tight mt-1">
                      Disconnect main electrical switches during peak surge. Do not go near harbor walls or beaches to watch storm waves. Tune exclusively to official civil defense radio.
                    </p>
                  </div>
                </div>
              </div>

              {/* Nearest Shelters Card */}
              <div className="pt-3 border-t border-[#e2e6e9] space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#0f5b6c] uppercase flex items-center gap-1.5">
                    <Home className="h-4 w-4" />
                    Nearest Verified Evacuation Shelters (Demo Data)
                  </span>
                  <span className="px-1.5 py-0.2 text-[9px] font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
                    DEMO / SIMULATION
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  {DEMO_SHELTERS.map((s, sIdx) => (
                    <div key={sIdx} className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#182026] text-[11px] truncate max-w-[170px]">
                          {s.name}
                        </span>
                        <span className="text-[9px] px-1 py-0.2 bg-[#dcfce7] text-[#15803d] border border-[#bbf7d0] rounded-[2px] font-bold">
                          {s.status}
                        </span>
                      </div>
                      <div className="text-[10px] text-[#5a6872]">
                        Distance: <strong className="text-[#182026]">{s.distance}</strong> · {s.elevation}
                      </div>
                      <div className="text-[10px] text-[#5a6872]">
                        Capacity: <strong className="text-[#0f5b6c]">{s.capacity.toLocaleString()} persons</strong>
                      </div>
                      <div className="text-[9px] text-[#5a6872] pt-1 border-t border-[#e2e6e9] truncate">
                        {s.facilities}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

        {/* ========================================================================= */}
        {/* 2. FISHERMAN MODE: Marine Risk / Distance / Unsafe Zones / NavIC Preview */}
        {/* ========================================================================= */}
        <div className={activeAudience === "fishermen" ? "space-y-6 font-mono" : "hidden"}>
            {/* Marine Danger Callout Banner */}
            <div className="p-5 rounded-[4px] border-2 border-[#b91c1c] bg-[#fee2e2]/30 space-y-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-full bg-[#b91c1c] text-white">
                    <AlertTriangle className="h-6 w-6" />
                  </div>
                  <div>
                    <span className="text-[10px] text-[#b91c1c] font-bold uppercase tracking-widest block">
                      MARITIME WARNING BULLETIN · ALL CRAFTS MUST ACT
                    </span>
                    <h2 className="text-lg sm:text-xl font-bold text-[#182026]">
                      CRITICAL MARITIME DANGER · PHENOMENAL SEAS (WAVE HEIGHT 8–10M)
                    </h2>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold text-[#b91c1c] uppercase block">
                    TOTAL SEA SUSPENSION
                  </span>
                  <span className="text-[10px] text-[#5a6872]">Zero Craft Sailing Order</span>
                </div>
              </div>

              {/* Crucial Immediate Directive */}
              <div className="p-3 bg-white rounded-[3px] border border-[#fca5a5] text-xs font-bold text-[#b91c1c] flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-[#b91c1c]" />
                <span>
                  &ldquo;RETURN TO SHORE IMMEDIATELY / DO NOT VENTURE INTO DEEP SEAS — Follow official maritime and Coast Guard emergency guidance.&rdquo;
                </span>
              </div>
            </div>

            {/* Maritime Metrics Grid: Cyclone Distance / Direction / Dangerous Period */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-white rounded-[4px] border border-[#cbd2d6] shadow-xs space-y-1">
                <span className="text-[10px] text-[#5a6872] uppercase block">Cyclone Direction & Distance</span>
                <span className="text-base font-bold text-[#182026] block">
                  ~820 km ESE of Al Mukalla
                </span>
                <span className="text-[11px] text-[#0f5b6c] block">
                  Fix: 13.1°N, 64.6°E · Heading West (268°) @ 7.5 kt
                </span>
              </div>

              <div className="p-4 bg-white rounded-[4px] border border-[#cbd2d6] shadow-xs space-y-1">
                <span className="text-[10px] text-[#5a6872] uppercase block">Dangerous Maritime Period</span>
                <span className="text-base font-bold text-[#b91c1c] block">
                  Next 120 Hours Continuous
                </span>
                <span className="text-[11px] text-[#5a6872] block">
                  Oct 30, 00:00 UTC through Nov 04, 12:00 UTC
                </span>
              </div>

              <div className="p-4 bg-white rounded-[4px] border border-[#cbd2d6] shadow-xs space-y-1">
                <span className="text-[10px] text-[#5a6872] uppercase block">Expected Offshore Sea State</span>
                <span className="text-base font-bold text-[#b45309] block">
                  Phenomenal to High (Code 9)
                </span>
                <span className="text-[11px] text-[#5a6872] block">
                  Sustained gusts up to 145 km/h over open water
                </span>
              </div>
            </div>

            {/* Safe / Unsafe Sea Zones Table */}
            <div className="p-4 bg-white rounded-[4px] border border-[#cbd2d6] shadow-xs space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-[#e2e6e9]">
                <span className="font-bold text-[#182026] uppercase flex items-center gap-1.5">
                  <Compass className="h-4 w-4 text-[#0f5b6c]" />
                  Operational Sea Zones Classification
                </span>
                <span className="text-[10px] text-[#5a6872]">Indian Ocean Coast Guard Grid</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 bg-[#fee2e2]/40 rounded-[3px] border border-[#fca5a5] space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-[#b91c1c]">
                    <span>❌ UNSAFE ZONE (PROHIBITED)</span>
                  </div>
                  <ul className="text-[11px] text-[#334155] space-y-1 pt-1 font-sans">
                    <li>• Central Arabian Sea (West of 66°E)</li>
                    <li>• Gulf of Aden Entrance (11°N to 15°N)</li>
                    <li>• Waters surrounding Socotra Archipelago</li>
                    <li>• Hadramaut Coastal Continental Shelf</li>
                  </ul>
                </div>

                <div className="p-3 bg-[#fef9c3]/50 rounded-[3px] border border-[#fde047] space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-[#a16207]">
                    <span>⚠️ MARGINAL / ADVISORY ZONE</span>
                  </div>
                  <ul className="text-[11px] text-[#334155] space-y-1 pt-1 font-sans">
                    <li>• Northern Oman Coast (Dhofar to Ras Al Hadd)</li>
                    <li>• Extreme Southern Arabian Sea (South of 9°N)</li>
                    <li>• Heavy swell warning; proceed with high caution</li>
                    <li>• Keep continuous VHF Channel 16 watch</li>
                  </ul>
                </div>

                <div className="p-3 bg-[#dcfce7]/40 rounded-[3px] border border-[#86efac] space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-[#15803d]">
                    <span>✅ SAFE ANCHORAGE LOCATIONS</span>
                  </div>
                  <ul className="text-[11px] text-[#334155] space-y-1 pt-1 font-sans">
                    <li>• Designated inner tidal creeks and lagoons</li>
                    <li>• High-elevation slips behind breakwaters</li>
                    <li>• Secure boats with cross-spring heavy moorings</li>
                    <li>• Remove outboard engines to high ground</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* NavIC-Style Marine Satellite Terminal Display Preview */}
            <div className="rounded-[4px] border-2 border-[#1e293b] bg-[#0b1520] text-[#f8fafc] p-4 shadow-sm space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-slate-800 gap-2">
                <div className="flex items-center gap-2">
                  <Radio className="h-4 w-4 text-emerald-400 animate-pulse" />
                  <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">
                    NavIC / SATELLITE RECEIVER DONGLE DISPLAY PREVIEW
                  </span>
                </div>
                <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800 rounded-[2px]">
                  SIMULATED FORMAT · NOT CONNECTED TO LIVE SATELLITE
                </span>
              </div>

              {/* Monospace Marine LCD Receiver Preview Box */}
              <div className="p-3.5 bg-black/60 rounded-[3px] border border-emerald-500/40 text-emerald-300 font-mono text-xs leading-relaxed space-y-2">
                <div className="flex justify-between text-[10px] text-emerald-500 border-b border-emerald-900/50 pb-1">
                  <span>FREQ: 1176.45 MHz (L5 NavIC)</span>
                  <span>SIGNAL: OPTIMAL (4/4 SATELLITES)</span>
                  <span>TIME: 2015-10-28 18:00 UTC</span>
                </div>
                <p className="tracking-wide">
                  [NAVIC-WARN/MET-01] 281800Z ARABIAN SEA CYCLONE CHAPALA GALE/HURRICANE FORCE WINDS 65-115KT SURGE 3.2M. ALL FISHING CRAFTS WITHIN 10N-16N / 50E-66E DIRECTED TO SEEK IMMEDIATE HARBOR. SUSPEND ALL SAILINGS.
                </p>
                <div className="text-[10px] text-emerald-600 pt-1">
                  CHECKSUM: 0x8F4A2C · STATUS: BROADCAST VERIFIED · SATELLITE PRN-01
                </div>
              </div>

              <p className="text-[10px] text-slate-400 font-sans">
                *Note: This terminal simulates the low-bandwidth broadcast packet received by coastal fishermen via battery-backed Bluetooth NavIC transponders distributed by fisheries departments.
              </p>
            </div>
          </div>

        {/* ========================================================================= */}
        {/* 3. OFFICIALS VIEW: Ports / District Collectors / Police & NDRF Directives */}
        {/* ========================================================================= */}
        <div className={activeAudience === "officials" ? "space-y-4 font-mono text-xs" : "hidden"}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {alerts.map((alt) => {
                const isAuthorized = alt.status === "AUTHORIZED_DISPATCHED";
                const isRedAlert = alt.severity === "RED_ALERT";

                let recipientIcon = <Ship className="h-4 w-4" />;
                if (alt.recipient_group === "FISHERMEN") recipientIcon = <Anchor className="h-4 w-4" />;
                if (alt.recipient_group === "DISTRICT_COLLECTOR") recipientIcon = <Building2 className="h-4 w-4" />;
                if (alt.recipient_group === "STATE_DISASTER_MANAGEMENT") recipientIcon = <Radio className="h-4 w-4" />;

                return (
                  <div
                    key={alt.alert_id}
                    className={`p-5 rounded-[4px] border bg-white shadow-xs flex flex-col justify-between space-y-4 ${
                      isRedAlert ? "border-[#fca5a5]" : "border-[#cbd2d6]"
                    }`}
                  >
                    <div className="space-y-3">
                      {/* Top Role & Severity Bar */}
                      <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                        <span className="font-bold text-[#0f5b6c] uppercase flex items-center gap-1.5 text-[11px]">
                          {recipientIcon}
                          {alt.recipient_group.replace(/_/g, " ")}
                        </span>
                        <Badge variant={isRedAlert ? "danger" : "warning"}>
                          {alt.severity.replace(/_/g, " ")}
                        </Badge>
                      </div>

                      <div>
                        <h3 className="font-bold text-sm text-[#182026] leading-snug">
                          {alt.title}
                        </h3>
                        <p className="text-[11px] text-[#5a6872] font-sans mt-1 leading-relaxed">
                          {alt.plain_language_summary}
                        </p>
                      </div>

                      {/* Actionable Directives */}
                      <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1.5">
                        <span className="text-[10px] font-bold text-[#182026] uppercase block">
                          Mandatory Operational Directives:
                        </span>
                        <ul className="space-y-1 text-[11px] text-[#334155] font-sans">
                          {alt.actionable_directives.map((act, aIdx) => (
                            <li key={aIdx} className="flex items-start gap-1.5">
                              <span className="text-[#0f5b6c] font-bold shrink-0">&rsaquo;</span>
                              <span>{act}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Footer Status & Dispatch Action */}
                    <div className="pt-3 border-t border-[#e2e6e9] flex items-center justify-between">
                      <div className="text-[10px] text-[#5a6872]">
                        <div>Channel: {alt.dispatch_channel.split("/")[0]}</div>
                        <div>Lead Time: {alt.lead_time_hours}h</div>
                      </div>

                      <div>
                        {isAuthorized ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold bg-[#ecfdf5] text-[#059669] border border-[#a7f3d0] rounded-[3px]">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            DISPATCHED
                          </span>
                        ) : (
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => authorizeAlert(alt.alert_id)}
                            className="text-xs"
                          >
                            <Send className="h-3 w-3 mr-1" />
                            Authorize Alert
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/risk">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: Risk & Impact
            </Button>
          </Link>
          <Link href="/review">
            <Button variant="primary" size="sm">
              Next Stage: Authority Review
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
