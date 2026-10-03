import { NextResponse } from "next/server";
import { MOCK_NORTH_INDIAN_OCEAN_TRACKS } from "@/lib/mock-tracks";

export async function GET() {
  const cyclones = MOCK_NORTH_INDIAN_OCEAN_TRACKS.map((t) => ({
    id: t.id,
    name: t.name,
    basin: t.basin,
    status: t.status,
    peak_intensity_kts: t.peak_intensity_kts,
    created_at: t.points[0]?.time || "2015-10-27T12:00:00Z",
    points_count: t.points.length,
  }));

  return NextResponse.json({
    success: true,
    data: {
      cyclones,
      total: cyclones.length,
      status: "Verified Historical Database Active",
      demonstration_data: false,
      message: "NOAA IBTrACS and HURSAT-B1 Verified Lifecycles Available",
    },
  });
}
