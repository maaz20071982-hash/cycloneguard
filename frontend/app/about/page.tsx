"use client";

import React from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import {
  Shield,
  Layers,
  Activity,
  Cpu,
  BarChart3,
  Compass,
  Database,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Play,
} from "lucide-react";

export default function AboutSciencePage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fa] text-[#182026]">
      <Header />

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Breadcrumb Navigation */}
        <Breadcrumb
          items={[
            { label: "Home", href: "/" },
            { label: "Scientific Architecture & Methodology" },
          ]}
        />

        {/* Hero Section */}
        <div className="border-b border-[#e2e6e9] pb-6">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge variant="brand">Scientific Architecture Document</Badge>
            <span className="text-[11px] font-mono text-[#5f6b7c]">
              CycloneGuard-RI-Multimodal-TS-Final · v3.0.0-frozen
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#182026] uppercase font-mono">
            Scientific Methodology & System Architecture
          </h1>
          <p className="text-xs sm:text-sm text-[#5f6b7c] mt-2 leading-relaxed max-w-3xl">
            A comprehensive technical specification of CycloneGuard's multimodal rapid intensification prediction baseline, feature schemas, out-of-fold validation, data provenance, and governance boundaries.
          </p>

          <div className="pt-4 flex items-center gap-3">
            <Link href="/demo">
              <Button size="sm" variant="primary">
                <Play className="h-3.5 w-3.5 mr-1 text-white fill-white" />
                Launch Guided Judge Demo
              </Button>
            </Link>
            <Link href="/user/cyclones">
              <Button size="sm" variant="outline">
                <Database className="h-3.5 w-3.5 mr-1 text-[#0f5b6c]" />
                Explore Cyclone Case Studies
              </Button>
            </Link>
            <Link href="/admin/models">
              <Button size="sm" variant="ghost">
                <Cpu className="h-3.5 w-3.5 mr-1" />
                View Admin Model Card
              </Button>
            </Link>
          </div>
        </div>

        {/* ------------------------------------------------------------ */}
        {/* 1. WHAT CYCLONEGUARD DOES                                    */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="1. What CycloneGuard Does"
            subtitle="Operational mission, scope, and decision-support focus"
          />
          <div className="p-6 space-y-3 text-xs sm:text-sm text-[#5f6b7c] leading-relaxed">
            <p>
              CycloneGuard is an AI-assisted meteorological decision-support research prototype designed to detect early precursor signals of <strong>Tropical Cyclone Rapid Intensification (RI)</strong> across the North Indian Ocean basin.
            </p>
            <p>
              Rapid intensification is meteorologically defined as an increase in maximum sustained surface wind speed of at least <strong>30 knots (55 km/h) within a 24-hour window</strong> (&Delta;V_24h &ge; 30 kt). RI accounts for a disproportionate percentage of tropical cyclone disasters when an intensifying vortex reaches severe category strength shortly before coastal landfall, severely compressing disaster preparedness windows.
            </p>
            <p>
              CycloneGuard analyzes coincident observation fixes from historical archives to compute an <strong>Empirical RI Risk Index</strong> compared against an established operating threshold (&tau; = 0.125).
            </p>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 2. DATA SOURCES & MULTISPECTRAL SENSORS                      */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="2. Observational Data Sources"
            subtitle="NOAA IBTrACS best-track and NOAA HURSAT-B1 calibrated geostationary reanalysis"
          />
          <div className="p-6 space-y-4 text-xs text-[#5f6b7c] leading-relaxed">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
                <span className="font-bold font-mono text-[#0f5b6c] text-xs uppercase block">
                  1. Best-Track Kinematics (NOAA IBTrACS v04r01)
                </span>
                <p>
                  Global Tropical Cyclone Best Track archive providing verified 3-hourly and 6-hourly center fix coordinates, maximum sustained wind speeds (V_max, 1-minute sustained), minimum central surface pressure (P_min / MSLP), forward translation velocity, and historical rates of change.
                </p>
              </div>

              <div className="p-4 rounded-[4px] border border-[#e2e6e9] bg-[#f8f9fa] space-y-2">
                <span className="font-bold font-mono text-[#0f5b6c] text-xs uppercase block">
                  2. Satellite Radiometry (NOAA NCEI HURSAT-B1 v06)
                </span>
                <p>
                  Calibrated geostationary satellite archive delivering 64 &times; 64 pixel spatial patches centered on storm fixes:
                </p>
                <ul className="list-disc pl-4 space-y-1 text-[11px]">
                  <li><strong>IRWIN (11 µm Clean Window):</strong> Thermal cloud-top brightness temperatures (185 K to 300 K).</li>
                  <li><strong>IRWVP (6.7 µm Water Vapor):</strong> Upper-tropospheric moisture and convective organization.</li>
                  <li><strong>VSCHN (0.6 µm Visible):</strong> Daytime cloud reflectance (nighttime frames flagged 0.0).</li>
                </ul>
              </div>
            </div>

            <div className="p-3 bg-[#fef8ee] border border-[#fbd38d] rounded-[3px] text-[11px] text-[#b45309]">
              <strong>Environmental Reanalysis Ablation (Sprint 10):</strong> Coarse 2.5° atmospheric reanalysis variables (NCEP/DOE R2 vertical wind shear and OISST sea surface temperature) were systematically ablated. Environmental features diluted fine-scale kinematic signals and were <strong>strictly excluded from the final production model</strong>.
            </div>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 3 & 4. TEMPORAL & SATELLITE FEATURES                         */}
        {/* ------------------------------------------------------------ */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 3. Temporal Features */}
          <Panel>
            <PanelHeader
              title="3. Temporal Features (23 Features)"
              subtitle="Backward-looking kinematic trajectory indicators"
            />
            <div className="p-5 space-y-3 text-xs text-[#5f6b7c] leading-relaxed font-mono">
              <p className="font-sans">
                Extracted strictly from observation history prior to $t_0$. Captures vortex rotational momentum:
              </p>
              <ul className="list-disc pl-4 space-y-1.5 text-[11px] text-[#182026]">
                <li><code className="text-[#0f5b6c]">lat, lon</code>: Storm center coordinates</li>
                <li><code className="text-[#0f5b6c]">v_max</code>: Current sustained intensity (kt)</li>
                <li><code className="text-[#0f5b6c]">p_min</code>: Minimum central pressure (hPa)</li>
                <li><code className="text-[#0f5b6c]">dv_6h, dv_12h</code>: 6h & 12h wind tendencies</li>
                <li><code className="text-[#0f5b6c]">dp_6h</code>: 6h central pressure tendency</li>
                <li><code className="text-[#0f5b6c]">storm_speed, storm_bearing</code>: Forward kinematics</li>
                <li><code className="text-[#0f5b6c]">ir_min_change_6h</code>: 6h core cooling rate</li>
                <li>Quality flags & historical tendency indicators</li>
              </ul>
            </div>
          </Panel>

          {/* 4. Satellite Features */}
          <Panel>
            <PanelHeader
              title="4. Satellite Features (38 Features)"
              subtitle="Physical structural proxies extracted from HURSAT patches"
            />
            <div className="p-5 space-y-3 text-xs text-[#5f6b7c] leading-relaxed font-mono">
              <p className="font-sans">
                Computed across the $64 \times 64$ float32 infrared and multispectral grids:
              </p>
              <ul className="list-disc pl-4 space-y-1.5 text-[11px] text-[#182026]">
                <li><strong>Bulk Statistics (12):</strong> Mean, std, min, percentiles ($p_{10}$–$p_{90}$), cold fractions (&lt;233K, &lt;219K, &lt;203K)</li>
                <li><strong>Radial Core/Ring Proxies (11):</strong> Core mean $T_b$, core min, ring mean, core-ring gradient, azimuthal symmetry</li>
                <li><strong>Texture & Gradients (4):</strong> Max spatial gradient, mean gradient, local variance, spatial entropy</li>
                <li><strong>Multispectral & Visible (11):</strong> WV mean/min, IR-WV core difference, channel spatial correlation, visible reflectance</li>
              </ul>
            </div>
          </Panel>
        </div>

        {/* ------------------------------------------------------------ */}
        {/* 5. FROZEN PRODUCTION MODEL                                   */}
        {/* ------------------------------------------------------------ */}
        <Panel className="border-2 border-[#0f5b6c]">
          <PanelHeader
            title="5. Frozen Production Machine Learning Model"
            subtitle="CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen)"
          />
          <div className="p-6 space-y-4 text-xs font-mono">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[3px]">
                <span className="text-[10px] text-[#5f6b7c] uppercase block">Architecture</span>
                <span className="font-bold text-[#0f5b6c] text-xs">Balanced Logistic Reg.</span>
                <span className="text-[9px] text-[#5a6872] block">L2 penalty, C=1.0, lbfgs</span>
              </div>
              <div className="p-3 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[3px]">
                <span className="text-[10px] text-[#5f6b7c] uppercase block">Total Features</span>
                <span className="font-bold text-[#0f5b6c] text-xs">61 Features</span>
                <span className="text-[9px] text-[#5a6872] block">23 Temporal + 38 Spatial</span>
              </div>
              <div className="p-3 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[3px]">
                <span className="text-[10px] text-[#5f6b7c] uppercase block">Operating Threshold</span>
                <span className="font-bold text-[#b45309] text-xs">τ = 0.125</span>
                <span className="text-[9px] text-[#5a6872] block">Optimized on validation storm</span>
              </div>
              <div className="p-3 bg-[#f0f9fa] border border-[#a2d4dc] rounded-[3px]">
                <span className="text-[10px] text-[#5f6b7c] uppercase block">Output Type</span>
                <span className="font-bold text-[#182026] text-xs">Empirical Risk Index</span>
                <span className="text-[9px] text-[#5a6872] block">Uncalibrated score (0 to 1)</span>
              </div>
            </div>

            <p className="text-xs text-[#5f6b7c] font-sans leading-relaxed pt-1">
              The model applies balanced class weighting (<code className="text-[#0f5b6c]">class_weight="balanced"</code>) to compensate for severe class imbalance (~13% RI+ frequency). Deep neural networks (CNNs, Vision Transformers) were evaluated and strictly rejected due to sample scale constraints and high cross-storm overfitting.
            </p>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 6. VALIDATION APPROACH (LEAVE-ONE-STORM-OUT)                 */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="6. Validation Approach: Multi-Storm Generalization"
            subtitle="Leave-One-Storm-Out (LOSO) cross-validation across 6 historical lifecycles"
          />
          <div className="p-6 space-y-4 text-xs text-[#5f6b7c] leading-relaxed">
            <p>
              To eliminate dependency on a single held-out test storm, the final model was evaluated via <strong>Leave-One-Storm-Out (LOSO) cross-validation</strong> across 6 historical North Indian Ocean cyclones (299 supervised samples, 39 RI+ events):
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] text-[#182026]">
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>PHAILIN (2013)</strong>: BoB, N=45, 11 RI+
              </div>
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>HELEN (2013)</strong>: BoB, N=36, 0 RI+
              </div>
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>HUDHUD (2014)</strong>: BoB, N=57, 1 RI+
              </div>
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>NILOFAR (2014)</strong>: AS, N=66, 11 RI+
              </div>
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>MEGH (2015)</strong>: AS, N=42, 6 RI+
              </div>
              <div className="p-2.5 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px]">
                <strong>CHAPALA (2015)</strong>: AS, N=53, 10 RI+
              </div>
            </div>

            <div className="p-3 bg-white border border-[#cbd2d6] rounded-[3px] font-mono text-xs space-y-1">
              <div>• Mean Cross-Storm ROC-AUC: <strong>0.6997 ± 0.117</strong> (32.7% lower variance than temporal-only baseline)</div>
              <div>• Mean Cross-Storm PR-AUC: <strong>0.3832 ± 0.302</strong> (+29.5% higher discrimination than temporal-only)</div>
              <div>• Held-Out Benchmark Test on Chapala: <strong>ROC-AUC = 0.7791, Precision = 100.0%, 0 False Alarms</strong></div>
            </div>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 7. LEAKAGE PREVENTION & LOOKAHEAD PROTECTION                 */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="7. Data Leakage Prevention & Lookahead Protection"
            subtitle="Strict temporal quarantine separating observation fix t0 from future ground truth"
          />
          <div className="p-6 space-y-3 text-xs text-[#5f6b7c] leading-relaxed">
            <p>
              CycloneGuard strictly enforces three architectural safeguards to prevent temporal data leakage:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-xs text-[#182026]">
              <li>
                <strong>Train-Only Preprocessing:</strong> Imputation medians (<code className="font-mono text-[#0f5b6c]">SimpleImputer</code>) and feature scalers (<code className="font-mono text-[#0f5b6c]">StandardScaler</code>) are fitted strictly on training folds and applied downstream via <code className="font-mono text-[#0f5b6c]">transform()</code>. No test-storm statistics ever bleed into feature scaling.
              </li>
              <li>
                <strong>Strict 24h Outcome Quarantine:</strong> The future ground-truth observation (t_0 + 24h) is strictly isolated in a quarantined payload (<code className="font-mono text-[#0f5b6c]">HistoricalOutcomeVerification</code>) used solely for retrospective evaluation.
              </li>
              <li>
                <strong>Feature Contract Enforcement:</strong> Any submission containing future variables or forbidden environmental reanalysis fields is rejected by <code className="font-mono text-[#0f5b6c]">InferenceFeatureContract</code> with an explicit validation error.
              </li>
            </ul>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 8. EXPLAINABILITY & FEATURE ATTRIBUTION                      */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="8. Explainability: Standardized Feature Attribution"
            subtitle="Transparent linear decision factor weights with mandatory non-causality notices"
          />
          <div className="p-6 space-y-3 text-xs text-[#5f6b7c] leading-relaxed">
            <p>
              Because the frozen model is a Regularized Balanced Logistic Regression model, every prediction is fully explainable through <strong>standardized feature attribution</strong>:
            </p>
            <div className="p-3 bg-[#f8f9fa] border border-[#e2e6e9] rounded-[3px] font-mono text-xs text-[#182026]">
              Contribution = β_j × z_j = β_j × ((x_j - μ_j) / σ_j)
            </div>
            <p>
              The top supporting features (factors pushing the log-odds toward RI+) and top suppressing factors (factors dampening the risk score) are displayed with standardized weight bars.
            </p>
            <p className="font-semibold text-[#b45309]">
              Scientific Non-Causality Standard: Feature attributions represent linear decision factors within the statistical model manifold; they do NOT establish atmospheric thermodynamic causality.
            </p>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 9. KNOWN SCIENTIFIC LIMITATIONS                              */}
        {/* ------------------------------------------------------------ */}
        <Panel>
          <PanelHeader
            title="9. Documented Scientific Limitations"
            subtitle="Explicit boundary conditions and research constraints"
          />
          <div className="p-6 space-y-3 text-xs text-[#5f6b7c] leading-relaxed">
            <ul className="list-disc pl-5 space-y-2 text-[#182026]">
              <li>
                <strong>Sample Scale:</strong> Evaluated across 6 historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+ events). Global multi-basin operational generalization cannot be asserted without multi-basin archive expansion.
              </li>
              <li>
                <strong>Uncalibrated Score:</strong> Model outputs represent an empirical risk index, not a calibrated Bayesian probability.
              </li>
              <li>
                <strong>Cross-Storm Variance:</strong> Model precision varies across different storms (e.g. 100% on Chapala vs lower precision on Hudhud).
              </li>
              <li>
                <strong>Surveillance Mode:</strong> The platform operates in verified historical surveillance mode; automated live satellite ingest pipelines are not connected in the current prototype.
              </li>
            </ul>
          </div>
        </Panel>

        {/* ------------------------------------------------------------ */}
        {/* 10. AUTHORITATIVE WARNING AUTHORITY PRECEDENCE               */}
        {/* ------------------------------------------------------------ */}
        <Alert variant="warning" title="10. Authoritative Meteorological Warning Authority">
          <div className="space-y-2 text-xs leading-relaxed">
            <p className="font-semibold text-[#182026]">
              CycloneGuard is an academic and operational research decision-support tool. It does NOT issue official cyclone warnings, landfall alerts, or evacuation orders.
            </p>
            <p className="text-[#5a6872]">
              Official tropical cyclone bulletins, track forecasts, and civil defense advisories issued by statutory meteorological authorities—specifically the India Meteorological Department (IMD / RSMC New Delhi) and the Joint Typhoon Warning Center (JTWC)—remain strictly authoritative for all operational and life-safety planning.
            </p>
          </div>
        </Alert>

        {/* Bottom Navigation */}
        <div className="p-5 border border-[#e2e6e9] bg-white rounded-[4px] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-[#182026] font-mono uppercase">Explore the System</h4>
            <p className="text-xs text-[#5f6b7c]">Experience the guided presentation or examine the historical case studies.</p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/demo">
              <Button size="sm" variant="primary">
                <Play className="h-3.5 w-3.5 mr-1 text-white fill-white" />
                Launch Demo
              </Button>
            </Link>
            <Link href="/user/cyclones">
              <Button size="sm" variant="outline">
                <Database className="h-3.5 w-3.5 mr-1" />
                Cyclone Database
              </Button>
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
