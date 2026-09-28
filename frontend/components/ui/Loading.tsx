import React from "react";
import { cn } from "@/lib/utils";

export function LoadingSpinner({ size = "md", className }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const sizes = {
    sm: "h-3.5 w-3.5 border-2",
    md: "h-5 w-5 border-2",
    lg: "h-8 w-8 border-2",
  };

  return (
    <div
      className={cn(
        "animate-spin rounded-full border-[#0f5b6c] border-t-transparent",
        sizes[size],
        className
      )}
      role="status"
      aria-label="Loading"
    />
  );
}

export function SkeletonLoader({ className, count = 1 }: { className?: string; count?: number }) {
  return (
    <div className="space-y-2 w-full">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn("h-4 w-full animate-pulse rounded-[2px] bg-[#eaedef]", className)}
        />
      ))}
    </div>
  );
}

export function PageLoading({ text = "Loading platform data..." }: { text?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center space-y-3">
      <LoadingSpinner size="md" />
      <p className="text-xs uppercase tracking-wider text-[#5a6872] font-mono">{text}</p>
    </div>
  );
}

export function AIProcessingState({
  title = "ANALYZING CYCLONE",
  subtitle = "Processing multi-source satellite observations...",
  progress,
}: {
  title?: string;
  subtitle?: string;
  progress?: number;
}) {
  return (
    <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-6 max-w-md mx-auto text-center space-y-3 shadow-sm">
      <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-[#edf5f7] text-[#0f5b6c] mb-1">
        <LoadingSpinner size="sm" />
      </div>
      <h4 className="text-xs font-semibold tracking-wider uppercase text-[#182026] font-mono">{title}</h4>
      <p className="text-xs text-[#5a6872] leading-relaxed">{subtitle}</p>
      {progress !== undefined ? (
        <div className="w-full bg-[#f1f3f4] h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-[#0f5b6c] h-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      ) : (
        <div className="w-full bg-[#f1f3f4] h-1 rounded-full overflow-hidden">
          <div className="bg-[#0f5b6c] h-full w-1/3 animate-pulse" />
        </div>
      )}
    </div>
  );
}

export const LoadingState = AIProcessingState;
