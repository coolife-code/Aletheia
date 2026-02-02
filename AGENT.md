# Aletheia - Agent 系统详细设计文档

## 概述

本文档详细描述 Aletheia 舆情谎言鉴定系统的三个核心 Agent 的设计，包括职责边界、协作机制、所需 Skill 和接口规范。

---

## 1. Agent 协作总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        舆情谎言鉴定任务流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ① 解析预处理 Agent (Parser Agent)                                          │
│     职责: 提取舆情核心信息并标准化                                            │
│     输入: 原始内容(文本/图片/视频/链接)                                        │
│     输出: 结构化检索任务包                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 精准检索指令
┌─────────────────────────────────────────────────────────────────────────────┐
│  ② 搜索 Agent (Search Agent)                                                │
│     职责: 执行定制化全网检索，回传权威信源数据                                  │
│     输入: 检索任务包                                                         │
│     输出: 结构化证据数据集                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 权威信源数据
┌─────────────────────────────────────────────────────────────────────────────┐
│  ③ 鉴定结论 Agent (Verdict Agent)                                           │
│     职责: 逻辑分析+交叉验证，生成带溯源证据的鉴定结论                           │
│     输入: 证据数据集                                                         │
│     输出: 完整鉴定报告(可追溯、可复现)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 解析预处理 Agent (Parser Agent)

### 2.1 职责边界
- **输入**: 原始舆情内容（文本/图片/视频/链接）
- **输出**: 结构化的检索任务包
- **核心目标**: 将非结构化内容转化为机器可理解的检索指令

### 2.2 内部处理流程
```
原始内容 → 内容类型识别 → 内容提取 → 主张分解 → 要素提取 → 检索指令生成 → 任务包输出
```

### 2.3 所需 Skill

| Skill 名称 | 功能描述 | 依赖 |
|------------|----------|------|
| `content_classifier` | 识别内容类型（文本/图片/视频/混合） | - |
| `text_extractor` | 从图片/OCR/视频字幕提取文本 | OCR, ASR |
| `claim_extractor` | 提取关键主张和声明 | LLM |
| `entity_recognizer` | 识别人物、组织、地点、时间等实体 | NER模型 |
| `query_generator` | 将主张转化为搜索引擎查询语句 | LLM |
| `metadata_parser` | 解析发布时间、来源平台等元数据 | - |

### 2.4 输出规范
```json
{
  "task_id": "uuid",
  "content_summary": "核心主张摘要",
  "key_claims": [
    {
      "claim_id": "c1",
      "claim_text": "具体主张内容",
      "claim_type": "fact|opinion|prediction",
      "entities": ["实体1", "实体2"],
      "time_reference": "时间引用",
      "location_reference": "地点引用"
    }
  ],
  "search_queries": [
    {
      "query_id": "q1",
      "query_text": "检索语句",
      "target_sources": ["news", "academic", "government"],
      "priority": 1
    }
  ],
  "metadata": {
    "source_type": "social_media|news|forum",
    "original_platform": "weibo|zhihu|twitter",
    "publish_time": "ISO8601",
    "content_hash": "sha256"
  },
  "parser_log": {
    "version": "1.0",
    "processing_time_ms": 1200,
    "confidence": 0.95
  }
}
```

### 2.5 错误处理

| 故障场景 | 处理策略 |
|----------|----------|
| 内容无法解析 | 返回原始内容+人工标注提示 |
| LLM 超时 | 使用规则引擎提取关键词降级 |
| 多媒体提取失败 | 返回已提取的文本部分+失败原因 |

---

## 3. 搜索 Agent (Search Agent)

### 3.1 职责边界
- **输入**: 解析预处理 Agent 生成的检索任务包
- **输出**: 结构化的权威信源数据集
- **核心目标**: 全面、高效、可信地收集相关证据

### 3.2 内部处理流程
```
检索任务包 → 查询分发 → 多源并行检索 → 结果去重 → 可信度评估 → 相关性排序 → 结构化输出
```

### 3.3 所需 Skill

| Skill 名称 | 功能描述 | 依赖 |
|------------|----------|------|
| `search_dispatcher` | 将查询分发到不同搜索引擎 | - |
| `web_searcher` | 通用网页搜索（Google/Bing/百度） | Search API |
| `news_searcher` | 新闻源专项搜索 | News API |
| `academic_searcher` | 学术论文搜索 | Google Scholar, CNKI |
| `social_searcher` | 社交媒体搜索 | 各平台API |
| `source_evaluator` | 评估信源可信度（域名、机构、历史） | 信源数据库 |
| `content_fetcher` | 抓取网页全文内容 | Scrapy, Playwright |
| `deduplicator` | 去除重复/相似内容 | 文本相似度算法 |
| `relevance_ranker` | 按相关性排序结果 | Embedding模型 |

