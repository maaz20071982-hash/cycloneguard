import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "brand" | "default" | "secondary" | "success" | "warning" | "danger" | "neutral" | "outline";
  shape?: "square" | "pill";
}

export function Badge({ className, variant = "default", shape = "square", ...props }: BadgeProps) {
  const variants = {
    brand: "bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2]",
    default: "bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2]",
    secondary: "bg-[#f1f3f4] text-[#5a6872] border border-[#e2e6e9]",
    success: "bg-[#f0fdf4] text-[#1b7a4f] border border-[#bbf7d0]",
    warning: "bg-[#fef8ee] text-[#b45309] border border-[#fbd38d]",
    danger: "bg-[#fef2f2] text-[#b91c1c] border border-[#fecaca]",
    neutral: "bg-[#f8f9fa] text-[#5a6872] border border-[#e2e6e9]",
    outline: "bg-transparent text-[#5a6872] border border-[#cbd2d6]",
  };

  const shapes = {
    square: "rounded-[2px]",
    pill: "rounded-full",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 text-[10px] font-medium tracking-wide uppercase font-mono select-none",
        variants[variant],
        shapes[shape],
        className
      )}
      {...props}
    />
  );
}
