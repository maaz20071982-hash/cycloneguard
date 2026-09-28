import React from "react";
import { cn } from "@/lib/utils";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options?: { value: string; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, id, options, children, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-xs font-semibold uppercase tracking-wider text-[#5a6872] mb-1.5 font-mono">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            id={id}
            ref={ref}
            className={cn(
              "flex h-9 w-full appearance-none rounded-[4px] border border-[#cbd2d6] bg-white px-3 py-1.5 text-xs text-[#182026] transition-colors focus:border-[#0f5b6c] focus:outline-none focus:ring-1 focus:ring-[#0f5b6c] disabled:cursor-not-allowed disabled:bg-[#f1f3f4] cursor-pointer",
              error && "border-[#b91c1c] focus:border-[#b91c1c] focus:ring-[#b91c1c]",
              className
            )}
            {...props}
          >
            {options ? options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            )) : children}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-[#5a6872]">
            <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>
        {error && <p className="mt-1 text-[11px] text-[#b91c1c] font-medium">{error}</p>}
      </div>
    );
  }
);
Select.displayName = "Select";
