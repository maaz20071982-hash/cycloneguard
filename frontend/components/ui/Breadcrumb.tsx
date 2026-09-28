import React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className={cn("flex items-center text-xs font-mono", className)}>
      <ol className="flex items-center space-x-1.5 text-[#5a6872]">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} className="flex items-center">
              {index > 0 && <ChevronRight className="h-3 w-3 text-[#7d8c97] mx-1 shrink-0" />}
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className="hover:text-[#0f5b6c] transition-colors"
                >
                  {item.label}
                </Link>
              ) : (
                <span className={isLast ? "text-[#182026] font-semibold" : ""}>{item.label}</span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
