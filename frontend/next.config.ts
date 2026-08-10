import { join } from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Absolute ProvinceSystem root so ../shared/skins resolves (local + Docker).
  turbopack: {
    root: join(__dirname, ".."),
  },
  devIndicators: false,
};

export default nextConfig;
