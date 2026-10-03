import { NextResponse } from "next/server";
import { MOCK_NORTH_INDIAN_OCEAN_TRACKS } from "@/lib/mock-tracks";

export async function GET() {
  return NextResponse.json({
    success: true,
    cyclones: MOCK_NORTH_INDIAN_OCEAN_TRACKS,
    total: MOCK_NORTH_INDIAN_OCEAN_TRACKS.length,
    status: "Verified Reanalysis",
  });
}
