# ============================================
# Aletheia - AI 舆情谎言鉴定系统
# 魔搭社区空间部署 Dockerfile
# ============================================

FROM node:20-slim AS frontend-builder

# 设置工作目录
WORKDIR /app

# 先复制配置文件
COPY frontend/package*.json ./
COPY frontend/tsconfig.json ./
COPY frontend/next.config.ts ./
COPY frontend/postcss.config.mjs ./
COPY frontend/components.json ./
COPY frontend/eslint.config.mjs ./
COPY frontend/next-env.d.ts ./

# 安装依赖
RUN npm ci

# 复制源码
COPY frontend/src ./src
COPY frontend/public ./public

# 构建前端
RUN npm run build

# ============================================
# 后端服务阶段
# ============================================
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制后端依赖文件
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist

# 复制启动脚本
COPY start.sh ./
RUN chmod +x start.sh

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV BACKEND_PORT=8000

# 暴露端口
EXPOSE 7860

# 启动命令
CMD ["./start.sh"]
