"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { checkBackendHealth } from "@/lib/api/system";
import {
  ArrowRight,
  Compass,
  Satellite,
  Layers,
  Zap,
  Shield,
  ChevronRight,
  Play,
  Activity,
  CheckCircle2,
  Clock,
  TrendingUp,
  AlertTriangle,
  Eye,
  Database,
  ArrowDown,
} from "lucide-react";

export default function LandingPage() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [backendVersion, setBackendVersion] = useState<string>("0.1.0");

  useEffect(() => {
    checkBackendHealth()
      .then((res) => {
        setBackendOk(true);
        setBackendVersion(res.version);
      })
      .catch(() => {
        setBackendOk(false);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      {/* ------------------------------------------------------------ */}
      {/* 1. HERO SECTION — ANSWERS WHAT, WHY, HOW IMMEDIATELY          */}
      {/* ------------------------------------------------------------ */}
      <section className="pt-10 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {/* Verification Status Pill */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span className="text-[11px] font-mono uppercase tracking-widest text-[#0f5b6c] font-bold">
            Scientific Research Prototype
          </span>
          <span className="text-[#cbd2d6]">•</span>
          <StatusBadge
            status={backendOk ? "operational" : "standby"}
            label={backendOk ? "Inference Engine Ready" : "System Standby"}
          />
          <span className="text-[#cbd2d6]">•</span>
          <span className="text-[11px] font-mono text-[#5a6872]">
            Model: CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen)
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          {/* Left Narrative */}
          <div className="lg:col-span-7 space-y-6">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#182026] uppercase font-mono leading-[1.08]">
              CYCLONEGUARD
            </h1>

            <p className="text-lg sm:text-xl font-medium text-[#0f5b6c] leading-snug">
              Detecting rapid tropical cyclone intensification before it becomes a disaster-management surprise.
            </p>

            <p className="text-sm sm:text-base text-[#5a6872] leading-relaxed max-w-2xl">
              AI-assisted analysis of cyclone evolution using temporal track behaviour and multi-source satellite evidence. Built for high-consequence meteorological decision support across the North Indian Ocean.
            </p>

            {/* Primary CTAs including Judge Demo */}
            <div className="pt-2 flex flex-wrap items-center gap-3">
              <Link href="/demo">
                <Button size="lg" variant="primary" className="shadow-sm">
                  <Play className="h-4 w-4 mr-2 text-white fill-white" />
                  Launch Guided Judge Demo
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Link href="/user/cyclones">
                <Button size="lg" variant="outline">
                  <Database className="h-4 w-4 mr-2 text-[#0f5b6c]" />
                  Explore Historical Cyclones
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button size="lg" variant="ghost">
                  View How It Works
                  <ArrowDown className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </div>

            {/* Disclaimers & Governance Notice */}
            <div className="pt-4 border-t border-[#e2e6e9] flex flex-wrap items-center gap-4 text-[11px] text-[#7d8c97] font-mono">
              <span className="flex items-center gap-1.5 text-[#0f5b6c] font-semibold">
                <CheckCircle2 className="h-3.5 w-3.5" />
                61-FEATURE CANONICAL CONTRACT
              </span>
              <span>•</span>
              <span>ZERO FABRICATED DATA</span>
              <span>•</span>
              <span className="text-[#b45309]">OFFICIAL WARNINGS REMAIN AUTHORITATIVE</span>
            </div>
          </div>

          {/* Right Hero Card: 3 Core Questions At a Glance */}
          <div className="lg:col-span-5">
            <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-5 shadow-[0_2px_8px_rgba(0,0,0,0.06)] space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-3">
                <span className="text-[11px] font-bold text-[#182026] uppercase tracking-wider flex items-center gap-2">
                  <Compass className="h-4 w-4 text-[#0f5b6c]" />
                  Platform At A Glance
                </span>
                <Badge variant="brand">3 Core Questions</Badge>
              </div>

              {/* 1. WHAT */}
              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1">
                <span className="text-[10px] font-bold text-[#0f5b6c] uppercase tracking-wider block">
                  1. WHAT is CycloneGuard?
                </span>
                <p className="text-[12px] text-[#182026] font-sans leading-relaxed">
                  An AI early-warning decision-support system analyzing tropical cyclone rapid intensification (≥30 kt wind increase in 24 hours) from observational data.
                </p>
              </div>

              {/* 2. WHY */}
              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1">
                <span className="text-[10px] font-bold text-[#b45309] uppercase tracking-wider block">
                  2. WHY does it matter?
                </span>
                <p className="text-[12px] text-[#182026] font-sans leading-relaxed">
                  Rapid intensification causes unexpected coastal disasters when a weak storm explodes into a major cyclone shortly before landfall, leaving inadequate evacuation time.
                </p>
              </div>

              {/* 3. HOW */}
              <div className="p-3 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9] space-y-1">
                <span className="text-[10px] font-bold text-[#1b7a4f] uppercase tracking-wider block">
                  3. HOW does it work?
                </span>
                <p className="text-[12px] text-[#182026] font-sans leading-relaxed">
                  Extracts 23 temporal kinematic features and 38 HURSAT-B1 spatial structural proxies into a frozen regularized model yielding an Empirical RI Risk Index vs τ = 0.125.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------ */}
      {/* 2. THE PROBLEM — UNDERSTANDING RAPID INTENSIFICATION          */}
      {/* ------------------------------------------------------------ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-[#e2e6e9] bg-white">
        <div className="max-w-3xl mb-10">
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-semibold mb-1">
            Forecasting Dilemma
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#182026] uppercase font-mono">
            The Problem: Why Traditional Monitoring Gets Surprised
          </h2>
          <p className="text-sm text-[#5a6872] mt-2 leading-relaxed">
            Cyclone intensity can change rapidly. Rapid Intensification (RI)—defined as an intensity surge of at least 30 knots (55 km/h) in 24 hours—accounts for a disproportionate share of catastrophic tropical cyclone landfalls.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
            <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block">SIGNAL 01</span>
            <h3 className="text-xs font-bold uppercase font-mono text-[#182026]">Current Intensity</h3>
            <p className="text-xs text-[#5a6872] leading-relaxed">
              A single snapshot of current Vmax cannot distinguish a stalling depression from an accelerating convective vortex.
            </p>
          </div>

          <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
            <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block">SIGNAL 02</span>
            <h3 className="text-xs font-bold uppercase font-mono text-[#182026]">Recent Evolution</h3>
            <p className="text-xs text-[#5a6872] leading-relaxed">
              6h and 12h wind tendencies (ΔV6h, ΔV12h) and pressure drop rates reveal kinetic acceleration before surface winds peak.
            </p>
          </div>

          <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
            <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block">SIGNAL 03</span>
            <h3 className="text-xs font-bold uppercase font-mono text-[#182026]">Cloud Structure</h3>
            <p className="text-xs text-[#5a6872] leading-relaxed">
              Central cold cover, radial cloud-top gradients, and convective asymmetry reflect latent heat release and vortex organization.
            </p>
          </div>

          <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
            <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block">SIGNAL 04</span>
            <h3 className="text-xs font-bold uppercase font-mono text-[#182026]">Satellite Evidence</h3>
            <p className="text-xs text-[#5a6872] leading-relaxed">
              Calibrated geostationary infrared (IRWIN 11 µm) captures brightness temperature distributions that track data alone cannot represent.
            </p>
          </div>

          <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
            <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block">SIGNAL 05</span>
            <h3 className="text-xs font-bold uppercase font-mono text-[#182026]">Decision Uncertainty</h3>
            <p className="text-xs text-[#5a6872] leading-relaxed">
              Operating at a calibrated empirical threshold (τ = 0.125) balances early warning lead-time with operational false alarms.
            </p>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------ */}
      {/* 3. HOW IT WORKS — VISUAL PIPELINE                             */}
      {/* ------------------------------------------------------------ */}
      <section id="how-it-works" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-[#e2e6e9]">
        <div className="max-w-3xl mb-12">
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-semibold mb-1">
            System Architecture
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#182026] uppercase font-mono">
            How It Works: Evidence-First Pipeline
          </h2>
          <p className="text-sm text-[#5a6872] mt-2 leading-relaxed">
            CycloneGuard operates a strictly quarantined sequential pipeline where future ground truth is isolated and every prediction links to traceable observational evidence.
          </p>
        </div>

        {/* Visual Pipeline Progression */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            {
              step: "01",
              title: "OBSERVATIONS",
              badge: "INPUT FEEDS",
              desc: "NOAA IBTrACS best-track history and NOAA HURSAT-B1 calibrated geostationary satellite imagery at time t0.",
            },
            {
              step: "02",
              title: "TEMPORAL + SATELLITE",
              badge: "61 FEATURES",
              desc: "23 kinematic trajectory variables + 38 HURSAT spatial structural proxies (core Tb, radial rings, gradients).",
            },
            {
              step: "03",
              title: "AI MODEL",
              badge: "FROZEN v3.0.0",
              desc: "Regularized Balanced Logistic Regression (L2, C=1.0, lbfgs) trained with strict leave-one-storm-out isolation.",
            },
            {
              step: "04",
              title: "EMPIRICAL RI RISK",
              badge: "THRESHOLD τ=0.125",
              desc: "Generates an Empirical RI Risk Index. Scores ≥ 0.125 flag high likelihood of impending rapid intensification.",
            },
            {
              step: "05",
              title: "DECISION SUPPORT",
              badge: "VERIFICATION",
              desc: "Displays standardized feature attribution, satellite evidence, and historical 24h outcome for verification.",
            },
          ].map((item, idx) => (
            <div key={item.step} className="p-4 rounded-[4px] border border-[#e2e6e9] bg-white relative flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-mono text-[#0f5b6c] font-bold">{item.step}</span>
                  <Badge variant="neutral" className="text-[9px]">{item.badge}</Badge>
                </div>
                <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-[#182026] mb-1.5">
                  {item.title}
                </h4>
                <p className="text-[11px] text-[#5a6872] leading-relaxed">
                  {item.desc}
                </p>
              </div>
              {idx < 4 && (
                <div className="hidden md:flex justify-end pt-2 text-[#cbd2d6]">
                  <ChevronRight className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ------------------------------------------------------------ */}
      {/* 4. REAL HISTORICAL EVIDENCE — PROOF ON CYCLONE CHAPALA         */}
      {/* ------------------------------------------------------------ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-[#e2e6e9] bg-white">
        <div className="max-w-3xl mb-8">
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#0f5b6c] font-semibold mb-1">
            Ground-Truth Verification
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#182026] uppercase font-mono">
            Real Evidence: Cyclone Chapala RI Detection Benchmark
          </h2>
          <p className="text-sm text-[#5a6872] mt-2 leading-relaxed">
            CycloneGuard uses actual historical evidence from NOAA IBTrACS and HURSAT-B1. Below is the verified observation fix for Cyclone Chapala at the exact onset of its historic rapid intensification surge.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Authentic Satellite Patch Visual */}
          <div className="lg:col-span-5 p-5 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold font-mono text-[#182026] uppercase">
                  NOAA HURSAT-B1 IRWIN (11 µm)
                </span>
                <Badge variant="brand">2015-10-28 18:00 UTC</Badge>
              </div>
              <p className="text-[11px] text-[#5a6872]">
                Authentic 64×64 float32 geostationary infrared brightness temperature patch centered on Cyclone Chapala (13.1° N, 64.6° E).
              </p>

              {/* Satellite Image Frame with Live API Endpoint */}
              <div className="relative aspect-square w-full rounded-[3px] overflow-hidden border border-[#cbd2d6] bg-[#0b1520] flex items-center justify-center mt-3">
                <img
                  src="/api/v1/cyclones/2015301N11065/observations/20151028180000/patch/IRWIN"
                  alt="Cyclone Chapala HURSAT-B1 Clean IR Window Brightness Temperature Patch"
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    // Fallback visual if backend is offline
                    e.currentTarget.style.display = "none";
                  }}
                />
                <div className="absolute bottom-2 left-2 right-2 bg-black/75 px-2.5 py-1 rounded-[2px] text-[10px] font-mono text-white flex justify-between">
                  <span>Tb Range: 185 K – 300 K</span>
                  <span>Patch: 64 × 64 px</span>
                </div>
              </div>
            </div>

            <div className="mt-3 text-[11px] font-mono text-[#5a6872] border-t border-[#e2e6e9] pt-2 flex justify-between">
              <span>Source: NOAA NCEI HURSAT-B1 v06</span>
              <span className="text-[#0f5b6c] font-semibold">Zero Synthetic Imagery</span>
            </div>
          </div>

          {/* Model Signals vs Historical Outcome */}
          <div className="lg:col-span-7 space-y-4 flex flex-col justify-between">
            {/* Section A: What The Model Saw at t0 */}
            <div className="p-4 rounded-[4px] border border-[#cbd2d6] bg-[#ffffff] space-y-3">
              <div className="flex items-center justify-between border-b border-[#e2e6e9] pb-2">
                <span className="text-xs font-bold font-mono text-[#0f5b6c] uppercase flex items-center gap-1.5">
                  <Activity className="h-4 w-4" />
                  What the Model Saw at Observation Fix (t0)
                </span>
                <span className="text-[11px] font-mono text-[#5a6872]">Current Vmax: <strong>30 kt</strong> (Tropical Depression)</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                  <span className="text-[9px] text-[#5a6872] block">Current Intensity</span>
                  <span className="font-bold text-[#182026] text-sm">30 kt</span>
                </div>
                <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                  <span className="text-[9px] text-[#5a6872] block">6h Tendency (ΔV6h)</span>
                  <span className="font-bold text-[#0f5b6c] text-sm">+5 kt</span>
                </div>
                <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                  <span className="text-[9px] text-[#5a6872] block">Central Pressure</span>
                  <span className="font-bold text-[#182026] text-sm">1000 hPa</span>
                </div>
                <div className="p-2 bg-[#f8f9fa] rounded-[3px] border border-[#e2e6e9]">
                  <span className="text-[9px] text-[#5a6872] block">Translation Speed</span>
                  <span className="font-bold text-[#182026] text-sm">6.8 kt</span>
                </div>
              </div>

              {/* Model Result Callout */}
              <div className="p-3 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[3px] flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-[#0f5b6c] font-bold block uppercase">
                    Empirical RI Risk Index
                  </span>
                  <span className="text-xl font-bold font-mono text-[#0f5b6c]">0.3592</span>
                  <span className="text-[11px] text-[#5a6872] ml-2">vs Operating Threshold τ = 0.125</span>
                </div>
                <Badge variant="danger" className="text-xs px-2.5 py-1 font-mono font-bold">
                  HIGH_RISK (RI+ Flagged)
                </Badge>
              </div>
            </div>

            {/* Section B: Historical Ground-Truth Outcome */}
            <div className="p-4 rounded-[4px] border-2 border-[#b91c1c] bg-[#fef2f2]/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold font-mono text-[#b91c1c] uppercase flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" />
                  Historical Outcome — Not Used as Model Input
                </span>
                <Badge variant="danger">Verified Ground Truth (t0 + 24h)</Badge>
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs font-mono pt-1">
                <div className="p-2 bg-white rounded-[3px] border border-[#fecaca]">
                  <span className="text-[9px] text-[#5a6872] block">Observed Vmax (t0+24h)</span>
                  <span className="font-bold text-[#b91c1c] text-sm">65 kt (Hurricane Force)</span>
                </div>
                <div className="p-2 bg-white rounded-[3px] border border-[#fecaca]">
                  <span className="text-[9px] text-[#5a6872] block">24h Intensity Delta</span>
                  <span className="font-bold text-[#b91c1c] text-sm">+35 kt (RI Threshold ≥30)</span>
                </div>
                <div className="p-2 bg-white rounded-[3px] border border-[#fecaca]">
                  <span className="text-[9px] text-[#5a6872] block">Ground Truth Target</span>
                  <span className="font-bold text-[#b91c1c] text-sm">RI Occurred (RI+)</span>
                </div>
              </div>

              <p className="text-[11px] text-[#5a6872] pt-1 leading-relaxed">
                The model-estimated RI signal (0.3592) was triggered at 30 kt intensity before the verified 24-hour intensification outcome. (This historical case study illustrates model sensitivity, not guaranteed operational superiority).
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------ */}
      {/* 5. SCIENTIFIC STATUS & GOVERNANCE DISCLAIMERS                 */}
      {/* ------------------------------------------------------------ */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-[#e2e6e9]">
        <div className="rounded-[4px] border border-[#cbd2d6] bg-white p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-2 text-[#0f5b6c]">
            <Shield className="h-5 w-5" />
            <span className="text-xs font-mono uppercase tracking-wider font-bold">
              Scientific Classification C · Research Prototype Status
            </span>
          </div>

          <h3 className="text-base sm:text-lg font-bold text-[#182026] font-mono">
            Scientific Governance, Dataset Boundaries & Authoritative Precedence
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#5a6872] leading-relaxed pt-1">
            <div className="space-y-2">
              <p>
                • <strong>Research Prototype:</strong> CycloneGuard is an academic and operational research decision-support tool. It operates exclusively on verified historical cyclone observations (NOAA IBTrACS v04r01) and geostationary reanalysis (NOAA HURSAT-B1 v06).
              </p>
              <p>
                • <strong>Uncalibrated Risk Index:</strong> The model score (0.0 to 1.0) represents an empirical risk ranking index, not a calibrated Bayesian or frequentist probability.
              </p>
            </div>

            <div className="space-y-2">
              <p>
                • <strong>Dataset Scale:</strong> Supervised training and validation are bounded by 6 historical North Indian Ocean cyclone lifecycles (299 supervised observations, 39 RI+ events).
              </p>
              <p>
                • <strong>Authoritative Precedence:</strong> Under no circumstances should CycloneGuard outputs supersede official advisories, track cones, or evacuation warnings issued by the India Meteorological Department (IMD), Joint Typhoon Warning Center (JTWC), or Regional Specialized Meteorological Centres (RSMC).
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------ */}
      {/* 6. CALL TO ACTION                                             */}
      {/* ------------------------------------------------------------ */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-[#e2e6e9] bg-[#edf5f7]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-[#182026] font-mono uppercase">
              Ready for the Judge Walkthrough?
            </h3>
            <p className="text-xs text-[#5a6872]">
              Experience the 8-stage interactive demo or explore full historical case-study workstations.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link href="/demo">
              <Button size="lg" variant="primary">
                <Play className="h-4 w-4 mr-2 text-white fill-white" />
                Start Guided Demo
              </Button>
            </Link>
            <Link href="/user/cyclones">
              <Button size="lg" variant="outline">
                Explore Cyclone Case Studies
              </Button>
            </Link>
            <Link href="/about">
              <Button size="lg" variant="ghost">
                Read Science Architecture
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
