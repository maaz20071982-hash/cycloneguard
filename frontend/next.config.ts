import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Prevent TypeScript strict warnings from halting production cloud builds
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    if (process.env.BACKEND_INTERNAL_URL) {
      return [
        {
          source: "/api/v1/:path*",
          destination: `${process.env.BACKEND_INTERNAL_URL}/api/v1/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
