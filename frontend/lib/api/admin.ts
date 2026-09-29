import { apiClient } from "@/lib/api/client";
import {
  AdminDashboardData,
  AdminDataSource,
  AdminModel,
  AuditLog,
  User,
  AdminSystemTelemetry,
  UserRole,
} from "@/types";

export interface AdminDataSourcesResponse {
  data_sources: AdminDataSource[];
  total: number;
  connected_count: number;
  status: string;
}

export interface AdminModelsResponse {
  models: AdminModel[];
  total: number;
  active_deployments: number;
  status: string;
  ri_model_v1?: any;
  baseline_model?: any;
  spatial_model_s?: any;
  combined_model_st?: any;
  environmental_model_e?: any;
  multimodal_model_ste?: any;
  final_frozen_model?: any;
}

export interface EnvironmentalCoverageResponse {
  dataset_version: string;
  status: string;
  total_observations: number;
  supervised_samples: number;
  vws_observed_count: number;
  vws_coverage_pct: number;
  sst_observed_count: number;
  sst_coverage_pct: number;
  rh_observed_count: number;
  rh_coverage_pct: number;
  mean_sst_celsius: number | null;
  mean_vws_kts: number | null;
  max_temporal_offset_minutes: number;
  directional_causality_enforced: boolean;
  future_lookahead_violations: number;
  sources: Array<{
    source_name: string;
    type: string;
    variables: string[];
    resolution: string;
  }>;
  storm_breakdown: Record<string, any>;
  limitations: string[];
}

export interface AdminPredictionsResponse {
  predictions: any[];
  total: number;
  status: string;
  message: string;
  columns: string[];
}

export interface AdminAlertsResponse {
  alerts: any[];
  total: number;
  status: string;
  message: string;
  disclaimer: string;
  columns: string[];
}

export interface AdminUsersResponse {
  users: User[];
  total: number;
  skip: number;
  limit: number;
}

export interface AdminAuditLogsResponse {
  logs: AuditLog[];
  total: number;
  skip: number;
  limit: number;
}

export interface HistoricalHursatCoverageResponse {
  dataset_version: string;
  historical_assets: number;
  downloaded_assets: number;
  valid_assets: number;
  corrupted_assets: number;
  cyclone_matches: number;
  patches: number;
  ri_labeled_samples: number;
  ri_positive_samples: number;
  ri_negative_samples: number;
  ri_prevalence_pct: number;
  historical_years: number[];
  unique_storms: number;
  channels_extracted: string[];
  dataset_readiness_classification: string;
}

export async function fetchAdminDashboard(): Promise<AdminDashboardData> {
  return await apiClient<AdminDashboardData>("/admin/dashboard");
}

export async function fetchAdminDataSources(): Promise<AdminDataSourcesResponse> {
  return await apiClient<AdminDataSourcesResponse>("/admin/data-sources");
}

export async function fetchHistoricalHursatCoverage(): Promise<HistoricalHursatCoverageResponse> {
  return await apiClient<HistoricalHursatCoverageResponse>("/admin/historical-hursat-coverage");
}

export async function fetchEnvironmentalCoverage(): Promise<EnvironmentalCoverageResponse> {
  return await apiClient<EnvironmentalCoverageResponse>("/admin/environmental-coverage");
}

export async function fetchAdminModels(): Promise<AdminModelsResponse> {
  return await apiClient<AdminModelsResponse>("/admin/models");
}

export async function fetchAdminPredictions(params: {
  storm?: string;
  risk_category?: string;
  model_version?: string;
  skip?: number;
  limit?: number;
} = {}): Promise<AdminPredictionsResponse> {
  const query = new URLSearchParams();
  if (params.storm) query.set("storm", params.storm);
  if (params.risk_category) query.set("risk_category", params.risk_category);
  if (params.model_version) query.set("model_version", params.model_version);
  if (params.skip !== undefined) query.set("skip", params.skip.toString());
  if (params.limit !== undefined) query.set("limit", params.limit.toString());
  const qs = query.toString();
  return await apiClient<AdminPredictionsResponse>(`/admin/predictions${qs ? `?${qs}` : ""}`);
}

export async function fetchAdminPredictionById(id: string): Promise<any> {
  return await apiClient<any>(`/admin/predictions/${id}`);
}

export async function fetchAdminAlerts(): Promise<AdminAlertsResponse> {
  return await apiClient<AdminAlertsResponse>("/admin/alerts");
}

export async function fetchAdminUsers(params: {
  skip?: number;
  limit?: number;
  role?: UserRole;
  is_active?: boolean;
} = {}): Promise<AdminUsersResponse> {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.set("skip", params.skip.toString());
  if (params.limit !== undefined) query.set("limit", params.limit.toString());
  if (params.role) query.set("role", params.role);
  if (params.is_active !== undefined) query.set("is_active", params.is_active.toString());

  const qs = query.toString();
  return await apiClient<AdminUsersResponse>(`/admin/users${qs ? `?${qs}` : ""}`);
}

export async function fetchAdminUserById(id: string): Promise<User> {
  return await apiClient<User>(`/admin/users/${id}`);
}

export async function updateAdminUser(
  id: string,
  payload: { name?: string; role?: UserRole }
): Promise<User> {
  return await apiClient<User>(`/admin/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminUserStatus(
  id: string,
  isActive: boolean
): Promise<User> {
  return await apiClient<User>(`/admin/users/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ is_active: isActive }),
  });
}

export async function fetchAdminAuditLogs(params: {
  skip?: number;
  limit?: number;
  action?: string;
  resource_type?: string;
} = {}): Promise<AdminAuditLogsResponse> {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.set("skip", params.skip.toString());
  if (params.limit !== undefined) query.set("limit", params.limit.toString());
  if (params.action) query.set("action", params.action);
  if (params.resource_type) query.set("resource_type", params.resource_type);

  const qs = query.toString();
  return await apiClient<AdminAuditLogsResponse>(`/admin/audit-logs${qs ? `?${qs}` : ""}`);
}

export async function fetchAdminSystem(): Promise<AdminSystemTelemetry> {
  return await apiClient<AdminSystemTelemetry>("/admin/system");
}
