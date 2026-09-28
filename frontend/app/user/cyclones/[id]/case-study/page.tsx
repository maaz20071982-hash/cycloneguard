"use client";

import React, { use, useEffect, useState } from "react";
import Link from "next/link";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { CycloneMap, MapTrackPoint } from "@/components/ui/CycloneMap";
import { CycloneTimeline } from "@/components/ui/CycloneTimeline";
import { RIRiskTimeline } from "@/components/ui/RIRiskTimeline";
import { TemporalEvolutionPanel } from "@/components/ui/TemporalEvolutionPanel";
import { EvidencePanel } from "@/components/ui/EvidencePanel";
import { ModelFeatureAttributionPanel } from "@/components/ui/ModelFeatureAttributionPanel";
import { PredictionOutcomeCard } from "@/components/ui/PredictionOutcomeCard";
import { RIRiskPanel } from "@/components/ui/RIRiskPanel";
import { getCycloneCaseStudy, CaseStudyData } from "@/lib/api/cyclones";
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  Clock,
  Compass,
  Database,
  ExternalLink,
  Layers,
  RefreshCw,
  ShieldAlert,
  Wind,
  Cpu,
} from "lucide-react";

export default function CycloneCaseStudyPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const cycloneId = resolvedParams.id;

  const [caseStudy, setCaseStudy] = useState<CaseStudyData | null>(null);
  const [selectedObsTime, setSelectedObsTime] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadCaseStudyData = async (obsTime?: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await getCycloneCaseStudy(cycloneId, obsTime);
      setCaseStudy(data);
      if (!obsTime) {
        setSelectedObsTime(data.selected_observation_time_utc);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load historical case study.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCaseStudyData();
  }, [cycloneId]);

  const handleSelectObservation = (obsTime: string) => {
    setSelectedObsTime(obsTime);
    loadCaseStudyData(obsTime);
  };

  if (isLoading && !caseStudy) {
    return (
      <PortalLayout type="user">
        <div className="p-12 text-center space-y-3 font-mono text-xs text-[#5f6b7c]">
          <RefreshCw className="h-6 w-6 animate-spin mx-auto text-[#0f5b6c]" />
          <p>Loading historical cyclone case study and observational evidence...</p>
        </div>
      </PortalLayout>
    );
  }

  if (errorMsg && !caseStudy) {
    return (
      <PortalLayout type="user">
        <div className="space-y-4">
          <Link href={`/user/cyclones/${cycloneId}`}>
            <Button size="sm" variant="outline">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Back to Cyclone View
            </Button>
          </Link>
          <Alert variant="danger" title="Case Study Unavailable">
            <p className="text-xs">{errorMsg}</p>
          </Alert>
        </div>
      </PortalLayout>
    );
  }

  if (!caseStudy) return null;

  const { what_the_model_saw, historical_outcome } = caseStudy;
  const modelScore = what_the_model_saw.model_score;
  const isElevated = modelScore.ri_flag;

  // Derive imagery URL for authentic satellite patch
  const normTime = what_the_model_saw.observation_time_utc.replace(/-/g, "").replace(/:/g, "").slice(0, 16);
  const patchUrl = `/api/v1/cyclones/${caseStudy.storm_id}/observations/${normTime}/patch/IRWIN`;

  const caseStudyMapPoints: MapTrackPoint[] = (caseStudy.timeline || []).map((t) => ({
    lat: t.latitude,
    lon: t.longitude,
    time: t.observation_time,
    intensity_kts: t.current_wind_kts,
    intensity_kmh: Math.round(t.current_wind_kts * 1.852),
    pressure_mb: t.central_pressure_mb || undefined,
    agency_grade: "NOAA IBTrACS",
  }));

  return (
    <PortalLayout type="user">
      <div className="space-y-6">
        {/* Navigation & Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#e2e6e9]">
          <Breadcrumb
            items={[
              { label: "Dashboard", href: "/user/dashboard" },
              { label: "Cyclone Database", href: "/user/cyclones" },
              { label: caseStudy.storm_name, href: `/user/cyclones/${cycloneId}` },
              { label: "Historical Case Study" },
            ]}
          />
          <div className="flex items-center gap-2">
            <Link href={`/user/cyclones/${cycloneId}`}>
              <Button size="sm" variant="outline">
                <ArrowLeft className="h-3.5 w-3.5 mr-1" />
                Operational Cyclone View
              </Button>
            </Link>
          </div>
        </div>

        {/* 1. CYCLONE OVERVIEW BANNER */}
        <div className="border border-[#e2e6e9] bg-[#ffffff] p-5 rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#0f5b6c] font-bold">
                  Scientific Historical Case Study
                </span>
                <StatusBadge status="operational" text="Verified Benchmark Lifecycle" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-[#0f5b6c]" />
                TROPICAL CYCLONE {caseStudy.storm_name.toUpperCase()} (NIO)
              </h1>
              <p className="text-xs text-[#5f6b7c] mt-1 max-w-3xl leading-relaxed">
                {caseStudy.summary}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 shrink-0">
              <Badge variant="brand">Target Fix: {caseStudy.canonical_observation_time_utc.slice(0, 16)}Z</Badge>
              <Badge variant="neutral">Designation: {caseStudy.international_id || caseStudy.storm_id}</Badge>
            </div>
          </div>

          {/* Storm Lifecycle Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <span className="block text-[10px] text-[#5f6b7c] uppercase">Peak Intensity</span>
              <span className="text-base font-bold text-[#182026]">{caseStudy.peak_intensity_kts} kt</span>
              <span className="block text-[9px] text-[#5f6b7c]">IBTrACS 1-min sustained</span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <span className="block text-[10px] text-[#5f6b7c] uppercase">Min Central Pressure</span>
              <span className="text-base font-bold text-[#182026]">
                {caseStudy.min_central_pressure_mb ? `${caseStudy.min_central_pressure_mb} hPa` : "—"}
              </span>
              <span className="block text-[9px] text-[#5f6b7c]">Estimated MSLP</span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <span className="block text-[10px] text-[#5f6b7c] uppercase">Verified Observations</span>
              <span className="text-base font-bold text-[#0f5b6c]">{caseStudy.total_verified_observations} Fixes</span>
              <span className="block text-[9px] text-[#5f6b7c]">Coincident HURSAT-B1</span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <span className="block text-[10px] text-[#5f6b7c] uppercase">RI Events Observed</span>
              <span className="text-base font-bold text-[#cf1322]">{caseStudy.ri_events_count} RI+ Fixes</span>
              <span className="block text-[9px] text-[#5f6b7c]">ΔV ≥ 30 kt / 24h</span>
            </div>
          </div>
        </div>

        {/* 2. INTERACTIVE BEST-TRACK MAP CENTERPIECE */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-[#182026] uppercase font-bold flex items-center gap-1.5">
              <Compass className="h-4 w-4 text-[#0f5b6c]" />
              Historical Best-Track & Selected Fix Geography
            </span>
            <span className="text-[#0f5b6c] font-semibold">
              Fix: {(selectedObsTime || caseStudy.selected_observation_time_utc).slice(0, 16)} UTC · V0 = {what_the_model_saw.temporal_indicators.current_wind_kts} kt
            </span>
          </div>
          <CycloneMap
            title={`Historical Track Map · ${caseStudy.storm_name.toUpperCase()}`}
            subtitle="Authentic NOAA IBTrACS observation track · Interactive fixes, wind radii, and WMO intensity colors"
            basin={caseStudy.basin}
            center={[what_the_model_saw.latitude, what_the_model_saw.longitude]}
            zoom={5}
            tracks={caseStudyMapPoints}
            selectedTime={selectedObsTime || caseStudy.selected_observation_time_utc}
            className="h-[460px]"
          />
        </div>

        {/* 3. HISTORICAL OBSERVATION TIMELINE */}
        <CycloneTimeline
          timeline={caseStudy.timeline}
          selectedObservationTime={selectedObsTime || caseStudy.selected_observation_time_utc}
          onSelectObservation={handleSelectObservation}
        />

        {/* 3. RI EVOLUTION CHART */}
        <RIRiskTimeline
          timeline={caseStudy.timeline}
          selectedObservationTime={selectedObsTime || caseStudy.selected_observation_time_utc}
          onSelectObservation={handleSelectObservation}
        />

        {/* 4. PREDICTION VS OUTCOME CARD (Strict Section A vs Section B Separation) */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#182026]">
              Temporal Grounding & Prediction vs Outcome Verification
            </span>
            <span className="text-[11px] font-mono text-[#5f6b7c]">
              Fix: {what_the_model_saw.observation_time_utc.replace("T", " ")}
            </span>
          </div>
          <PredictionOutcomeCard
            whatTheModelSaw={what_the_model_saw}
            historicalOutcome={historical_outcome}
          />
        </div>

        {/* 5. TEMPORAL EVOLUTION PANEL */}
        <TemporalEvolutionPanel
          indicators={what_the_model_saw.temporal_indicators}
          rawFeatures={what_the_model_saw.temporal_features}
        />

        {/* 6. SATELLITE STRUCTURAL EVIDENCE VIEW */}
        <EvidencePanel
          satelliteAvailable={true}
          temporalAvailable={true}
          imageryUrl={patchUrl}
          observationTimeUtc={what_the_model_saw.observation_time_utc}
          spatialFeatures={what_the_model_saw.spatial_features}
          channelsAvailable={what_the_model_saw.satellite_evidence.channels_available}
        />

        {/* 7. MODEL RI RISK INDEX PANEL */}
        <RIRiskPanel
          state={isElevated ? "elevated" : "low"}
          riAssessment={{
            storm_id: caseStudy.storm_id,
            storm_name: caseStudy.storm_name,
            observation_time_utc: what_the_model_saw.observation_time_utc,
            forecast_horizon_hours: 24.0,
            ri_risk_index: modelScore.ri_risk_index,
            ri_probability: modelScore.ri_risk_index,
            operating_threshold: modelScore.operating_threshold,
            decision_threshold: modelScore.operating_threshold,
            ri_flag: modelScore.ri_flag,
            risk_category: modelScore.risk_category,
            risk_tier: isElevated ? "ELEVATED_RI_RISK" : "LOW_RISK",
            calibration_status: modelScore.calibration_status,
            model_name: modelScore.model_name,
            model_version: modelScore.model_version,
            temporal_evidence_available: true,
            satellite_evidence_available: true,
            available_sources: ["NOAA IBTrACS", "NOAA HURSAT-B1"],
            limitations: caseStudy.scientific_limitations,
          }}
        />

        {/* 8. MODEL FEATURE ATTRIBUTION PANEL */}
        <ModelFeatureAttributionPanel
          topSupporting={what_the_model_saw.model_feature_attribution.top_supporting_features}
          topSuppressing={what_the_model_saw.model_feature_attribution.top_suppressing_features}
          method={what_the_model_saw.model_feature_attribution.method}
          disclaimer={what_the_model_saw.model_feature_attribution.attribution_disclaimer}
        />

        {/* 9. SCIENTIFIC LIMITATIONS */}
        <Panel>
          <PanelHeader
            title="Scientific Limitations & Data Provenance"
            subtitle="Verified constraints of CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen)"
          />
          <div className="p-5 space-y-3 text-xs leading-relaxed text-[#182026]">
            <ul className="list-disc pl-5 space-y-1.5 text-[#5f6b7c]">
              {caseStudy.scientific_limitations.map((limit, i) => (
                <li key={i} className="text-[#182026]">
                  {limit}
                </li>
              ))}
            </ul>
          </div>
        </Panel>

        {/* 10. AUTHORITATIVE WARNING ADVISORY */}
        <Alert variant="warning" title="Operational Advisory & Scientific Governance">
          <div className="space-y-1 text-xs">
            <p className="font-semibold text-[#182026]">
              {caseStudy.authoritative_warning_advisory}
            </p>
            <p className="text-[#5f6b7c]">
              CycloneGuard is an experimental AI research framework. Model-derived empirical risk indices do not constitute an official warning service.
              Official meteorological advisories, track cones, and warnings issued by the India Meteorological Department (IMD), Regional Specialized Meteorological Centre (RSMC New Delhi), and Joint Typhoon Warning Center (JTWC) remain authoritative.
            </p>
          </div>
        </Alert>
      </div>
    </PortalLayout>
  );
}
