import React from "react";
import { AdminDataSource } from "@/types";
import { SystemStatus } from "@/components/ui/SystemStatus";
import { Button } from "@/components/ui/Button";
import { Radio, Database, Activity, ExternalLink, Settings, Wrench } from "lucide-react";

interface DataSourceCardProps {
  source: AdminDataSource;
  onAction?: (actionName: string, source: AdminDataSource) => void;
}

export function DataSourceCard({ source, onAction }: DataSourceCardProps) {
  const handleAction = (actionName: string) => {
    if (onAction) {
      onAction(actionName, source);
    }
  };

  return (
    <div className="border border-[#e2e6e9] bg-[#ffffff] rounded-[3px] p-4 flex flex-col justify-between shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-[#cbd2d6] transition-colors">
      <div>
        {/* Header: Type tag and Status badge */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] bg-[#f8f9fa] border border-[#e2e6e9] px-1.5 py-0.5 rounded-[2px] truncate max-w-[180px]">
            {source.type}
          </span>
          <SystemStatus status={source.status} size="sm" />
        </div>

        {/* Source Name & Provider */}
        <h3 className="text-sm font-bold text-[#182026] flex items-center gap-1.5 leading-snug">
          <Radio className="h-4 w-4 text-[#0f5b6c] shrink-0" />
          <span className="truncate">{source.name}</span>
        </h3>
        <p className="text-xs text-[#5f6b7c] mt-0.5 line-clamp-1">
          {source.provider}
        </p>

        {/* Data Grid with truthful '—' for unavailable values */}
        <div className="mt-4 pt-3 border-t border-[#e2e6e9] grid grid-cols-2 gap-2 text-xs font-mono">
          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Coverage
            </span>
            <span className="text-[#182026] font-medium text-[11px] truncate block" title={source.data_coverage}>
              {source.data_coverage || "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Processed
            </span>
            <span className="text-[#182026] font-medium text-[11px]">
              {source.records_processed !== null && source.records_processed !== undefined
                ? source.records_processed.toLocaleString()
                : "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Last Update
            </span>
            <span className="text-[#5f6b7c] text-[11px]">
              {source.last_successful_update || "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Last Failure
            </span>
            <span className="text-[#5f6b7c] text-[11px]">
              {source.last_failure || "—"}
            </span>
          </div>
        </div>

        {/* Channels */}
        {source.channels && source.channels.length > 0 && (
          <div className="mt-3">
            <span className="text-[9px] font-mono text-[#5f6b7c] uppercase tracking-wider block mb-1">
              Observable Channels
            </span>
            <div className="flex flex-wrap gap-1">
              {source.channels.map((ch) => (
                <span
                  key={ch}
                  className="px-1.5 py-0.5 border border-[#e2e6e9] bg-[#f8f9fa] text-[10px] text-[#5f6b7c] font-mono rounded-[2px]"
                >
                  {ch}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-4 pt-3 border-t border-[#e2e6e9] flex items-center justify-end gap-2">
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-7 px-2.5"
          onClick={() => handleAction("View")}
        >
          View
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-7 px-2.5"
          onClick={() => handleAction("Configure")}
        >
          Configure
        </Button>
        <Button
          size="sm"
          variant="secondary"
          className="text-xs h-7 px-2.5"
          onClick={() => handleAction("Test Connection")}
        >
          Test Connection
        </Button>
      </div>
    </div>
  );
}
