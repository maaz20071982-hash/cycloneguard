import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-[#080d16] text-slate-400 text-xs font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Purpose */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-sm shadow-cyan-500/30">
                <Shield className="h-4 w-4" />
              </div>
              <span className="text-base font-bold text-white tracking-tight font-sans">
                CycloneSense <span className="text-cyan-400">AI</span>
              </span>
            </div>
            <p className="text-slate-400 max-w-sm leading-relaxed text-xs">
              Scientific multi-source satellite intelligence platform for tropical cyclone monitoring,
              intensity estimation, rapid-intensification analysis, and disaster-management decision support.
            </p>
            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3.5 text-xs text-amber-300 max-w-md">
              <strong className="font-semibold block mb-1 font-sans text-amber-200">
                Scientific Governance & Statutory Notice
              </strong>
              CycloneSense AI is a research and decision-support prototype (SIH26070). Official warnings require authorized human forecaster review prior to release.
            </div>
          </div>

          {/* Quick Navigation */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3 font-sans">
              Platform Modules
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/" className="hover:text-cyan-400 transition-colors">Main Dashboard</Link></li>
              <li><Link href="/demo" className="text-cyan-400 font-semibold hover:underline transition-colors">Judge Demo (9 Stages)</Link></li>
              <li><Link href="/about" className="hover:text-cyan-400 transition-colors">Science & Architecture</Link></li>
              <li><Link href="/user/dashboard" className="hover:text-cyan-400 transition-colors">User Portal</Link></li>
              <li><Link href="/admin/dashboard" className="hover:text-cyan-400 transition-colors">Admin Console</Link></li>
            </ul>
          </div>

          {/* Planned Capabilities */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3 font-sans">
              Intelligence Pipeline
            </h4>
            <ul className="space-y-2 text-slate-400 text-xs">
              <li>• Multi-Source Sensor Fusion (6 Data Streams)</li>
              <li>• IMD Dvorak Intensity Estimation</li>
              <li>• AI Track & Uncertainty Cone Modeling</li>
              <li>• Geo-Spatial Impact & Shelter Matrix</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 font-sans">
          <p>© {new Date().getFullYear()} CycloneSense AI · SIH26070 Research Platform</p>
          <div className="flex items-center gap-3">
            <span>Meteorological Operations Center</span>
            <span>•</span>
            <span className="text-cyan-400 font-medium">Deep Oceanic Observatory</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
