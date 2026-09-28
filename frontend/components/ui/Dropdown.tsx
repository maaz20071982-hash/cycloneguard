"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

export interface DropdownItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  danger?: boolean;
  onClick: () => void;
}

export interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: "left" | "right";
  className?: string;
}

export function Dropdown({
  trigger,
  items,
  align = "left",
  className = "",
}: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className={`relative inline-block text-left ${className}`} ref={containerRef}>
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>

      {isOpen && (
        <div
          className={`absolute z-50 mt-1 min-w-[180px] bg-[#ffffff] border border-[#e2e6e9] shadow-[0_4px_12px_rgba(0,0,0,0.08)] py-1 focus:outline-none ${
            align === "right" ? "right-0" : "left-0"
          }`}
          role="menu"
          aria-orientation="vertical"
        >
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                if (!item.disabled) {
                  item.onClick();
                  setIsOpen(false);
                }
              }}
              disabled={item.disabled}
              className={`w-full text-left px-3 py-1.5 text-xs flex items-center gap-2 transition-colors cursor-pointer ${
                item.disabled
                  ? "text-[#5f6b7c] opacity-50 cursor-not-allowed"
                  : item.danger
                  ? "text-[#b91c1c] hover:bg-[#fef2f2]"
                  : "text-[#182026] hover:bg-[#eaedef]"
              }`}
              role="menuitem"
            >
              {item.icon && <span className="shrink-0">{item.icon}</span>}
              <span className="truncate">{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
