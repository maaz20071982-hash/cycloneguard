"use client";

import React, { useState } from "react";
import { PortalLayout } from "@/components/layout/PortalLayout";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { Modal } from "@/components/ui/Modal";
import { useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/utils";
import { changeUserPassword } from "@/lib/api/cyclones";
import { User, Shield, Key, LogOut, Lock, CheckCircle2, AlertCircle } from "lucide-react";

export default function ProfilePage() {
  const { user, logout } = useAuth();

  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordStatus, setPasswordStatus] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordStatus(null);

    if (newPassword.length < 8) {
      setPasswordStatus({ type: "error", text: "New password must be at least 8 characters long." });
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordStatus({ type: "error", text: "New passwords do not match." });
      return;
    }

    setIsSubmitting(true);
    try {
      await changeUserPassword(currentPassword, newPassword);
      setPasswordStatus({ type: "success", text: "Your password was successfully updated." });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => {
        setIsPasswordModalOpen(false);
        setPasswordStatus(null);
      }, 1500);
    } catch (err: any) {
      setPasswordStatus({
        type: "error",
        text: err.message || "Failed to update password. Please check your current password and try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PortalLayout type="user">
      <div className="space-y-6 max-w-3xl">
        {/* Breadcrumb */}
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/user/dashboard" },
            { label: "Analyst Profile" },
          ]}
        />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e2e6e9]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c]">
                Session Identity
              </span>
              <StatusBadge status="operational" text="Active Session" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#182026] flex items-center gap-2">
              <User className="h-6 w-6 text-[#0f5b6c]" />
              Analyst Profile & Credentials
            </h1>
            <p className="text-xs text-[#5f6b7c] mt-0.5">
              Account identity, assigned platform permissions, and security authorization controls.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={() => setIsPasswordModalOpen(true)}>
              <Key className="h-3.5 w-3.5 mr-1" />
              Change Password
            </Button>
            <Button size="sm" variant="danger" onClick={logout}>
              <LogOut className="h-3.5 w-3.5 mr-1" />
              Sign Out
            </Button>
          </div>
        </div>

        {/* Account Details Panel */}
        <Panel>
          <PanelHeader
            title="User Account Details"
            subtitle="Verified platform identity and role assignment"
          />
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block mb-1">
                  Full Name
                </span>
                <span className="text-sm font-semibold text-[#182026]">
                  {user?.name || "Meteorological Analyst"}
                </span>
              </div>

              <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block mb-1">
                  Email Address
                </span>
                <span className="text-sm font-mono text-[#182026]">
                  {user?.email || "—"}
                </span>
              </div>

              <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block mb-1">
                  Account Role
                </span>
                <div className="pt-0.5">
                  <Badge variant={user?.role === "ADMIN" ? "danger" : "default"}>
                    {user?.role || "USER"}
                  </Badge>
                </div>
              </div>

              <div className="p-3.5 border border-[#e2e6e9] bg-[#f8f9fa] rounded-[3px]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#5f6b7c] block mb-1">
                  Account Creation Date
                </span>
                <span className="text-xs font-mono text-[#182026]">
                  {user?.created_at ? formatDate(user.created_at) : "Sprint 1 Initial Session"}
                </span>
              </div>
            </div>

            <div className="pt-4 border-t border-[#e2e6e9] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 text-[#5f6b7c]">
                <Shield className="h-4 w-4 text-[#0f5b6c]" />
                <span>Role-Based Access: {user?.role === "ADMIN" ? "Full Administrative Scope" : "Standard Analyst Scope"}</span>
              </div>
              <span className="text-[#5f6b7c] text-[11px]">
                Bcrypt Password Hash • Secure Cryptographic Storage
              </span>
            </div>
          </div>
        </Panel>

        {/* Change Password Modal */}
        <Modal
          isOpen={isPasswordModalOpen}
          onClose={() => setIsPasswordModalOpen(false)}
          title="Change Account Password"
        >
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <p className="text-xs text-[#5f6b7c]">
              Enter your current password to authorize this security change, followed by your new password.
            </p>

            {passwordStatus && (
              <Alert
                variant={passwordStatus.type === "success" ? "success" : "danger"}
                title={passwordStatus.type === "success" ? "Success" : "Error"}
              >
                {passwordStatus.text}
              </Alert>
            )}

            <Input
              label="Current Password"
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••••••"
            />

            <Input
              label="New Password"
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Minimum 8 characters..."
            />

            <Input
              label="Confirm New Password"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter new password..."
            />

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#e2e6e9]">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsPasswordModalOpen(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={isSubmitting}>
                <Lock className="h-3.5 w-3.5 mr-1" />
                Update Password
              </Button>
            </div>
          </form>
        </Modal>

        {/* Security & Access Notice */}
        <Alert variant="info" title="Privacy & Security Assurance">
          CycloneGuard enforces strict security best practices: raw passwords, cryptographic salts, hashes, and session tokens are never rendered in client DOM or accessible to browser inspect tools.
        </Alert>
      </div>
    </PortalLayout>
  );
}
