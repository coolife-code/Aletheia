# Aletheia 魔搭社区创空间部署指南

## 项目简介

Aletheia 是一个基于多Agent协作的AI舆情谎言鉴定系统，通过Parser、Search、Verdict三个Agent的深度协作，从多维度分析舆情内容的真实性。

## 部署到魔搭社区创空间

### 1. 准备工作

确保你已经在魔搭社区注册了账号，并且已经创建了创空间。

### 2. 配置环境变量

在创空间的 **Settings -> Secrets** 中配置以下环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | sk-xxx |
| `OPENAI_BASE_URL` | OpenAI API基础URL | https://api.openai.com/v1 |
| `OPENAI_MODEL` | 使用的模型 | gpt-4 |
| `LLM_PROVIDER` | LLM提供商 | openai |

如果使用阿里百炼的DeepSeek模型：
| `OPENAI_BASE_URL` | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| `OPENAI_MODEL` | deepseek-r1 |

### 3. 上传代码

将以下文件上传到创空间的代码仓库：

```
aletheia/
├── app.py                    # Gradio主入口（必需）
├── requirements.txt          # Python依赖（必需）
├── backend/                  # 后端代码
│   └── app/
│       ├── agents/           # Agent实现
│       │   ├── __init__.py
│       │   ├── parser.py
│       │   ├── search.py
│       │   └── verdict.py
│       ├── core/             # 核心配置
│       │   ├── __init__.py
│       │   └── config.py
│       ├── models/           # 数据模型
│       │   ├── __init__.py
│       │   └── schemas.py
│       └── __init__.py
└── .gitattributes            # Git配置
```

### 4. 启动应用

创空间会自动检测到 `app.py` 文件并启动Gradio应用。

默认访问地址：`https://www.modelscope.cn/studios/<your-username>/<your-space-name>`

### 5. 使用说明

1. 在输入框中输入需要鉴定的舆情内容
2. 点击"开始鉴定"按钮
3. 系统会实时显示：
   - **推理过程**：Parser、Search、Verdict三个Agent的详细推理步骤
   - **鉴定结果**：最终结论、置信度、多维度分析
   - **证据列表**：关键信源和相关证据

## 技术架构

```
┌─────────────────────────────────────────┐
│           Gradio Web Interface          │
│              (app.py)                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Backend Agents                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Parser  │ │ Search  │ │ Verdict │   │
│  │  Agent  │ │  Agent  │ │  Agent  │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
```

## 文件说明

- **app.py**: Gradio应用入口，包含完整的Web界面和Agent调用逻辑
- **requirements.txt**: Python依赖列表，包含Gradio、OpenAI等库
- **backend/app/agents/**: 三个核心Agent的实现
- **backend/app/core/config.py**: 配置管理，支持环境变量

## 注意事项

1. **API密钥安全**: 不要将API密钥直接写在代码中，使用创空间的Secrets功能
2. **联网搜索**: Search Agent使用DeepSeek的联网搜索功能，需要正确配置API
3. **流式输出**: 应用支持流式输出，可以实时看到鉴定过程

## 故障排查

### 应用无法启动
- 检查 `requirements.txt` 是否正确上传
- 检查环境变量是否配置正确

### 鉴定失败
- 检查API密钥是否有效
- 检查网络连接是否正常
- 查看应用日志获取详细错误信息

## 更新日志

- 2025-02-09: 初始版本，支持Gradio部署到魔搭创空间
