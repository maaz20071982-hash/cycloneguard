"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { registerUser } from "@/lib/api/auth";
import { useAuth } from "@/lib/auth-context";
import { ApiClientError } from "@/lib/api/client";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!name.trim() || name.trim().length < 2) {
      newErrors.name = "Full name is required (at least 2 characters)";
    }

    if (!email.trim()) {
      newErrors.email = "Email address is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
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
      await registerUser({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        role: "USER",
      });

      const loginResult = await login({ email: email.trim().toLowerCase(), password });
      if (loginResult.user.role === "ADMIN") {
        router.push("/admin/dashboard");
      } else {
        router.push("/user/dashboard");
      }
    } catch (err: any) {
      if (err instanceof ApiClientError) {
        setGeneralError(err.message);
      } else {
        setGeneralError("Registration failed. Please verify backend service availability.");
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
          Create Platform Account
        </h2>
        <p className="mt-1 text-center text-xs text-[#5a6872]">
          Register for meteorological analyst workspace access
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white border border-[#e2e6e9] py-8 px-6 shadow-xs rounded-[4px] sm:px-8">
          {generalError && (
            <Alert variant="danger" title="Registration Error" className="mb-5">
              {generalError}
            </Alert>
          )}

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <Input
                id="name"
                label="Full Name / Operational Title"
                placeholder="Dr. Eleanor Vance"
                value={name}
                onChange={(e) => setName(e.target.value)}
                error={errors.name}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <Input
                id="email"
                type="email"
                label="Official / Organization Email"
                placeholder="e.vance@meteo-institute.org"
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
                label="Password (min 8 characters)"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <Input
                id="confirmPassword"
                type="password"
                label="Confirm Password"
                placeholder="••••••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                error={errors.confirmPassword}
                disabled={isSubmitting}
              />
            </div>

            <div className="pt-2">
              <Button type="submit" variant="primary" className="w-full" isLoading={isSubmitting}>
                <UserPlus className="h-4 w-4 mr-2" />
                Register Account
              </Button>
            </div>
          </form>

          <div className="mt-5 text-center text-xs text-[#5a6872] border-t border-[#e2e6e9] pt-4">
            Already have an account?{" "}
            <Link href="/login" className="text-[#0f5b6c] hover:underline font-semibold">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
