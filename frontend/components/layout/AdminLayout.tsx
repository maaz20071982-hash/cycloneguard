"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { PageLoading } from "@/components/ui/Loading";
import { Header } from "@/components/layout/Header";
import { AdminNav } from "@/components/layout/AdminNav";
import { AlertTriangle, Menu, X, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface AdminLayoutProps {
  children: React.ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  const { user, isLoading, isAuthenticated, isAdmin } = useAuth();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isLoading, isAuthenticated, router]);

  // Handle ESC key to dismiss mobile drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };
    if (mobileMenuOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mobileMenuOpen]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center">
        <PageLoading text="Verifying administrative credentials..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  // Enforce ADMIN role restriction
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex flex-col font-sans">
        <Header />
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full rounded-[4px] border border-[#fecaca] bg-white p-6 text-center text-[#182026] shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
            <div className="h-12 w-12 rounded-full bg-[#fef2f2] text-[#b91c1c] flex items-center justify-center mx-auto mb-4 border border-[#fecaca]">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <span className="text-[10px] font-mono uppercase tracking-widest text-[#b91c1c] font-bold block mb-1">
              Restricted Operational Module
            </span>
            <h2 className="text-base font-bold text-[#182026]">
              Administrative Authorization Required
            </h2>
            <p className="text-xs text-[#5f6b7c] mt-2 leading-relaxed">
              Your account (<span className="font-mono text-[#182026]">{user?.email}</span>) possesses standard analyst privileges (<span className="font-mono font-bold text-[#0f5b6c]">USER</span>). The administrative operations console is strictly restricted to designated platform administrators.
            </p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => router.push("/user/dashboard")}
              >
                Return to Analyst Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa] flex flex-col font-sans">
      <Header />

      {/* Mobile Drawer Bar (below 768px) */}
      <div className="md:hidden flex items-center justify-between px-4 py-2 bg-[#f1f3f4] border-b border-[#e2e6e9] text-xs font-mono">
        <div className="flex items-center gap-1.5 text-[#0f5b6c] font-bold">
          <ShieldAlert className="h-3.5 w-3.5" />
          <span>Admin Console</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="flex items-center gap-1 text-[#0f5b6c] font-medium py-1 px-2 border border-[#cbd2d6] bg-white rounded-[3px] cursor-pointer"
          aria-expanded={mobileMenuOpen}
          aria-label="Toggle admin navigation menu"
        >
          {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          <span>{mobileMenuOpen ? "Close" : "Menu"}</span>
        </button>
      </div>

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Desktop Sidebar Navigation */}
        <div className="hidden md:block">
          <AdminNav />
        </div>

        {/* Mobile Navigation Drawer Modal */}
        {mobileMenuOpen && (
          <div
            className="md:hidden fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex"
            role="dialog"
            aria-modal="true"
            aria-label="Admin Navigation Menu"
          >
            <div className="w-64 bg-white h-full shadow-lg flex flex-col">
              <div className="p-3 border-b border-[#e2e6e9] flex items-center justify-between bg-[#f8f9fa]">
                <span className="text-xs font-mono font-bold text-[#0f5b6c]">Navigation</span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 text-[#5f6b7c] hover:text-[#182026] rounded-[2px] cursor-pointer"
                  aria-label="Close menu"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <AdminNav onNavigate={() => setMobileMenuOpen(false)} />
              </div>
            </div>
            <div
              className="flex-1 cursor-pointer"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Close navigation backdrop"
            />
          </div>
        )}

        {/* Main Administrative Content Canvas */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
}
