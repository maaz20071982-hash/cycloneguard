import React from "react";
import { cn } from "@/lib/utils";

export interface PanelProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  variant?: "default" | "muted" | "bordered";
}

export function Panel({
  className,
  title,
  subtitle,
  action,
  variant = "default",
  children,
  ...props
}: PanelProps) {
  const variants = {
    default: "bg-[#0e1726]/80 backdrop-blur-md border border-slate-800/80 shadow-md",
    muted: "bg-[#111c2e]/70 backdrop-blur-md border border-slate-800/80 shadow-sm",
    bordered: "bg-slate-900/40 backdrop-blur-xs border border-slate-800",
  };

  return (
    <div
      className={cn(
        "rounded-xl overflow-hidden transition-all duration-200",
        variants[variant],
        className
      )}
      {...props}
    >
      {title ? (
        <>
          <PanelHeader title={title} subtitle={subtitle} action={action} />
          <div className="p-4 sm:p-5">{children}</div>
        </>
      ) : (
        children
      )}
    </div>
  );
}

export function PanelHeader({
  title,
  subtitle,
  action,
  className = "",
}: {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 px-4 sm:px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/50",
        className
      )}
    >
      <div>
        <div className="text-sm font-semibold tracking-tight text-white font-sans">
          {title}
        </div>
        {subtitle && (
          <div className="text-xs text-slate-400 mt-0.5 font-normal font-sans">
            {subtitle}
          </div>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

export function PanelContent({
  className = "",
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("p-4 sm:p-5", className)} {...props}>
      {children}
    </div>
  );
}
