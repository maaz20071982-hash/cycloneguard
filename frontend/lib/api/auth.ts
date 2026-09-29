import { apiClient, setAuthToken, removeAuthToken } from "@/lib/api/client";
import { User, LoginResult } from "@/types";

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role?: "USER" | "ADMIN";
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function loginUser(payload: LoginPayload): Promise<LoginResult> {
  const result = await apiClient<LoginResult>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (result.access_token) {
    setAuthToken(result.access_token);
  }
  return result;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  return await apiClient<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser(): Promise<User> {
  return await apiClient<User>("/auth/me", {
    method: "GET",
  });
}

export function logoutUser(): void {
  removeAuthToken();
}
