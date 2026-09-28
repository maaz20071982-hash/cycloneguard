import React from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Satellite } from "lucide-react";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  statusBadge?: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  statusBadge,
  actionText,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[4px] border border-dashed border-[#cbd2d6] bg-white p-8 text-center",
        className
      )}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-[4px] bg-[#f1f3f4] text-[#5a6872] mb-3 border border-[#e2e6e9]">
        {icon || <Satellite className="h-5 w-5" />}
      </div>

      {statusBadge && (
        <Badge variant="neutral" className="mb-2">
          {statusBadge}
        </Badge>
      )}

      <h3 className="text-xs font-semibold uppercase tracking-wider text-[#182026] font-mono">{title}</h3>
      <p className="mt-1.5 max-w-sm text-xs leading-relaxed text-[#5a6872]">{description}</p>

      {actionText && onAction && (
        <div className="mt-4">
          <Button variant="outline" size="sm" onClick={onAction}>
            {actionText}
          </Button>
        </div>
      )}
    </div>
  );
}
