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
  // 配置路径别名
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };
    return config;
  },
};

export default nextConfig;
