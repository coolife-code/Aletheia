# 🚀 Aletheia 魔搭社区空间部署指南

## 📋 部署前准备

### 1. 注册魔搭社区账号
- 访问 [ModelScope](https://www.modelscope.cn/)
- 注册并登录账号

### 2. 准备 API Key
- **阿里百炼 API Key**: 访问 [阿里云百炼](https://bailian.console.aliyun.com/) 获取
- **SerpAPI Key** (可选): 用于增强搜索功能
- **NewsAPI Key** (可选): 用于新闻搜索

## 🛠️ 部署步骤

### 方式一：通过 GitHub 导入部署（推荐）

1. **确保代码已推送到 GitHub**
   ```bash
   git push origin master
   ```

2. **进入魔搭社区空间创建页面**
   - 访问: https://www.modelscope.cn/spaces
   - 点击 "创建空间"

3. **配置空间信息**
   - **空间名称**: `aletheia`（或你喜欢的名称）
   - **空间类型**: 选择 "自定义 Docker"
   - **可见性**: 公开或私有
   - **代码源**: 选择 "GitHub"
   - **仓库地址**: `https://github.com/coolife-code/aletheia`

4. **配置环境变量**
   在空间设置中添加以下环境变量：

   | 变量名 | 值 | 是否必填 |
   |--------|-----|----------|
   | `OPENAI_API_KEY` | 你的阿里百炼 API Key | ✅ |
   | `OPENAI_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | ❌ |
   | `OPENAI_MODEL` | `deepseek-v3.2` | ❌ |
   | `SERPAPI_KEY` | 你的 SerpAPI Key | ❌ |
   | `NEWSAPI_KEY` | 你的 NewsAPI Key | ❌ |

5. **启动部署**
   - 点击 "创建并部署"
   - 等待构建完成（约 3-5 分钟）

### 方式二：本地构建后上传

1. **构建 Docker 镜像**
   ```bash
   docker build -t registry.cn-hangzhou.aliyuncs.com/your-namespace/aletheia:latest .
   ```

2. **推送到阿里云镜像仓库**
   ```bash
   docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/aletheia:latest
   ```

3. **在魔搭空间中使用自定义镜像**

## 📁 部署文件说明

### 关键文件

| 文件 | 说明 |
|------|------|
| `Dockerfile` | Docker 镜像构建配置 |
| `modelscope.yaml` | 魔搭空间配置文件 |
| `start.sh` | 容器启动脚本 |
| `frontend/next.config.ts` | 前端静态导出配置 |

### 目录结构

```
aletheia/
├── backend/           # 后端 FastAPI 服务
│   ├── app/          # 应用代码
│   ├── main.py       # 入口文件
│   └── requirements.txt
├── frontend/          # 前端 Next.js 应用
│   ├── src/          # 源码
│   └── dist/         # 构建产物（自动创建）
├── Dockerfile         # Docker 配置
├── modelscope.yaml    # 魔搭空间配置
├── start.sh          # 启动脚本
└── DEPLOY.md         # 本部署文档
```

## 🔧 配置说明

### 环境变量

#### 必需配置
- `OPENAI_API_KEY`: 阿里百炼 API Key，用于调用 DeepSeek 模型

#### 可选配置
- `OPENAI_BASE_URL`: API 基础 URL，默认使用阿里百炼
- `OPENAI_MODEL`: 模型名称，默认 `deepseek-v3.2`
- `SERPAPI_KEY`: SerpAPI 密钥，用于增强搜索
- `NEWSAPI_KEY`: NewsAPI 密钥，用于新闻搜索

### 资源需求

- **CPU**: 2 核
- **内存**: 4 GB
- **存储**: 2 GB
- **GPU**: 不需要

## 🐛 故障排查

### 1. 构建失败

**问题**: Docker 构建失败
```bash
# 本地测试构建
docker build -t aletheia:test .

# 查看构建日志
docker build --progress=plain -t aletheia:test .
```

### 2. 服务启动失败

**问题**: 容器启动后无法访问

检查日志：
```bash
# 在魔搭空间控制台查看日志
# 或本地测试
docker run -p 7860:7860 -e OPENAI_API_KEY=your-key aletheia:test
```

### 3. API 连接失败

**问题**: 前端无法连接后端

- 检查环境变量是否正确设置
- 确认 API Key 有效
- 查看后端服务日志

### 4. 前端显示空白

**问题**: 页面加载后空白

- 检查 `frontend/dist` 目录是否正确生成
- 确认静态文件路径正确
- 查看浏览器控制台错误

## 🔄 更新部署

### 自动更新（GitHub 集成）

如果通过 GitHub 导入部署，推送新代码后会自动触发重新部署：

```bash
git add .
git commit -m "更新功能"
git push origin master
```

### 手动更新

1. 在魔搭空间控制台点击 "重新部署"
2. 或更新镜像后重新部署

## 📊 监控和维护

### 查看日志

在魔搭空间控制台：
1. 进入你的空间
2. 点击 "日志" 标签
3. 查看实时日志

### 性能监控

- CPU 使用率
- 内存使用率
- 网络流量
- 请求响应时间

## 🌐 访问应用

部署成功后，访问地址：
```
https://www.modelscope.cn/spaces/{你的用户名}/aletheia
```

## 💡 最佳实践

1. **API Key 安全**
   - 使用魔搭空间的 Secret 功能存储敏感信息
   - 定期轮换 API Key
   - 不要在代码中硬编码密钥

2. **性能优化**
   - 启用响应缓存
   - 优化数据库查询
   - 使用 CDN 加速静态资源

3. **监控告警**
   - 设置错误率告警
   - 监控 API 调用配额
   - 跟踪用户访问量

## 📞 获取帮助

- **GitHub Issues**: https://github.com/coolife-code/aletheia/issues
- **魔搭社区文档**: https://www.modelscope.cn/docs
- **阿里百炼文档**: https://help.aliyun.com/zh/model-studio/

## 📝 更新记录

### v1.0.0 (2025-02-08)
- ✨ 初始版本发布
- 🔍 支持 DeepSeek 联网搜索
- 🤖 多智能体协作分析
- 📊 实时推理过程展示
