import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ProvinceSystem root so ../shared/skins constants resolve under turbopack.
  // Docker copies shared → /shared (see frontend/Dockerfile).
  turbopack: {
    root: "..",
  },
  devIndicators: false,
};

export default nextConfig;
