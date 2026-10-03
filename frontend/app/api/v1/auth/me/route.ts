import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    id: "usr-prod-001",
    email: "duty.officer@imd.gov.in",
    full_name: "Dr. A. Sharma (Duty Meteorologist)",
    role: "ADMIN",
    is_active: true,
    created_at: "2026-09-30T00:00:00Z",
  });
}
