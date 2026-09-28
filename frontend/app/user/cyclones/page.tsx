"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { getCyclones } from "@/lib/api/cyclones";
import { Cyclone } from "@/types";
import { Database, Search, Filter, RefreshCw, Compass, ArrowRight } from "lucide-react";

export default function CycloneListPage() {
  const [cyclones, setCyclones] = useState<Cyclone[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBasin, setSelectedBasin] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await getCyclones();
      setCyclones(res.cyclones || []);
    } catch {
      setCyclones([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredCyclones = cyclones.filter((c) => {
    const matchesSearch = searchQuery === "" || c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBasin = selectedBasin === "all" || c.basin.toLowerCase() === selectedBasin.toLowerCase();
    return matchesSearch && matchesBasin;
  });

  return (
    <PortalLayout type="user">
      <div className="space-y-6">
        {/* Breadcrumb Navigation */}
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/user/dashboard" },
            { label: "Cyclone Database" },
          ]}
        />

        {/* Section Header: CYCLONE DATABASE */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Operational & Historical Records
              </span>
              <StatusBadge status="disconnected" text="Pipeline Standby" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
              <Database className="h-6 w-6 text-[#0f5b6c]" />
              Cyclone Database
            </h1>
            <p className="text-xs text-[#5f6b7c] mt-0.5">
              Historical and operational cyclone systems across surveillance basins.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={loadData} isLoading={isLoading}>
              <RefreshCw className="h-3.5 w-3.5 mr-1" />
              Refresh
            </Button>
            <Link href="/user/monitor">
              <Button size="sm" variant="secondary">
                <Compass className="h-3.5 w-3.5 mr-1" />
                Live Map Monitor
              </Button>
            </Link>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <Panel className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
            <div className="sm:col-span-6">
              <Input
                label="Search Cyclone Database"
                placeholder="Search by storm name or international designation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="sm:col-span-4">
              <Select
                label="Ocean Basin Filter"
                value={selectedBasin}
                onChange={(e) => setSelectedBasin(e.target.value)}
                options={[
                  { value: "all", label: "All Ocean Basins" },
                  { value: "NIO", label: "North Indian Ocean (NIO)" },
                  { value: "WPAC", label: "Western North Pacific (WPAC)" },
                  { value: "EPAC", label: "Eastern Pacific (EPAC)" },
                  { value: "ATL", label: "North Atlantic (ATL)" },
                ]}
              />
            </div>
            <div className="sm:col-span-2">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedBasin("all");
                }}
              >
                <Filter className="h-3.5 w-3.5 mr-1" />
                Reset
              </Button>
            </div>
          </div>
        </Panel>

        {/* Cyclone Records Table / Empty State */}
        <Panel>
          <PanelHeader
            title="Tracked Cyclone Systems"
            subtitle="Observation metrics, estimated wind speed, trend trajectory, and rapid intensification risk levels"
          />

          {filteredCyclones.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Database className="h-8 w-8 text-[#0f5b6c]" />}
                title="No cyclone records are currently available."
                description="Data will appear when a cyclone data source is connected. Geostationary satellite ingestion microservices (INSAT-3D/3DR and Himawari-9) are scheduled for Sprint 3."
                statusBadge="Awaiting Data Source"
                actionText="Refresh Ingestion State"
                onAction={loadData}
              />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Cyclone Name</TableHead>
                  <TableHead>Observation Date</TableHead>
                  <TableHead>Region / Basin</TableHead>
                  <TableHead>Current Intensity</TableHead>
                  <TableHead>Trend</TableHead>
                  <TableHead>RI Risk</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCyclones.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-semibold text-[#182026] flex items-center gap-1.5">
                      <Compass className="h-3.5 w-3.5 text-[#0f5b6c]" />
                      {c.name}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-[#5f6b7c]">
                      {c.observation_time || "Standby"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-[#182026]">
                      {c.basin}
                    </TableCell>
                    <TableCell className="font-mono text-xs font-bold text-[#182026]">
                      {c.current_intensity_kmh ? `${c.current_intensity_kmh} km/h` : "—"}
                    </TableCell>
                    <TableCell className="text-xs text-[#5f6b7c]">
                      {c.intensity_trend || "—"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={c.ri_risk_level === "high" || c.ri_risk_level === "critical" ? "danger" : "neutral"}>
                        {c.ri_risk_level?.toUpperCase() || "UNAVAILABLE"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status="standby" text={c.status} />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1.5">
                        <Link href={`/user/cyclones/${c.id}`}>
                          <Button size="sm" variant="outline" className="text-xs h-7">
                            Inspect
                          </Button>
                        </Link>
                        <Link href={`/user/cyclones/${c.id}/case-study`}>
                          <Button size="sm" variant="primary" className="text-xs h-7">
                            Case Study
                          </Button>
                        </Link>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Panel>

        {/* Benchmark Case Study Quick Link */}
        <div className="p-4 rounded-[4px] border border-[#0f5b6c] bg-[#f8fafc] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-bold text-[#0f5b6c] uppercase font-mono text-[11px]">
                Verified Benchmark Case Study: Cyclone CHAPALA (2015)
              </span>
              <Badge variant="danger" className="text-[10px]">RI+ VERIFIED</Badge>
            </div>
            <p className="text-[#5f6b7c]">
              Examine the verified multimodal case study workstation, HURSAT-B1 satellite infrared imagery, and standardized feature attribution.
            </p>
          </div>
          <Link href="/user/cyclones/2015301N11065/case-study?time=2015-10-28T18:00:00Z">
            <Button size="sm" variant="primary">
              Open Chapala Case Study <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </div>
      </div>
    </PortalLayout>
  );
}
