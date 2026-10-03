"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";

export interface MapTrackPoint {
  lat: number;
  lon: number;
  time: string;
  intensity_kmh?: number;
  intensity_kts?: number;
  pressure_mb?: number;
  category?: string;
  agency_grade?: string;
}

export interface StormTrackGroup {
  id: string;
  name: string;
  status?: string;
  basin?: string;
  points: MapTrackPoint[];
  color?: string;
  isSelected?: boolean;
  peak_intensity_kts?: number;
}

export interface LeafletMapProps {
  center?: [number, number];
  zoom?: number;
  tracks?: MapTrackPoint[];
  multiStormTracks?: StormTrackGroup[];
  selectedPointTime?: string;
  activeStormId?: string;
  onSelectStorm?: (stormId: string) => void;
  onSelectPoint?: (point: MapTrackPoint) => void;
  windRadii?: {
    lat: number;
    lon: number;
    r34_nm?: number;
    r50_nm?: number;
    r64_nm?: number;
  };
  forecastPath?: MapTrackPoint[];
  markers?: Array<{
    lat: number;
    lon: number;
    label: string;
    sublabel?: string;
    type?: "landfall" | "center" | "station";
  }>;
  showWindRadii?: boolean;
  showForecastCone?: boolean;
  showTrackPoints?: boolean;
  basemap?: "dark" | "satellite" | "ocean" | "osm";
  height?: string | number;
  className?: string;
}

// Meteorological color scale based on sustained winds (knots)
export function getIntensityColor(windKts: number = 0): string {
  if (windKts >= 120) return "#d946ef"; // Super Cyclone (>=120 kt) - Magenta
  if (windKts >= 90) return "#ef4444";  // Extremely Severe (90-119 kt) - Red
  if (windKts >= 64) return "#f97316";  // Very Severe (64-89 kt) - Orange
  if (windKts >= 48) return "#eab308";  // Severe Cyclonic Storm (48-63 kt) - Amber
  if (windKts >= 34) return "#14b8a6";  // Cyclonic Storm (34-47 kt) - Teal
  return "#0ea5e9";                     // Depression / Low (<34 kt) - Sky Blue
}

export function getStormCategory(windKts: number = 0): string {
  if (windKts >= 120) return "Super Cyclonic Storm";
  if (windKts >= 90) return "Extremely Severe Cyclonic Storm";
  if (windKts >= 64) return "Very Severe Cyclonic Storm";
  if (windKts >= 48) return "Severe Cyclonic Storm";
  if (windKts >= 34) return "Cyclonic Storm";
  if (windKts >= 28) return "Deep Depression";
  return "Tropical Depression";
}

// 100% Free, Zero-API-Key Tile Providers (No rate limits, no watermarks, no registration required)
const BASEMAP_CONFIGS = {
  // 1. Dark Meteorological Radar (Default): Esri World Dark Gray Base + Reference Labels
  dark: {
    base: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, DeLorme, NAVTEQ',
        maxZoom: 16,
      },
    },
    reference: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: "",
        maxZoom: 16,
      },
    },
  },

  // 2. High-Resolution Earth Satellite: Esri World Imagery + Boundaries
  satellite: {
    base: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, Maxar, Earthstar Geographics',
        maxZoom: 17,
      },
    },
    reference: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: "",
        maxZoom: 17,
      },
    },
  },

  // 3. Maritime / Oceanic Bathymetry: Esri World Ocean Base
  ocean: {
    base: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, GEBCO, NOAA, National Geographic',
        maxZoom: 13,
      },
    },
    reference: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}",
      options: {
        attribution: "",
        maxZoom: 13,
      },
    },
  },

  // 4. Standard OpenStreetMap (Global Open Data)
  osm: {
    base: {
      url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      options: {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      },
    },
    reference: null,
  },
};

