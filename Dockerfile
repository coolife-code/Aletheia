# ============================================
# Aletheia - AI 舆情谎言鉴定系统
# 魔搭社区空间部署 Dockerfile
# ============================================

# 前端构建阶段
FROM node:20-slim AS frontend-builder

WORKDIR /app

# 复制整个前端目录（避免分步复制的缓存问题）
COPY frontend/ ./

# 安装依赖并构建
RUN npm ci && npm run build

# ============================================
# 后端服务阶段
# ============================================
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制后端依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist

# 复制启动脚本
COPY start.sh ./
RUN chmod +x start.sh

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV BACKEND_PORT=8000

EXPOSE 7860

CMD ["./start.sh"]
