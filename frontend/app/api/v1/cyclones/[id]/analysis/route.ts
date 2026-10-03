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
      status: "completed",
      ri_risk: {
        probability: storm.explainable_confidence.empirical_ri_risk_index,
        category: storm.explainable_confidence.risk_tier,
        confidence: storm.explainable_confidence.baseline_confidence_pct / 100,
        model_version: "v3.0.0-frozen",
        operating_threshold: storm.explainable_confidence.operating_threshold_tau,
      },
      evidence: {
        satellite_available: true,
        irwin_mean_tb_k: storm.observation_data.irwin_mean_tb_k,
        cold_cloud_fraction: storm.observation_data.cold_cloud_fraction_233k,
        shear_kts: storm.observation_data.nwp_environment.vertical_wind_shear_kts,
        sst_celsius: storm.observation_data.buoy_telemetry.sst_celsius,
      },
      explanation: {
        top_positive_features: storm.explainable_confidence.top_contributing_features,
        top_negative_features: [],
      },
    },
  });
}
