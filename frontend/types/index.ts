export type UserRole = "USER" | "ADMIN";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SystemInfo {
  app_name: string;
  version: string;
  environment: string;
  platform_status: string;
  research_status: string;
  database_connected: boolean;
  data_sources_status: string;
  model_inference_status: string;
  active_sprint: string;
}

export interface ModelInfo {
  name: string;
  target: string;
  architecture: string;
  status: string;
  deployed: boolean;
  version: string;
  note: string;
}

export interface DataSourceInfo {
  name: string;
  type: string;
  basin: string;
  channels: string[];
  status: string;
  note: string;
}

// -------------------------------------------------------------
// SPRINT 3 ADMIN PORTAL & OPERATIONAL TELEMETRY TYPES
// -------------------------------------------------------------

export interface AuditLog {
  id: string;
  user_id?: string | null;
  user_email?: string | null;
  user_name?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  timestamp: string;
  metadata?: Record<string, any> | null;
}

export interface AdminDashboardData {
  data_sources: {
    connected: number;
    total: number;
    status: string;
    message: string;
  };
  models: {
    deployed: number;
    total: number;
    status: string;
    message: string;
  };
  predictions: {
    total: number;
    status: string;
    message: string;
  };
  alerts: {
    active: number;
    status: string;
    message: string;
  };
  users: {
    total: number;
    active: number;
    admins: number;
  };
  health: {
    application: string;
    database: string;
    ai_engine: string;
    data_pipeline: string;
    version: string;
  };
  recent_activity: AuditLog[];
}

export interface AdminDataSource {
  name: string;
  provider: string;
  type: string;
  status: string;
  last_successful_update: string | null;
  last_failure: string | null;
  data_coverage: string;
  records_processed: number | null;
  channels: string[];
  actions: string[];
}

export interface AdminModel {
  model_name: string;
  version: string;
  status: string;
  framework: string;
  dataset: string;
  dataset_version: string | null;
  evaluation: Record<string, any> | null;
  deployment_status: string;
  deployed: boolean;
  target: string;
  trained_at: string | null;
  metrics: Record<string, any> | null;
}

export interface AdminSystemTelemetry {
  app_name: string;
  version: string;
  environment: string;
  platform_status: string;
  research_status: string;
  backend: {
    status: string;
    framework: string;
    uptime_check: string;
  };
  database: {
    status: string;
    engine: string;
    migration_revision: string;
  };
  ai_engine: {
    status: string;
    registered_models: number;
    active_deployments: number;
  };
  data_pipeline: {
    status: string;
    registered_sources: number;
    connected_sources: number;
  };
  access_control: {
    total_users: number;
    active_users: number;
    admin_users: number;
    role_enforcement: string;
  };
  timestamp: string;
}


// -------------------------------------------------------------
// SPRINT 2 CYCLONE INTELLIGENCE & SCIENTIFIC DATA ARCHITECTURE
// -------------------------------------------------------------

export type CycloneStatus = "INVEST" | "DEPRESSION" | "CYCLONIC_STORM" | "SEVERE_CYCLONIC_STORM" | "VERY_SEVERE" | "EXTREMELY_SEVERE" | "SUPER_CYCLONE" | "DISSIPATED" | "STANDBY";

export interface Cyclone {
  id: string;
  name: string;
  basin: string; // e.g., NIO, WPAC, EPAC, ATL
  status: CycloneStatus;
  current_intensity_kmh?: number | null; // Vmax in km/h
  current_intensity_kts?: number | null; // Vmax in knots
  estimated_mslp_hpa?: number | null; // Central pressure
  intensity_trend?: "increasing" | "decreasing" | "steady" | "rapid_intensification" | null;
  ri_risk_level?: RIRiskLevel;
  lat?: number | null;
  lon?: number | null;
  observation_time?: string | null;
  is_demonstration?: boolean;
}

export interface CycloneObservation {
  id: string;
  cyclone_id: string;
  timestamp: string;
  vmax_kmh?: number;
  mslp_hpa?: number;
  satellite_sensor?: string;
  ir_channel?: string;
  cdo_symmetry?: string;
  observation_agency?: string;
}

export interface ForecastHorizon {
  hour: 12 | 24 | 36 | 48;
  vmax_kmh?: number | null;
  mslp_hpa?: number | null;
  lat?: number | null;
  lon?: number | null;
  cone_radius_km?: number | null;
  ri_probability?: number | null;
}

export interface CycloneForecast {
  cyclone_id: string;
  generated_at?: string | null;
  status: "available" | "unavailable" | "pending";
  horizons: ForecastHorizon[];
  message?: string;
}

export type RIRiskLevel = "unavailable" | "low" | "moderate" | "elevated" | "high" | "critical";

export interface RIRisk {
  cyclone_id: string;
  state: RIRiskLevel;
  probability_24h?: number | null;
  probability_48h?: number | null;
  vertical_wind_shear_kts?: number | null;
  sea_surface_temp_celsius?: number | null;
  inner_core_convection?: string | null;
  status_message: string;
}

export interface EvidenceSource {
  id: string;
  sensor: string;
  type: string;
  channel: string;
  resolution: string;
  status: "connected" | "not_connected" | "awaiting_feed";
  last_pass?: string | null;
}

export interface Evidence {
  cyclone_id: string;
  sources: EvidenceSource[];
  summary: string;
  satellite_structural?: SatelliteStructuralEvidence | null;
  environmental_context?: EnvironmentalEvidence | null;
}

export interface EnvironmentalEvidence {
  sources: string[];
  observation_time_utc?: string;
  data_quality: string;
  sea_surface_temp_celsius?: number | null;
  sst_potential_above_26c?: number | null;
  vertical_wind_shear_kts?: number | null;
  shear_direction_deg?: number | null;
  wind_speed_850hpa_kts?: number | null;
  wind_speed_200hpa_kts?: number | null;
  relative_humidity_700hpa_pct?: number | null;
  relative_humidity_500hpa_pct?: number | null;
  temporal_offset_minutes: number;
  availability: {
    sst_observed: boolean;
    vws_observed: boolean;
    rh_observed: boolean;
  };
  disclaimer: string;
}

export interface SatelliteStructuralEvidence {
  satellite_source: string;
  observation_time_utc?: string;
  available_channels: string[];
  data_quality: string;
  grid_resolution: string;
  key_spatial_features: {
    irwin_core_mean_k?: number;
    irwin_core_very_cold_frac?: number;
    irwin_core_ring_diff_k?: number;
    ir_wv_diff_mean_k?: number;
    irwin_spatial_entropy?: number;
  };
  disclaimer: string;
}

export interface AttributionFeature {
  name: string;
  importance: number; // 0.0 to 1.0
  description: string;
}

export interface Explanation {
  cyclone_id: string;
  method: "Grad-CAM" | "Feature Attribution" | "Awaiting Model";
  summary: string;
  is_available: boolean;
  features: AttributionFeature[];
}

export interface HistoricalCyclone {
  id: string;
  name: string;
  season: number;
  basin: string;
  category: string;
  peak_intensity_kmh: number;
  min_mslp_hpa: number;
  had_ri_event: boolean;
  source_dataset: string; // e.g., IBTrACS, IMD, JTWC
}

export interface CycloneFilterParams {
  search?: string;
  basin?: string;
  category?: string;
  season?: string;
  has_ri?: boolean;
}
