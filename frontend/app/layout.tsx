import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "CycloneGuard — AI-Powered Tropical Cyclone Intelligence",
  description:
    "Multi-source satellite intelligence platform for tropical cyclone monitoring, intensity estimation, rapid-intensification analysis, and disaster-management decision support.",
  keywords: [
    "tropical cyclone",
    "meteorology",
    "satellite intelligence",
    "rapid intensification",
    "INSAT-3D",
    "Himawari-9",
    "disaster management",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-[var(--background)] text-[var(--foreground)] min-h-screen flex flex-col font-sans antialiased selection:bg-[var(--brand-subtle)] selection:text-[var(--brand)]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
