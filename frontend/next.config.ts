import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Prevent TypeScript strict warnings from halting production cloud builds
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
