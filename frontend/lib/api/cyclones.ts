import { apiClient } from "@/lib/api/client";
import {
  Cyclone,
  CycloneForecast,
  Evidence,
  Explanation,
  RIRisk,
  HistoricalCyclone,
  ModelInfo,
  DataSourceInfo,
  User,
} from "@/types";

export interface CyclonesListResponse {
  cyclones: Cyclone[];
  total: number;
  status: string;
  demonstration_data: boolean;
  message: string;
}

export interface CycloneDetailResponse {
  cyclone_id: string;
  cyclone?: Cyclone | null;
  status: string;
  message: string;
}

export interface HistoricalCyclonesResponse {
  historical_cyclones: HistoricalCyclone[];
  total: number;
  status: string;
  demonstration_data: boolean;
  message: string;
}

export interface ForecastResponse {
  cyclone_id: string;
  status: "available" | "unavailable" | "pending";
  horizons: any[];
  message: string;
}

export interface AnalysisResponse {
  cyclone_id: string;
  status: string;
  ri_risk: RIRisk;
  evidence: Evidence;
  explanation: Explanation;
}

export interface DataSourcesResponse {
  data_sources: DataSourceInfo[];
  connected_count: number;
}

export interface ModelsStatusResponse {
  models: ModelInfo[];
  active_deployments: number;
}

export interface PredictionsResponse {
  predictions: any[];
  total: number;
  status: string;
  message: string;
}

export interface AlertsResponse {
  alerts: any[];
  total: number;
  status: string;
  message: string;
}

