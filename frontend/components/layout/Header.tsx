"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Menu, X, LogIn, LayoutDashboard, ShieldAlert, LogOut, User, Compass } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { useAuth } from "@/lib/auth-context";

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, isAdmin, logout } = useAuth();

  const navLinks = [
    { label: "Judge Demo", href: "/demo", isSpecial: true },
    { label: "Monitor", href: "/user/monitor" },
    { label: "Cyclones", href: "/user/cyclones" },
    { label: "History", href: "/user/history" },
    { label: "About", href: "/about" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#e2e6e9] bg-white">
      {/* Top Banner: Research & Demonstration Platform */}
      <div className="bg-[#edf5f7] border-b border-[#bcdbe2] px-4 py-1 text-center">
        <p className="text-[11px] font-mono tracking-wider text-[#0f5b6c]">
          <span className="font-semibold uppercase">Research Prototype</span> — Verified historical meteorological surveillance · Official warnings remain authoritative
        </p>
      </div>

      <div className="max-w-7xl mx-auto flex h-14 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo & Editorial Title */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="flex h-7 w-7 items-center justify-center rounded-[3px] bg-[#0f5b6c] text-white">
            <Shield className="h-4 w-4" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold tracking-tight text-[#182026] uppercase font-mono">
              CycloneGuard
            </span>
            <span className="text-[10px] text-[#5f6b7c] font-mono uppercase tracking-wider hidden sm:inline">
              Meteorological Intelligence
            </span>
          </div>
        </Link>

        {/* Compact Top Navigation (User-facing) */}
        <nav className="hidden md:flex items-center space-x-6 text-xs font-mono uppercase tracking-wider">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || (link.href === "/user/monitor" && pathname === "/user/monitor");
            if (link.isSpecial) {
              return (
                <Link
                  key={link.label}
                  href={link.href}
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[3px] font-semibold transition-colors ${
                    pathname === "/demo"
                      ? "bg-[#0f5b6c] text-white"
                      : "bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] hover:bg-[#0f5b6c] hover:text-white"
                  }`}
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  {link.label}
                </Link>
              );
            }
            return (
              <Link
                key={link.label}
                href={link.href}
                className={`transition-colors py-1 ${
                  isActive
                    ? "text-[#0f5b6c] font-semibold border-b-2 border-[#0f5b6c] -mb-px"
                    : "text-[#5f6b7c] hover:text-[#182026]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Session Controls */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link href="/user/dashboard">
                <Button
                  size="sm"
                  variant={pathname === "/user/dashboard" ? "secondary" : "ghost"}
                  className="text-xs"
                >
                  <LayoutDashboard className="h-3.5 w-3.5 mr-1" />
                  Dashboard
                </Button>
              </Link>

              <Link href="/user/profile">
                <Button
                  size="sm"
                  variant={pathname === "/user/profile" ? "secondary" : "ghost"}
                  className="text-xs"
                >
                  <User className="h-3.5 w-3.5 mr-1" />
                  Profile
                </Button>
              </Link>

              {isAdmin && (
                <Link href="/admin/dashboard">
                  <Button size="sm" variant="outline" className="border-[#cbd2d6] text-[#b91c1c] hover:bg-[#fef2f2] text-xs">
                    <ShieldAlert className="h-3.5 w-3.5 mr-1 text-[#b91c1c]" />
                    Admin
                  </Button>
                </Link>
              )}

              <Button
                size="sm"
                variant="ghost"
                onClick={logout}
                className="text-[#5f6b7c] hover:text-[#b91c1c] text-xs"
                title="Sign out"
              >
                <LogOut className="h-3.5 w-3.5 mr-1" />
                Sign out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button size="sm" variant="ghost">
                  <LogIn className="h-3.5 w-3.5 mr-1" />
                  Sign In
                </Button>
              </Link>
              <Link href="/user/monitor">
                <Button size="sm" variant="primary">
                  Explore Monitor
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="text-[#182026] p-1.5 rounded-[3px] hover:bg-[#f1f3f4]"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-[#e2e6e9] bg-white px-4 pt-3 pb-5 space-y-2 text-xs font-mono">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className={`block uppercase tracking-wider py-1.5 ${
                link.isSpecial
                  ? "text-[#0f5b6c] font-bold flex items-center gap-1.5"
                  : "text-[#5f6b7c] hover:text-[#182026]"
              }`}
            >
              {link.isSpecial && <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />}
              {link.label}
            </Link>
          ))}
          <div className="pt-3 border-t border-[#e2e6e9] flex flex-col gap-2">
            {isAuthenticated ? (
              <>
                <Link href="/user/dashboard" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="secondary" className="w-full">
                    User Dashboard
                  </Button>
                </Link>
                <Link href="/user/profile" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="outline" className="w-full">
                    Analyst Profile
                  </Button>
                </Link>
                {isAdmin && (
                  <Link href="/admin/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <Button size="sm" variant="outline" className="w-full text-[#b91c1c]">
                      Admin Operations
                    </Button>
                  </Link>
                )}
                <Button size="sm" variant="ghost" onClick={logout} className="w-full text-[#b91c1c]">
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="outline" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="primary" className="w-full">
                    Create Account
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
