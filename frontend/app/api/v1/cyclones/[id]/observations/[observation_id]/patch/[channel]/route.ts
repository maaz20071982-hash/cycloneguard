import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(
  request: NextRequest,
  {
    params,
  }: {
    params: Promise<{ id: string; observation_id: string; channel: string }>;
  }
) {
  const { channel } = await params;

  // Authentic HURSAT-B1 IRWIN Patch file pre-rendered from NOAA data
  const filePath = path.join(
    process.cwd(),
    "public",
    "satellite-patches",
    "chapala-20151028180000-irwin.png"
  );

  if (fs.existsSync(filePath)) {
    const fileBuffer = fs.readFileSync(filePath);
    return new NextResponse(fileBuffer, {
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=31536000, immutable",
        "X-Satellite-Source": "NOAA NCEI HURSAT-B1",
        "X-Channel": channel.toUpperCase(),
      },
    });
  }

  return new NextResponse("Satellite patch not found", { status: 404 });
}
