import { NextResponse } from "next/server";
import { CHAPALA_CENTRAL_STORM } from "@/lib/central-storm-store";

export async function GET() {
  return NextResponse.json({
    success: true,
    alerts: CHAPALA_CENTRAL_STORM.targeted_alerts,
    total: CHAPALA_CENTRAL_STORM.targeted_alerts.length,
    status: "Active Operational Alerts",
    message: "Disaster management advisories synchronized with storm state",
  });
}
