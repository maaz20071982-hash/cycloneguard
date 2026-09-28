"use client";

import React, { useEffect } from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function Modal({ isOpen, onClose, title, description, children, className }: ModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-[2px] animate-in fade-in duration-150">
      <div
        className={cn(
          "relative w-full max-w-lg rounded-[4px] border border-[#cbd2d6] bg-white p-6 shadow-[0_4px_16px_rgba(24,32,38,0.12)] text-[#182026] animate-in zoom-in-98 duration-100",
          className
        )}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-[2px] text-[#5a6872] hover:text-[#182026] hover:bg-[#f1f3f4] p-1 transition-colors cursor-pointer"
          aria-label="Close dialog"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="mb-4 pr-6">
          <h3 className="text-base font-semibold text-[#182026]">{title}</h3>
          {description && <p className="text-xs text-[#5a6872] mt-1">{description}</p>}
        </div>

        <div className="text-xs leading-relaxed text-[#182026]">{children}</div>
      </div>
    </div>
  );
}
