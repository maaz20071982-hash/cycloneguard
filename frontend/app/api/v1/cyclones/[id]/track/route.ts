import { NextRequest, NextResponse } from "next/server";
import { MOCK_NORTH_INDIAN_OCEAN_TRACKS } from "@/lib/mock-tracks";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const track = MOCK_NORTH_INDIAN_OCEAN_TRACKS.find(
    (t) => t.id === id || t.name.toUpperCase() === id.toUpperCase()
  );

  if (!track) {
    return NextResponse.json({
      success: false,
      message: "Cyclone track not found",
    }, { status: 404 });
  }

  return NextResponse.json({
    success: true,
    data: {
      cyclone_id: track.id,
      storm_name: track.name,
      basin: track.basin,
      points: track.points,
      total_points: track.points.length,
    },
  });
}
