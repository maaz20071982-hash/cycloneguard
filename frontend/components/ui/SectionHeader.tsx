import React from "react";
import { cn } from "@/lib/utils";

export interface SectionHeaderProps {
  title: string;
  badge?: React.ReactNode;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function SectionHeader({ title, badge, description, action, className }: SectionHeaderProps) {
  return (
    <div className={cn("flex flex-col sm:flex-row sm:items-end justify-between gap-3 pb-3 border-b border-[#e2e6e9]", className)}>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold tracking-tight text-[#182026]">{title}</h2>
          {badge}
        </div>
        {description && <p className="text-xs text-[#5a6872] leading-relaxed max-w-2xl">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
