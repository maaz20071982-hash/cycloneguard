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
      bg: "bg-[#f0fdf4]",
      text: "text-[#1b7a4f]",
      border: "border-[#bbf7d0]",
      dot: "bg-[#1b7a4f]",
      defaultLabel: "Operational",
    },
    standby: {
      bg: "bg-[#f0f6fa]",
      text: "text-[#1f5f7c]",
      border: "border-[#bae6fd]",
      dot: "bg-[#1f5f7c]",
      defaultLabel: "Standby",
    },
    warning: {
      bg: "bg-[#fef8ee]",
      text: "text-[#b45309]",
      border: "border-[#fbd38d]",
      dot: "bg-[#b45309]",
      defaultLabel: "Warning",
    },
    critical: {
      bg: "bg-[#fef2f2]",
      text: "text-[#b91c1c]",
      border: "border-[#fecaca]",
      dot: "bg-[#b91c1c]",
      defaultLabel: "Critical",
    },
    disconnected: {
      bg: "bg-[#f8f9fa]",
      text: "text-[#5a6872]",
      border: "border-[#e2e6e9]",
      dot: "bg-[#7d8c97]",
      defaultLabel: "Disconnected",
    },
    awaiting: {
      bg: "bg-[#fffbeb]",
      text: "text-[#92400e]",
      border: "border-[#fde68a]",
      dot: "bg-[#d97706]",
      defaultLabel: "Awaiting Data",
    },
  };

  const normalizedKey = (status?.toLowerCase() || "disconnected") as "operational" | "standby" | "warning" | "critical" | "disconnected" | "awaiting";
  const config = configs[normalizedKey] || configs.disconnected;
  const displayLabel = label || text || config.defaultLabel;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium border select-none",
        config.bg,
        config.text,
        config.border,
        className
      )}
      {...props}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          config.dot,
          pulse && "animate-pulse"
        )}
      />
      <span>{displayLabel}</span>
    </span>
  );
}