### 3.4 信源可信度分级

| 等级 | 描述 | 示例 |
|------|------|------|
| **High** | 权威官方/顶级媒体 | 新华社、人民日报、政府官网、顶级期刊 |
| **Medium** | 正规媒体/知名机构 | 主流商业媒体、知名智库、认证账号 |
| **Low** | 自媒体/未验证来源 | 个人博客、匿名论坛、营销号 |

### 3.5 输出规范
```json
{
  "search_id": "uuid",
  "parser_task_ref": "parser_task_uuid",
  "query_sources": [
    {
      "evidence_id": "e1",
      "source_url": "https://example.com/news",
      "source_domain": "example.com",
      "source_credibility": "high|medium|low",
      "source_category": "news|academic|government|social",
      "publish_time": "ISO8601",
      "fetch_time": "ISO8601",
      "title": "文章标题",
      "content_snippet": "关键内容摘要",
      "full_text": "完整内容（缓存）",
      "relevance_score": 0.95,
      "evidence_type": "primary|secondary|hearsay",
      "supports_claims": ["c1", "c2"],
      "snapshot_path": "/cache/snapshots/xxx.html"
    }
  ],
  "search_metadata": {
    "total_queries": 5,
    "sources_found": 23,
    "sources_after_dedup": 15,
    "coverage_score": 0.85,
    "completeness_score": 0.78,
    "search_duration_ms": 3500
  }
}
```

### 3.6 错误处理

| 故障场景 | 处理策略 |
|----------|----------|
| 搜索引擎不可用 | 切换备用搜索源 |
| 无相关结果 | 扩大查询范围，返回低相关性提示 |
| 抓取失败 | 记录失败URL，使用搜索结果摘要 |
| API 限流 | 启用缓存结果或延迟重试 |

---

## 4. 鉴定结论 Agent (Verdict Agent)

### 4.1 职责边界
- **输入**: 搜索 Agent 返回的结构化证据数据集
- **输出**: 带完整证据链的鉴定结论报告
- **核心目标**: 基于证据进行逻辑推理，得出可信的鉴定结论

### 4.2 内部处理流程
```
证据数据集 → 证据分组 → 交叉验证 → 逻辑分析 → 可信度评分 → 结论生成 → 报告组装
```

### 4.3 所需 Skill

| Skill 名称 | 功能描述 | 依赖 |
|------------|----------|------|
| `evidence_grouper` | 按主张将证据分组 | - |
| `cross_validator` | 多源证据交叉验证 | LLM |
| `contradiction_detector` | 检测证据间矛盾 | LLM |
| `logical_reasoner` | 逻辑推理链构建 | LLM |
| `fact_checker` | 事实核查核心判断 | LLM + RAG |
| `confidence_calculator` | 综合可信度计算 | 概率模型 |
| `report_generator` | 生成结构化鉴定报告 | 模板引擎 |
| `traceability_logger` | 记录完整决策过程 | - |

### 4.4 鉴定结论类型

| 结论 | 定义 | 适用场景 |
|------|------|----------|
| **TRUE** | 内容属实 | 有多个高可信度信源证实 |
| **FALSE** | 内容虚假 | 有明确证据证伪 |
| **MIXED** | 部分真实 | 部分内容属实，部分不实 |
| **UNCERTAIN** | 存疑待证 | 证据不足或相互矛盾 |
| **UNVERIFIABLE** | 无法核实 | 缺乏可验证的客观依据 |

### 4.5 输出规范
```json
{
  "verdict_id": "uuid",
  "search_task_ref": "search_task_uuid",
  "conclusion": "true|false|mixed|uncertain|unverifiable",
  "confidence_score": 0.92,
  "conclusion_summary": "结论摘要",
  "reasoning_chain": [
    {
      "step_id": 1,
      "reasoning": "推理内容",
      "basis": ["evidence_id_1", "evidence_id_2"],
      "logic_type": "deductive|inductive|abductive"
    }
  ],
  "evidence_chain": [
    {
      "evidence_id": "e1",
      "source_ref": "search_result_ref",
      "claim_ref": "c1",
      "supports": true,
      "weight": 0.8,
      "reason": "支持理由"
    }
  ],
  "findings": {
    "verified_claims": ["已证实主张"],
    "refuted_claims": ["已证伪主张"],
    "uncertain_claims": ["存疑主张"]
  },
  "traceability_log": {
    "agent_version": "1.0",
    "processing_steps": [],
    "decision_points": [],
    "confidence_breakdown": {
      "source_credibility": 0.9,
      "evidence_consistency": 0.85,
      "coverage_completeness": 0.95
    }
  },
  "generated_at": "ISO8601",
  "processing_time_ms": 2800
}
```

### 4.6 错误处理

