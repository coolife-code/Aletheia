# Aletheia - AI 舆情谣言鉴别系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Gradio-5.0+-FF6B6B?style=flat-square" />
  <img src="https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai" />
</p>

<p align="center">
  <b>基于多 Agent 协作的舆情内容真实性鉴定平台</b>
</p>

---

## 🎯 项目简介

**Aletheia**（希腊语"真理"）是一个 AI 驱动的舆情谣言鉴别系统，通过创新的多 Agent 协作架构，对用户输入的舆情内容进行多角度事实核查、可信度评分和证据溯源。

### 核心能力

- ✅ **智能方向判定** - 自动识别事件类型，动态激活相关分析角度
- 🔍 **多角度调查** - 15个专业角度 Agent 并行分析（事实核查、时间线、利益相关方等）
- 📊 **可信度评分** - 0-100% 的可信度量化评估
- 🔗 **证据溯源** - 提供权威信源和完整证据链
- 🧠 **可解释推理** - 展示 AI 的完整推理过程和判断依据
- ✨ **流式输出** - 打字机效果实时展示分析过程

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Frontend                         │
│              流式输出 + 打字机效果 + 交互式界面               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AletheiaSystem 核心调度                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Direction   │  │  Angle      │  │  Judgment           │  │
│  │ Agent       │─►│  Agents     │─►│  Agent              │  │
│  │ (方向判定)  │  │  (15个角度) │  │  (综合研判)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM 接口层                              │
│              OpenAI API / DashScope API                      │
│                     DeepSeek 模型                            │
└─────────────────────────────────────────────────────────────┘
```

### Agent 协作流程

1. **Direction Agent（方向判定 Agent）** - 分析内容特征，识别事件类型，动态激活 1-3 个最相关的角度 Agent
2. **Angle Agents（角度 Agent 集群）** - 15 个专业角度 Agent 并行分析，每个专注特定维度
3. **Judgment Agent（综合研判 Agent）** - 整合多角度报告，进行最终真实性判定

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.11
- **OpenAI API Key** 或 **DashScope API Key**

### 1. 克隆项目

```bash
git clone https://github.com/coolife-code/Aletheia.git
cd Aletheia
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
# OPENAI_API_KEY=your_api_key
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# OPENAI_MODEL=deepseek-v3.2
```

### 3. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动应用

```bash
python app.py
```

应用将在 http://localhost:7861 启动

---

## 📁 项目结构

```
aletheia/
├── aletheia/                      # 核心代码
│   ├── agents/                    # Agent 模块
│   │   ├── angles/                # 15个角度 Agent
│   │   │   ├── core_fact_checker.py      # 核心事实核查
│   │   │   ├── timeline_builder.py       # 时间线构建
│   │   │   ├── stakeholder_mapper.py     # 利益相关方分析
│   │   │   ├── sentiment_analyzer.py     # 舆论情绪分析
│   │   │   ├── data_verifier.py          # 数据验证
│   │   │   ├── source_credibility.py     # 信源可信度
│   │   │   ├── context_analyzer.py       # 背景语境分析
│   │   │   ├── technical_analyzer.py     # 技术细节分析
│   │   │   ├── legal_analyzer.py         # 法律合规分析
│   │   │   ├── psychological_analyzer.py # 心理动机分析
│   │   │   ├── economic_analyzer.py      # 经济影响分析
│   │   │   ├── media_coverage.py         # 媒体报道分析
│   │   │   ├── social_impact.py          # 社会影响分析
│   │   │   ├── causality_analyzer.py     # 因果逻辑分析
│   │   │   └── comparison_analyzer.py    # 对比参照分析
│   │   ├── base.py                # Agent 基类
│   │   ├── direction.py           # 方向判定 Agent
│   │   └── judgment.py            # 综合研判 Agent
│   ├── core/                      # 核心配置
│   │   └── config.py              # 配置管理
│   ├── utils/                     # 工具函数
│   │   └── helpers.py
│   └── system.py                  # 系统调度器
├── app.py                         # Gradio 前端
├── .env                           # 环境变量
├── .env.example                   # 环境变量示例
├── requirements.txt               # Python 依赖
├── PROJECT_DOCUMENTATION.md       # 项目技术文档
└── README.md                      # 项目说明文档
```

---

## 🛠️ 技术栈

### 后端 & AI

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| Gradio | 5.0+ | Web 界面框架 |
| OpenAI | 1.0+ | LLM API 客户端 |
| Pydantic | 2.0+ | 数据验证 |
| AsyncIO | - | 异步编程 |

### AI 模型

| 模型 | 用途 |
|------|------|
| DeepSeek-V3 | 主要推理模型 |
| GPT-4 | 备选模型 |

---

## 📊 功能特性

### 核心功能

- 🎯 **智能方向判定** - 基于内容特征自动识别事件类型，动态激活相关角度
- 🔍 **多角度调查** - 15个专业角度并行分析，覆盖事实、时间线、利益相关方等维度
- 🧠 **AI 综合研判** - 基于多角度报告进行逻辑分析和交叉验证
- 📈 **可信度评分** - 量化的可信度评估（0-100%）
- 📋 **证据溯源** - 完整的证据链和来源链接
- 💡 **推理展示** - 透明的 AI 推理过程（打字机效果实时显示）

### 15个分析角度

| 角度 | 功能 |
|------|------|
| 核心事实核查 | 验证具体主张和数据的真实性 |
| 时间线构建 | 还原事件的时间脉络 |
| 利益相关方分析 | 识别各方立场和动机 |
| 舆论情绪分析 | 分析公众情绪倾向 |
| 数据验证 | 验证数字和统计的准确性 |
| 信源可信度 | 评估信息来源的可靠性 |
| 背景语境分析 | 分析事件的历史和社会背景 |
| 技术细节分析 | 验证技术相关内容 |
| 法律合规分析 | 分析法律合规性 |
| 心理动机分析 | 分析行为背后的心理因素 |
| 经济影响分析 | 评估经济影响 |
| 媒体报道分析 | 分析媒体报道的偏差 |
| 社会影响分析 | 评估社会影响力 |
| 因果逻辑分析 | 验证因果关系 |
| 对比参照分析 | 与类似事件对比 |

### 支持的鉴定结论

| 结论 | 说明 |
|------|------|
| 真实/属实 | 内容经多个权威信源证实 |
| 虚假/不实 | 内容已被权威信源证伪 |
| 无法核实/存疑 | 证据不足，存在争议 |

---

## 🔧 配置说明

### 必需的环境变量

```env
# LLM 配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=deepseek-v3.2
```

### 可选的环境变量

```env
# 应用配置
DEBUG=True
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

---

## 🙏 致谢

- [DeepSeek](https://deepseek.com/) - 提供强大的 LLM 能力
- [DashScope](https://dashscope.aliyun.com/) - 提供 API 服务
- [Gradio](https://gradio.app/) - 提供 Web 界面框架

---

<p align="center">
  Made with ❤️ by Aletheia Team
</p>
