"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/Header";
import { AdminNav } from "@/components/layout/AdminNav";
import { ShieldAlert, Menu, X } from "lucide-react";

interface AdminLayoutProps {
  children: React.ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#080d16] flex flex-col font-sans text-slate-100">
      <Header />

      {/* Mobile Drawer Bar (below 768px) */}
      <div className="md:hidden flex items-center justify-between px-4 py-2 bg-slate-900/90 border-b border-slate-800 text-xs font-sans">
        <div className="flex items-center gap-2 text-rose-400 font-bold">
          <ShieldAlert className="h-4 w-4" />
          <span>Admin Console</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="flex items-center gap-1.5 text-slate-300 hover:text-white font-medium py-1 px-2.5 border border-slate-700 bg-slate-800 rounded-lg cursor-pointer text-xs"
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
            className="md:hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex"
            role="dialog"
            aria-modal="true"
            aria-label="Admin Navigation Menu"
          >
            <div className="w-64 bg-[#080d16] border-r border-slate-800 h-full shadow-2xl flex flex-col">
              <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
                <span className="text-xs font-sans font-bold text-white">Admin Navigation</span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 text-slate-400 hover:text-white rounded-lg cursor-pointer"
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
