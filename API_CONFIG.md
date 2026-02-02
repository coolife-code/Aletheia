# Aletheia - API 配置清单

本文档列出系统运行所需的所有外部 API，按 Agent 分类整理。

---

## 1. Parser Agent 所需 API

### 1.1 LLM API（必需）

| API 名称 | 用途 | 必需性 | 推荐方案 |
|----------|------|--------|----------|
| **OpenAI API** | claim_extractor, query_generator | 高 | GPT-4 / GPT-3.5-turbo |
| **Claude API** | claim_extractor, query_generator | 高 | Claude 3.5 Sonnet |
| **Azure OpenAI** | claim_extractor, query_generator | 中 | 企业合规场景 |
| **DeepSeek API** | claim_extractor, query_generator | 中 | 国产替代方案 |

**配置项**:
```env
LLM_PROVIDER=openai  # openai | claude | azure | deepseek
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Claude 配置
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# DeepSeek 配置
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
```

### 1.2 OCR/ASR API（可选）

| API 名称 | 用途 | 必需性 | 备注 |
|----------|------|--------|------|
| **百度 OCR** | 图片文字提取 | 中 | 中文场景效果好 |
| **腾讯云 OCR** | 图片文字提取 | 中 | - |
| **Azure Computer Vision** | 图片文字提取 | 中 | 多语言支持 |
| **Whisper API** | 视频/音频转文字 | 低 | OpenAI 语音识别 |
| **阿里云智能语音** | 视频/音频转文字 | 低 | 中文优化 |

**配置项**:
```env
# OCR 配置
OCR_PROVIDER=baidu  # baidu | tencent | azure
BAIDU_OCR_API_KEY=xxx
BAIDU_OCR_SECRET_KEY=xxx

# ASR 配置
ASR_PROVIDER=whisper  # whisper | aliyun
OPENAI_API_KEY=sk-xxx  # Whisper 复用 OpenAI Key
```

---

## 2. Search Agent 所需 API

### 2.1 通用搜索引擎 API（必需）

| API 名称 | 用途 | 必需性 | 免费额度 | 特点 |
|----------|------|--------|----------|------|
| **SerpAPI** ⭐推荐 | 聚合搜索 | 高 | 100次/月 | 一站式多引擎、结构化数据、无需管理多个API |
| **百度千帆搜索** ⭐推荐 | 网页/新闻搜索 | 高 | 需开通 | 中文搜索优化、国内访问稳定、与文心大模型生态整合 |
| **Google Custom Search** | web_searcher | 中 | 100次/天 | 需配置CSE、结果可控 |
| **Bing Search API** | web_searcher | 中 | 1000次/月 | 微软生态、中文支持好 |
| **Tavily** | AI 搜索 | 低 | 1000次/月 | AI优化、自动提取内容 |

**配置项**:
```env
# 方案一：SerpAPI（推荐 - 一站式解决，适合国际搜索）
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-serpapi-key

# 方案二：百度千帆搜索（推荐 - 中文搜索优化，国内稳定）
SEARCH_PROVIDER=baidu_qianfan
BAIDU_QIANFAN_API_KEY=your-qianfan-api-key
BAIDU_QIANFAN_SECRET_KEY=your-qianfan-secret-key

# 备选方案
# Google Search
GOOGLE_SEARCH_API_KEY=AIzaSyAxxx
GOOGLE_SEARCH_ENGINE_ID=xxx

# Bing Search
BING_SEARCH_API_KEY=xxx

# Tavily
TAVILY_API_KEY=tvly-xxx
```

### 2.2 新闻搜索 API（推荐）

| API 名称 | 用途 | 必需性 | 备注 |
|----------|------|--------|------|
| **NewsAPI** | news_searcher | 中 | 全球新闻源 |
| **GNews** | news_searcher | 中 | 替代方案 |
| **New York Times API** | news_searcher | 低 | 英文新闻 |
| **腾讯新闻 API** | news_searcher | 低 | 中文新闻 |

