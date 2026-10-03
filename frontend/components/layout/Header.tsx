"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  Menu,
  X,
  LayoutDashboard,
  ShieldAlert,
  Compass,
  Layers,
  History,
  Info,
  ExternalLink,
  Activity,
  Flame,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: "Judge Demo (9 Stages)", href: "/demo", isSpecial: true },
    { label: "Overview", href: "/" },
    { label: "User Dashboard", href: "/user/dashboard" },
    { label: "Admin Console", href: "/admin/dashboard" },
    { label: "Basin Monitor", href: "/user/monitor" },
    { label: "History Archive", href: "/user/history" },
    { label: "About", href: "/about" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#080d16]/90 backdrop-blur-md">
      {/* Top Banner: Research & Demonstration Platform */}
      <div className="bg-cyan-950/40 border-b border-cyan-800/30 px-4 py-1.5 text-center flex flex-wrap items-center justify-center gap-2 text-xs">
        <span className="text-[11px] font-sans font-bold text-cyan-400">
          SIH 2026 (SIH26070) Prototype
        </span>
        <span className="text-slate-600 hidden sm:inline">•</span>
        <span className="text-xs font-sans text-slate-300">
          Multi-Source Cyclone Fusion & Disaster Decision Support · Official warnings require authorized human review
        </span>
        <span className="px-2 py-0.5 text-[10px] font-sans font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30 rounded-full">
          DEMO / SIMULATION
        </span>
      </div>

      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo & Editorial Title */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
            <Shield className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-tight text-white font-sans">
                CycloneSense <span className="text-cyan-400">AI</span>
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-sans font-semibold rounded-md bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 hidden sm:inline">
                SIH26070
              </span>
            </div>
            <span className="text-[11px] text-slate-400 font-sans hidden sm:inline">
              Meteorological Intelligence Observatory
            </span>
          </div>
        </Link>

        {/* Center Navigation Links */}
        <nav className="hidden lg:flex items-center space-x-1 text-sm font-sans">
          {navLinks.map((link) => {
            const isActive =
              link.href === "/"
                ? pathname === "/"
                : pathname === link.href || (pathname.startsWith(link.href) && link.href !== "/");

            if (link.isSpecial) {
              return (
                <Link
                  key={link.label}
                  href={link.href}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    pathname === "/demo"
                      ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/30"
                      : "bg-cyan-950/60 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-900/60 hover:text-white"
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  {link.label}
                </Link>
              );
            }

            return (
              <Link
                key={link.label}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-slate-800/80 text-cyan-400 border border-cyan-500/30 font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/50"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Dashboard Switcher: User Dashboard vs Admin Dashboard */}
        <div className="hidden sm:flex items-center gap-2 text-xs font-sans">
          <Link href="/user/dashboard">
            <Button
              size="sm"
              variant={pathname.startsWith("/user") ? "cyan" : "secondary"}
              className="text-xs h-8.5 px-3 rounded-lg"
            >
              <LayoutDashboard className="h-3.5 w-3.5 mr-1.5" />
              User Portal
            </Button>
          </Link>

          <Link href="/admin/dashboard">
            <Button
              size="sm"
              variant={pathname.startsWith("/admin") ? "danger" : "outline"}
              className={`text-xs h-8.5 px-3 rounded-lg ${
                pathname.startsWith("/admin")
                  ? ""
                  : "border-rose-900/50 text-rose-300 hover:bg-rose-950/40 hover:border-rose-700/60"
              }`}
            >
              <ShieldAlert className="h-3.5 w-3.5 mr-1.5" />
              Admin Console
            </Button>
          </Link>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex lg:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="text-slate-200 p-2 rounded-lg hover:bg-slate-800 border border-slate-700/80"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-slate-800 bg-[#0e1726] px-4 pt-3 pb-5 space-y-2 text-sm font-sans">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className={`block px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                pathname === link.href
                  ? "bg-slate-800 text-cyan-400 font-bold border border-cyan-500/30"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              }`}
            >
              {link.label}
            </Link>
          ))}

          <div className="pt-3 border-t border-slate-800 flex flex-col gap-2">
            <Link href="/user/dashboard" onClick={() => setMobileMenuOpen(false)}>
              <Button size="sm" variant="secondary" className="w-full justify-start text-xs h-9">
                <LayoutDashboard className="h-3.5 w-3.5 mr-2" />
                User Dashboard
              </Button>
            </Link>
            <Link href="/admin/dashboard" onClick={() => setMobileMenuOpen(false)}>
              <Button size="sm" variant="danger" className="w-full justify-start text-xs h-9">
                <ShieldAlert className="h-3.5 w-3.5 mr-2" />
                Admin Console
              </Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
