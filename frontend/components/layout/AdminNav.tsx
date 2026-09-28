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
  LogOut,
  Shield,
  Activity,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Badge } from "@/components/ui/Badge";

interface AdminNavProps {
  onNavigate?: () => void;
}

export function AdminNav({ onNavigate }: AdminNavProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const operationsLinks = [
    { label: "Dashboard", href: "/admin/dashboard", icon: <LayoutDashboard className="h-3.5 w-3.5" /> },
    { label: "Data Sources", href: "/admin/data", icon: <Database className="h-3.5 w-3.5" /> },
    { label: "Models", href: "/admin/models", icon: <Cpu className="h-3.5 w-3.5" /> },
    { label: "Predictions", href: "/admin/predictions", icon: <TrendingUp className="h-3.5 w-3.5" /> },
    { label: "Alerts", href: "/admin/alerts", icon: <AlertTriangle className="h-3.5 w-3.5" /> },
  ];

  const managementLinks = [
    { label: "Users", href: "/admin/users", icon: <Users className="h-3.5 w-3.5" /> },
  ];

  const systemLinks = [
    { label: "System", href: "/admin/system", icon: <Server className="h-3.5 w-3.5" /> },
  ];

  const renderNavGroup = (title: string, links: typeof operationsLinks) => (
    <div className="space-y-1">
      <div className="text-[10px] font-mono uppercase tracking-widest text-[#5f6b7c] px-2.5 py-1 font-semibold">
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
            className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-[3px] transition-colors text-xs font-mono ${
              isActive
                ? "bg-[#0f5b6c] text-white font-semibold shadow-xs"
                : "text-[#5f6b7c] hover:text-[#182026] hover:bg-[#eaedef]"
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
    <aside className="w-56 border-r border-[#e2e6e9] bg-[#f8f9fa] flex flex-col justify-between shrink-0 h-full min-h-[calc(100vh-3.5rem)] text-xs font-mono">
      <div className="p-4 space-y-5">
        {/* CycloneGuard Branding & Role Indicator */}
        <div className="pb-3 border-b border-[#e2e6e9]">
          <div className="flex items-center justify-between gap-1 mb-1">
            <div className="flex items-center gap-1.5 text-[#0f5b6c] font-bold text-xs uppercase tracking-wider">
              <Shield className="h-4 w-4" />
              CycloneGuard
            </div>
            <Badge variant="danger" className="text-[9px] px-1 py-0">ADMIN</Badge>
          </div>
          <div className="text-[10px] uppercase tracking-widest text-[#5f6b7c]">
            Operations Console
          </div>
        </div>

        {/* Navigation Sections */}
        <nav className="space-y-4" aria-label="Admin Navigation">
          {renderNavGroup("OPERATIONS", operationsLinks)}
          {renderNavGroup("MANAGEMENT", managementLinks)}
          {renderNavGroup("SYSTEM", systemLinks)}
        </nav>
      </div>

      {/* Admin Session Identity & Sign Out */}
      <div className="p-4 border-t border-[#e2e6e9] space-y-2 bg-[#ffffff]">
        <div className="text-[11px] truncate">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-[#182026] block truncate">
              {user?.name || "Admin Officer"}
            </span>
            <span className="h-1.5 w-1.5 rounded-full bg-[#1b7a4f]" title="Active Session" />
          </div>
          <span className="text-[10px] text-[#5f6b7c] block truncate">{user?.email}</span>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-1.5 text-[11px] text-[#b91c1c] hover:underline pt-1 cursor-pointer font-mono font-medium"
        >
          <LogOut className="h-3 w-3" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
