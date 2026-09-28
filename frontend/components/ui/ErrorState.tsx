import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface ErrorStateProps {
  title?: string;
  message?: string;
  code?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "ANALYSIS UNAVAILABLE",
  message = "The requested cyclone observation or telemetry service could not be contacted.",
  code,
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[4px] border border-[#fecaca] bg-[#fef2f2] p-6 text-center text-[#182026]",
        className
      )}
    >
      <div className="flex h-9 w-9 items-center justify-center rounded-[4px] bg-white text-[#b91c1c] mb-2.5 border border-[#fecaca] shadow-xs">
        <AlertCircle className="h-5 w-5" />
      </div>

      <h4 className="text-xs font-semibold tracking-wider uppercase text-[#b91c1c] font-mono">{title}</h4>
      <p className="mt-1 max-w-sm text-xs text-[#5a6872] leading-relaxed">{message}</p>

      {code && (
        <span className="mt-2 text-[10px] font-mono text-[#b91c1c] bg-white px-2 py-0.5 rounded-[2px] border border-[#fecaca]">
          CODE: {code}
        </span>
      )}

      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-4 border-[#fecaca] text-[#b91c1c] hover:bg-white">
          <RefreshCw className="h-3 w-3 mr-1.5" />
          Try Again
        </Button>
      )}
    </div>
  );
}
