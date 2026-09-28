import React from "react";
import { cn } from "@/lib/utils";

export interface DataRowProps {
  label: string;
  value: React.ReactNode;
  detail?: string;
  className?: string;
}

export function DataRow({ label, value, detail, className }: DataRowProps) {
  return (
    <div className={cn("flex items-center justify-between py-2 border-b border-[#edf0f2] text-xs font-mono", className)}>
      <span className="text-[#5a6872]">{label}</span>
      <div className="flex items-center gap-2 text-right">
        <span className="font-semibold text-[#182026]">{value}</span>
        {detail && <span className="text-[10px] text-[#7d8c97]">({detail})</span>}
      </div>
    </div>
  );
}
