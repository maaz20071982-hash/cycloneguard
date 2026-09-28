import React from "react";
import { AdminModel } from "@/types";
import { SystemStatus } from "@/components/ui/SystemStatus";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Cpu, Layers, GitBranch, Binary, ShieldCheck } from "lucide-react";

interface ModelStatusCardProps {
  model: AdminModel;
  onAction?: (actionName: string, model: AdminModel) => void;
}

export function ModelStatusCard({ model, onAction }: ModelStatusCardProps) {
  const handleAction = (actionName: string) => {
    if (onAction) {
      onAction(actionName, model);
    }
  };

  return (
    <div className="border border-[#e2e6e9] bg-[#ffffff] rounded-[3px] p-4 flex flex-col justify-between shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-[#cbd2d6] transition-colors">
      <div>
        {/* Header: Framework tag and Status badge */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-[10px] font-mono text-[#5f6b7c] bg-[#f8f9fa] border border-[#e2e6e9] px-1.5 py-0.5 rounded-[2px] truncate max-w-[190px]">
            {model.framework}
          </span>
          <SystemStatus status={model.status} size="sm" />
        </div>

        {/* Model Identifier and Version */}
        <div className="flex items-baseline justify-between gap-2">
          <h3 className="text-sm font-bold text-[#182026] flex items-center gap-1.5 truncate">
            <Cpu className="h-4 w-4 text-[#0f5b6c] shrink-0" />
            <span className="truncate">{model.model_name}</span>
          </h3>
          <span className="text-[10px] font-mono text-[#5f6b7c] shrink-0">
            {model.version}
          </span>
        </div>

        {/* Target Objective */}
        <p className="text-xs text-[#5f6b7c] mt-1 line-clamp-2 leading-relaxed">
          {model.target}
        </p>

        {/* Data Grid with truthful '—' for unavailable values */}
        <div className="mt-4 pt-3 border-t border-[#e2e6e9] grid grid-cols-2 gap-2 text-xs font-mono">
          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Training Set
            </span>
            <span className="text-[#182026] text-[11px] truncate block" title={model.dataset}>
              {model.dataset || "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Dataset Ver.
            </span>
            <span className="text-[#5f6b7c] text-[11px]">
              {model.dataset_version || "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Trained At
            </span>
            <span className="text-[#5f6b7c] text-[11px]">
              {model.trained_at || "—"}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[#5f6b7c] block uppercase tracking-wider">
              Metrics
            </span>
            <span className="text-[#5f6b7c] text-[11px]">
              {model.metrics ? JSON.stringify(model.metrics) : "—"}
            </span>
          </div>
        </div>

        {/* Deployment notice */}
        <div className="mt-3 p-2 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[2px] text-[11px] text-[#5f6b7c]">
          <span className="font-semibold text-[#182026] block mb-0.5">Deployment Registry</span>
          {model.deployed ? (
            <span className="text-[#1b7a4f] font-mono">Active in inference pipeline</span>
          ) : (
            <span className="text-[#5f6b7c] font-mono">Checkpoints uninitialized (No inference weights)</span>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-4 pt-3 border-t border-[#e2e6e9] flex items-center justify-end gap-2">
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-7 px-2.5"
          onClick={() => handleAction("View Architecture")}
        >
          Architecture
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-7 px-2.5"
          onClick={() => handleAction("Configure Weights")}
        >
          Configure
        </Button>
      </div>
    </div>
  );
}