**配置项**:
```env
NEWSAPI_KEY=xxx
GNEWS_API_KEY=xxx
NYT_API_KEY=xxx
```

### 2.3 学术搜索 API（可选）

| API 名称 | 用途 | 必需性 | 备注 |
|----------|------|--------|------|
| **Google Scholar** | academic_searcher | 低 | 需爬虫/第三方服务 |
| **Semantic Scholar** | academic_searcher | 低 | 免费 API |
| **CrossRef** | academic_searcher | 低 | 学术论文元数据 |
| **CNKI** | academic_searcher | 低 | 中文论文，需机构账号 |
| **万方数据** | academic_searcher | 低 | 中文论文 |

**配置项**:
```env
SEMANTIC_SCHOLAR_API_KEY=xxx
CNKI_USERNAME=xxx
CNKI_PASSWORD=xxx
```

### 2.4 社交媒体 API（可选）

| API 名称 | 用途 | 必需性 | 备注 |
|----------|------|--------|------|
| **Twitter/X API** | social_searcher | 低 | v2 付费 |
| **Reddit API** | social_searcher | 低 | 免费 |
| **微博 API** | social_searcher | 低 | 需申请 |
| **知乎 API** | social_searcher | 低 | 非官方/爬虫 |

**配置项**:
```env
TWITTER_BEARER_TOKEN=xxx
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx

REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USER_AGENT=aletheia/1.0

WEIBO_APP_KEY=xxx
WEIBO_APP_SECRET=xxx
```

---

## 3. Verdict Agent 所需 API

### 3.1 LLM API（必需）

与 Parser Agent 共用 LLM 配置，用于:
- cross_validator (多源证据交叉验证)
- contradiction_detector (矛盾检测)
- logical_reasoner (逻辑推理)
- fact_checker (事实核查)

**建议**: 使用更强的模型（GPT-4 / Claude 3.5 Opus）

```env
# 可单独配置 Verdict Agent 使用更强的模型
VERDICT_LLM_MODEL=gpt-4
VERDICT_LLM_TEMPERATURE=0.1  # 低温度，更确定性
```

### 3.2 Embedding API（推荐）

| API 名称 | 用途 | 必需性 | 备注 |
|----------|------|--------|------|
| **OpenAI Embedding** | relevance_ranker, deduplicator | 中 | text-embedding-3-small |
| **Azure OpenAI Embedding** | relevance_ranker, deduplicator | 中 | 企业合规 |
| **本地 Embedding** | relevance_ranker, deduplicator | 中 | 隐私优先 |

**配置项**:
```env
EMBEDDING_PROVIDER=openai  # openai | azure | local
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

## 4. 基础设施 API

### 4.1 数据库（必需）

| 服务 | 用途 | 必需性 |
|------|------|--------|
| **PostgreSQL** | 主数据库 | 高 |
| **Redis** | 缓存/队列 | 高 |
| **Milvus** | 向量数据库 | 中 |
| **Elasticsearch** | 全文搜索 | 低 |

**配置项**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/aletheia
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost
MILVUS_PORT=19530
ELASTICSEARCH_URL=http://localhost:9200
```

### 4.2 监控与日志（推荐）

| 服务 | 用途 | 必需性 |
|------|------|--------|
| **Sentry** | 错误追踪 | 推荐 |
| **LogRocket** | 前端监控 | 可选 |

