import React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", error, label, helperText, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-xs font-semibold uppercase tracking-wider text-[#5a6872] mb-1.5 font-mono">
            {label}
          </label>
        )}
        <input
          id={id}
          type={type}
          ref={ref}
          className={cn(
            "flex h-9 w-full rounded-[4px] border border-[#cbd2d6] bg-white px-3 py-1.5 text-xs text-[#182026] placeholder:text-[#7d8c97] transition-colors focus:border-[#0f5b6c] focus:outline-none focus:ring-1 focus:ring-[#0f5b6c] disabled:cursor-not-allowed disabled:bg-[#f1f3f4] disabled:text-[#7d8c97]",
            error && "border-[#b91c1c] focus:border-[#b91c1c] focus:ring-[#b91c1c]",
            className
          )}
          {...props}
        />
        {helperText && !error && (
          <p className="mt-1 text-[11px] text-[#5a6872]">{helperText}</p>
        )}
        {error && <p className="mt-1 text-[11px] text-[#b91c1c] font-medium">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";

export function Label({ className, children, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label
      className={cn("block text-xs font-semibold uppercase tracking-wider text-[#5a6872] mb-1.5 font-mono", className)}
      {...props}
    >
      {children}
    </label>
  );
}
