import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    success: true,
    status: "healthy",
    version: "3.0.0-frozen",
    database: "connected",
    model_name: "CycloneGuard-RI-Multimodal-TS-Final",
    operating_threshold_tau: 0.125,
    timestamp: new Date().toISOString(),
  });
}
