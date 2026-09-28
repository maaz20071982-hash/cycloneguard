"use client";

import React from "react";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { DataRow } from "@/components/ui/DataRow";
import { Activity, ShieldAlert, Clock, AlertTriangle, Layers, Satellite } from "lucide-react";
import { RIRisk, RIRiskLevel } from "@/types";

export interface RIRiskPanelProps {
  risk?: RIRisk | null;
  state?: RIRiskLevel;
  className?: string;
  riAssessment?: {
    prediction_id?: string;
    storm_id?: string;
    storm_name?: string;
    observation_time_utc?: string;
    forecast_horizon_hours?: number;
    ri_risk_index?: number;
    ri_probability?: number;
    operating_threshold?: number;
    decision_threshold?: number;
    ri_flag?: boolean;
    risk_category?: string;
    risk_tier?: string;
    calibration_status?: string;
    model_name?: string;
    model_version?: string;
    temporal_evidence_available?: boolean;
    satellite_evidence_available?: boolean;
    satellite_channels_available?: string[];
    input_data_timestamp?: string;
    input_data_provenance?: {
      track_dataset?: string;
      satellite_dataset?: string;
      observation_time_utc?: string;
      cyclone_center_lat?: number;
      cyclone_center_lon?: number;
    };
    data_quality?: {
      quality_overall_flag?: string;
      quality_ir_available?: boolean;
      quality_microwave_available?: boolean;
      quality_track_gap_hours?: number;
      quality_flags_count?: number;
    };
    available_sources?: string[];
    top_supporting_features?: Array<{ feature_name: string; attribution_score: number; direction: string }>;
    top_suppressing_features?: Array<{ feature_name: string; attribution_score: number; direction: string }>;
    explanation?: {
      method?: string;
      top_supporting_features?: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      top_suppressing_features?: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      attribution_list?: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      disclaimer?: string;
    };
    limitations?: string[];
    disclaimers?: string[];
  } | null;
}

