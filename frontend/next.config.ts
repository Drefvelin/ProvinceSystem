import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ProvinceSystem root so ../shared/skins constants resolve under turbopack.
  turbopack: {
    root: "..",
  },
  devIndicators: false,
};

export default nextConfig;
