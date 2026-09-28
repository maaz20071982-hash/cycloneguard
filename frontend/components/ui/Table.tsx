import React from "react";
import { cn } from "@/lib/utils";

export function Table({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="relative w-full overflow-auto rounded-[4px] border border-[#e2e6e9] bg-white">
      <table className={cn("w-full caption-bottom text-xs text-left", className)} {...props} />
    </div>
  );
}

export function TableHeader({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead
      className={cn(
        "border-b border-[#e2e6e9] bg-[#f1f3f4] text-[10px] uppercase tracking-wider text-[#5a6872] font-mono",
        className
      )}
      {...props}
    />
  );
}

export function TableBody({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={cn("divide-y divide-[#edf0f2] text-[#182026]", className)} {...props} />;
}

export function TableRow({ className, ...props }: React.HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={cn(
        "transition-colors hover:bg-[#f8f9fa] data-[state=selected]:bg-[#f1f3f4]",
        className
      )}
      {...props}
    />
  );
}

export function TableHead({ className, ...props }: React.ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        "h-9 px-3.5 text-left align-middle font-semibold text-[#5a6872] [&:has([role=checkbox])]:pr-0 select-none",
        className
      )}
      {...props}
    />
  );
}

export function TableCell({ className, ...props }: React.TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td
      className={cn("p-3.5 align-middle text-xs [&:has([role=checkbox])]:pr-0", className)}
      {...props}
    />
  );
}
