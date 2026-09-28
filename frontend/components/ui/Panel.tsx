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
    default: "bg-white border border-[#e2e6e9]",
    muted: "bg-[#f1f3f4] border border-[#e2e6e9]",
    bordered: "bg-transparent border border-[#cbd2d6]",
  };

  return (
    <div
      className={cn(
        "rounded-[4px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden",
        variants[variant],
        className
      )}
      {...props}
    >
      {title ? (
        <>
          <PanelHeader title={title} subtitle={subtitle} action={action} />
          <div className="p-4">{children}</div>
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
        "flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 px-4 py-3 border-b border-[#e2e6e9] bg-[#f8f9fa]",
        className
      )}
    >
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-[#182026] font-mono">
          {title}
        </div>
        {subtitle && (
          <div className="text-[11px] text-[#5f6b7c] mt-0.5 font-normal">
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
    <div className={cn("p-4", className)} {...props}>
      {children}
    </div>
  );
}
