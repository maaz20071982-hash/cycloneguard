import React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading = false, children, disabled, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-[#0f5b6c] focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none rounded-[4px] cursor-pointer select-none text-sm";

    const variants = {
      primary: "bg-[#0f5b6c] text-white hover:bg-[#0a4350] active:bg-[#083640] shadow-sm",
      secondary: "bg-white text-[#182026] hover:bg-[#f1f3f4] border border-[#e2e6e9] active:bg-[#eaedef]",
      outline: "border border-[#cbd2d6] bg-transparent text-[#182026] hover:bg-[#f1f3f4] active:bg-[#eaedef]",
      danger: "bg-[#b91c1c] text-white hover:bg-[#991b1b] active:bg-[#7f1d1d] shadow-sm",
      ghost: "text-[#5a6872] hover:text-[#182026] hover:bg-[#f1f3f4] active:bg-[#eaedef]",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-9 px-4 text-xs font-semibold gap-2",
      lg: "h-11 px-5 text-sm font-semibold gap-2.5",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin h-3.5 w-3.5 mr-1 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
