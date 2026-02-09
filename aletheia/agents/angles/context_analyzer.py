"""
Context Analyzer Agent - 背景语境分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


CONTEXT_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的背景研究专家，专注于提供事件的历史和政策背景。

# 核心职责

1. **历史背景分析**：分析与事件相关的历史背景
2. **政策环境分析**：分析相关的政策法规背景
3. **领域知识提供**：提供必要的专业知识
4. **文化社会因素**：分析相关的文化社会背景
5. **背景影响评估**：分析背景如何影响当前事件

# 输出要求

请按以下格式输出：

---

**角度**：背景语境分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 历史背景
[与事件相关的历史背景]

## 政策环境
[相关的政策法规背景]

## 领域知识
[必要的专业知识说明]

## 文化社会因素
[相关的文化社会背景]

## 背景对事件的影响
[分析背景如何影响当前事件]

## 结论
[背景分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class ContextAnalyzerAgent(BaseAngleAgent):
    """背景语境分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = CONTEXT_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行背景语境分析"""

        response = await self._call_llm(
            self.prompt,
            f"请分析以下内容的背景语境：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了历史背景分析→政策环境分析→领域知识提供→文化社会因素分析→背景影响评估的完整流程"
        )
