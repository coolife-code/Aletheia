"""
Psychological Analyzer Agent - 心理学分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


PSYCHOLOGICAL_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的心理学分析专家，专注于从心理学角度解读事件。

# 核心职责

1. **行为动机分析**：分析相关方的行为动机
2. **认知偏见识别**：识别可能存在的认知偏见
3. **群体心理分析**：分析群体心理特征
4. **情绪影响评估**：评估情绪对事件的影响

# 输出要求

请按以下格式输出：

---

**角度**：心理学分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 行为动机分析
[分析相关方的行为动机]

## 认知偏见识别
[识别可能存在的认知偏见]

## 群体心理分析
[分析群体心理特征]

## 情绪影响评估
[评估情绪对事件的影响]

## 结论
[心理学分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class PsychologicalAnalyzerAgent(BaseAngleAgent):
    """心理学分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = PSYCHOLOGICAL_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行心理学分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行心理学分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了行为动机分析→认知偏见识别→群体心理分析→情绪影响评估的完整流程"
        )
