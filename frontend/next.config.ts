import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // 静态导出配置（用于魔搭空间部署）
  output: 'export',
  distDir: 'dist',
  // 禁用图片优化（静态导出需要）
  images: {
    unoptimized: true,
  },
  // 开发环境 API 代理
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
