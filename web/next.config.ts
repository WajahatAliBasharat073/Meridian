import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Dev-only badge defaults to bottom-left, where it sits over real
  // content on narrow viewports (e.g. the bandwidth control card on
  // Today) — move it out of the way. No effect on production builds.
  devIndicators: {
    position: "top-right",
  },
};

export default nextConfig;
