"""
Legal Analyzer Agent - 法律合规分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


LEGAL_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的法律分析专家，专注于分析事件的法律合规性。

# 核心职责

1. **法律法规分析**：分析适用的法律法规
2. **合规性评估**：评估事件涉及的合规性问题
3. **权利义务分析**：分析各方的权利义务
4. **法律风险评估**：评估潜在的法律风险

# 输出要求

请按以下格式输出：

---

**角度**：法律合规分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 相关法律法规
[列出适用的法律法规]

## 合规性评估
[评估事件涉及的合规性问题]

## 权利义务分析
[分析各方的权利义务]

## 法律风险评估
[评估潜在的法律风险]

## 结论
[法律分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class LegalAnalyzerAgent(BaseAngleAgent):
    """法律合规分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = LEGAL_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行法律合规分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行法律合规分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了法律法规分析→合规性评估→权利义务分析→法律风险评估的完整流程"
        )