export function LeafletMap({
  center = [15.0, 75.0],
  zoom = 4,
  tracks = [],
  multiStormTracks = [],
  selectedPointTime,
  activeStormId,
  onSelectStorm,
  onSelectPoint,
  windRadii,
  forecastPath = [],
  markers = [],
  showWindRadii = true,
  showForecastCone = true,
  showTrackPoints = true,
  basemap = "dark",
  height = "100%",
  className = "",
}: LeafletMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  const baseTileLayerRef = useRef<L.TileLayer | null>(null);
  const refTileLayerRef = useRef<L.TileLayer | null>(null);
  const layersGroupRef = useRef<L.LayerGroup | null>(null);
  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);

  const containerHeight = typeof height === "number" ? `${height}px` : height || "100%";

  // 1. Initialize Leaflet Map Instance with robust sizing & lifecycle safety
  useEffect(() => {
    if (!mapContainerRef.current) return;
    const container = mapContainerRef.current;

    // Remove any orphaned leaflet state on the container to prevent "Map container is already initialized"
    if ((container as any)._leaflet_id) {
      delete (container as any)._leaflet_id;
    }

    const map = L.map(container, {
      center: center,
      zoom: zoom,
      zoomControl: false,
      attributionControl: false,
      worldCopyJump: true,
      minZoom: 2,
      maxZoom: 18,
    });

    // Scale control
    L.control.scale({ position: "bottomleft", imperial: true, metric: true }).addTo(map);

    // Mouse coordinates readout
    map.on("mousemove", (e) => {
      setCursorCoords({
        lat: Number(e.latlng.lat.toFixed(2)),
        lon: Number(e.latlng.lng.toFixed(2)),
      });
    });

    map.on("mouseout", () => {
      setCursorCoords(null);
    });

    const layersGroup = L.layerGroup().addTo(map);
    layersGroupRef.current = layersGroup;
    setMapInstance(map);

    // Use ResizeObserver to ensure map size never collapses or becomes invisible
    const resizeObserver = new ResizeObserver(() => {
      try {
        map.invalidateSize();
      } catch {}
    });
    resizeObserver.observe(container);

    // Staggered size invalidations to ensure full rendering across initial load, tab switches, and flex reflows
    const t1 = setTimeout(() => {
      try {
        map.invalidateSize();
        setMapLoaded(true);
      } catch {}
    }, 80);
    const t2 = setTimeout(() => {
      try { map.invalidateSize(); } catch {}
    }, 250);
    const t3 = setTimeout(() => {
      try { map.invalidateSize(); } catch {}
    }, 600);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      resizeObserver.disconnect();
      setMapInstance(null);
      layersGroupRef.current = null;
      try {
        map.remove();
      } catch {}
      if ((container as any)._leaflet_id) {
        delete (container as any)._leaflet_id;
      }
    };
  }, []);

  // 2. Basemap Tile Management (Free, Zero API Key) - Reliably triggered whenever mapInstance or basemap changes
  useEffect(() => {
    if (!mapInstance) return;
    const map = mapInstance;

    // Remove old layers
    if (baseTileLayerRef.current) {
      try { map.removeLayer(baseTileLayerRef.current); } catch {}
      baseTileLayerRef.current = null;
    }
    if (refTileLayerRef.current) {
      try { map.removeLayer(refTileLayerRef.current); } catch {}
      refTileLayerRef.current = null;
    }

    const config = BASEMAP_CONFIGS[basemap] || BASEMAP_CONFIGS.dark;

    // Base Tile Layer
    const baseLayer = L.tileLayer(config.base.url, {
      ...config.base.options,
      crossOrigin: true,
    }).addTo(map);
    baseLayer.bringToBack();
    baseTileLayerRef.current = baseLayer;

    // Reference Layer (Borders, labels, coastlines)
    if (config.reference) {
      const refLayer = L.tileLayer(config.reference.url, {
        ...config.reference.options,
        crossOrigin: true,
      }).addTo(map);
      refTileLayerRef.current = refLayer;
    }

    // Refresh size whenever basemap switches
    map.invalidateSize();
  }, [mapInstance, basemap]);

  // 3. Render Vectors, Storm Tracks, Wind Radii, Vortex Glyphs
  useEffect(() => {
    if (!mapInstance || !layersGroupRef.current) return;
    const map = mapInstance;
    const group = layersGroupRef.current;
    group.clearLayers();

    const allLatLons: L.LatLng[] = [];

    // Helper to render a storm track
    const renderTrack = (
      points: MapTrackPoint[],
      stormName: string,
      stormId: string,
      isPrimary: boolean,
      customColor?: string
    ) => {
      if (!points || points.length === 0) return;

      const latLngs = points.map((p) => L.latLng(p.lat, p.lon));
      latLngs.forEach((ll) => allLatLons.push(ll));

      // Draw color-coded line segments
      for (let i = 0; i < points.length - 1; i++) {
        const p1 = points[i];
        const p2 = points[i + 1];
        const segWind = Math.max(p1.intensity_kts || 0, p2.intensity_kts || 0);
        const color = customColor || getIntensityColor(segWind);

        const polyline = L.polyline([
          [p1.lat, p1.lon],
          [p2.lat, p2.lon],
        ], {
          color: color,
          weight: isPrimary ? 3.5 : 2,
          opacity: isPrimary ? 0.95 : 0.45,
          lineJoin: "round",
          lineCap: "round",
        });

        polyline.on("click", () => {
          if (onSelectStorm) onSelectStorm(stormId);
        });

        polyline.addTo(group);
      }

      // Draw track points
      if (showTrackPoints) {
        points.forEach((p) => {
          const windKts = p.intensity_kts || Math.round((p.intensity_kmh || 0) / 1.852);
          const color = customColor || getIntensityColor(windKts);
          const isSelected = selectedPointTime && p.time.startsWith(selectedPointTime.slice(0, 13));

          const circleMarker = L.circleMarker([p.lat, p.lon], {
            radius: isSelected ? 8 : (isPrimary ? 4.5 : 3),
            fillColor: color,
            color: isSelected ? "#ffffff" : "#0f172a",
            weight: isSelected ? 2.5 : 1,
            fillOpacity: isPrimary ? 0.95 : 0.6,
          });

          const timeFormatted = p.time.replace("T", " ").slice(0, 16) + " UTC";
          const kmh = p.intensity_kmh || Math.round((p.intensity_kts || 0) * 1.852);
          const category = p.category || getStormCategory(windKts);
          const pressureStr = p.pressure_mb ? `${p.pressure_mb} hPa` : "N/A";

          const popupContent = `
            <div style="font-family: ui-monospace, SFMono-Regular, Menlo, monospace; padding: 10px 12px; min-width: 230px; background: #182026; color: #f8fafc; border-radius: 4px;">
              <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="font-weight: 700; color: #f8fafc; font-size: 13px; text-transform: uppercase;">
                  ${stormName}
                </span>
                <span style="font-size: 10px; background: ${color}25; color: ${color}; border: 1px solid ${color}; padding: 1px 6px; border-radius: 3px; font-weight: 700;">
                  ${windKts} KT
                </span>
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
                <strong style="color: #cbd5e1;">TIME:</strong> ${timeFormatted}
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
                <strong style="color: #cbd5e1;">POSITION:</strong> ${p.lat.toFixed(2)}°N, ${p.lon.toFixed(2)}°E
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
                <strong style="color: #cbd5e1;">VMAX:</strong> ${windKts} kt (${kmh} km/h)
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
                <strong style="color: #cbd5e1;">PRESSURE:</strong> ${pressureStr}
              </div>
              <div style="font-size: 10px; color: #e2e8f0; background: #0f172a; padding: 4px 6px; border-radius: 2px; border-left: 3px solid ${color};">
                ${category}
              </div>
            </div>
          `;

          circleMarker.bindPopup(popupContent, {
            offset: [0, -6],
            className: "cyclone-meteorological-popup",
          });

          circleMarker.on("click", () => {
            if (onSelectPoint) onSelectPoint(p);
            if (onSelectStorm) onSelectStorm(stormId);
          });

          circleMarker.addTo(group);
        });
      }

      // Add animated vortex eye marker at the active point
      const activePoint = (selectedPointTime
        ? points.find((p) => p.time.startsWith(selectedPointTime.slice(0, 13)))
        : null) || points[points.length - 1];

      if (activePoint && isPrimary) {
        const windKts = activePoint.intensity_kts || 35;
        const color = customColor || getIntensityColor(windKts);

        const vortexIcon = L.divIcon({
          className: "cyclone-vortex-icon-container",
          iconSize: [40, 40],
          iconAnchor: [20, 20],
          html: `
            <div style="position: relative; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
              <div class="radar-ping" style="position: absolute; width: 40px; height: 40px; border-radius: 9999px; background-color: ${color}40; border: 2px solid ${color};"></div>
              <div class="vortex-spin" style="position: relative; font-size: 22px; line-height: 1; filter: drop-shadow(0 0 10px ${color});">
                🌀
              </div>
            </div>
          `,
        });

        const vortexMarker = L.marker([activePoint.lat, activePoint.lon], {
          icon: vortexIcon,
          zIndexOffset: 1000,
        }).addTo(group);

        vortexMarker.bindPopup(`
          <div style="font-family: ui-monospace, monospace; padding: 8px 10px; font-size: 11px; background: #182026; color: #f8fafc; border-radius: 4px;">
            <div style="font-weight: 700; color: #38bdf8; margin-bottom: 2px;">VORTEX CENTER / ACTIVE FIX</div>
            <div style="color: #cbd5e1;">${stormName} · ${activePoint.lat.toFixed(2)}°N, ${activePoint.lon.toFixed(2)}°E</div>
            <div style="color: #94a3b8; font-size: 10px; margin-top: 4px;">Sustained Wind: ${activePoint.intensity_kts || 'Verified'} kt</div>
          </div>
        `);
      }
    };

    // Multi-storm mode (Basin Surveillance)
    if (multiStormTracks.length > 0) {
      multiStormTracks.forEach((storm) => {
        const isPrimary = !activeStormId || storm.id === activeStormId;
        renderTrack(storm.points, storm.name, storm.id, isPrimary, storm.color);
      });
    }

    // Single storm mode
    if (tracks.length > 0) {
      renderTrack(tracks, "Selected Cyclone", activeStormId || "active", true);
    }

    // Render Wind Radii (R34, R50, R64)
    if (showWindRadii && windRadii) {
      const { lat, lon, r34_nm = 120, r50_nm = 60, r64_nm = 30 } = windRadii;
      const nmToMeters = 1852;

      // Gale Force Wind (34 kt)
      if (r34_nm > 0) {
        L.circle([lat, lon], {
          radius: r34_nm * nmToMeters,
          color: "#eab308",
          weight: 1.5,
          dashArray: "4, 4",
          fillColor: "#eab308",
          fillOpacity: 0.08,
        })
          .bindTooltip(`R34 (Gale Wind Radius): ${r34_nm} nm`, { sticky: true })
          .addTo(group);
      }

      // Storm Force Wind (50 kt)
      if (r50_nm > 0) {
        L.circle([lat, lon], {
          radius: r50_nm * nmToMeters,
          color: "#f97316",
          weight: 1.5,
          dashArray: "3, 3",
          fillColor: "#f97316",
          fillOpacity: 0.12,
        })
          .bindTooltip(`R50 (Storm Wind Radius): ${r50_nm} nm`, { sticky: true })
          .addTo(group);
      }

      // Hurricane Force Wind (64 kt)
      if (r64_nm > 0) {
        L.circle([lat, lon], {
          radius: r64_nm * nmToMeters,
          color: "#ef4444",
          weight: 2,
          fillColor: "#ef4444",
          fillOpacity: 0.16,
        })
          .bindTooltip(`R64 (Hurricane Wind Radius): ${r64_nm} nm`, { sticky: true })
          .addTo(group);
      }
    }

    // Render Projected Forecast / RI Uncertainty Cone Corridor & Circles
    if (showForecastCone && forecastPath.length > 0) {
      const fLatLngs = forecastPath.map((p) => [p.lat, p.lon] as [number, number]);
      fLatLngs.forEach(([la, lo]) => allLatLons.push(L.latLng(la, lo)));

      // Construct Uncertainty Cone Corridor Polygon
      if (forecastPath.length >= 2) {
        const leftPoints: [number, number][] = [];
        const rightPoints: [number, number][] = [];

        forecastPath.forEach((fp, idx) => {
          const radiusKm = 25 + idx * 45;
          const radLat = radiusKm / 111.0;
          const radLon = radiusKm / (111.0 * Math.max(0.1, Math.cos((fp.lat * Math.PI) / 180)));

          let dLat = 0;
          let dLon = 0;
          if (idx < forecastPath.length - 1) {
            dLat = forecastPath[idx + 1].lat - fp.lat;
            dLon = forecastPath[idx + 1].lon - fp.lon;
          } else {
            dLat = fp.lat - forecastPath[idx - 1].lat;
            dLon = fp.lon - forecastPath[idx - 1].lon;
          }
          const angle = Math.atan2(dLat, dLon);
          const normalLeft = angle + Math.PI / 2;
          const normalRight = angle - Math.PI / 2;

          leftPoints.push([fp.lat + radLat * Math.sin(normalLeft), fp.lon + radLon * Math.cos(normalLeft)]);
          rightPoints.push([fp.lat + radLat * Math.sin(normalRight), fp.lon + radLon * Math.cos(normalRight)]);
        });

        const conePolygon: [number, number][] = [...leftPoints, ...rightPoints.reverse()];

        L.polygon(conePolygon, {
          color: "#0284c7",
          weight: 1.5,
          dashArray: "4, 4",
          fillColor: "#38bdf8",
          fillOpacity: 0.16,
        })
          .bindTooltip("Forecast Uncertainty Cone (JTWC/IMD Standard Envelope)", { sticky: true })
          .addTo(group);
      }

      // Draw Forecast Track Line
      L.polyline(fLatLngs, {
        color: "#38bdf8",
        weight: 3,
        dashArray: "6, 8",
        opacity: 0.9,
      }).addTo(group);

      // Forecast points with expanding uncertainty circles
      forecastPath.forEach((fp, idx) => {
        const radiusKm = 25 + idx * 45;
        L.circle([fp.lat, fp.lon], {
          radius: radiusKm * 1000,
          color: "#0284c7",
          weight: 1,
          dashArray: "3, 5",
          fillColor: "#0284c7",
          fillOpacity: 0.04,
        }).addTo(group);

        L.circleMarker([fp.lat, fp.lon], {
          radius: 5.5,
          fillColor: "#38bdf8",
          color: "#0369a1",
          weight: 1.5,
          fillOpacity: 0.95,
        })
          .bindPopup(`
            <div style="font-family: monospace; font-size: 11px; padding: 6px 8px; background: #182026; color: #fff; border-radius: 3px;">
              <strong style="color: #38bdf8;">PROJECTED FORECAST POINT</strong>
              <div>Time: ${fp.time.replace("T", " ").slice(0, 16)} UTC</div>
              <div>Pos: ${fp.lat.toFixed(2)}°N, ${fp.lon.toFixed(2)}°E</div>
              <div>Exp. Intensity: ${fp.intensity_kts || "—"} kt (${fp.category || "Forecast"})</div>
              <div style="color: #7dd3fc; font-size: 10px; margin-top: 3px;">Uncertainty Radius: ±${radiusKm} km</div>
            </div>
          `)
          .addTo(group);
      });
    }

    // Render Custom Markers (e.g. Landfall Target Marker)
    if (markers && markers.length > 0) {
      markers.forEach((m) => {
        allLatLons.push(L.latLng(m.lat, m.lon));

        const isLandfall = m.type === "landfall" || m.label.toLowerCase().includes("landfall");
        const markerColor = isLandfall ? "#dc2626" : "#0f5b6c";

        const markerHtml = `
          <div style="display: flex; flex-direction: column; align-items: center; cursor: pointer;">
            <div style="background: ${markerColor}; color: white; font-family: monospace; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.7); box-shadow: 0 2px 6px rgba(0,0,0,0.4); white-space: nowrap; display: flex; align-items: center; gap: 4px;">
              <span>${isLandfall ? "🎯" : "📍"}</span>
              <span>${m.label}</span>
            </div>
            <div style="width: 2px; height: 10px; background: ${markerColor};"></div>
            <div style="width: 8px; height: 8px; border-radius: 50%; background: ${markerColor}; border: 2px solid white; box-shadow: 0 0 6px ${markerColor};"></div>
          </div>
        `;

        const customIcon = L.divIcon({
          className: "custom-gis-marker",
          html: markerHtml,
          iconSize: [140, 40],
          iconAnchor: [70, 36],
        });

        const lMarker = L.marker([m.lat, m.lon], {
          icon: customIcon,
          zIndexOffset: 1200,
        }).addTo(group);

        lMarker.bindPopup(`
          <div style="font-family: monospace; font-size: 11px; padding: 6px 8px; background: #182026; color: #fff; border-radius: 3px;">
            <div style="font-weight: bold; color: ${isLandfall ? "#f87171" : "#38bdf8"}; margin-bottom: 2px;">
              ${m.label}
            </div>
            <div>Position: ${m.lat.toFixed(2)}°N, ${m.lon.toFixed(2)}°E</div>
            ${m.sublabel ? `<div style="color: #cbd5e1; margin-top: 3px;">${m.sublabel}</div>` : ""}
          </div>
        `);
      });
    }

    // Auto-fit bounds if we have track points, with size-readiness check
    if (allLatLons.length > 0) {
      try {
        const bounds = L.latLngBounds(allLatLons);
        if (bounds.isValid()) {
          const mapSize = map.getSize();
          if (mapSize.x > 0 && mapSize.y > 0) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 8 });
          } else {
            map.setView(bounds.getCenter(), zoom);
          }
        } else {
          map.setView(center, zoom);
        }
      } catch (e) {
        map.setView(center, zoom);
      }
    } else {
      map.setView(center, zoom);
    }

    // Extra invalidation after vector rendering
    map.invalidateSize();
  }, [
    mapInstance,
    tracks,
    multiStormTracks,
    selectedPointTime,
    activeStormId,
    windRadii,
    forecastPath,
    markers,
    showWindRadii,
    showForecastCone,
    showTrackPoints,
    center,
    zoom,
  ]);

  const handleZoomIn = () => mapInstance?.zoomIn();
  const handleZoomOut = () => mapInstance?.zoomOut();
  const handleReset = () => {
    if (mapInstance) {
      mapInstance.setView(center, zoom);
    }
  };

  return (
    <div
      className={`relative w-full overflow-hidden select-none bg-[#0b1520] ${className}`}
      style={{ height: containerHeight, minHeight: "380px" }}
    >
      {/* Map DOM Element with explicit height & position */}
      <div
        ref={mapContainerRef}
        className="w-full h-full z-0"
        style={{ width: "100%", height: "100%", minHeight: "380px", position: "relative" }}
      />

      {/* Floating Coordinate Bar (Bottom-Left) */}
      <div className="absolute bottom-2.5 left-2.5 z-[500] bg-[#182026]/95 backdrop-blur-xs border border-slate-700/80 px-2 py-1 rounded-[3px] text-[10px] font-mono text-slate-300 pointer-events-none flex items-center gap-2 shadow-md">
        <span className="h-1.5 w-1.5 rounded-full bg-teal-400" />
        <span>
          {cursorCoords
            ? `LAT ${cursorCoords.lat.toFixed(2)}° · LON ${cursorCoords.lon.toFixed(2)}°`
            : "WGS84 · MERCATOR PROJECTION"}
        </span>
      </div>

      {/* Map Action Buttons (Top-Right) */}
      <div className="absolute top-2.5 right-2.5 z-[500] flex flex-col gap-1">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="h-7 w-7 bg-[#182026]/95 hover:bg-[#0f172a] text-slate-200 border border-slate-700 rounded-[3px] flex items-center justify-center font-bold text-sm cursor-pointer transition-colors shadow-md"
        >
          +
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="h-7 w-7 bg-[#182026]/95 hover:bg-[#0f172a] text-slate-200 border border-slate-700 rounded-[3px] flex items-center justify-center font-bold text-sm cursor-pointer transition-colors shadow-md"
        >
          &minus;
        </button>
        <button
          onClick={handleReset}
          title="Reset Basin View"
          className="h-7 w-7 bg-[#182026]/95 hover:bg-[#0f172a] text-slate-200 border border-slate-700 rounded-[3px] flex items-center justify-center text-[11px] font-mono cursor-pointer transition-colors shadow-md"
        >
          ⟲
        </button>
      </div>
    </div>
  );
}