| 故障场景 | 处理策略 |
|----------|----------|
| 证据不足 | 返回 UNCERTAIN + 证据缺口说明 |
| 推理超时 | 返回基于简单投票的初步结论 |
| 证据矛盾 | 标记矛盾点，返回 UNCERTAIN |
| LLM 不可用 | 使用规则引擎基于信源等级投票 |

---

## 5. Agent 协作时序图

```
用户          Frontend    Backend    Parser    Search    Verdict    External
 │              │           │          │          │          │          │
 │──提交内容──→│           │          │          │          │          │
 │              │────────提交任务────→│          │          │          │
 │              │           │────────调用──────→│          │          │
 │              │           │          │─解析处理─│          │          │
 │              │           │          │          │          │          │
 │              │           │          │──提取主张、生成查询              │
 │              │           │          │          │          │          │
 │              │           │←────返回任务包─────│          │          │
 │              │           │────────────────────调用──────→│          │
 │              │           │                     │─执行检索─│          │
 │              │           │                     │          │          │
 │              │           │                     │────调用搜索引擎────→│
 │              │           │                     │←────────返回结果────│
 │              │           │                     │          │          │
 │              │           │                     │─评估、去重、排序     │
 │              │           │                     │          │          │
 │              │           │←───────────────────返回证据集──│          │
 │              │           │─────────────────────────────────调用────→│
 │              │           │                                │─分析验证─│
 │              │           │                                │          │
 │              │           │                                │─交叉验证─│
 │              │           │                                │─逻辑推理─│
 │              │           │                                │─生成结论─│
 │              │           │                                │          │
 │              │           │←──────────────────────────────返回报告───│
 │              │←────────────────────────────返回结果─────────────────│
 │←──────────展示报告────────│                                │          │
 │              │           │          │          │          │          │
```

---

## 6. 数据流转规范

| 阶段 | 输入 | 处理 | 输出 | 可追溯点 |
|------|------|------|------|----------|
| 解析预处理 | 原始舆情内容 | 结构化提取 | 检索任务包 | 解析日志、提取规则版本 |
| 搜索 | 检索指令 | 多源检索 | 证据数据集 | 检索时间、来源URL、原始快照 |
| 鉴定结论 | 证据数据集 | 逻辑验证 | 鉴定报告 | 推理链、证据权重、决策依据 |

---

## 7. Skill 汇总表

### 7.1 Parser Agent Skills (6个)

| # | Skill 名称 | 优先级 | 实现复杂度 |
|---|------------|--------|------------|
| 1 | `content_classifier` | P0 | 低 |
| 2 | `text_extractor` | P0 | 中 |
| 3 | `claim_extractor` | P0 | 高 |
| 4 | `entity_recognizer` | P1 | 中 |
| 5 | `query_generator` | P0 | 高 |
| 6 | `metadata_parser` | P1 | 低 |

### 7.2 Search Agent Skills (9个)

| # | Skill 名称 | 优先级 | 实现复杂度 |
|---|------------|--------|------------|
| 1 | `search_dispatcher` | P0 | 低 |
| 2 | `web_searcher` | P0 | 中 |
| 3 | `news_searcher` | P1 | 中 |
| 4 | `academic_searcher` | P2 | 中 |
| 5 | `social_searcher` | P2 | 高 |
| 6 | `source_evaluator` | P0 | 中 |
| 7 | `content_fetcher` | P0 | 中 |
| 8 | `deduplicator` | P1 | 中 |
| 9 | `relevance_ranker` | P1 | 中 |

### 7.3 Verdict Agent Skills (8个)

| # | Skill 名称 | 优先级 | 实现复杂度 |
|---|------------|--------|------------|
| 1 | `evidence_grouper` | P0 | 低 |
| 2 | `cross_validator` | P0 | 高 |
| 3 | `contradiction_detector` | P1 | 高 |
| 4 | `logical_reasoner` | P0 | 高 |
| 5 | `fact_checker` | P0 | 高 |
| 6 | `confidence_calculator` | P0 | 中 |
| 7 | `report_generator` | P0 | 低 |
| 8 | `traceability_logger` | P1 | 低 |

---

## 8. 整体流程监控

### 8.1 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| `parser_latency` | 解析处理耗时 | > 3s |
| `search_latency` | 搜索执行耗时 | > 10s |
| `verdict_latency` | 结论生成耗时 | > 5s |
| `success_rate` | 整体成功率 | < 95% |
| `evidence_coverage` | 证据覆盖率 | < 0.7 |

### 8.2 日志要求

- 每个 Agent 执行记录详细日志
- 关键节点设置超时检查点
- 支持任务中断后从断点恢复
- 最终结果附带完整处理轨迹

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-02-01 | 初始版本，定义三个 Agent 及其 Skill |
