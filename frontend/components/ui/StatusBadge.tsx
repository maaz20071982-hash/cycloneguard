import React from "react";
import { cn } from "@/lib/utils";

export type SystemStatusType =
  | "operational"
  | "standby"
  | "warning"
  | "critical"
  | "disconnected"
  | "awaiting"
  | "Operational"
  | "Standby"
  | "Warning"
  | "Critical"
  | "Disconnected"
  | "Awaiting";

export interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: SystemStatusType;
  label?: string;
  text?: string;
  pulse?: boolean;
}

export function StatusBadge({ status, label, text, pulse = false, className, ...props }: StatusBadgeProps) {
  const configs: Record<string, { bg: string; text: string; border: string; dot: string; defaultLabel: string }> = {
    operational: {
      bg: "bg-emerald-950/60",
      text: "text-emerald-300",
      border: "border-emerald-500/30",
      dot: "bg-emerald-400 shadow-sm shadow-emerald-400/50",
      defaultLabel: "Operational",
    },
    standby: {
      bg: "bg-cyan-950/60",
      text: "text-cyan-300",
      border: "border-cyan-500/30",
      dot: "bg-cyan-400 shadow-sm shadow-cyan-400/50",
      defaultLabel: "Standby",
    },
    warning: {
      bg: "bg-amber-950/60",
      text: "text-amber-300",
      border: "border-amber-500/30",
      dot: "bg-amber-400 shadow-sm shadow-amber-400/50",
      defaultLabel: "Warning",
    },
    critical: {
      bg: "bg-rose-950/60",
      text: "text-rose-300",
      border: "border-rose-500/30",
      dot: "bg-rose-400 shadow-sm shadow-rose-400/50",
      defaultLabel: "Critical",
    },
    disconnected: {
      bg: "bg-slate-800/60",
      text: "text-slate-400",
      border: "border-slate-700/60",
      dot: "bg-slate-500",
      defaultLabel: "Disconnected",
    },
    awaiting: {
      bg: "bg-amber-950/40",
      text: "text-amber-400",
      border: "border-amber-500/30",
      dot: "bg-amber-500",
      defaultLabel: "Awaiting Data",
    },
  };

  const normalizedKey = (status?.toLowerCase() || "disconnected") as "operational" | "standby" | "warning" | "critical" | "disconnected" | "awaiting";
  const config = configs[normalizedKey] || configs.disconnected;
  const displayLabel = label || text || config.defaultLabel;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-sans font-medium border select-none backdrop-blur-xs",
        config.bg,
        config.text,
        config.border,
        className
      )}
      {...props}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full shrink-0",
          config.dot,
          pulse && "animate-pulse"
        )}
      />
      <span>{displayLabel}</span>
    </span>
  );
}
