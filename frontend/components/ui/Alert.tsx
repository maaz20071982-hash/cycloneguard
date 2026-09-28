import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "warning" | "danger" | "success";
  title?: string;
}

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  const configs = {
    info: {
      container: "bg-[#f0f6fa] border-[#bae6fd] text-[#1f5f7c]",
      icon: <Info className="h-4 w-4 text-[#1f5f7c] mt-0.5 shrink-0" />,
      titleColor: "text-[#1f5f7c]",
    },
    warning: {
      container: "bg-[#fef8ee] border-[#fbd38d] text-[#92400e]",
      icon: <AlertTriangle className="h-4 w-4 text-[#b45309] mt-0.5 shrink-0" />,
      titleColor: "text-[#b45309]",
    },
    danger: {
      container: "bg-[#fef2f2] border-[#fecaca] text-[#991b1b]",
      icon: <AlertCircle className="h-4 w-4 text-[#b91c1c] mt-0.5 shrink-0" />,
      titleColor: "text-[#b91c1c]",
    },
    success: {
      container: "bg-[#f0fdf4] border-[#bbf7d0] text-[#166534]",
      icon: <CheckCircle2 className="h-4 w-4 text-[#1b7a4f] mt-0.5 shrink-0" />,
      titleColor: "text-[#1b7a4f]",
    },
  };

  const current = configs[variant] || configs.info;

  return (
    <div
      role="alert"
      className={cn(
        "relative w-full rounded-[4px] border p-3.5 text-xs flex items-start gap-3",
        current.container,
        className
      )}
      {...props}
    >
      {current.icon}
      <div className="flex-1 min-w-0">
        {title && (
          <h5 className={cn("font-semibold text-xs tracking-wider uppercase mb-0.5 font-mono", current.titleColor)}>
            {title}
          </h5>
        )}
        <div className="text-xs leading-relaxed opacity-95">{children}</div>
      </div>
    </div>
  );
}
