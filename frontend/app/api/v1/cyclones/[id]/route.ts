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

  return NextResponse.json({
    success: true,
    data: {
      id: storm.storm_id,
      name: storm.storm_name,
      basin: storm.basin,
      status: "HISTORICAL_VERIFIED",
      genesis_time: track?.points[0]?.time || storm.observation_time_utc,
      current_intensity_kts: storm.observation_data.current_wind_kts,
      central_pressure_mb: storm.observation_data.central_pressure_mb,
      latitude: storm.observation_data.latitude,
      longitude: storm.observation_data.longitude,
      ri_risk_index: storm.explainable_confidence.empirical_ri_risk_index,
      operating_threshold: storm.explainable_confidence.operating_threshold_tau,
      ri_flag: storm.explainable_confidence.empirical_ri_risk_index >= 0.125,
      risk_category: storm.explainable_confidence.risk_tier,
    },
  });
}
