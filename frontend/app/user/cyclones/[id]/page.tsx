"use client";

import React, { use, useEffect, useState } from "react";
import Link from "next/link";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Metric } from "@/components/ui/Metric";
import { CycloneMap } from "@/components/ui/CycloneMap";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { RIRiskPanel } from "@/components/ui/RIRiskPanel";
import { EvidencePanel } from "@/components/ui/EvidencePanel";
import { ExplanationPanel } from "@/components/ui/ExplanationPanel";
import { ForecastTimeline } from "@/components/ui/ForecastTimeline";
import { getCycloneRIRisk, getCycloneTrack, RIPredictionResponse, CycloneTrackResponse } from "@/lib/api/cyclones";
import type { MapTrackPoint } from "@/components/ui/CycloneMap";
import {
  ArrowLeft,
  Wind,
  Gauge,
  Clock,
  Activity,
  Layers,
  Sparkles,
  AlertTriangle,
  Radio,
  Eye,
  Calendar,
  Cpu,
} from "lucide-react";

export default function CycloneDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const cycloneId = resolvedParams.id;

  const [riResult, setRiResult] = useState<RIPredictionResponse | null>(null);
  const [trackData, setTrackData] = useState<CycloneTrackResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setIsLoading(true);
      try {
        const [res, trackRes] = await Promise.all([
          getCycloneRIRisk(cycloneId).catch(() => null),
          getCycloneTrack(cycloneId).catch(() => null),
        ]);
        if (isMounted) {
          setRiResult(res);
          setTrackData(trackRes);
        }
      } catch (e) {
        if (isMounted) {
          setRiResult(null);
          setTrackData(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [cycloneId]);

  const assessment = riResult?.ri_assessment;
  const isEvaluated = Boolean(assessment && assessment.ri_probability !== undefined);
  const isElevated = Boolean(assessment?.ri_flag);

  const mapPoints: MapTrackPoint[] = (trackData?.track_points || []).map((p) => ({
    lat: p.latitude,
    lon: p.longitude,
    time: p.timestamp,
    intensity_kts: p.wind_speed_kts,
    intensity_kmh: Math.round(p.wind_speed_kts * 1.852),
    pressure_mb: p.central_pressure_mb || undefined,
    agency_grade: p.agency_grade,
  }));

  const midPoint = mapPoints.length > 0 ? mapPoints[Math.floor(mapPoints.length / 2)] : null;
  const mapCenter: [number, number] = midPoint ? [midPoint.lat, midPoint.lon] : [15.0, 75.0];
  const stormDisplayName = assessment?.storm_name || trackData?.name || cycloneId;

  return (
    <PortalLayout type="user">
      <div className="space-y-6">
        {/* Navigation & Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#e2e6e9]">
          <Breadcrumb
            items={[
              { label: "Dashboard", href: "/user/dashboard" },
              { label: "Cyclone Database", href: "/user/cyclones" },
              { label: `Vortex ID: ${cycloneId}` },
            ]}
          />
          <Link href="/user/cyclones">
            <Button size="sm" variant="outline">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Back to Cyclone List
            </Button>
          </Link>
        </div>

        {/* 1. Header: Cyclone Name, Region, Observation Time */}
        <div className="border border-[#e2e6e9] bg-[#ffffff] p-5 rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                  Cyclone Surveillance Target
                </span>
                <StatusBadge
                  status={isEvaluated ? "operational" : "awaiting"}
                  text={isEvaluated ? "Evaluated (Frozen Model v3.0.0)" : "Awaiting Ingest"}
                />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-[#182026]">
                VORTEX REFERENCE: {(assessment?.storm_name || cycloneId).toUpperCase()}
              </h1>
              <div className="flex flex-wrap items-center gap-3 text-xs text-[#5f6b7c] mt-1 font-mono">
                <span>REGION: <strong>North Indian Ocean (NIO)</strong></span>
                <span>•</span>
                <span>
                  OBSERVATION TIME: <strong>{assessment?.observation_time_utc ? `${assessment.observation_time_utc} UTC` : "Verified Track Fix"}</strong>
                </span>
                <span>•</span>
                <span>MODEL: <strong>CycloneGuard v3.0.0-frozen (61 Features)</strong></span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Link href={`/user/cyclones/${cycloneId}/case-study`}>
                <Button size="sm" variant="primary">
                  <Activity className="h-3.5 w-3.5 mr-1 text-[#ffffff]" />
                  Historical Case Study Workstation
                </Button>
              </Link>
              <Badge variant={isEvaluated ? (isElevated ? "warning" : "success") : "neutral"}>
                {isEvaluated ? (isElevated ? "RI Risk: Elevated" : "RI Risk: Low") : "Status: Standby"}
              </Badge>
              <Badge variant="neutral">Slot ID: {cycloneId}</Badge>
            </div>
          </div>

          {/* 2. Main Information Bar: CURRENT INTENSITY, TREND, RI RISK */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
            <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <Metric
                label="Current Intensity (Vmax)"
                value={
                  mapPoints.length > 0
                    ? `${mapPoints[mapPoints.length - 1].intensity_kts} kt`
                    : isEvaluated
                    ? "Verified"
                    : "—"
                }
                unit={mapPoints.length > 0 ? `(${mapPoints[mapPoints.length - 1].intensity_kmh} km/h)` : isEvaluated ? "Track fix" : "km/h"}
                trend={mapPoints.length > 0 ? `${mapPoints.length} FIXES` : isEvaluated ? "ACTIVE FIX" : "STANDBY"}
                trendDirection={isEvaluated ? "neutral" : "neutral"}
                trendLabel={mapPoints.length > 0 ? "NOAA IBTrACS Ground Truth Series" : isEvaluated ? "From NOAA IBTrACS observation series" : "Awaiting Dvorak / AI estimation"}
              />
            </div>

            <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <Metric
                label="Intensity Trend"
                value={isElevated ? "ELEVATED" : isEvaluated ? "STEADY" : "STANDBY"}
                trend={isElevated ? "WARNING" : "NEUTRAL"}
                trendDirection={isElevated ? "increasing" : "neutral"}
                trendLabel={isElevated ? "ΔV ≥ 30 kt / 24h risk elevated" : isEvaluated ? "Below RI escalation threshold" : "Baseline evaluation pending"}
              />
            </div>

            <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
              <Metric
                label="Empirical RI Risk Index"
                value={isElevated ? "ELEVATED" : isEvaluated ? "LOW RISK" : "PENDING"}
                trend={isEvaluated ? `SCORE: ${(assessment?.ri_risk_index ?? assessment?.ri_probability ?? 0).toFixed(3)}` : "AWAITING"}
                trendDirection={isElevated ? "increasing" : "neutral"}
                trendLabel={isEvaluated ? `Operating threshold: τ = ${assessment?.operating_threshold ?? assessment?.decision_threshold ?? 0.125}` : "Requires 24h temporal sequence"}
              />
            </div>
          </div>
        </div>

        {/* Informational State Banner */}
        {isEvaluated ? (
          <div className="p-4 border border-[#0f5b6c]/30 bg-[#edf5f7] rounded-[4px] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div>
              <span className="font-bold text-[#0f5b6c] uppercase font-mono block text-xs mb-0.5 flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-[#0f5b6c]" />
                Frozen Production Model Active (v3.0.0-frozen)
              </span>
              <p className="text-[#182026]">
                Evaluated using <strong>CycloneGuard-RI-Multimodal-TS-Final</strong>. 61 multimodal features (23 temporal kinematics + 38 HURSAT-B1 spatial structural proxies). Environmental features strictly excluded.
              </p>
            </div>
            <Badge variant="brand" className="shrink-0 font-mono text-[10px]">
              MODEL {assessment?.model_version || "v3.0.0-frozen"} (24H HORIZON)
            </Badge>
          </div>
        ) : (
          <div className="p-4 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[4px] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div>
              <span className="font-bold text-[#182026] uppercase font-mono block text-xs mb-0.5">
                Analysis Standby / Unindexed Storm
              </span>
              <p className="text-[#5f6b7c]">
                This cyclone target does not currently have coincident historical observations staged in the test sample partition.
              </p>
            </div>
            <Badge variant="neutral" className="shrink-0 font-mono text-[10px]">
              ZERO FAKE DATA ADHERENCE
            </Badge>
          </div>
        )}

        {/* 3. LARGE MAP */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5f6b7c] font-mono flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5 text-[#0f5b6c]" />
              Geographic Centerpiece: Observed Track & Cone
            </span>
            <span className="text-[11px] font-mono text-[#5f6b7c]">
              Projection: Mercator 1:10M · 0.05° Lat/Lon Grid
            </span>
          </div>

          <CycloneMap
            title={`Operational Cyclone Map · ${stormDisplayName.toUpperCase()}`}
            subtitle="Authentic NOAA IBTrACS best-track fixes, WMO category velocity vectors & wind radii"
            basin={trackData?.basin || "North Indian Ocean (Bay of Bengal / Arabian Sea)"}
            center={mapCenter}
            zoom={5}
            tracks={mapPoints}
            className="h-[540px]"
          />
        </div>

        {/* 4. INTENSITY EVOLUTION */}
        <Panel>
          <PanelHeader
            title="Intensity Evolution Trajectory"
            subtitle="Observed 10-minute sustained winds (Vmax) vs. Central Pressure (MSLP)"
          />
          <div className="p-5 space-y-4">
            <div className="h-44 border border-dashed border-[#e2e6e9] bg-[#f8f9fa] flex flex-col items-center justify-center p-6 text-center rounded-[3px]">
              <Gauge className="h-8 w-8 text-[#5f6b7c] mb-2 opacity-50" />
              <h4 className="text-xs font-bold text-[#182026] uppercase font-mono tracking-wider">
                {isEvaluated ? "Temporal Kinematics Extracted" : "Intensity Evolution Unavailable"}
              </h4>
              <p className="text-[11px] text-[#5f6b7c] max-w-sm mt-1 leading-relaxed">
                {isEvaluated
                  ? "Temporal evolution derivatives (6h/12h rate-of-change, central pressure tendency, acceleration) were verified and ingested by Model B."
                  : "Time-series trajectory showing 12h, 24h, and 36h progression renders when continuous observational sequences are connected."}
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
              <div className="p-2.5 border border-[#e2e6e9] bg-[#ffffff] rounded-[2px]">
                <span className="block text-[10px] text-[#5f6b7c]">Forecast Horizon</span>
                <span className="font-semibold text-[#182026]">24 hours</span>
              </div>
              <div className="p-2.5 border border-[#e2e6e9] bg-[#ffffff] rounded-[2px]">
                <span className="block text-[10px] text-[#5f6b7c]">WMO RI Criterion</span>
                <span className="font-semibold text-[#182026]">ΔV ≥ 30 kt</span>
              </div>
              <div className="p-2.5 border border-[#e2e6e9] bg-[#ffffff] rounded-[2px]">
                <span className="block text-[10px] text-[#5f6b7c]">Model Version</span>
                <span className="font-semibold text-[#182026]">{assessment?.model_version || "v3.0.0-frozen"}</span>
              </div>
            </div>
          </div>
        </Panel>

        {/* 5. RAPID INTENSIFICATION ANALYSIS (Reusable RIRiskPanel) */}
        <RIRiskPanel
          state={isEvaluated ? (isElevated ? "elevated" : "low") : "unavailable"}
          riAssessment={assessment}
        />

        {/* 6. MULTI-SOURCE EVIDENCE (Reusable EvidencePanel) */}
        <EvidencePanel
          satelliteAvailable={assessment?.satellite_evidence_available !== false}
          temporalAvailable={assessment?.temporal_evidence_available !== false}
        />

        {/* 7. MODEL EXPLANATION (Reusable ExplanationPanel) */}
        <ExplanationPanel
          explanation={
            assessment?.explanation
              ? {
                  cyclone_id: cycloneId,
                  method: "Feature Attribution",
                  summary:
                    "Model attribution assigns weights to recent intensity changes and central pressure rate-of-change. Note: attribution does not establish physical causation.",
                  is_available: true,
                  features: (
                    assessment.explanation.attribution_list ||
                    assessment.explanation.top_supporting_features ||
                    []
                  ).map((f) => ({
                    name: f.feature_name,
                    importance: Math.min(1.0, Math.abs(f.attribution_score)),
                    description:
                      f.direction === "supports_ri"
                        ? "Feature value statistically supports elevated RI risk"
                        : "Feature value statistically dampens RI risk",
                  })),
                }
              : null
          }
        />

        {/* 8. FORECAST TIMELINE (Reusable ForecastTimeline) */}
        <ForecastTimeline />

        {/* 9. DATA SOURCES */}
        <Panel>
          <PanelHeader
            title="Multi-Source Observational Sensor Registry"
            subtitle="Satellite sensors and atmospheric boundary condition feeds contributing to this storm's intelligence"
          />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sensor / Agency</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Channel / Parameter</TableHead>
                <TableHead>Resolution</TableHead>
                <TableHead>Ingestion Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[
                {
                  sensor: "INSAT-3D/3DR (ISRO)",
                  type: "Geostationary Optical/IR",
                  channel: "TIR1 (10.8 µm), WV (6.8 µm)",
                  res: "4 km / 15 min",
                  status: "Awaiting Pipeline",
                },
                {
                  sensor: "Himawari-9 (JMA)",
                  type: "Advanced Baseline Imager",
                  channel: "Band 13 Clean IR, Band 8 Mid-WV",
                  res: "2 km / 10 min",
                  status: "Awaiting Pipeline",
                },
                {
                  sensor: "MetOp ASCAT (EUMETSAT)",
                  type: "Microwave Scatterometer",
                  channel: "Surface Ocean Wind Vectors (10m)",
                  res: "25 km swath",
                  status: "Awaiting Pipeline",
                },
                {
                  sensor: "ERA5 Reanalysis (ECMWF)",
                  type: "Atmospheric Model",
                  channel: "850-200 hPa Shear, SST, RH",
                  res: "0.25° grid",
                  status: "Awaiting Pipeline",
                },
              ].map((row) => (
                <TableRow key={row.sensor}>
                  <TableCell className="font-semibold text-[#182026] flex items-center gap-1.5">
                    <Radio className="h-3.5 w-3.5 text-[#0f5b6c]" />
                    {row.sensor}
                  </TableCell>
                  <TableCell className="text-[#5f6b7c]">{row.type}</TableCell>
                  <TableCell className="font-mono text-[11px] text-[#182026]">{row.channel}</TableCell>
                  <TableCell className="font-mono text-[11px] text-[#5f6b7c]">{row.res}</TableCell>
                  <TableCell>
                    <StatusBadge status="awaiting" text={row.status} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>

        {/* 10. DISCLAIMER */}
        <Alert
          variant="warning"
          title="Operational Advisory & Scientific Limitations"
        >
          <div className="space-y-1 text-xs">
            <p>
              CycloneGuard provides experimental meteorological intelligence and machine learning research evaluations. Predictions and estimations generated by automated neural pipelines must not supersede official advisories, warnings, or evacuation orders issued by national meteorological authorities (e.g., India Meteorological Department — IMD, Joint Typhoon Warning Center — JTWC, or Regional Specialized Meteorological Centres — RSMC).
            </p>
            <p className="text-[11px] text-[#5f6b7c]">
              Rapid intensification predictions are produced by Frozen Model v3.0.0-frozen using verified historical observations (NOAA IBTrACS and HURSAT-B1). Model risk indices represent empirical research decision support; official meteorological advisories remain authoritative.
            </p>
          </div>
        </Alert>
      </div>
    </PortalLayout>
  );
}
