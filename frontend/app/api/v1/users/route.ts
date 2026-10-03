import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    users: [
      {
        id: "usr-admin-1",
        email: "admin@cycloneguard.internal",
        full_name: "Lead Meteorological Director",
        role: "ADMIN",
        is_active: true,
        created_at: "2026-09-25T11:22:00Z",
      },
      {
        id: "usr-duty-2",
        email: "duty.officer@imd.gov.in",
        full_name: "Dr. A. Sharma (Duty Meteorologist)",
        role: "ADMIN",
        is_active: true,
        created_at: "2026-09-30T00:00:00Z",
      },
      {
        id: "usr-analyst-3",
        email: "live_analyst@meteo.org",
        full_name: "Operational Analyst",
        role: "USER",
        is_active: true,
        created_at: "2026-09-28T09:00:00Z",
      },
    ],
    total: 3,
    skip: 0,
    limit: 50,
  });
}
