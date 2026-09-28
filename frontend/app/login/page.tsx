"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, LogIn, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { useAuth } from "@/lib/auth-context";
import { ApiClientError } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: { email?: string; password?: string } = {};
    if (!email.trim()) {
      newErrors.email = "Email address is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const result = await login({ email, password });
      if (result.user.role === "ADMIN") {
        router.push("/admin/dashboard");
      } else {
        router.push("/user/dashboard");
      }
    } catch (err: any) {
      if (err instanceof ApiClientError) {
        setGeneralError(err.message);
      } else {
        setGeneralError("Authentication service unavailable. Please check backend connection.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-[#f8f9fa]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link href="/" className="flex items-center justify-center gap-2 mb-4 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-[3px] bg-[#0f5b6c] text-white">
            <Shield className="h-4 w-4" />
          </div>
          <span className="text-base font-bold tracking-tight text-[#182026] uppercase font-mono">
            CycloneGuard
          </span>
        </Link>
        <h2 className="text-center text-lg font-bold tracking-tight text-[#182026] uppercase font-mono">
          Sign In to Meteorological Portal
        </h2>
        <p className="mt-1 text-center text-xs text-[#5a6872]">
          Authorized workspace for cyclone analysts and system administrators
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white border border-[#e2e6e9] py-8 px-6 shadow-xs rounded-[4px] sm:px-8">
          {generalError && (
            <Alert variant="danger" title="Authentication Error" className="mb-5">
              {generalError}
            </Alert>
          )}

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <Input
                id="email"
                type="email"
                label="Official / Work Email"
                placeholder="analyst@agency.gov"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <Input
                id="password"
                type="password"
                label="Password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                disabled={isSubmitting}
              />
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-xs text-[#5a6872] cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded-[2px] border-[#cbd2d6] text-[#0f5b6c] focus:ring-[#0f5b6c]"
                />
                Remember this workstation
              </label>
              <span className="text-[10px] text-[#7d8c97] font-mono">Encrypted JWT</span>
            </div>

            <div className="pt-2">
              <Button type="submit" variant="primary" className="w-full" isLoading={isSubmitting}>
                <LogIn className="h-4 w-4 mr-2" />
                Sign In
              </Button>
            </div>
          </form>

          {/* Development Quick Credentials Note */}
          <div className="mt-6 pt-5 border-t border-[#e2e6e9] text-[11px] text-[#5a6872]">
            <span className="font-semibold text-[#182026] block mb-1 font-mono uppercase text-[10px]">
              Development Note:
            </span>
            <p className="leading-relaxed">
              Use seeded admin credentials from <code className="text-[#0f5b6c]">.env</code> or register a new user account below.
            </p>
          </div>

          <div className="mt-4 text-center text-xs text-[#5a6872]">
            Don't have an account?{" "}
            <Link href="/register" className="text-[#0f5b6c] hover:underline font-semibold">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
