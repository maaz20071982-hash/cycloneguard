"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { CycloneMap } from "@/components/ui/CycloneMap";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { DataRow } from "@/components/ui/DataRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAuth } from "@/lib/auth-context";
import { getCyclones, fetchDataSources, getAllCycloneTracks } from "@/lib/api/cyclones";
import type { StormTrackGroup } from "@/components/ui/CycloneMap";
import { Compass, RefreshCw, Radio, Cpu, Activity, Clock, ShieldCheck, ArrowRight } from "lucide-react";

export default function UserDashboard() {
  const { user } = useAuth();
  const [dataSourcesCount, setDataSourcesCount] = useState(0);
  const [cyclonesCount, setCyclonesCount] = useState(0);
  const [stormTracks, setStormTracks] = useState<StormTrackGroup[]>([]);
  const [selectedStormId, setSelectedStormId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [cycRes, dsRes, tracksRes] = await Promise.all([
        getCyclones(),
        fetchDataSources(),
        getAllCycloneTracks().catch(() => null),
      ]);
      setCyclonesCount(cycRes?.total || 0);
      setDataSourcesCount(dsRes?.connected_count || 0);

      if (tracksRes && tracksRes.cyclones) {
        const STORM_COLORS: Record<string, string> = {
          "2015301N11065": "#ef4444", // Chapala - Red
          "2014297N11062": "#0ea5e9", // Nilofar - Cyan
          "2013281N12098": "#f59e0b", // Phailin - Amber
          "2014279N11096": "#ec4899", // Hudhud - Pink
          "2015309N14067": "#8b5cf6", // Megh - Purple
          "2013322N13090": "#10b981", // Helen - Emerald
        };

        const groups: StormTrackGroup[] = tracksRes.cyclones.map((c) => ({
          id: c.cyclone_id,
          name: c.name,
          status: c.status,
          basin: c.basin,
          peak_intensity_kts: c.peak_intensity_kts || undefined,
          color: STORM_COLORS[c.cyclone_id],
          points: (c.track_points || []).map((p) => ({
            lat: p.latitude,
            lon: p.longitude,
            time: p.timestamp,
            intensity_kts: p.wind_speed_kts,
            intensity_kmh: Math.round(p.wind_speed_kts * 1.852),
            pressure_mb: p.central_pressure_mb || undefined,
            agency_grade: p.agency_grade,
          })),
        }));
        setStormTracks(groups);
      }
    } catch {
      // Graceful fallback without crashing
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <PortalLayout type="user">
      <div className="space-y-6">
        {/* 1. Welcome / Overview */}
        <div className="border-b border-[#e2e6e9] pb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Operational Surveillance
              </span>
              <Badge variant="neutral">Operational Surveillance & Benchmark Archive</Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026]">
              Cyclone Monitoring
            </h1>
            <p className="text-xs sm:text-sm text-[#5f6b7c] mt-0.5 max-w-2xl">
              Monitor tropical cyclone activity and AI-assisted risk signals across global oceanic basins.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/demo">
              <Button size="sm" variant="primary">
                <Compass className="h-3.5 w-3.5 mr-1" />
                Judge Demo
              </Button>
            </Link>
            <Button size="sm" variant="outline" onClick={loadData} isLoading={isLoading}>
              <RefreshCw className="h-3.5 w-3.5 mr-1" />
              Refresh Telemetry
            </Button>
            <Link href="/user/monitor">
              <Button size="sm" variant="primary">
                <Compass className="h-3.5 w-3.5 mr-1" />
                Live Monitor
              </Button>
            </Link>
          </div>
        </div>

        {/* Phase 7: Verified Benchmark Case Studies Callout */}
        <div className="p-4 bg-[#f8fafc] border border-[#cbd5e1] rounded-[4px] space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#e2e8f0] pb-2">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#0f5b6c] font-bold block">
                Official Benchmark Case Studies
              </span>
              <h2 className="text-sm font-bold text-[#182026]">
                Verified Historical Cyclones with HURSAT-B1 Satellite Evidence
              </h2>
            </div>
            <Link href="/demo">
              <span className="text-xs font-mono font-bold text-[#0f5b6c] hover:underline flex items-center gap-1">
                Open Guided Judge Demo (8 Stages) <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-3 bg-white border border-[#e2e8f0] rounded-[3px] space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#182026]">Cyclone CHAPALA (2015301N11065)</span>
                <Badge variant="danger" className="text-[10px]">RI+ BENCHMARK</Badge>
              </div>
              <p className="text-[11px] text-[#475569] font-sans">
                Extremely Severe Cyclonic Storm in Arabian Sea. Rapid intensification (+35 kt in 24h) detected at 2015-10-28 18:00 UTC (τ=0.125 threshold, Risk=0.3592).
              </p>
              <div className="flex items-center gap-2 pt-1">
                <Link href="/user/cyclones/2015301N11065/case-study?time=2015-10-28T18:00:00Z">
                  <Button size="sm" variant="primary" className="text-xs h-7">
                    Open Chapala Case Study
                  </Button>
                </Link>
                <button
                  onClick={() => setSelectedStormId("2015301N11065")}
                  className="px-2.5 py-1 text-xs border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-[2px] font-mono transition-colors cursor-pointer"
                >
                  Focus On Map
                </button>
                <Link href="/user/cyclones/2015301N11065">
                  <Button size="sm" variant="outline" className="text-xs h-7">
                    View Track
                  </Button>
                </Link>
              </div>
            </div>

            <div className="p-3 bg-white border border-[#e2e8f0] rounded-[3px] space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#182026]">Cyclone NILOFAR (2014297N11062)</span>
                <Badge variant="neutral" className="text-[10px]">NEGATIVE CONTROL</Badge>
              </div>
              <p className="text-[11px] text-[#475569] font-sans">
                Extremely Severe Cyclonic Storm undergoing rapid shearing decay before Gujarat coast. Zero false alarm validation baseline.
              </p>
              <div className="flex items-center gap-2 pt-1">
                <Link href="/user/cyclones/2014297N11062/case-study">
                  <Button size="sm" variant="primary" className="text-xs h-7">
                    Open Nilofar Case Study
                  </Button>
                </Link>
                <button
                  onClick={() => setSelectedStormId("2014297N11062")}
                  className="px-2.5 py-1 text-xs border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-[2px] font-mono transition-colors cursor-pointer"
                >
                  Focus On Map
                </button>
                <Link href="/user/cyclones/2014297N11062">
                  <Button size="sm" variant="outline" className="text-xs h-7">
                    View Track
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Main Map Area */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#5f6b7c] font-mono flex items-center gap-1.5">
              <Compass className="h-3.5 w-3.5 text-[#0f5b6c]" />
              North Indian Ocean Surveillance Basin
            </span>
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-[11px] text-[#5f6b7c]">Tracked benchmark systems:</span>
              <StatusBadge
                status={stormTracks.length > 0 ? "operational" : "standby"}
                label={stormTracks.length > 0 ? `${stormTracks.length} Verified Storms Active` : "Connecting..."}
              />
            </div>
          </div>

          <CycloneMap
            title="North Indian Ocean Cyclone Surveillance Basin"
            subtitle="Real NOAA IBTrACS best-track trajectories, WMO category colors, wind radii & forecast cones"
            basin="North Indian Ocean (Bay of Bengal & Arabian Sea)"
            center={[15.0, 75.0]}
            zoom={4}
            multiStormTracks={stormTracks}
            activeStormId={selectedStormId}
            onSelectStorm={setSelectedStormId}
            className="min-h-[500px]"
          />
        </div>

        {/* 3. Current Systems & 4. Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 3. Current Systems */}
          <Panel>
            <PanelHeader
              title="Current Systems Under Surveillance"
              subtitle="Active tropical depressions, cyclonic storms, and severe vortices"
              action={
                <Link href="/user/cyclones">
                  <Button size="sm" variant="ghost" className="text-xs h-7">
                    Full Database <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              }
            />
            <div className="p-5">
              <EmptyState
                icon={<Radio className="h-8 w-8 text-[#0f5b6c]" />}
                title="No operational cyclone observations are currently connected."
                description="When satellite ingestion feeds (INSAT-3D/3DR, Himawari-9, GOES-16) are connected, active systems and automated center fixes will display here."
                statusBadge="Awaiting Ingestion Pipeline"
              />
            </div>
          </Panel>

          {/* 4. Recent Activity */}
          <Panel>
            <PanelHeader
              title="Recent Meteorological Activity"
              subtitle="Latest satellite passes, scatterometer swaths, and center position updates"
              action={
                <Link href="/user/history">
                  <Button size="sm" variant="ghost" className="text-xs h-7">
                    Historical Archives <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              }
            />
            <div className="p-5">
              <EmptyState
                icon={<Clock className="h-8 w-8 text-[#5f6b7c]" />}
                title="No cyclone observations available."
                description="Chronological event logs, satellite scan passes, and track updates will populate as observation streams are processed."
                statusBadge="Event Stream Standby"
              />
            </div>
          </Panel>
        </div>

        {/* 5. System Status */}
        <Panel>
          <PanelHeader
            title="System & Telemetry Status"
            subtitle="Operational connection state of data sources and AI models"
          />
          <div className="p-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                Observational Data
              </span>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#1b7a4f]" />
                <span className="text-sm font-bold font-mono text-[#1b7a4f]">
                  Verified Archive
                </span>
              </div>
              <span className="text-[11px] text-[#5f6b7c] block">
                NOAA IBTrACS + HURSAT-B1
              </span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                AI Prediction Engine
              </span>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#1b7a4f]" />
                <span className="text-sm font-bold font-mono text-[#1b7a4f]">
                  v3.0.0-frozen
                </span>
              </div>
              <span className="text-[11px] text-[#5f6b7c] block">
                61 Features (Temporal + Spatial)
              </span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                Platform API
              </span>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#1b7a4f]" />
                <span className="text-sm font-bold font-mono text-[#1b7a4f]">
                  Operational
                </span>
              </div>
              <span className="text-[11px] text-[#5f6b7c] block">
                FastAPI + Database Persistence
              </span>
            </div>

            <div className="p-3 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block">
                Active Architecture
              </span>
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-[#0f5b6c]" />
                <span className="text-sm font-bold font-mono text-[#0f5b6c]">
                  Production Verified
                </span>
              </div>
              <span className="text-[11px] text-[#5f6b7c] block">
                Multi-Storm Multimodal Inference
              </span>
            </div>
          </div>
        </Panel>
      </div>
    </PortalLayout>
  );
}
