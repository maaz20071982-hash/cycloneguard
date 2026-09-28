"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface TabItem {
  id: string;
  label: string;
  count?: number | string;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  variant?: "underline" | "pill" | "segment" | "segmented";
}

export function Tabs({ tabs, activeTab, onChange, className, variant = "underline" }: TabsProps) {
  if (variant === "segment" || variant === "segmented") {
    return (
      <div className={cn("inline-flex p-1 bg-[#f1f3f4] rounded-[4px] border border-[#e2e6e9]", className)}>
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-[3px] transition-all cursor-pointer select-none",
                isActive
                  ? "bg-white text-[#0f5b6c] shadow-[0_1px_2px_rgba(24,32,38,0.08)] font-semibold"
                  : "text-[#5a6872] hover:text-[#182026]"
              )}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={cn("text-[10px] font-mono px-1 rounded", isActive ? "bg-[#edf5f7] text-[#0f5b6c]" : "bg-[#e2e6e9] text-[#5a6872]")}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className={cn("flex border-b border-[#e2e6e9] space-x-6", className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              "flex items-center gap-2 py-2.5 text-xs font-medium border-b-2 -mb-px transition-colors cursor-pointer select-none",
              isActive
                ? "border-[#0f5b6c] text-[#0f5b6c] font-semibold"
                : "border-transparent text-[#5a6872] hover:text-[#182026] hover:border-[#cbd2d6]"
            )}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className={cn("text-[10px] font-mono px-1.5 py-0.2 rounded", isActive ? "bg-[#edf5f7] text-[#0f5b6c]" : "bg-[#f1f3f4] text-[#5a6872]")}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
