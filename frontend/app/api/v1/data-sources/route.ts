import { NextResponse } from "next/server";
import { DEFAULT_OBSERVATION_SOURCES } from "@/lib/central-storm-store";

export async function GET() {
  const data_sources = DEFAULT_OBSERVATION_SOURCES.map((s) => ({
    id: s.id,
    name: s.name,
    category: s.category,
    status: s.status,
    frequency: s.frequency,
    latency: s.latency,
    resolution: s.resolution,
    channels: s.channels,
    description: s.description,
  }));

  return NextResponse.json({
    success: true,
    data_sources,
    connected_count: data_sources.filter((s) => s.status === "ACTIVE").length,
    total_count: data_sources.length,
  });
}
