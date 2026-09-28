"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Satellite, History, User as UserIcon, LogOut, Shield } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Badge } from "@/components/ui/Badge";

export function UserNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const userLinks = [
    { label: "Dashboard", href: "/user/dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: "Cyclone Monitor", href: "/user/cyclones", icon: <Satellite className="h-4 w-4" /> },
    { label: "History", href: "/user/history", icon: <History className="h-4 w-4" /> },
    { label: "Profile", href: "/user/profile", icon: <UserIcon className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0a0f1d] flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        {/* User Identity Box */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-white truncate">{user?.name || "Meteorological Analyst"}</span>
            <Badge variant="default" className="text-[9px] py-0 px-1">USER</Badge>
          </div>
          <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
        </div>

        {/* Navigation Section */}
        <div>
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 px-3 block mb-2">
            User Portal
          </span>
          <nav className="space-y-1">
            {userLinks.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/user/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
                  }`}
                >
                  {item.icon}
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Session Logout */}
      <div className="p-4 border-t border-slate-800/80">
        <button
          onClick={logout}
          className="flex w-full items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 rounded-md transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
