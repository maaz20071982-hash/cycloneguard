import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Unplug,
  Layers,
  HelpCircle,
} from "lucide-react";

export type SystemStatusType =
  | "Operational"
  | "Degraded"
  | "Unavailable"
  | "Not Connected"
  | "Not Deployed"
  | "Unknown";

interface SystemStatusProps {
  status: SystemStatusType | string;
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
  showIcon?: boolean;
}

export function SystemStatus({
  status,
  label,
  size = "md",
  className = "",
  showIcon = true,
}: SystemStatusProps) {
  const normalized = (status || "").toLowerCase().trim();

  let config = {
    canonical: "Unknown",
    textColor: "text-[#5f6b7c]",
    bgColor: "bg-[#f1f3f4]",
    borderColor: "border-[#e2e6e9]",
    iconColor: "text-[#5f6b7c]",
    icon: HelpCircle,
  };

  if (normalized.includes("operational") || normalized === "ok" || normalized === "connected" || normalized === "healthy") {
    config = {
      canonical: "Operational",
      textColor: "text-[#1b7a4f]",
      bgColor: "bg-[#f0fdf4]",
      borderColor: "border-[#bbf7d0]",
      iconColor: "text-[#1b7a4f]",
      icon: CheckCircle2,
    };
  } else if (normalized.includes("degraded") || normalized.includes("warning")) {
    config = {
      canonical: "Degraded",
      textColor: "text-[#b45309]",
      bgColor: "bg-[#fef8ee]",
      borderColor: "border-[#fed7aa]",
      iconColor: "text-[#b45309]",
      icon: AlertTriangle,
    };
  } else if (normalized.includes("unavailable") || normalized.includes("critical") || normalized.includes("unhealthy") || normalized.includes("error")) {
    config = {
      canonical: "Unavailable",
      textColor: "text-[#b91c1c]",
      bgColor: "bg-[#fef2f2]",
      borderColor: "border-[#fecaca]",
      iconColor: "text-[#b91c1c]",
      icon: XCircle,
    };
  } else if (normalized.includes("not connected") || normalized.includes("disconnected") || normalized.includes("pending")) {
    config = {
      canonical: "Not Connected",
      textColor: "text-[#5f6b7c]",
      bgColor: "bg-[#f1f3f4]",
      borderColor: "border-[#cbd2d6]",
      iconColor: "text-[#5f6b7c]",
      icon: Unplug,
    };
  } else if (normalized.includes("not deployed") || normalized.includes("uninitialized")) {
    config = {
      canonical: "Not Deployed",
      textColor: "text-[#1f5f7c]",
      bgColor: "bg-[#edf5f7]",
      borderColor: "border-[#b9e1e8]",
      iconColor: "text-[#0f5b6c]",
      icon: Layers,
    };
  }

  const IconComponent = config.icon;

  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5 gap-1",
    md: "text-xs px-2 py-0.5 gap-1.5",
    lg: "text-xs sm:text-sm px-2.5 py-1 gap-2",
  };

  const iconSizes = {
    sm: "h-3 w-3",
    md: "h-3.5 w-3.5",
    lg: "h-4 w-4",
  };

  const displayText = label || config.canonical;

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-[3px] border ${config.bgColor} ${config.borderColor} ${config.textColor} ${sizeClasses[size]} ${className}`}
      role="status"
      aria-label={`System status: ${displayText}`}
    >
      {showIcon && (
        <IconComponent className={`${iconSizes[size]} ${config.iconColor} shrink-0`} aria-hidden="true" />
      )}
      <span className="truncate">{displayText}</span>
    </span>
  );
}