**配置项**:
```env
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

---

## 5. API 配置汇总表

### 5.1 必需配置（MVP 最小可用）

| 类别 | API | 配置项 | 获取地址 |
|------|-----|--------|----------|
| LLM | OpenAI / 文心一言 | `OPENAI_API_KEY` / `QIANFAN_ACCESS_KEY` | https://platform.openai.com / https://qianfan.baidu.com |
| 搜索 | **SerpAPI** 或 **百度千帆** | `SERPAPI_KEY` / `BAIDU_QIANFAN_API_KEY` | https://serpapi.com / https://qianfan.baidu.com |
| 数据库 | PostgreSQL | `DATABASE_URL` | 自建/云服务 |
| 缓存 | Redis | `REDIS_URL` | 自建/云服务 |

> 💡 **推荐方案**:
> - **国际搜索**: SerpAPI 一个 Key 访问 Google、Bing、Yahoo 等多引擎
> - **中文搜索**: 百度千帆搜索，国内访问稳定，与文心大模型生态整合

### 5.2 推荐配置（完整功能）

| 类别 | API | 配置项 | 获取地址 |
|------|-----|--------|----------|
| LLM 备用 | Claude | `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| 搜索备用 | Bing | `BING_SEARCH_API_KEY` | https://www.microsoft.com/en-us/bing/apis |
| 新闻 | NewsAPI | `NEWSAPI_KEY` | https://newsapi.org |
| Embedding | OpenAI | `OPENAI_EMBEDDING_MODEL` | 复用 OpenAI Key |
| 向量库 | Milvus | `MILVUS_HOST` | https://milvus.io |

### 5.3 可选配置（增强功能）

| 类别 | API | 配置项 | 获取地址 |
|------|-----|--------|----------|
| OCR | 百度 OCR | `BAIDU_OCR_API_KEY` | https://cloud.baidu.com |
| ASR | Whisper | `OPENAI_API_KEY` | 复用 OpenAI Key |
| 学术 | Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | https://www.semanticscholar.org |
| 社交 | Twitter | `TWITTER_BEARER_TOKEN` | https://developer.twitter.com |
| 监控 | Sentry | `SENTRY_DSN` | https://sentry.io |

---

## 6. 配置优先级建议

### 阶段一：MVP（最小可行产品）

#### 方案 A：SerpAPI（适合国际搜索）
```env
# 仅需 4 个配置
OPENAI_API_KEY=sk-xxx
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-serpapi-key
DATABASE_URL=postgresql://user:pass@localhost:5432/aletheia
REDIS_URL=redis://localhost:6379/0
```

#### 方案 B：百度千帆（适合中文搜索）
```env
# 仅需 4 个配置
OPENAI_API_KEY=sk-xxx  # 或使用文心一言
SEARCH_PROVIDER=baidu_qianfan
BAIDU_QIANFAN_API_KEY=your-qianfan-api-key
BAIDU_QIANFAN_SECRET_KEY=your-qianfan-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/aletheia
REDIS_URL=redis://localhost:6379/0
```

### 阶段二：生产环境
```env
# LLM 主备
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# 搜索多源
GOOGLE_SEARCH_API_KEY=AIzaSyAxxx
GOOGLE_SEARCH_ENGINE_ID=xxx
BING_SEARCH_API_KEY=xxx
NEWSAPI_KEY=xxx

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/aletheia
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost

# Embedding
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 阶段三：完整功能
```env
# 包含所有可选 API
# ...（完整配置见上文）
```

---

## 7. 成本估算

### 7.1 开发测试阶段（月均）

| API | 调用量 | 预估费用 |
|-----|--------|----------|
| OpenAI GPT-4 | 10K 次 | $30-50 |
| Google Search | 3K 次 | 免费 |
| NewsAPI | 1K 次 | 免费 |
| **总计** | - | **$30-50** |

### 7.2 生产环境（月均，1000 次鉴定）

| API | 调用量 | 预估费用 |
|-----|--------|----------|
| OpenAI GPT-4 | 100K 次 | $300-500 |
| SerpAPI | 50K 次 | $250 (5K/月) |
| NewsAPI | 30K 次 | $15 |
| Embedding | 200K 次 | $10 |
| **总计** | - | **$575-775** |

> 💡 **成本优化**: SerpAPI 虽然单价较高，但省去了维护多个搜索 API 的成本，且提供更稳定的结构化数据。

---

## 8. 配置示例文件

### 8.1 `.env.example`

```env
# ============================================
# Aletheia API 配置示例
# 复制为 .env 并填入实际值
# ============================================

# ------------------- LLM -------------------
# 主 LLM 提供商: openai | claude | azure | deepseek
LLM_PROVIDER=openai

