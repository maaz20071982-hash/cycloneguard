import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { StormProvider } from "@/lib/storm-context";

export const metadata: Metadata = {
  title: "CycloneSense AI — Tropical Cyclone Disaster Intelligence (SIH26070)",
  description:
    "Multi-source satellite intelligence platform for tropical cyclone monitoring, intensity estimation, rapid-intensification analysis, GIS risk assessment, and targeted disaster alert decision support.",
  keywords: [
    "tropical cyclone",
    "meteorology",
    "satellite intelligence",
    "rapid intensification",
    "INSAT-3D",
    "disaster management",
    "Smart India Hackathon 2026",
    "SIH26070",
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
        <AuthProvider>
          <StormProvider>{children}</StormProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
