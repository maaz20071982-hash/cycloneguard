"use client";

import React from "react";
import { Header } from "@/components/layout/Header";
import { AdminLayout } from "@/components/layout/AdminLayout";

interface PortalLayoutProps {
  children: React.ReactNode;
  type: "user" | "admin";
}

export function PortalLayout({ children, type }: PortalLayoutProps) {
  if (type === "admin") {
    return <AdminLayout>{children}</AdminLayout>;
  }

  // USER PORTAL: Calm, map-centric, top-nav driven (NO permanent sidebar)
  return (
    <div className="min-h-screen bg-[#080d16] flex flex-col font-sans text-slate-100">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
