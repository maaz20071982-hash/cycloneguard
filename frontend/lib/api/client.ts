import { ApiResponse, ApiError } from "@/types";

const TOKEN_KEY = "cycloneguard_token";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {}
}

export function removeAuthToken(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {}
}

// Configurable API base URL: seamlessly routes through Next.js rewrites proxy on all devices
export function getApiBaseUrl(): string {
  // If explicitly configured, use that
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
  }
  // Client-side: use relative path so Next.js proxies to backend from ANY host/tunnel/device
  if (typeof window !== "undefined") {
    return "/api/v1";
  }
  // Server-side internal fetch fallback
  return process.env.BACKEND_INTERNAL_URL
    ? `${process.env.BACKEND_INTERNAL_URL}/api/v1`
    : "http://127.0.0.1:8000/api/v1";
}

export class ApiClientError extends Error {
  public code: string;
  public details?: Record<string, any>;
  public status?: number;

  constructor(message: string, code: string = "API_ERROR", status?: number, details?: Record<string, any>) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(options.headers as Record<string, string>),
  };

  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const isJson = response.headers.get("content-type")?.includes("application/json");
    const json = isJson ? await response.json() : null;

    if (!response.ok) {
      const errPayload = json?.error as ApiError | undefined;
      const message = errPayload?.message || json?.detail || `Request failed with status ${response.status}`;
      const code = errPayload?.code || `HTTP_${response.status}`;
      throw new ApiClientError(message, code, response.status, errPayload?.details);
    }

    // Backend returns standard envelope { success: true, data: T, error: null }
    if (json && typeof json === "object" && "success" in json) {
      if (!json.success && json.error) {
        throw new ApiClientError(json.error.message, json.error.code, response.status, json.error.details);
      }
      return json.data as T;
    }

    return json as T;
  } catch (error: any) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new ApiClientError(
      error.message || "Network connectivity failure. Unable to reach backend service.",
      "NETWORK_ERROR"
    );
  }
}
