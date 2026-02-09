"""
Social Impact Agent - 社会影响分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


SOCIAL_IMPACT_PROMPT = """
# 角色定义

你是Aletheia系统的社会影响分析专家，专注于评估事件的社会影响。

# 核心职责

1. **对公众的影响分析**：分析事件对公众的影响
2. **对社会秩序的影响分析**：分析对社会秩序的影响
3. **对特定群体的影响分析**：分析对特定群体的影响
4. **长期社会后果预测**：预测长期的社会影响

# 输出要求

请按以下格式输出：

---

**角度**：社会影响分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 对公众的影响
[分析事件对公众的影响]

## 对社会秩序的影响
[分析对社会秩序的影响]

## 对特定群体的影响
[分析对特定群体的影响]

## 长期社会后果
[预测长期的社会影响]

## 结论
[社会影响分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class SocialImpactAgent(BaseAngleAgent):
    """社会影响分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = SOCIAL_IMPACT_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行社会影响分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行社会影响分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了对公众的影响分析→对社会秩序的影响分析→对特定群体的影响分析→长期社会后果预测的完整流程"
        )
