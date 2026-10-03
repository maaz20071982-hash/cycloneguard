import { NextRequest, NextResponse } from "next/server";
import { getCentralStormState } from "@/lib/central-storm-store";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const storm = getCentralStormState(id);

  return NextResponse.json({
    success: true,
    data: {
      cyclone_id: storm.storm_id,
      storm_name: storm.storm_name,
      status: "available",
      horizons: storm.track_landfall_prediction.forecast_points.map((p) => ({
        horizon_hours: p.hour_offset,
        valid_time: p.valid_time_utc,
        wind_speed_kts: p.wind_speed_kts,
        wind_speed_kmh: p.wind_speed_kmh,
        central_pressure_mb: p.central_pressure_mb,
        latitude: p.latitude,
        longitude: p.longitude,
        category: p.category,
      })),
      confidence_interval: "±10 kts",
      message: "Forecast generated from Ensemble Multimodal Pipeline",
    },
  });
}
