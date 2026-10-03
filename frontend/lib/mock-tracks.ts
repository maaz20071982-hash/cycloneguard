// =============================================================================
// VERIFIED HISTORICAL TRACKS & TELEMETRY FOR NORTH INDIAN OCEAN
// Fallback / Demonstration Data for CycloneSense AI (SIH26070)
// =============================================================================

import { StormTrackGroup, MapTrackPoint } from "@/components/ui/CycloneMap";

export const MOCK_NORTH_INDIAN_OCEAN_TRACKS: StormTrackGroup[] = [
  {
    id: "2015301N11065",
    name: "CHAPALA",
    basin: "North Indian Ocean (Arabian Sea)",
    status: "HISTORICAL_VERIFIED",
    peak_intensity_kts: 115,
    color: "#ef4444",
    points: [
      { lat: 10.5, lon: 68.2, time: "2015-10-27T12:00:00Z", intensity_kts: 25, intensity_kmh: 46, pressure_mb: 1004, category: "Depression" },
      { lat: 11.2, lon: 67.5, time: "2015-10-28T00:00:00Z", intensity_kts: 25, intensity_kmh: 46, pressure_mb: 1003, category: "Depression" },
      { lat: 12.0, lon: 66.4, time: "2015-10-28T06:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1002, category: "Depression" },
      { lat: 12.6, lon: 65.5, time: "2015-10-28T12:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1001, category: "Depression" },
      { lat: 13.1, lon: 64.6, time: "2015-10-28T18:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1001, category: "Depression" }, // Target Fix t0
      { lat: 13.4, lon: 63.8, time: "2015-10-29T00:00:00Z", intensity_kts: 35, intensity_kmh: 65, pressure_mb: 998, category: "Deep Depression" },
      { lat: 13.8, lon: 62.9, time: "2015-10-29T06:00:00Z", intensity_kts: 45, intensity_kmh: 83, pressure_mb: 992, category: "Cyclonic Storm" },
      { lat: 14.1, lon: 61.8, time: "2015-10-29T12:00:00Z", intensity_kts: 55, intensity_kmh: 102, pressure_mb: 986, category: "Severe Cyclonic Storm" },
      { lat: 14.3, lon: 60.8, time: "2015-10-29T18:00:00Z", intensity_kts: 65, intensity_kmh: 120, pressure_mb: 980, category: "Very Severe Cyclonic Storm" }, // +24h RI Verified (+35kt surge)
      { lat: 14.5, lon: 59.5, time: "2015-10-30T00:00:00Z", intensity_kts: 85, intensity_kmh: 157, pressure_mb: 965, category: "Very Severe Cyclonic Storm" },
      { lat: 14.7, lon: 58.0, time: "2015-10-30T06:00:00Z", intensity_kts: 105, intensity_kmh: 194, pressure_mb: 948, category: "Extremely Severe Cyclonic Storm" },
      { lat: 14.4, lon: 56.4, time: "2015-10-30T12:00:00Z", intensity_kts: 115, intensity_kmh: 213, pressure_mb: 940, category: "Extremely Severe Cyclonic Storm" },
      { lat: 13.8, lon: 54.8, time: "2015-10-31T00:00:00Z", intensity_kts: 110, intensity_kmh: 204, pressure_mb: 944, category: "Extremely Severe Cyclonic Storm" },
      { lat: 13.5, lon: 52.8, time: "2015-11-01T00:00:00Z", intensity_kts: 95, intensity_kmh: 176, pressure_mb: 955, category: "Very Severe Cyclonic Storm" },
      { lat: 13.7, lon: 50.5, time: "2015-11-02T00:00:00Z", intensity_kts: 85, intensity_kmh: 157, pressure_mb: 964, category: "Very Severe Cyclonic Storm" },
      { lat: 14.1, lon: 49.0, time: "2015-11-03T00:00:00Z", intensity_kts: 70, intensity_kmh: 130, pressure_mb: 978, category: "Severe Cyclonic Storm (Landfall)" },
      { lat: 14.4, lon: 48.2, time: "2015-11-03T12:00:00Z", intensity_kts: 35, intensity_kmh: 65, pressure_mb: 998, category: "Deep Depression (Inland)" },
    ],
  },
  {
    id: "2023131N05093",
    name: "MOCHA",
    basin: "North Indian Ocean (Bay of Bengal)",
    status: "HISTORICAL_VERIFIED",
    peak_intensity_kts: 145,
    color: "#d946ef",
    points: [
      { lat: 8.5, lon: 88.5, time: "2023-05-09T06:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1002, category: "Depression" },
      { lat: 10.8, lon: 88.2, time: "2023-05-10T06:00:00Z", intensity_kts: 35, intensity_kmh: 65, pressure_mb: 998, category: "Deep Depression" },
      { lat: 12.3, lon: 87.8, time: "2023-05-11T06:00:00Z", intensity_kts: 45, intensity_kmh: 83, pressure_mb: 992, category: "Cyclonic Storm" },
      { lat: 13.9, lon: 87.7, time: "2023-05-12T06:00:00Z", intensity_kts: 70, intensity_kmh: 130, pressure_mb: 976, category: "Very Severe Cyclonic Storm" },
      { lat: 16.2, lon: 89.4, time: "2023-05-13T06:00:00Z", intensity_kts: 110, intensity_kmh: 204, pressure_mb: 945, category: "Extremely Severe Cyclonic Storm" },
      { lat: 18.8, lon: 91.5, time: "2023-05-14T00:00:00Z", intensity_kts: 145, intensity_kmh: 268, pressure_mb: 918, category: "Super Cyclonic Storm" },
      { lat: 20.3, lon: 92.9, time: "2023-05-14T08:00:00Z", intensity_kts: 115, intensity_kmh: 213, pressure_mb: 940, category: "Extremely Severe Cyclonic Storm (Landfall Sittwe)" },
    ],
  },
  {
    id: "2014297N11062",
    name: "NILOFAR",
    basin: "North Indian Ocean (Arabian Sea)",
    status: "HISTORICAL_VERIFIED",
    peak_intensity_kts: 110,
    color: "#0ea5e9",
    points: [
      { lat: 12.5, lon: 66.0, time: "2014-10-25T06:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1002, category: "Depression" },
      { lat: 13.8, lon: 64.5, time: "2014-10-26T00:00:00Z", intensity_kts: 45, intensity_kmh: 83, pressure_mb: 994, category: "Cyclonic Storm" },
      { lat: 15.2, lon: 63.0, time: "2014-10-27T00:00:00Z", intensity_kts: 75, intensity_kmh: 139, pressure_mb: 972, category: "Very Severe Cyclonic Storm" },
      { lat: 16.5, lon: 62.2, time: "2014-10-28T06:00:00Z", intensity_kts: 110, intensity_kmh: 204, pressure_mb: 950, category: "Extremely Severe Cyclonic Storm" },
      { lat: 18.2, lon: 63.8, time: "2014-10-29T12:00:00Z", intensity_kts: 80, intensity_kmh: 148, pressure_mb: 975, category: "Very Severe Cyclonic Storm" },
      { lat: 20.5, lon: 66.8, time: "2014-10-31T00:00:00Z", intensity_kts: 35, intensity_kmh: 65, pressure_mb: 998, category: "Cyclonic Storm (Approaching Naliya, Gujarat)" },
    ],
  },
  {
    id: "2013281N12098",
    name: "PHAILIN",
    basin: "North Indian Ocean (Bay of Bengal)",
    status: "HISTORICAL_VERIFIED",
    peak_intensity_kts: 115,
    color: "#f59e0b",
    points: [
      { lat: 12.0, lon: 96.0, time: "2013-10-08T06:00:00Z", intensity_kts: 25, intensity_kmh: 46, pressure_mb: 1004, category: "Depression" },
      { lat: 13.5, lon: 93.2, time: "2013-10-09T06:00:00Z", intensity_kts: 35, intensity_kmh: 65, pressure_mb: 998, category: "Deep Depression" },
      { lat: 15.0, lon: 89.8, time: "2013-10-10T12:00:00Z", intensity_kts: 65, intensity_kmh: 120, pressure_mb: 980, category: "Very Severe Cyclonic Storm" },
      { lat: 16.8, lon: 86.8, time: "2013-10-11T12:00:00Z", intensity_kts: 115, intensity_kmh: 213, pressure_mb: 940, category: "Extremely Severe Cyclonic Storm" },
      { lat: 18.5, lon: 85.0, time: "2013-10-12T15:00:00Z", intensity_kts: 115, intensity_kmh: 213, pressure_mb: 940, category: "Extremely Severe Cyclonic Storm (Gopalpur Landfall)" },
    ],
  },
  {
    id: "2014279N11096",
    name: "HUDHUD",
    basin: "North Indian Ocean (Bay of Bengal)",
    status: "HISTORICAL_VERIFIED",
    peak_intensity_kts: 100,
    color: "#ec4899",
    points: [
      { lat: 12.0, lon: 92.5, time: "2014-10-08T06:00:00Z", intensity_kts: 30, intensity_kmh: 55, pressure_mb: 1002, category: "Depression" },
      { lat: 13.8, lon: 89.0, time: "2014-10-09T12:00:00Z", intensity_kts: 45, intensity_kmh: 83, pressure_mb: 994, category: "Cyclonic Storm" },
      { lat: 15.6, lon: 86.2, time: "2014-10-10T18:00:00Z", intensity_kts: 70, intensity_kmh: 130, pressure_mb: 976, category: "Very Severe Cyclonic Storm" },
      { lat: 17.2, lon: 83.8, time: "2014-10-12T06:00:00Z", intensity_kts: 100, intensity_kmh: 185, pressure_mb: 950, category: "Very Severe Cyclonic Storm (Visakhapatnam Landfall)" },
    ],
  },
];
