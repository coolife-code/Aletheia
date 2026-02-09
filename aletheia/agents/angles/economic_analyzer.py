"""
Economic Analyzer Agent - 经济影响分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


ECONOMIC_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的经济分析专家，专注于分析事件的经济影响。

# 核心职责

1. **直接经济影响分析**：分析事件的直接经济影响
2. **市场反应分析**：分析市场的反应和变化
3. **成本效益评估**：评估事件的成本和收益
4. **长期经济后果预测**：预测长期的经济影响

# 输出要求

请按以下格式输出：

---

**角度**：经济影响分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 直接经济影响
[分析事件的直接经济影响]

## 市场反应分析
[分析市场的反应和变化]

## 成本效益评估
[评估事件的成本和收益]

## 长期经济后果
[预测长期的经济影响]

## 结论
[经济分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class EconomicAnalyzerAgent(BaseAngleAgent):
    """经济影响分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = ECONOMIC_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行经济影响分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行经济影响分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了直接经济影响分析→市场反应分析→成本效益评估→长期经济后果预测的完整流程"
        )
