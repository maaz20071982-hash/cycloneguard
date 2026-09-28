"use client";

import React from "react";
import { CycloneMap, MapTrackPoint, StormTrackGroup } from "./CycloneMap";

export interface MapContainerProps {
  title?: string;
  subtitle?: string;
  timestamp?: string;
  basin?: string;
  hasActiveData?: boolean;
  activeLayers?: string[];
  tracks?: MapTrackPoint[];
  multiStormTracks?: StormTrackGroup[];
  className?: string;
}

export function MapContainer({
  title = "Tropical Cyclone Monitoring Basin",
  subtitle,
  timestamp,
  basin = "North Indian Ocean & West Pacific",
  hasActiveData = false,
  tracks = [],
  multiStormTracks = [],
  className,
}: MapContainerProps) {
  return (
    <CycloneMap
      title={title}
      subtitle={subtitle || (timestamp ? `Observation Time: ${timestamp}` : undefined)}
      basin={basin}
      tracks={tracks}
      multiStormTracks={multiStormTracks}
      className={className}
    />
  );
}