export function RIRiskPanel({
  risk,
  state = "unavailable",
  className = "",
  riAssessment = null,
}: RIRiskPanelProps) {
  // If we have verified Sprint 12 Frozen Model RI assessment
  const hasAssessment = Boolean(
    riAssessment && (riAssessment.ri_risk_index !== undefined || riAssessment.ri_probability !== undefined)
  );

  if (hasAssessment && riAssessment) {
    const rawScore = riAssessment.ri_risk_index ?? riAssessment.ri_probability ?? 0.0;
    const scoreFormatted = Number(rawScore).toFixed(3);
    const threshold = riAssessment.operating_threshold ?? riAssessment.decision_threshold ?? 0.125;
    const thresholdFormatted = Number(threshold).toFixed(3);
    const horizonHours = riAssessment.forecast_horizon_hours || 24;
    const modelName = riAssessment.model_name || "CycloneGuard-RI-Multimodal-TS-Final";
    const modelVersion = riAssessment.model_version || "v3.0.0-frozen";
    const calibStatus = riAssessment.calibration_status || "Uncalibrated Empirical Risk Index";

    // Category determination (aligned with SPRINT12_RISK_PRESENTATION.md)
    const category = riAssessment.risk_category || (
      rawScore < threshold ? "LOW_RISK" : rawScore < 0.350 ? "ELEVATED_RISK" : "HIGH_RISK"
    );

    const isElevated = category === "ELEVATED_RISK" || category === "HIGH_RISK" || Boolean(riAssessment.ri_flag);

    const categoryBadgeVariant: "neutral" | "success" | "warning" | "danger" =
      category === "HIGH_RISK" ? "danger" : category === "ELEVATED_RISK" ? "warning" : "success";

    const categoryLabel =
      category === "HIGH_RISK"
        ? "High RI Risk"
        : category === "ELEVATED_RISK"
        ? "Elevated RI Risk"
        : "Low RI Risk";

    // Evidence availability flags
    const tempAvailable = riAssessment.temporal_evidence_available !== false;
    const satAvailable = riAssessment.satellite_evidence_available !== false;
    const satChannels = riAssessment.satellite_channels_available || ["IRWIN (11 µm)", "IRWVP (6.7 µm)"];

    // Provenance
    const trackSrc = riAssessment.input_data_provenance?.track_dataset || "NOAA IBTrACS v04r01 (Best Track)";
    const satSrc = riAssessment.input_data_provenance?.satellite_dataset || "NOAA HURSAT-B1 v06 (Geostationary)";
    const obsTime = riAssessment.observation_time_utc || riAssessment.input_data_timestamp || "Historical Observation";

    // Supporting & suppressing features
    const topSupporting = riAssessment.top_supporting_features ||
      riAssessment.explanation?.top_supporting_features || [];
    const topSuppressing = riAssessment.top_suppressing_features ||
      riAssessment.explanation?.top_suppressing_features || [];

    return (
      <Panel className={className}>
        <PanelHeader
          title="Rapid Intensification (RI) Risk Assessment"
          subtitle={`Model-estimated empirical RI risk index for ΔVmax ≥ 30 kt within ${horizonHours}h · Model ${modelVersion}`}
          action={
            <Badge variant={categoryBadgeVariant} className="font-mono text-[10px]">
              {categoryLabel}
            </Badge>
          }
        />

        <div className="p-5 space-y-4">
          {/* Main Risk Score Area */}
          <div className="p-4 border border-[#e2e6e9] bg-[#ffffff] rounded-[3px]">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                  Model Decision Classification ({horizonHours}h Horizon)
                </span>
                <span className={`text-base sm:text-lg font-bold ${
                  category === "HIGH_RISK"
                    ? "text-[#dc2626]"
                    : isElevated
                    ? "text-[#b45309]"
                    : "text-[#16a34a]"
                }`}>
                  {categoryLabel}
                </span>
                <span className="text-xs text-[#5f6b7c] block mt-0.5">
                  Operating threshold rule: Empirical score ≥ {thresholdFormatted} triggers elevated vigilance.
                </span>
              </div>
              <div className="sm:text-right border-t sm:border-t-0 pt-2 sm:pt-0 border-[#e2e6e9]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                  Empirical RI Risk Index
                </span>
                <span className="text-2xl font-bold font-tabular text-[#182026]">
                  {scoreFormatted}
                </span>
                <span className="text-[10px] font-mono text-[#5f6b7c] block">
                  Operating Threshold: τ = {thresholdFormatted}
                </span>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-[#e2e6e9] flex flex-wrap gap-x-4 gap-y-1 text-xs text-[#5f6b7c] font-mono">
              <span>Model: <strong>{modelVersion}</strong></span>
              <span>•</span>
              <span>Architecture: <strong>Regularized Balanced Logistic Regression (61 Feats)</strong></span>
              <span>•</span>
              <span>Calibration: <strong>{calibStatus.split(";")[0]}</strong></span>
              <span>•</span>
              <span>Horizon: <strong>{horizonHours} hours</strong></span>
            </div>
          </div>

          {/* Evidence Availability Status */}
          <div className="space-y-2 pt-2 border-t border-[#e2e6e9]">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
              Observational Evidence Availability
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div className="p-2.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="block text-[9px] text-[#5f6b7c] uppercase font-mono">Temporal Evolution</span>
                <span className={`font-semibold text-xs font-mono ${tempAvailable ? "text-[#16a34a]" : "text-[#dc2626]"}`}>
                  {tempAvailable ? "Available (23 features)" : "Unavailable"}
                </span>
              </div>
              <div className="p-2.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="block text-[9px] text-[#5f6b7c] uppercase font-mono">Satellite Structure</span>
                <span className={`font-semibold text-xs font-mono ${satAvailable ? "text-[#16a34a]" : "text-[#b45309]"}`}>
                  {satAvailable ? "Available (38 features)" : "Unavailable (Imputed via train median)"}
                </span>
              </div>
              <div className="p-2.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="block text-[9px] text-[#5f6b7c] uppercase font-mono">Satellite Channels</span>
                <div className="flex flex-wrap gap-1 mt-0.5">
                  {satAvailable && satChannels.length > 0 ? (
                    satChannels.map((ch) => (
                      <span key={ch} className="px-1.5 py-0.2 bg-[#e1f0f5] text-[#0f5b6c] rounded-[2px] font-mono text-[9px]">
                        {ch.split(" ")[0]}
                      </span>
                    ))
                  ) : (
                    <span className="text-[10px] text-[#5f6b7c] font-mono">None observed</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Provenance Metadata */}
          <div className="space-y-1.5 pt-2 border-t border-[#e2e6e9]">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
              Data Provenance & Traceability
            </span>
            <DataRow label="Cyclone Track Provenance" value={trackSrc} />
            <DataRow label="Satellite Imagery Provenance" value={satSrc} />
            <DataRow label="Observation Timestamp" value={`${obsTime} UTC`} />
            {riAssessment.prediction_id && (
              <DataRow label="Prediction Record ID" value={riAssessment.prediction_id} />
            )}
          </div>

          {/* Model Attribution (Contributing Features) */}
          {(topSupporting.length > 0 || topSuppressing.length > 0) && (
            <div className="space-y-2 pt-2 border-t border-[#e2e6e9]">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                  Statistical Model Attribution
                </span>
                <span className="text-[10px] text-[#5f6b7c] italic">
                  Linear statistical contribution · Not physical causation
                </span>
              </div>

              {topSupporting.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-[#182026] block">
                    Top Contributing Features (Supporting RI Risk):
                  </span>
                  {topSupporting.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs font-mono py-0.5 px-2 bg-[#f8f9fa] rounded-[2px]">
                      <span className="text-[#182026]">{item.feature_name}</span>
                      <span className="text-[#b45309] font-semibold">+{Number(item.attribution_score).toFixed(3)}</span>
                    </div>
                  ))}
                </div>
              )}

              {topSuppressing.length > 0 && (
                <div className="space-y-1 mt-2">
                  <span className="text-[11px] font-semibold text-[#182026] block">
                    Top Dampening Features (Suppressing RI Risk):
                  </span>
                  {topSuppressing.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs font-mono py-0.5 px-2 bg-[#f8f9fa] rounded-[2px]">
                      <span className="text-[#182026]">{item.feature_name}</span>
                      <span className="text-[#16a34a] font-semibold">{Number(item.attribution_score).toFixed(3)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Mandatory Authoritative Warning Disclaimer */}
          <div className="p-3 bg-[#f1f5f9] border border-[#cbd5e1] rounded-[3px] text-xs text-[#334155] space-y-1.5">
            <div className="flex items-center gap-1.5 font-bold text-[#0f5b6c] text-[11px] uppercase font-mono">
              <ShieldAlert className="h-4 w-4" />
              Operational Authority & Scientific Advisory
            </div>
            <p className="leading-relaxed">
              <strong>This is a model-derived empirical RI risk index, not an official meteorological warning or calibrated probability.</strong>
            </p>
            <p className="text-[11px] text-[#475569] leading-relaxed">
              Official meteorological warnings issued by national weather centers (e.g., India Meteorological Department — IMD, Joint Typhoon Warning Center — JTWC) remain strictly authoritative. This statistical decision-support index does not guarantee rapid intensification, exact track landfall, or district-level evacuation timing.
            </p>
          </div>

          {/* Documented Limitations */}
          {riAssessment.limitations && riAssessment.limitations.length > 0 && (
            <div className="p-3 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] text-xs text-[#5f6b7c] space-y-1">
              <span className="font-semibold text-[#182026] block font-mono text-[10px] uppercase">
                Model Limitations:
              </span>
              <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                {riAssessment.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </Panel>
    );
  }

  // Fallback for when no real assessment is provided
  return (
    <Panel className={className}>
      <PanelHeader
        title="Rapid Intensification (RI) Analysis"
        subtitle="Empirical statistical prediction for ΔVmax ≥ 30 kt within 24 hours · Frozen Model v3.0.0-frozen"
        action={
          <Badge variant="neutral" className="font-mono text-[10px]">
            Awaiting Observation Ingest
          </Badge>
        }
      />

      <div className="p-5 space-y-4">
        <div className="h-44 border border-dashed border-[#e2e6e9] bg-[#f8f9fa] flex flex-col items-center justify-center p-6 text-center rounded-[3px]">
          <Activity className="h-8 w-8 text-[#5f6b7c] mb-2 opacity-50" />
          <h4 className="text-xs font-bold text-[#182026] uppercase font-mono tracking-wider">
            Awaiting Cyclone Observation Ingest
          </h4>
          <p className="text-[11px] text-[#5f6b7c] max-w-md mt-1 leading-relaxed">
            Rapid intensification inference requires verified cyclone track telemetry and coincident satellite structural features. Select a verified storm from the database or submit an observation fix to generate the empirical RI risk index.
          </p>
        </div>

        <div className="p-3 bg-[#f1f5f9] border border-[#cbd5e1] rounded-[3px] text-xs text-[#475569]">
          <span className="font-bold text-[#0f5b6c] block font-mono text-[10px] uppercase mb-1">
            Authoritative Guidance:
          </span>
          Official meteorological warnings from national agencies (IMD, JTWC) remain authoritative. Model outputs represent empirical research decision support.
        </div>
      </div>
    </Panel>
  );
}
