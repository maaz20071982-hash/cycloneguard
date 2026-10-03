"use client";

import React from "react";
import Link from "next/link";
import { Shield, LayoutDashboard, ShieldAlert, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-[#f8f9fa] font-mono">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-2">
        <Link href="/" className="inline-flex items-center justify-center gap-2 mb-2 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-[3px] bg-[#0f5b6c] text-white">
            <Shield className="h-4 w-4" />
          </div>
          <span className="text-base font-bold tracking-tight text-[#182026] uppercase">
            CycloneSense AI
          </span>
        </Link>
        <h2 className="text-lg font-bold tracking-tight text-[#182026] uppercase">
          Open Prototype Access
        </h2>
        <p className="text-xs text-[#5a6872]">
          Registration is bypassed for Hackathon judges and reviewers. Enter directly:
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white border border-[#e2e6e9] py-8 px-6 shadow-xs rounded-[4px] sm:px-8 space-y-4">
          <div className="space-y-3">
            <Link href="/user/dashboard" className="block">
              <Button variant="primary" className="w-full text-xs h-10 flex items-center justify-center gap-2">
                <LayoutDashboard className="h-4 w-4" />
                Open User Dashboard
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>

            <Link href="/admin/dashboard" className="block">
              <Button variant="outline" className="w-full text-xs h-10 flex items-center justify-center gap-2 border-[#fca5a5] text-[#b91c1c] hover:bg-[#fef2f2]">
                <ShieldAlert className="h-4 w-4 text-[#b91c1c]" />
                Open Admin Console
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="pt-3 border-t border-[#e2e6e9] text-center">
            <Link href="/" className="text-xs text-[#5a6872] hover:text-[#0f5b6c]">
              &larr; Return to Home Disaster Portal
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
