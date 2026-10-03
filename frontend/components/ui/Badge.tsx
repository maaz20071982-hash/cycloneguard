import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "brand" | "default" | "secondary" | "success" | "warning" | "danger" | "neutral" | "outline" | "cyan";
  shape?: "square" | "pill";
}

export function Badge({ className, variant = "default", shape = "pill", ...props }: BadgeProps) {
  const variants = {
    brand: "bg-cyan-950/70 text-cyan-300 border border-cyan-500/30",
    cyan: "bg-cyan-950/70 text-cyan-300 border border-cyan-500/30",
    default: "bg-cyan-950/70 text-cyan-300 border border-cyan-500/30",
    secondary: "bg-slate-800/80 text-slate-300 border border-slate-700/70",
    success: "bg-emerald-950/70 text-emerald-300 border border-emerald-500/30",
    warning: "bg-amber-950/70 text-amber-300 border border-amber-500/30",
    danger: "bg-rose-950/70 text-rose-300 border border-rose-500/30",
    neutral: "bg-slate-800/60 text-slate-300 border border-slate-700/50",
    outline: "bg-transparent text-slate-300 border border-slate-700",
  };

  const shapes = {
    square: "rounded-md",
    pill: "rounded-full",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 text-[11px] font-medium tracking-normal font-sans select-none shadow-xs",
        variants[variant],
        shapes[shape],
        className
      )}
      {...props}
    />
  );
}
