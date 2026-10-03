"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Layers,
  Eye,
  Wind,
  MapPin,
  AlertTriangle,
  Shield,
  ChevronRight,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";

export interface JudgeStep {
  id: string;
  name: string;
  href: string;
  badge: string;
  icon: React.ReactNode;
}

export const JUDGE_STEPS: JudgeStep[] = [
  {
    id: "dashboard",
    name: "Dashboard",
    href: "/",
    badge: "Basin Overview",
    icon: <LayoutDashboard className="h-4 w-4" />,
  },
  {
    id: "fusion",
    name: "Data Fusion",
    href: "/fusion",
    badge: "61 Features",
    icon: <Layers className="h-4 w-4" />,
  },
  {
    id: "analysis",
    name: "AI Analysis",
    href: "/analysis",
    badge: "Vortex & RI",
    icon: <Eye className="h-4 w-4" />,
  },
  {
    id: "prediction",
    name: "Prediction",
    href: "/prediction",
    badge: "Track & Cone",
    icon: <Wind className="h-4 w-4" />,
  },
  {
    id: "risk",
    name: "Risk & Impact",
    href: "/risk",
    badge: "GIS Exposure",
    icon: <MapPin className="h-4 w-4" />,
  },
  {
    id: "alerts",
    name: "Alerts",
    href: "/alerts",
    badge: "Directives",
    icon: <AlertTriangle className="h-4 w-4" />,
  },
  {
    id: "review",
    name: "Authority Review",
    href: "/review",
    badge: "Official Sign-Off",
    icon: <Shield className="h-4 w-4" />,
  },
];

export function JudgeFlowNav({
  currentPath,
  className = "",
}: {
  currentPath?: string;
  className?: string;
}) {
  const pathname = usePathname();
  const activePath = currentPath || pathname;

  const activeIndex = JUDGE_STEPS.findIndex(
    (s) => s.href === activePath || (s.href !== "/" && activePath.startsWith(s.href))
  );

  const prevStep = activeIndex > 0 ? JUDGE_STEPS[activeIndex - 1] : null;
  const nextStep = activeIndex >= 0 && activeIndex < JUDGE_STEPS.length - 1 ? JUDGE_STEPS[activeIndex + 1] : null;

  return (
    <div className={`rounded-xl border border-slate-800/80 bg-[#0e1726]/80 backdrop-blur-md shadow-lg overflow-hidden ${className}`}>
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-2.5 bg-slate-900/60 border-b border-slate-800/80 gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-sans font-bold text-cyan-400">
            Judge Decision Workflow
          </span>
          <span className="text-slate-600">•</span>
          <span className="text-xs font-sans text-slate-300">
            Stage {activeIndex >= 0 ? activeIndex + 1 : 1} of 7: <span className="text-white font-medium">{JUDGE_STEPS[activeIndex >= 0 ? activeIndex : 0].name}</span>
          </span>
        </div>

        {/* Step Navigation Controls */}
        <div className="flex items-center gap-2 text-xs font-sans">
          {prevStep ? (
            <Link
              href={prevStep.href}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-700/60 rounded-lg border border-slate-700/60 transition-all"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back: {prevStep.name}</span>
            </Link>
          ) : (
            <span className="text-xs text-slate-500 px-2 py-1">Start of Flow</span>
          )}

          {nextStep ? (
            <Link
              href={nextStep.href}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-400 hover:to-blue-500 font-semibold rounded-lg shadow-sm shadow-cyan-950/40 transition-all"
            >
              <span>Next: {nextStep.name}</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          ) : (
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-400 hover:to-blue-500 font-semibold rounded-lg shadow-sm shadow-cyan-950/40 transition-all"
            >
              <span>Return to Dashboard</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* Stepper Pipeline Grid */}
      <div className="flex items-stretch overflow-x-auto divide-x divide-slate-800/70 text-xs font-sans scrollbar-none">
        {JUDGE_STEPS.map((step, idx) => {
          const isActive =
            step.href === activePath ||
            (step.href !== "/" && activePath.startsWith(step.href)) ||
            (activePath === "/user/dashboard" && step.href === "/");

          const isCompleted = activeIndex > idx;

          return (
            <Link
              key={step.id}
              href={step.href}
              className={`flex-1 min-w-[140px] p-3 flex flex-col justify-between transition-all group cursor-pointer ${
                isActive
                  ? "bg-gradient-to-b from-cyan-950/60 to-slate-900/90 text-white border-b-2 border-cyan-400 shadow-inner"
                  : isCompleted
                  ? "bg-slate-900/40 text-slate-300 hover:bg-slate-800/50 hover:text-white"
                  : "bg-transparent text-slate-400 hover:bg-slate-900/40 hover:text-slate-200"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`text-xs font-bold font-mono ${
                    isActive ? "text-cyan-400" : isCompleted ? "text-emerald-400" : "text-slate-500"
                  }`}
                >
                  {isCompleted ? "✓ 0" + (idx + 1) : "0" + (idx + 1)}
                </span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-sans font-medium ${
                    isActive
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                      : isCompleted
                      ? "bg-emerald-950/50 text-emerald-300 border border-emerald-800/40"
                      : "bg-slate-800/60 text-slate-400 border border-slate-700/50"
                  }`}
                >
                  {step.badge}
                </span>
              </div>

              <div className="flex items-center gap-2 font-semibold text-xs">
                <span className={isActive ? "text-cyan-400" : isCompleted ? "text-emerald-400" : "text-slate-500"}>
                  {step.icon}
                </span>
                <span className="truncate">{step.name}</span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
