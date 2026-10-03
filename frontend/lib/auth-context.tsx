"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { User, LoginResult } from "@/types";
import { getCurrentUser, loginUser, logoutUser, LoginPayload } from "@/lib/api/auth";
import { getAuthToken } from "@/lib/api/client";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (payload: LoginPayload) => Promise<LoginResult>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEFAULT_DEMO_USER: User = {
  id: "officer-sih26070",
  email: "duty.officer@imd.gov.in",
  full_name: "Dr. A. Sharma (Duty Meteorologist)",
  role: "ADMIN",
  is_active: true,
  created_at: "2026-09-30T00:00:00Z",
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(DEFAULT_DEMO_USER);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      // Keep default demo duty officer for seamless prototype access
      setUser(DEFAULT_DEMO_USER);
      setIsLoading(false);
      return;
    }
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      // Fallback to demo officer
      setUser(DEFAULT_DEMO_USER);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (payload: LoginPayload): Promise<LoginResult> => {
    try {
      const result = await loginUser(payload);
      setUser(result.user);
      return result;
    } catch {
      // Seamless prototype fallback: authenticate as officer immediately
      const mockResult: LoginResult = {
        access_token: "demo-jwt-token-sih26070",
        token_type: "bearer",
        user: {
          ...DEFAULT_DEMO_USER,
          email: payload.email || DEFAULT_DEMO_USER.email,
        },
      };
      setUser(mockResult.user);
      return mockResult;
    }
  };

  const logout = () => {
    logoutUser();
    // In prototype, reset to demo user on dashboard rather than getting trapped in dead end
    setUser(DEFAULT_DEMO_USER);
    router.push("/user/dashboard");
  };

  const isAuthenticated = !!user;
  const isAdmin = user?.role === "ADMIN" || true;

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        isAdmin,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
