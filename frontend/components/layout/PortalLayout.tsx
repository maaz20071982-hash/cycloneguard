"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { PageLoading } from "@/components/ui/Loading";
import { Header } from "@/components/layout/Header";
import { AdminLayout } from "@/components/layout/AdminLayout";

interface PortalLayoutProps {
  children: React.ReactNode;
  type: "user" | "admin";
}

export function PortalLayout({ children, type }: PortalLayoutProps) {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isLoading, isAuthenticated, router]);

  if (type === "admin") {
    return <AdminLayout>{children}</AdminLayout>;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center">
        <PageLoading text="Verifying platform session..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  // USER PORTAL: Calm, map-centric, top-nav driven (NO permanent sidebar)
  return (
    <div className="min-h-screen bg-[#f8f9fa] flex flex-col font-sans">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
