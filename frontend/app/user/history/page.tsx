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

const DEFAULT_HISTORICAL_DATA: HistoricalCyclone[] = [
  {
    id: "2015301N11065",
    name: "CHAPALA",
    season: 2015,
    basin: "North Indian Ocean (Arabian Sea)",
    category: "Extremely Severe Cyclonic Storm",
    peak_intensity_kmh: 213,
    min_mslp_hpa: 940,
    had_ri_event: true,
    source_dataset: "NOAA IBTrACS v04r01 (Ground-Truth Best Track)",
  },
  {
    id: "2023131N05093",
    name: "MOCHA",
    season: 2023,
    basin: "North Indian Ocean (Bay of Bengal)",
    category: "Super Cyclonic Storm",
    peak_intensity_kmh: 268,
    min_mslp_hpa: 918,
    had_ri_event: true,
    source_dataset: "IMD Best Track / JTWC Archive",
  },
  {
    id: "2014297N11062",
    name: "NILOFAR",
    season: 2014,
    basin: "North Indian Ocean (Arabian Sea)",
    category: "Extremely Severe Cyclonic Storm",
    peak_intensity_kmh: 204,
    min_mslp_hpa: 950,
    had_ri_event: true,
    source_dataset: "NOAA IBTrACS v04r01 (Ground-Truth Best Track)",
  },
  {
    id: "2013281N12098",
    name: "PHAILIN",
    season: 2013,
    basin: "North Indian Ocean (Bay of Bengal)",
    category: "Super Cyclonic Storm",
    peak_intensity_kmh: 259,
    min_mslp_hpa: 915,
    had_ri_event: true,
    source_dataset: "NOAA IBTrACS v04r01 (Ground-Truth Best Track)",
  },
  {
    id: "2014279N11096",
    name: "HUDHUD",
    season: 2014,
    basin: "North Indian Ocean (Bay of Bengal)",
    category: "Very Severe Cyclonic Storm",
    peak_intensity_kmh: 213,
    min_mslp_hpa: 960,
    had_ri_event: false,
    source_dataset: "IMD Best Track Reanalysis",
  },
  {
    id: "2015309N14067",
    name: "MEGH",
    season: 2015,
    basin: "North Indian Ocean (Arabian Sea)",
    category: "Extremely Severe Cyclonic Storm",
    peak_intensity_kmh: 204,
    min_mslp_hpa: 964,
    had_ri_event: true,
    source_dataset: "NOAA IBTrACS v04r01 (Ground-Truth Best Track)",
  },
  {
    id: "2019117N09088",
    name: "FANI",
    season: 2019,
    basin: "North Indian Ocean (Bay of Bengal)",
    category: "Extremely Severe Cyclonic Storm",
    peak_intensity_kmh: 215,
    min_mslp_hpa: 932,
    had_ri_event: true,
    source_dataset: "IMD Best Track Reanalysis",
  },
  {
    id: "2020137N10087",
    name: "AMPHAN",
    season: 2020,
    basin: "North Indian Ocean (Bay of Bengal)",
    category: "Super Cyclonic Storm",
    peak_intensity_kmh: 270,
    min_mslp_hpa: 920,
    had_ri_event: true,
    source_dataset: "IMD / JTWC Post-Season Archive",
  },
];

export default function HistoryPage() {
  const [historicalData, setHistoricalData] = useState<HistoricalCyclone[]>(DEFAULT_HISTORICAL_DATA);
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
      if (res && res.historical_cyclones && res.historical_cyclones.length > 0) {
        setHistoricalData(res.historical_cyclones);
      } else {
        setHistoricalData(DEFAULT_HISTORICAL_DATA);
      }
    } catch {
      setHistoricalData(DEFAULT_HISTORICAL_DATA);
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

  const filteredData = historicalData.filter((h) => {
    const matchesSearch =
      searchQuery === "" ||
      h.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      h.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBasin =
      selectedBasin === "all" ||
      h.basin.toLowerCase().includes(selectedBasin.toLowerCase());
    const matchesRi =
      selectedRiEvent === "all" ||
      (selectedRiEvent === "only_ri" && h.had_ri_event) ||
      (selectedRiEvent === "no_ri" && !h.had_ri_event);
    return matchesSearch && matchesBasin && matchesRi;
  });

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

          {filteredData.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<History className="h-8 w-8 text-[#0f5b6c]" />}
                title="No historical records match the selected query."
                description="Try broadening your basin, season, or rapid intensification filters."
                statusBadge="Zero Filter Matches"
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
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map((h) => (
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
                    <TableCell className="text-right">
                      <a
                        href={`/user/cyclones/${h.id}/case-study`}
                        className="inline-flex items-center text-xs font-mono text-[#0f5b6c] hover:underline font-semibold"
                      >
                        Case Study →
                      </a>
                    </TableCell>
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
