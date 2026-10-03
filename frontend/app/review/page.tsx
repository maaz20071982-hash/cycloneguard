"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { JudgeFlowNav } from "@/components/layout/JudgeFlowNav";
import { useStorm } from "@/lib/storm-context";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  Shield,
  FileCheck,
  CheckCircle2,
  Clock,
  ArrowRight,
  ArrowLeft,
  Lock,
  FileText,
  AlertTriangle,
  RotateCcw,
  ExternalLink,
  History,
  Cpu,
  Layers,
  Check,
  AlertCircle,
  Building,
  MapPin,
  Wind,
} from "lucide-react";

export default function AuthorityReviewPage() {
  const { currentStorm, selectStorm, availableStorms, updateHumanReview, isFullyAuthorized } = useStorm();
  const review = currentStorm.authorized_human_review;
  const pred = currentStorm.track_landfall_prediction;
  const risk = currentStorm.gis_risk_impact;

  const [notes, setNotes] = useState<string>(review.meteorologist_notes);
  const [isSigned, setIsSigned] = useState<boolean>(review.review_status === "OFFICIALLY_AUTHORIZED");
  const [reanalysisFeedback, setReanalysisFeedback] = useState<string | null>(null);

  // Sort exposed districts by risk severity: Red (Critical) -> Orange (High) -> Yellow (Moderate) -> Green (Low)
  const sortedDistricts = [...risk.exposed_districts].sort((a, b) => {
    const order: Record<string, number> = { Red: 1, Orange: 2, Yellow: 3, Green: 4 };
    return (order[a.risk_color] || 5) - (order[b.risk_color] || 5);
  });

  const handleApproveWarning = () => {
    updateHumanReview(notes, "OFFICIALLY_AUTHORIZED");
    setIsSigned(true);
    setReanalysisFeedback(null);
  };

  const handleRequestReanalysis = () => {
    setReanalysisFeedback("Re-analysis requested: Triggering ensemble re-weighting with relaxed priors...");
    setTimeout(() => {
      setIsSigned(false);
      updateHumanReview(notes, "PENDING_REVIEW");
      setReanalysisFeedback("Re-analysis complete: Updated satellite thermal gradient ingested. Ready for review.");
      setTimeout(() => setReanalysisFeedback(null), 4000);
    }, 1200);
  };

  // 7-Stage Compact Activity Timeline
  const ACTIVITY_TIMELINE = [
    { title: "Observations Received", time: "18:00 UTC", desc: "INSAT-3D, Buoys, Radar", status: "completed" },
    { title: "Fusion Complete", time: "18:02 UTC", desc: "61 Multimodal Features", status: "completed" },
    { title: "AI Detected", time: "18:03 UTC", desc: "13.1°N, 64.6°E Fix (96.2%)", status: "completed" },
    { title: "Forecast Generated", time: "18:04 UTC", desc: "+12h to +72h Kinematics", status: "completed" },
    { title: "Risk Assessed", time: "18:05 UTC", desc: "4 Coastal Impact Zones", status: "completed" },
    { title: "Alert Drafted", time: "18:06 UTC", desc: "Public / Marine / Officials", status: "completed" },
    {
      title: "Human Reviewed",
      time: isSigned ? review.review_timestamp_utc.slice(11, 16) + " UTC" : "Pending",
      desc: isSigned ? "Approved for Release" : "Awaiting Lead Sign-Off",
      status: isSigned ? "completed" : "active",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 w-full">
        {/* Judge Flow Stepper Navigation */}
        <JudgeFlowNav currentPath="/review" />

        {/* Stage Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#cbd2d6]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
                STAGE 07 · AUTHORIZED HUMAN REVIEW & GOVERNANCE
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[2px]">
                DEMO / SIMULATION
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] uppercase font-mono">
              Authority Review & Operational Bulletin Sign-Off
            </h1>
            <p className="text-xs text-[#5a6872] mt-0.5">
              Authorized human-in-the-loop verification, multi-district threat summary, and release sign-off for Cyclone {currentStorm.storm_name}.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-[#5a6872]">Target Storm:</span>
            <select
              value={currentStorm.storm_id}
              onChange={(e) => selectStorm(e.target.value)}
              className="bg-white border border-[#cbd2d6] text-[#182026] text-xs font-mono px-2 py-1 rounded-[3px]"
            >
              {availableStorms.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.basin.split("(")[0]})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 5. Compact Activity Timeline Bar */}
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-4 shadow-xs font-mono">
          <div className="flex items-center justify-between pb-2 border-b border-[#e2e6e9] mb-3">
            <span className="text-xs font-bold uppercase text-[#182026] flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 text-[#0f5b6c]" />
              End-to-End Operational Lifecycle Activity Timeline
            </span>
            <span className="text-[10px] text-[#5a6872]">7 Sequential Verification Milestones</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
            {ACTIVITY_TIMELINE.map((step, idx) => {
              const isDone = step.status === "completed";
              const isActive = step.status === "active";

              return (
                <div
                  key={idx}
                  className={`p-2.5 rounded-[3px] border transition-all text-xs ${
                    isDone
                      ? "bg-[#ecfdf5] border-[#a7f3d0] text-[#065f46]"
                      : isActive
                      ? "bg-[#fef8ee] border-[#fed7aa] text-[#b45309]"
                      : "bg-[#f8f9fa] border-[#e2e6e9] text-[#5a6872]"
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1">
                    <span className="font-bold">0{idx + 1}</span>
                    <span>{step.time}</span>
                  </div>
                  <div className="font-bold text-[11px] leading-tight text-[#182026]">
                    {step.title}
                  </div>
                  <div className="text-[9px] text-[#5a6872] mt-0.5 truncate">
                    {step.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Re-analysis Feedback Toast */}
        {reanalysisFeedback && (
          <div className="p-3 bg-[#edf5f7] border border-[#0f5b6c] text-[#0f5b6c] rounded-[4px] font-mono text-xs flex items-center gap-2 animate-fadeIn">
            <RotateCcw className="h-4 w-4 shrink-0 animate-spin text-[#0f5b6c]" />
            <span>{reanalysisFeedback}</span>
          </div>
        )}

        {/* ========================================================================= */}
        {/* Forecaster Review Panel & Sorted Districts Breakdown                      */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Left Column: Official Decision-Support Bulletin (7 cols) */}
          <div className="lg:col-span-7 p-6 rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs space-y-4 font-mono text-xs flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#e2e6e9] pb-3 gap-2">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-[#0f5b6c]" />
                  <div>
                    <h3 className="font-bold text-sm text-[#182026] uppercase">
                      Official Warning Bulletin Release
                    </h3>
                    <span className="text-[10px] text-[#5a6872]">
                      Bulletin ID: {review.bulletin_number} · Storm {currentStorm.storm_name}
                    </span>
                  </div>
                </div>
                <div>
                  {isSigned ? (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#ecfdf5] text-[#059669] border border-[#a7f3d0] rounded-[3px] font-bold text-xs">
                      <CheckCircle2 className="h-4 w-4" />
                      APPROVED FOR RELEASE
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#fef8ee] text-[#b45309] border border-[#fed7aa] rounded-[3px] font-bold text-xs">
                      <AlertTriangle className="h-4 w-4" />
                      PENDING HUMAN APPROVAL
                    </span>
                  )}
                </div>
              </div>

              {/* Reviewer & Status Header */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] bg-[#f8f9fa] p-3 rounded-[3px] border border-[#e2e6e9]">
                <div>
                  <span className="text-[#5a6872] block">Duty Officer:</span>
                  <span className="font-bold text-[#182026] truncate block">{review.duty_officer_name}</span>
                </div>
                <div>
                  <span className="text-[#5a6872] block">Designation:</span>
                  <span className="font-bold text-[#182026] truncate block">{review.duty_officer_designation}</span>
                </div>
                <div>
                  <span className="text-[#5a6872] block">Release Status:</span>
                  <span className={`font-bold ${isSigned ? "text-[#059669]" : "text-[#b45309]"}`}>
                    {isSigned ? "APPROVED FOR RELEASE" : "UNDER SCRUTINY"}
                  </span>
                </div>
                <div>
                  <span className="text-[#5a6872] block">Review Timestamp:</span>
                  <span className="font-bold text-[#182026] block truncate">
                    {review.review_timestamp_utc.replace("T", " ").slice(0, 19)} UTC
                  </span>
                </div>
              </div>

              {/* AI Forecast & Landfall Summary */}
              <div className="p-3 bg-[#edf5f7] border border-[#bcdbe2] rounded-[3px] space-y-2 text-xs">
                <span className="text-[10px] font-bold text-[#0f5b6c] uppercase block">
                  AI Decision-Support Trajectory Summary:
                </span>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div>
                    <span className="text-[#5a6872]">Predicted Landfall:</span>{" "}
                    <strong className="text-[#182026]">{pred.landfall_prediction.predicted_landfall_sector}</strong>
                  </div>
                  <div>
                    <span className="text-[#5a6872]">Impact Window:</span>{" "}
                    <strong className="text-[#b91c1c]">Nov 03, 00:00 - 06:00 UTC (~130h)</strong>
                  </div>
                  <div>
                    <span className="text-[#5a6872]">Peak Wind Intensity:</span>{" "}
                    <strong className="text-[#182026]">{pred.landfall_prediction.expected_intensity_at_landfall_kts} kt (Cat 1 Equivalent)</strong>
                  </div>
                  <div>
                    <span className="text-[#5a6872]">Landfall Confidence:</span>{" "}
                    <strong className="text-[#0f5b6c]">{pred.landfall_prediction.confidence_score_pct || 78}% (High Agreement)</strong>
                  </div>
                </div>
              </div>

              {/* Duty Officer Notes / Technical Justification */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[#182026] uppercase block">
                  Lead Meteorologist Technical Justification & Sign-off Notes:
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  disabled={isSigned}
                  rows={3}
                  className="w-full p-2.5 rounded-[3px] border border-[#cbd2d6] bg-white text-xs font-mono text-[#182026] focus:outline-hidden focus:border-[#0f5b6c] disabled:bg-[#f8f9fa] disabled:text-[#5a6872]"
                />
              </div>
            </div>

            {/* Approval Action Buttons: APPROVE WARNING & REQUEST RE-ANALYSIS */}
            <div className="pt-4 border-t border-[#e2e6e9] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="text-[10px] text-[#5a6872]">
                <div className="flex items-center gap-1">
                  <Lock className="h-3 w-3 text-[#0f5b6c]" />
                  <span>Audit Hash: {review.audit_hash.slice(0, 22)}...</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRequestReanalysis}
                  className="text-xs"
                >
                  <RotateCcw className="h-3 w-3 mr-1" />
                  REQUEST RE-ANALYSIS
                </Button>

                {!isSigned ? (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleApproveWarning}
                    className="text-xs bg-[#059669] hover:bg-[#047857] text-white"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                    APPROVE WARNING (RELEASE)
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsSigned(false);
                      updateHumanReview(notes, "PENDING_REVIEW");
                    }}
                    className="text-xs text-[#5a6872]"
                  >
                    Modify / Re-open
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Affected Districts Sorted by Risk (5 cols) */}
          <div className="lg:col-span-5 p-5 rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs space-y-4 font-mono text-xs flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <span className="font-bold text-[#182026] uppercase flex items-center gap-1.5 text-xs">
                  <MapPin className="h-4 w-4 text-[#0f5b6c]" />
                  Affected Districts Sorted by Risk
                </span>
                <span className="text-[10px] text-[#5a6872]">4 Coastal Zones</span>
              </div>

              <div className="space-y-2">
                {sortedDistricts.map((d, idx) => {
                  const isRed = d.risk_color === "Red";
                  const isOrange = d.risk_color === "Orange";
                  const isYellow = d.risk_color === "Yellow";

                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-[3px] border ${
                        isRed
                          ? "bg-[#fee2e2]/40 border-[#fecaca]"
                          : isOrange
                          ? "bg-[#ffedd5]/40 border-[#fed7aa]"
                          : isYellow
                          ? "bg-[#fef9c3]/40 border-[#fef08a]"
                          : "bg-[#dcfce7]/40 border-[#bbf7d0]"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-[11px] text-[#182026]">
                          {d.district_name}
                        </span>
                        <span
                          className={`text-[9px] px-1.5 py-0.2 rounded-[2px] font-bold border ${
                            isRed
                              ? "bg-[#fee2e2] text-[#b91c1c] border-[#fecaca]"
                              : isOrange
                              ? "bg-[#ffedd5] text-[#c2410c] border-[#fed7aa]"
                              : isYellow
                              ? "bg-[#fef9c3] text-[#a16207] border-[#fef08a]"
                              : "bg-[#dcfce7] text-[#15803d] border-[#bbf7d0]"
                          }`}
                        >
                          {d.risk_color.toUpperCase()} · {d.risk_level}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-1 text-[10px] text-[#5a6872]">
                        <span>Pop: <strong className="text-[#182026]">{d.simulated_population_at_risk.toLocaleString()}</strong></span>
                        <span>Surge: <strong className="text-[#0f5b6c]">{d.surge_height_meters}m</strong></span>
                        <span>Gust: <strong className="text-[#b91c1c]">{d.peak_wind_gust_kmh}km/h</strong></span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Mandatory Governance Disclaimer */}
              <div className="p-3 bg-[#fef8ee] border border-[#fed7aa] rounded-[3px] space-y-1 text-[10px] text-[#b45309] leading-relaxed">
                <span className="font-bold uppercase flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  MANDATORY GOVERNANCE PROTOCOL:
                </span>
                <p className="font-sans">
                  Official meteorological warnings strictly require authorized human review prior to public or civil defense dissemination. CycloneSense AI generates automated decision support; human forecaster signature constitutes legal authorization under NDMA/WMO operational guidelines.
                </p>
              </div>
            </div>

            <div className="pt-2 text-[10px] text-[#5a6872] flex justify-between border-t border-[#e2e6e9]">
              <span>Smart India Hackathon 2026</span>
              <span className="font-bold text-[#0f5b6c]">Problem SIH26070</span>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 6. HISTORICAL REPLAY (Fani 2019) & MODEL PERFORMANCE BENCHMARK            */}
        {/* ========================================================================= */}
        <div className="space-y-3 font-mono">
          <div className="flex items-center justify-between pb-1 border-b border-[#cbd2d6]">
            <span className="text-xs font-bold uppercase text-[#182026] flex items-center gap-1.5">
              <History className="h-4 w-4 text-[#0f5b6c]" />
              Validation Modules: Historical Replay & Certified Model Performance
            </span>
            <span className="px-1.5 py-0.2 text-[9px] font-bold bg-[#edf5f7] text-[#0f5b6c] border border-[#bcdbe2] rounded-[2px]">
              GROUND-TRUTH BENCHMARKS
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Card 1: Historical Replay (Fani 2019 / Amphan 2020) */}
            <div className="p-4 rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs space-y-3 text-xs flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#182026] flex items-center gap-1.5">
                    <History className="h-4 w-4 text-[#0f5b6c]" />
                    Historical Replay: Cyclone Fani (2019)
                  </span>
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-[#edf5f7] text-[#0f5b6c] rounded-[2px]">
                    IBTrACS Ground Truth
                  </span>
                </div>
                <p className="text-[11px] text-[#5a6872] font-sans leading-relaxed">
                  Replay the historical trajectory and verified Rapid Intensification sequence of Extremely Severe Cyclonic Storm Fani (2019) in the Bay of Bengal, validated against official IMD best track archives.
                </p>
                <div className="p-2.5 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-[#5a6872]">Storm Identifier:</span>
                    <strong className="text-[#182026]">2019117N09088 (FANI)</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#5a6872]">Observed Peak Intensity:</span>
                    <strong className="text-[#b91c1c]">215 km/h (932 hPa)</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#5a6872]">Rapid Intensification:</span>
                    <strong className="text-[#059669]">VERIFIED TRUE POSITIVE (+45 kt / 24h)</strong>
                  </div>
                </div>
              </div>

              <Link href="/user/history">
                <Button variant="outline" size="sm" className="w-full text-xs text-[#0f5b6c] border-[#0f5b6c]">
                  Open Historical Cyclone Archive
                  <ExternalLink className="h-3 w-3 ml-1" />
                </Button>
              </Link>
            </div>

            {/* Card 2: Certified Model Performance Benchmark */}
            <div className="p-4 rounded-[4px] border border-[#cbd2d6] bg-white shadow-xs space-y-3 text-xs flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#182026] flex items-center gap-1.5">
                    <Cpu className="h-4 w-4 text-[#0f5b6c]" />
                    Model Performance & Audit Card
                  </span>
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-[#ecfdf5] text-[#059669] rounded-[2px]">
                    FROZEN v3.0.0
                  </span>
                </div>
                <p className="text-[11px] text-[#5a6872] font-sans leading-relaxed">
                  Evaluation metrics audited under Leave-One-Storm-Out cross-validation across 368 North Indian Ocean test points with strict temporal ordering and zero data leakage.
                </p>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                    <span className="text-[9px] text-[#5a6872] uppercase block">ROC-AUC</span>
                    <span className="text-sm font-bold text-[#0f5b6c]">0.865</span>
                  </div>
                  <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                    <span className="text-[9px] text-[#5a6872] uppercase block">PR-AUC</span>
                    <span className="text-sm font-bold text-[#182026]">0.642</span>
                  </div>
                  <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                    <span className="text-[9px] text-[#5a6872] uppercase block">Brier Score</span>
                    <span className="text-sm font-bold text-[#059669]">0.118</span>
                  </div>
                </div>
              </div>

              <Link href="/admin/models">
                <Button variant="outline" size="sm" className="w-full text-xs text-[#0f5b6c] border-[#0f5b6c]">
                  View Full ML Model Registry
                  <ExternalLink className="h-3 w-3 ml-1" />
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#cbd2d6]">
          <Link href="/alerts">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-3.5 w-3.5 mr-1" />
              Previous: Targeted Alerts
            </Button>
          </Link>
          <Link href="/">
            <Button variant="primary" size="sm">
              Complete: Return to Dashboard
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
