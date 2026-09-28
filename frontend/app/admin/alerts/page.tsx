"use client";

import React, { useEffect, useState } from "react";
import { AdminLayout } from "@/components/layout/AdminLayout";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { Alert } from "@/components/ui/Alert";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingSpinner } from "@/components/ui/Loading";
import { fetchAdminAlerts, AdminAlertsResponse } from "@/lib/api/admin";
import { AlertTriangle, RefreshCw, Bell, Shield, Info } from "lucide-react";

export default function AdminAlertsPage() {
  const [data, setData] = useState<AdminAlertsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await fetchAdminAlerts();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Breadcrumb */}
        <Breadcrumb
          items={[
            { label: "Admin Console", href: "/admin/dashboard" },
            { label: "Alerts" },
          ]}
        />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-3 border-b border-[#e2e6e9]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Advisory Dissemination
              </span>
              <Badge variant="warning">AI-Assisted Monitoring</Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-[#b45309]" />
              AI-Assisted Operational Alerts & Monitoring Rules
            </h1>
            <p className="text-xs text-[#5f6b7c] mt-0.5">
              Automated threshold triggers for Rapid Intensification, intensity fluctuations, data feed anomalies, and system health.
            </p>
          </div>

          <Button size="sm" variant="outline" onClick={loadAlerts} isLoading={isLoading}>
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Check Active Triggers
          </Button>
        </div>

        {/* Critical Statutory Disclaimer */}
        <Alert variant="warning" title="Operational Clarification & Government Warning Notice">
          {data?.disclaimer ||
            "CycloneGuard provides AI-assisted meteorological monitoring alerts exclusively for research and operations centers. These telemetry alerts are NOT official government warnings and DO NOT constitute evacuation orders. Official tropical cyclone warnings and landfall advisories remain the sole jurisdiction of designated meteorological agencies (e.g. IMD / RSMC New Delhi)."}
        </Alert>

        {/* Alerts Table with Prepared Structure */}
        <Panel>
          <PanelHeader
            title="Operational Alert Queue"
            subtitle="Triggered meteorological advisories and automated evaluation events"
          />

          {isLoading ? (
            <div className="flex justify-center p-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : !data?.alerts || data.alerts.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Bell className="h-8 w-8 text-[#b45309]" />}
                title="No alerts available."
                description="Zero meteorological risk threshold breaches or system alert conditions are currently active. Real-time alert triggers are not available in current research prototype (historical surveillance mode)."
                statusBadge="Alert Engine Standby"
              />

              {/* Prepared Alert Architecture Structure */}
              <div className="mt-8 border-t border-[#e2e6e9] pt-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] font-semibold">
                    Planned Alert Trigger Specifications
                  </span>
                  <div className="flex flex-wrap gap-1.5 text-[10px] font-mono">
                    <span className="px-2 py-0.5 rounded-[2px] bg-[#fef2f2] text-[#b91c1c] border border-[#fecaca]">
                      Rapid Intensification (RI &ge; 30kt / 24h)
                    </span>
                    <span className="px-2 py-0.5 rounded-[2px] bg-[#fef8ee] text-[#b45309] border border-[#fed7aa]">
                      Intensity Change (&plusmn;15kt)
                    </span>
                    <span className="px-2 py-0.5 rounded-[2px] bg-[#edf5f7] text-[#0f5b6c] border border-[#b9e1e8]">
                      Data Quality Anomaly
                    </span>
                    <span className="px-2 py-0.5 rounded-[2px] bg-[#f1f3f4] text-[#5f6b7c] border border-[#e2e6e9]">
                      System Failure Alert
                    </span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Alert ID</TableHead>
                        <TableHead>Timestamp</TableHead>
                        <TableHead>Cyclone</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Severity</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Source</TableHead>
                        <TableHead className="text-right">Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-[#5f6b7c] py-6 font-mono text-xs italic">
                          No active monitoring alerts in current evaluation cycle
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alert ID</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Cyclone</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.alerts.map((a, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-xs">{a.id}</TableCell>
                    <TableCell className="font-mono text-xs">{a.timestamp}</TableCell>
                    <TableCell className="font-semibold">{a.cyclone}</TableCell>
                    <TableCell>{a.type}</TableCell>
                    <TableCell>
                      <Badge variant="warning">{a.severity}</Badge>
                    </TableCell>
                    <TableCell>{a.status}</TableCell>
                    <TableCell>{a.source}</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" className="h-6 text-[11px] px-2">
                        Inspect
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Panel>
      </div>
    </AdminLayout>
  );
}
