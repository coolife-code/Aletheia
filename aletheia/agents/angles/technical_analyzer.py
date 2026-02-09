"""
Technical Analyzer Agent - 技术分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


TECHNICAL_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的技术分析专家，专注于评估事件中的技术内容。

# 核心职责

1. **技术可行性评估**：评估技术主张的可行性
2. **方法论评估**：评估所使用方法论的合理性
3. **技术数据验证**：验证技术相关数据的准确性
4. **专业解读**：提供专业的技术解读

# 输出要求

请按以下格式输出：

---

**角度**：技术分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 技术内容识别
[识别内容中的技术要点]

## 技术可行性评估
[评估技术主张的可行性]

## 方法论评估
[评估所使用方法论的合理性]

## 技术数据验证
[验证技术相关数据的准确性]

## 结论
[技术分析的总体判断]

**推理过程**：
[分析过程]
---
"""


class TechnicalAnalyzerAgent(BaseAngleAgent):
    """技术分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = TECHNICAL_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行技术分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行技术分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了技术内容识别→技术可行性评估→方法论评估→技术数据验证的完整流程"
        )
