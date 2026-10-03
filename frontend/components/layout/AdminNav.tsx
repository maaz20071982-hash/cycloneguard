"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  Cpu,
  TrendingUp,
  AlertTriangle,
  Users,
  Server,
  Shield,
  Activity,
  ArrowLeft,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface AdminNavProps {
  onNavigate?: () => void;
}

export function AdminNav({ onNavigate }: AdminNavProps) {
  const pathname = usePathname();

  const operationsLinks = [
    { label: "Overview", href: "/admin/dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: "Data Sources", href: "/admin/data", icon: <Database className="h-4 w-4" /> },
    { label: "Neural Models", href: "/admin/models", icon: <Cpu className="h-4 w-4" /> },
    { label: "Predictions Log", href: "/admin/predictions", icon: <TrendingUp className="h-4 w-4" /> },
    { label: "Alert Dispatch", href: "/admin/alerts", icon: <AlertTriangle className="h-4 w-4" /> },
  ];

  const managementLinks = [
    { label: "Authorized Personnel", href: "/admin/users", icon: <Users className="h-4 w-4" /> },
  ];

  const systemLinks = [
    { label: "System Telemetry", href: "/admin/system", icon: <Server className="h-4 w-4" /> },
  ];

  const renderNavGroup = (title: string, links: typeof operationsLinks) => (
    <div className="space-y-1">
      <div className="text-[11px] font-sans uppercase tracking-wider text-slate-400 px-3 py-1 font-semibold">
        {title}
      </div>
      {links.map((item) => {
        const isActive =
          pathname === item.href ||
          (item.href !== "/admin/dashboard" && pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all text-xs font-sans ${
              isActive
                ? "bg-rose-950/60 text-rose-300 font-semibold border border-rose-800/60 shadow-xs"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </Link>
        );
      })}
    </div>
  );

  return (
    <aside className="w-60 border-r border-slate-800/80 bg-[#080d16] flex flex-col justify-between shrink-0 h-full min-h-[calc(100vh-4rem)] text-xs font-sans">
      <div className="p-4 space-y-5">
        {/* Brand & Role Header */}
        <div className="pb-3 border-b border-slate-800/80">
          <div className="flex items-center justify-between gap-1 mb-1">
            <div className="flex items-center gap-2 text-white font-bold text-xs tracking-tight">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-rose-600 text-white shadow-xs">
                <Shield className="h-3.5 w-3.5" />
              </div>
              <span>Admin Console</span>
            </div>
            <Badge variant="danger" className="text-[10px] px-2 py-0.5">OPS ROOT</Badge>
          </div>
          <div className="text-[11px] text-slate-400 font-sans mt-1">
            CycloneSense AI Governance
          </div>
        </div>

        {/* Navigation Sections */}
        <nav className="space-y-4" aria-label="Admin Navigation">
          {renderNavGroup("OPERATIONS", operationsLinks)}
          {renderNavGroup("MANAGEMENT", managementLinks)}
          {renderNavGroup("INFRASTRUCTURE", systemLinks)}
        </nav>
      </div>

      {/* Switch to User Portal Link at Bottom */}
      <div className="p-4 border-t border-slate-800/80 space-y-2 bg-[#0b121e]">
        <div className="text-xs text-slate-400">
          Operational Role: <span className="text-white font-semibold">Chief Forecaster</span>
        </div>
        <Link
          href="/user/dashboard"
          className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 pt-1 font-medium transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Switch to User Portal</span>
        </Link>
      </div>
    </aside>
  );
}
