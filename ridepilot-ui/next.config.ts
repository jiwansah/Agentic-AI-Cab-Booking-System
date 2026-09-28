/*import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  
  experimental: {
    // Allows the HMR connection from your local network IP
    allowedOrigins: ['localhost:3000', '192.168.29.7:3000'],
  },
  reactStrictMode: true,
};

export default nextConfig;
*/

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Your other config options here */
  
  // Placed at the top level, without the port number (:3000)
  allowedDevOrigins: ['192.168.29.7'],
};

export default nextConfig;
