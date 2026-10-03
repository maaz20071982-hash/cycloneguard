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
      container: "bg-sky-950/40 border-sky-500/30 text-sky-200",
      icon: <Info className="h-4 w-4 text-sky-400 mt-0.5 shrink-0" />,
      titleColor: "text-sky-300",
    },
    warning: {
      container: "bg-amber-950/40 border-amber-500/30 text-amber-200",
      icon: <AlertTriangle className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />,
      titleColor: "text-amber-300",
    },
    danger: {
      container: "bg-rose-950/40 border-rose-500/30 text-rose-200",
      icon: <AlertCircle className="h-4 w-4 text-rose-400 mt-0.5 shrink-0" />,
      titleColor: "text-rose-300",
    },
    success: {
      container: "bg-emerald-950/40 border-emerald-500/30 text-emerald-200",
      icon: <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />,
      titleColor: "text-emerald-300",
    },
  };

  const current = configs[variant] || configs.info;

  return (
    <div
      role="alert"
      className={cn(
        "relative w-full rounded-xl border p-4 text-xs sm:text-sm font-sans flex items-start gap-3 backdrop-blur-md shadow-sm",
        current.container,
        className
      )}
      {...props}
    >
      {current.icon}
      <div className="flex-1 min-w-0">
        {title && (
          <h5 className={cn("font-semibold text-xs sm:text-sm tracking-normal mb-1 font-sans", current.titleColor)}>
            {title}
          </h5>
        )}
        <div className="text-xs sm:text-sm leading-relaxed opacity-95 text-slate-300">{children}</div>
      </div>
    </div>
  );
}
