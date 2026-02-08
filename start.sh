#!/bin/bash
# ============================================
# Aletheia 启动脚本
# 用于魔搭社区空间部署
# ============================================

set -e

echo "🚀 启动 Aletheia AI 舆情谎言鉴定系统..."

# 设置环境变量
export PORT=${PORT:-7860}
export BACKEND_PORT=${BACKEND_PORT:-8000}

# 如果环境变量文件存在，加载它
if [ -f "/app/backend/.env" ]; then
    echo "📋 加载环境变量..."
    export $(cat /app/backend/.env | grep -v '^#' | xargs)
fi

# 使用魔搭空间提供的环境变量（如果存在）
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ 使用魔搭空间配置的 API Key"
fi

# 启动后端服务
echo "🔧 启动后端服务 (端口: $BACKEND_PORT)..."
cd /app/backend
python -c "
import uvicorn
import sys
sys.path.insert(0, '/app/backend')
from main import app
uvicorn.run(app, host='0.0.0.0', port=$BACKEND_PORT, log_level='info')
" &

# 等待后端启动
sleep 3

echo "✅ 后端服务已启动"

# 启动前端静态文件服务
echo "🎨 启动前端服务 (端口: $PORT)..."
cd /app/frontend/dist

# 使用 Python 的 http.server 提供静态文件服务
python -c "
import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 7860))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # 处理前端路由
        if self.path.startswith('/api'):
            # API 请求转发到后端
            self.send_response(502)
            self.end_headers()
            return
        
        # 静态文件服务
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

with socketserver.TCPServer(('', PORT), MyHTTPRequestHandler) as httpd:
    print(f'Serving at port {PORT}')
    httpd.serve_forever()
"
