import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-[#e2e6e9] bg-[#f1f3f4] text-[#5a6872] text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Purpose */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-[2px] bg-[#0f5b6c] text-white">
                <Shield className="h-3.5 w-3.5" />
              </div>
              <span className="text-sm font-bold text-[#182026] tracking-tight font-mono uppercase">
                CycloneGuard
              </span>
            </div>
            <p className="text-[#5a6872] max-w-sm leading-relaxed text-xs">
              Scientific multi-source satellite intelligence platform for tropical cyclone monitoring,
              intensity estimation, rapid-intensification analysis, and disaster-management decision support.
            </p>
            <div className="rounded-[3px] border border-[#fbd38d] bg-[#fef8ee] p-3 text-[11px] text-[#92400e] max-w-md">
              <strong className="font-semibold block uppercase tracking-wider mb-0.5 font-mono">
                Scientific Governance & Statutory Notice
              </strong>
              CycloneGuard is an academic and operational intelligence research platform. It does NOT issue official meteorological warnings.
              Always consult official national meteorological agencies (IMD, JTWC, NHC, JMA) for statutory disaster instructions.
            </div>
          </div>

          {/* Quick Navigation */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#182026] mb-3 font-mono">
              Platform
            </h4>
            <ul className="space-y-2">
              <li><Link href="/" className="hover:text-[#0f5b6c] transition-colors">Home</Link></li>
              <li><Link href="/demo" className="text-[#0f5b6c] font-bold hover:underline transition-colors">Judge Demo</Link></li>
              <li><Link href="/about" className="hover:text-[#0f5b6c] transition-colors">Science & Architecture</Link></li>
              <li><Link href="/user/cyclones" className="hover:text-[#0f5b6c] transition-colors">Cyclone Database</Link></li>
              <li><Link href="/login" className="hover:text-[#0f5b6c] transition-colors">Analyst Sign In</Link></li>
            </ul>
          </div>

          {/* Planned Capabilities */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#182026] mb-3 font-mono">
              Research Baseline
            </h4>
            <ul className="space-y-1.5 text-[#7d8c97] text-[11px] font-mono">
              <li>• Frozen Baseline (v3.0.0-frozen)</li>
              <li>• 61-Feature Multimodal Fusion</li>
              <li>• Standardized Linear Attribution</li>
              <li>• Real-time Sat Downlinks (Future)</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-[#e2e6e9] flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-[#7d8c97] font-mono">
          <p>© {new Date().getFullYear()} CycloneGuard Platform. Research & Demonstration Architecture.</p>
          <div className="flex items-center gap-3">
            <span>Meteorological Operations Center</span>
            <span>•</span>
            <span>Light-First Editorial Interface</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
