import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    success: true,
    models: [
      {
        id: "cycloneguard-v3-frozen",
        name: "CycloneGuard-RI-Multimodal-TS-Final",
        version: "v3.0.0-frozen",
        status: "ACTIVE_PRODUCTION",
        type: "Regularized Balanced Logistic Regression (L2, C=1.0)",
        features_count: 61,
        kinematic_features: 23,
        spatial_features: 38,
        operating_threshold_tau: 0.125,
        dataset_benchmark: "NOAA IBTrACS v04r01 + NOAA HURSAT-B1 v06",
        training_method: "Leave-One-Storm-Out Zero Leakage Protocol",
      },
    ],
    active_deployments: 1,
  });
}