# OpenAI 配置
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Claude 配置（备用）
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Verdict Agent 专用（可选，默认使用主配置）
VERDICT_LLM_MODEL=gpt-4
VERDICT_LLM_TEMPERATURE=0.1

# ------------------- 搜索 -------------------
# 搜索提供商: serpapi | baidu_qianfan | google | bing
SEARCH_PROVIDER=serpapi

# SerpAPI（推荐 - 一站式搜索解决方案）
SERPAPI_KEY=your-serpapi-key

# 百度千帆搜索（推荐 - 中文搜索优化）
BAIDU_QIANFAN_API_KEY=your-qianfan-api-key
BAIDU_QIANFAN_SECRET_KEY=your-qianfan-secret-key

# Google Custom Search（备选）
GOOGLE_SEARCH_API_KEY=AIzaSyA-your-google-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Bing Search（备选）
BING_SEARCH_API_KEY=your-bing-key

# NewsAPI
NEWSAPI_KEY=your-newsapi-key

# ------------------- Embedding -------------------
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ------------------- OCR/ASR -------------------
# OCR 提供商: baidu | tencent | azure
OCR_PROVIDER=baidu
BAIDU_OCR_API_KEY=your-baidu-ocr-key
BAIDU_OCR_SECRET_KEY=your-baidu-ocr-secret

# ASR 提供商: whisper | aliyun
ASR_PROVIDER=whisper
# Whisper 复用 OPENAI_API_KEY

# ------------------- 数据库 -------------------
DATABASE_URL=postgresql://user:password@localhost:5432/aletheia
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost
MILVUS_PORT=19530

# ------------------- 监控 -------------------
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# ------------------- 其他 -------------------
ENVIRONMENT=development  # development | staging | production
DEBUG=true
LOG_LEVEL=INFO
```

---

## 9. 获取 API Key 指南

### 9.1 OpenAI
1. 访问 https://platform.openai.com
2. 注册/登录账号
3. 进入 Billing 充值
4. 进入 API Keys 创建 Key

### 9.2 SerpAPI ⭐推荐（国际搜索）
1. 访问 https://serpapi.com
2. 注册账号
3. 进入 Dashboard
4. 复制 API Key
5. 选择订阅计划（开发测试用免费版即可）

> **SerpAPI 优势**:
> - 一个 Key 访问 Google、Bing、百度、Yahoo 等多个搜索引擎
> - 返回结构化 JSON 数据，无需解析 HTML
> - 支持高级搜索参数（时间范围、地区、语言等）
> - 内置反爬虫处理，稳定性高

### 9.3 百度千帆搜索 ⭐推荐（中文搜索）
1. 访问 https://qianfan.baidu.com
2. 注册/登录百度智能云账号
3. 进入控制台 → 千帆大模型平台
4. 开通「搜索服务」API
5. 创建应用，获取 API Key 和 Secret Key

> **百度千帆搜索优势**:
> - 专为中文搜索优化，结果更精准
> - 国内访问稳定，无需翻墙
> - 与文心大模型生态深度整合
> - 支持网页、新闻、图片等多类型搜索
> - 价格相对优惠

### 9.4 Google Custom Search（备选）
1. 访问 https://developers.google.com/custom-search
2. 创建 Custom Search Engine
3. 在 Control Panel 获取 Search Engine ID
4. 在 Google Cloud Console 创建 API Key

### 9.5 Bing Search（备选）
1. 访问 https://www.microsoft.com/en-us/bing/apis
2. 注册 Azure 账号
3. 创建 Bing Search v7 资源
4. 获取 API Key

### 9.6 NewsAPI
1. 访问 https://newsapi.org
2. 注册免费账号
3. 获取 API Key

### 9.7 百度 OCR
1. 访问 https://cloud.baidu.com
2. 注册百度智能云账号
3. 创建文字识别应用
4. 获取 API Key 和 Secret Key

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-02-01 | 初始版本，整理所有 API 配置需求 |
