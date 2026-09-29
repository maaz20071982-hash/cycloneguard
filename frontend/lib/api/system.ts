import { apiClient } from "@/lib/api/client";
import { SystemInfo } from "@/types";

export interface HealthCheckResult {
  status: string;
  timestamp: string;
  database: string;
  version: string;
}

export async function checkBackendHealth(): Promise<HealthCheckResult> {
  return await apiClient<HealthCheckResult>("/health", {
    method: "GET",
  });
}

export async function fetchSystemInfo(): Promise<SystemInfo> {
  return await apiClient<SystemInfo>("/system/info", {
    method: "GET",
  });
}
