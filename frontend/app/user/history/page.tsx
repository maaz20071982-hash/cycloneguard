"use client";

import React, { useState, useEffect } from "react";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { EmptyState } from "@/components/ui/EmptyState";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { getHistoricalCyclones } from "@/lib/api/cyclones";
import { HistoricalCyclone } from "@/types";
import { History, Search, Filter, Calendar, Compass, RefreshCw, Database } from "lucide-react";

export default function HistoryPage() {
  const [historicalData, setHistoricalData] = useState<HistoricalCyclone[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBasin, setSelectedBasin] = useState("all");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedSeason, setSelectedSeason] = useState("all");
  const [selectedRiEvent, setSelectedRiEvent] = useState("all");
  const [selectedIntensity, setSelectedIntensity] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await getHistoricalCyclones();
      setHistoricalData(res.historical_cyclones || []);
    } catch {
      setHistoricalData([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResetFilters = () => {
    setSearchQuery("");
    setSelectedBasin("all");
    setSelectedCategory("all");
    setSelectedSeason("all");
    setSelectedRiEvent("all");
    setSelectedIntensity("all");
  };

  return (
    <PortalLayout type="user">
      <div className="space-y-6">
        {/* Breadcrumb */}
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/user/dashboard" },
            { label: "Historical Cyclone Analysis" },
          ]}
        />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Reanalysis Database
              </span>
              <StatusBadge status="disconnected" text="Archive Standby" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
              <History className="h-6 w-6 text-[#0f5b6c]" />
              Historical Cyclone Analysis
            </h1>
            <p className="text-xs text-[#5f6b7c] mt-0.5">
              Multi-decade tropical cyclone benchmark archives (IBTrACS, IMD Best Track, JTWC, and NHC Hurdat2).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={loadData} isLoading={isLoading}>
              <RefreshCw className="h-3.5 w-3.5 mr-1" />
              Check Archive State
            </Button>
          </div>
        </div>

        {/* Search & Filter Architecture (Date range, Region, Category, Intensity, RI Event) */}
        <Panel>
          <PanelHeader
            title="Search & Archive Query Filters"
            subtitle="Prepare parametric criteria across historical best tracks and analog storm searches"
          />
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <Input
                label="Storm Search"
                placeholder="e.g. Fani, Amphan, Tauktae, Biparjoy..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />

              <Select
                label="Region / Basin"
                value={selectedBasin}
                onChange={(e) => setSelectedBasin(e.target.value)}
                options={[
                  { value: "all", label: "All Ocean Basins" },
                  { value: "NIO", label: "North Indian Ocean (Bay of Bengal / Arabian Sea)" },
                  { value: "WPAC", label: "Western North Pacific (Typhoons)" },
                  { value: "EPAC", label: "Eastern Pacific (Hurricanes)" },
                  { value: "ATL", label: "North Atlantic (Hurricanes)" },
                ]}
              />

              <Select
                label="Season / Year Range"
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(e.target.value)}
                options={[
                  { value: "all", label: "All Historical Seasons (1990 – 2025)" },
                  { value: "2020-2025", label: "Recent Era (2020 – 2025)" },
                  { value: "2010-2019", label: "Satellite Era 2 (2010 – 2019)" },
                  { value: "2000-2009", label: "Satellite Era 1 (2000 – 2009)" },
                  { value: "1990-1999", label: "Early Digital Archive (1990 – 1999)" },
                ]}
              />

              <Select
                label="Cyclone Category"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                options={[
                  { value: "all", label: "All Cyclone Categories" },
                  { value: "depression", label: "Depression (31–61 km/h)" },
                  { value: "cyclonic_storm", label: "Cyclonic Storm (62–88 km/h)" },
                  { value: "severe", label: "Severe Cyclonic Storm (89–117 km/h)" },
                  { value: "very_severe", label: "Very Severe (118–165 km/h)" },
                  { value: "super_cyclone", label: "Super Cyclone (> 221 km/h)" },
                ]}
              />

              <Select
                label="Intensity Threshold"
                value={selectedIntensity}
                onChange={(e) => setSelectedIntensity(e.target.value)}
                options={[
                  { value: "all", label: "All Peak Intensities" },
                  { value: "gale", label: "Vmax ≥ 63 km/h (Gale Force)" },
                  { value: "storm", label: "Vmax ≥ 118 km/h (Hurricane Strength)" },
                  { value: "major", label: "Vmax ≥ 178 km/h (Major Cyclone)" },
                ]}
              />

              <Select
                label="Rapid Intensification (RI) Event"
                value={selectedRiEvent}
                onChange={(e) => setSelectedRiEvent(e.target.value)}
                options={[
                  { value: "all", label: "All Cases (RI and Non-RI)" },
                  { value: "only_ri", label: "Confirmed RI Cases Only (ΔVmax ≥ 30 kt / 24h)" },
                  { value: "no_ri", label: "Non-RI Standard Trajectories" },
                ]}
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#e2e6e9]">
              <Button size="sm" variant="outline" onClick={handleResetFilters}>
                <Filter className="h-3.5 w-3.5 mr-1" />
                Reset Filters
              </Button>
            </div>
          </div>
        </Panel>

        {/* Historical Records Container / Empty State */}
        <Panel>
          <PanelHeader
            title="Archived Cyclone Trajectories"
            subtitle="Standardized ground-truth observations, analog track similarity, and reanalysis wind fields"
          />

          {historicalData.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<History className="h-8 w-8 text-[#0f5b6c]" />}
                title="No historical records are currently connected."
                description="Historical best-track reanalysis records (IBTrACS, IMD, JTWC) and benchmark datasets for AI model evaluation will be ingested in Sprint 3."
                statusBadge="Scheduled for Sprint 3 Ingestion"
                actionText="Reset Filter Parameters"
                onAction={handleResetFilters}
              />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Storm Identifier</TableHead>
                  <TableHead>Season</TableHead>
                  <TableHead>Basin</TableHead>
                  <TableHead>Classification</TableHead>
                  <TableHead>Peak Vmax</TableHead>
                  <TableHead>Min MSLP</TableHead>
                  <TableHead>RI Event</TableHead>
                  <TableHead>Dataset Source</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historicalData.map((h) => (
                  <TableRow key={h.id}>
                    <TableCell className="font-semibold text-[#182026] flex items-center gap-1.5">
                      <Compass className="h-3.5 w-3.5 text-[#0f5b6c]" />
                      {h.name}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{h.season}</TableCell>
                    <TableCell className="font-mono text-xs">{h.basin}</TableCell>
                    <TableCell>{h.category}</TableCell>
                    <TableCell className="font-mono font-bold">{h.peak_intensity_kmh} km/h</TableCell>
                    <TableCell className="font-mono">{h.min_mslp_hpa} hPa</TableCell>
                    <TableCell>
                      <Badge variant={h.had_ri_event ? "danger" : "neutral"}>
                        {h.had_ri_event ? "CONFIRMED RI" : "NON-RI"}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-[11px] text-[#5f6b7c]">{h.source_dataset}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Panel>
      </div>
    </PortalLayout>
  );
}
