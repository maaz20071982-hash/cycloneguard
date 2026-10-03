import { NextResponse } from "next/server";
import { CHAPALA_CENTRAL_STORM } from "@/lib/central-storm-store";

export async function GET() {
  return NextResponse.json({
    success: true,
    predictions: [
      {
        id: "pred-chapala-t0",
        storm_id: CHAPALA_CENTRAL_STORM.storm_id,
        storm_name: CHAPALA_CENTRAL_STORM.storm_name,
        observation_time: CHAPALA_CENTRAL_STORM.observation_time_utc,
        empirical_ri_risk_index: CHAPALA_CENTRAL_STORM.explainable_confidence.empirical_ri_risk_index,
        operating_threshold_tau: CHAPALA_CENTRAL_STORM.explainable_confidence.operating_threshold_tau,
        risk_tier: CHAPALA_CENTRAL_STORM.explainable_confidence.risk_tier,
        confidence_pct: CHAPALA_CENTRAL_STORM.explainable_confidence.baseline_confidence_pct,
        ri_flag: true,
        historical_outcome: "RI Verified (+35 kt in 24h)",
      },
    ],
    total: 1,
    status: "Verified Historical Stream Active",
    message: "Inference stream operating on frozen verified benchmark",
  });
}
