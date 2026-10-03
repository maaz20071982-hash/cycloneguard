import { NextRequest, NextResponse } from "next/server";
import { getCentralStormState } from "@/lib/central-storm-store";
import { MOCK_NORTH_INDIAN_OCEAN_TRACKS } from "@/lib/mock-tracks";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const storm = getCentralStormState(id);
  const track = MOCK_NORTH_INDIAN_OCEAN_TRACKS.find(
    (t) => t.id === id || t.name.toUpperCase() === id.toUpperCase()
  );

  const observations = (track?.points || []).map((p, idx) => ({
    id: p.time.replace(/[-:]/g, "").slice(0, 16),
    cyclone_id: storm.storm_id,
    source: "NOAA HURSAT-B1",
    channel: "IRWIN",
    observation_time: p.time,
    latitude: p.lat,
    longitude: p.lon,
    current_wind_kts: p.intensity_kts,
    central_pressure_mb: p.pressure_mb,
    has_irwin: true,
  }));

  return NextResponse.json({
    success: true,
    data: {
      observations,
      total: observations.length,
      storm_name: storm.storm_name,
    },
  });
}