export interface AdminUsersResponse {
  users: User[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================
// SPRINT 2 USER PORTAL SERVICE ABSTRACTIONS
// ============================================================

export async function getCyclones(): Promise<CyclonesListResponse> {
  return await apiClient<CyclonesListResponse>("/cyclones");
}

export async function getCyclone(id: string): Promise<CycloneDetailResponse> {
  return await apiClient<CycloneDetailResponse>(`/cyclones/${id}`);
}

export async function getHistoricalCyclones(): Promise<HistoricalCyclonesResponse> {
  return await apiClient<HistoricalCyclonesResponse>("/cyclones/historical");
}

export async function getCycloneForecast(id: string): Promise<ForecastResponse> {
  return await apiClient<ForecastResponse>(`/cyclones/${id}/forecast`);
}

export async function getCycloneAnalysis(id: string): Promise<AnalysisResponse> {
  return await apiClient<AnalysisResponse>(`/cyclones/${id}/analysis`);
}

export async function changeUserPassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
  return await apiClient<{ message: string }>("/users/change-password", {
    method: "POST",
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
}

// Backward-compatible aliases
export const fetchCyclones = getCyclones;
export const fetchCycloneById = getCyclone;

export async function fetchDataSources(): Promise<DataSourcesResponse> {
  return await apiClient<DataSourcesResponse>("/data-sources");
}

export async function fetchModelsStatus(): Promise<ModelsStatusResponse> {
  return await apiClient<ModelsStatusResponse>("/models");
}

export async function fetchPredictions(): Promise<PredictionsResponse> {
  return await apiClient<PredictionsResponse>("/predictions");
}

export async function fetchAlerts(): Promise<AlertsResponse> {
  return await apiClient<AlertsResponse>("/alerts");
}

export async function fetchAdminUsers(skip: number = 0, limit: number = 50): Promise<AdminUsersResponse> {
  return await apiClient<AdminUsersResponse>(`/users?skip=${skip}&limit=${limit}`);
}

// ============================================================
// SPRINT 12 FROZEN RAPID INTENSIFICATION PREDICTION APIS
// ============================================================

export interface PredictionFeatureAttribution {
  feature_name: string;
  attribution_score: number;
  direction: string;
  model_coefficient?: number;
  raw_value?: number;
}

export interface PredictionProvenance {
  track_dataset: string;
  satellite_dataset: string;
  observation_time_utc: string;
  cyclone_center_lat: number;
  cyclone_center_lon: number;
  temporal_match_offset_minutes?: number;
}

export interface RIPredictionResponse {
  prediction_id?: string;
  storm_id: string;
  storm_name?: string;
  status: string;
  message?: string;
  ri_assessment?: {
    prediction_id?: string;
    storm_id: string;
    storm_name: string;
    observation_time_utc: string;
    forecast_horizon_hours: number;
    ri_risk_index?: number;
    ri_probability: number;
    operating_threshold?: number;
    decision_threshold: number;
    ri_flag: boolean;
    risk_category?: string;
    risk_tier: string;
    calibration_status: string;
    model_name?: string;
    model_version: string;
    temporal_evidence_available?: boolean;
    satellite_evidence_available?: boolean;
    satellite_channels_available?: string[];
    input_data_timestamp?: string;
    input_data_provenance?: PredictionProvenance;
    data_quality?: {
      quality_overall_flag: string;
      quality_ir_available: boolean;
      quality_microwave_available: boolean;
      quality_track_gap_hours: number;
      quality_flags_count: number;
    };
    available_sources: string[];
    top_supporting_features?: PredictionFeatureAttribution[];
    top_suppressing_features?: PredictionFeatureAttribution[];
    explanation?: {
      method: string;
      top_supporting_features: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      top_suppressing_features: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      attribution_list: Array<{ feature_name: string; attribution_score: number; direction: string }>;
      disclaimer: string;
    };
    limitations: string[];
    disclaimers?: string[];
  } | null;
}

export async function getCycloneRIRisk(stormId: string, threshold?: number): Promise<RIPredictionResponse> {
  const query = threshold !== undefined ? `?threshold=${threshold}` : "";
  return await apiClient<RIPredictionResponse>(`/cyclones/${stormId}/ri-risk${query}`);
}

export async function getPredictionById(predictionId: string): Promise<any> {
  return await apiClient<any>(`/predictions/ri/${predictionId}`);
}

export async function getRIModelMetadata(): Promise<any> {
  return await apiClient<any>("/models/ri");
}

// ============================================================
// SPRINT 13 HISTORICAL CASE STUDY & EVIDENCE APIS
// ============================================================

export interface TimelineObservation {
  observation_id: string;
  observation_time: string;
  storm_id: string;
  storm_name: string;
  latitude: number;
  longitude: number;
  current_wind_kts: number;
  central_pressure_mb?: number | null;
  has_irwin: boolean;
  has_irwvp: boolean;
  has_vschn: boolean;
  satellite_channels: string[];
  ri_risk_index?: number | null;
  operating_threshold: number;
  ri_flag?: boolean | null;
  risk_category?: string | null;
  source_status: string;
  is_canonical: boolean;
}

export interface CaseStudyTimelineResponse {
  storm_id: string;
  total: number;
  timeline: TimelineObservation[];
}

export interface HistoricalOutcome {
  title: string;
  observation_time: string;
  verification_time_24h: string;
  observed_future_wind_kts: number;
  observed_delta_v_24h: number;
  ri_occurred: boolean;
  wmo_ri_criterion: string;
  disclaimer: string;
}

export interface AttributionItem {
  feature_name: string;
  display_name: string;
  direction: "supports_ri" | "suppresses_ri";
  attribution_score: number;
  contribution_magnitude: number;
  normalized_value?: number | null;
  explanation_note: string;
}

export interface TemporalIndicators {
  current_wind_kts: number;
  wind_change_6h_kts?: number | null;
  wind_change_12h_kts?: number | null;
  central_pressure_mb?: number | null;
  pressure_drop_6h_mb?: number | null;
  translation_speed_kts?: number | null;
  translation_bearing_deg?: number | null;
  translation_heading?: string | null;
  source_label: string;
}

export interface SatelliteStructuralEvidence {
  source: string;
  channels_available: string[];
  has_irwin: boolean;
  has_irwvp: boolean;
  has_vschn: boolean;
  irwin_mean_tb_k?: number | null;
  irwin_min_tb_k?: number | null;
  cold_cloud_fraction_233k?: number | null;
  very_cold_cloud_fraction_219k?: number | null;
  overshooting_top_fraction_203k?: number | null;
  core_convection_mean_k?: number | null;
  core_ring_temperature_diff_k?: number | null;
  azimuthal_symmetry_metric?: number | null;
  imagery_endpoint?: string | null;
}

export interface WhatTheModelSawData {
  observation_time_utc: string;
  storm_id: string;
  storm_name: string;
  latitude: number;
  longitude: number;
  temporal_indicators: TemporalIndicators;
  temporal_features: Record<string, number>;
  satellite_evidence: SatelliteStructuralEvidence;
  spatial_features: Record<string, number>;
  model_score: {
    model_name: string;
    model_version: string;
    ri_risk_index: number;
    operating_threshold: number;
    ri_flag: boolean;
    risk_category: string;
    forecast_horizon_hours: number;
    score_label: string;
    threshold_label: string;
    calibration_status: string;
  };
  model_feature_attribution: {
    title: string;
    method: string;
    top_supporting_features: AttributionItem[];
    top_suppressing_features: AttributionItem[];
    attribution_disclaimer: string;
  };
}

export interface CaseStudyData {
  storm_id: string;
  storm_name: string;
  basin: string;
  international_id?: string;
  summary: string;
  lifecycle_start_utc: string;
  lifecycle_end_utc: string;
  peak_intensity_kts: number;
  min_central_pressure_mb?: number | null;
  total_verified_observations: number;
  ri_events_count: number;
  canonical_observation_time_utc: string;
  selected_observation_time_utc: string;
  timeline: TimelineObservation[];
  what_the_model_saw: WhatTheModelSawData;
  historical_outcome: HistoricalOutcome;
  scientific_limitations: string[];
  authoritative_warning_advisory: string;
}

export async function getCycloneTimeline(cycloneId: string): Promise<CaseStudyTimelineResponse> {
  return await apiClient<CaseStudyTimelineResponse>(`/cyclones/${cycloneId}/timeline`);
}

export async function getCycloneCaseStudy(cycloneId: string, observationTime?: string): Promise<CaseStudyData> {
  const query = observationTime ? `?observation_time=${encodeURIComponent(observationTime)}` : "";
  return await apiClient<CaseStudyData>(`/cyclones/${cycloneId}/case-study${query}`);
}

export interface CycloneTrackPoint {
  timestamp: string;
  latitude: number;
  longitude: number;
  wind_speed_kts: number;
  central_pressure_mb?: number | null;
  agency_wind_kts?: number;
  agency_grade?: string;
}

export interface CycloneTrackResponse {
  cyclone_id: string;
  name: string;
  basin: string;
  total_points: number;
  track_points: CycloneTrackPoint[];
}

export interface MultiStormTrack {
  cyclone_id: string;
  name: string;
  basin: string;
  status: string;
  total_points: number;
  peak_intensity_kts?: number | null;
  genesis_time?: string;
  dissipation_time?: string;
  track_points: CycloneTrackPoint[];
}

export interface AllCycloneTracksResponse {
  cyclones: MultiStormTrack[];
  total: number;
  basin: string;
}

export async function getCycloneTrack(id: string): Promise<CycloneTrackResponse> {
  return await apiClient<CycloneTrackResponse>(`/cyclones/${id}/track`);
}

export async function getAllCycloneTracks(): Promise<AllCycloneTracksResponse> {
  return await apiClient<AllCycloneTracksResponse>("/cyclones/tracks/all");
}


