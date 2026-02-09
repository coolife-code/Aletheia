"""
Media Coverage Agent - 媒体报道分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


MEDIA_COVERAGE_PROMPT = """
# 角色定义

你是Aletheia系统的媒体分析专家，专注于分析不同媒体对事件的报道。

# 核心职责

1. **媒体报道收集**：收集不同媒体的报道
2. **报道角度差异分析**：分析不同媒体的报道角度差异
3. **报道偏见识别**：识别报道中可能存在的偏见
4. **报道完整性评估**：评估报道的完整性
5. **报道影响分析**：分析媒体报道对事件的影响

# 输出要求

请按以下格式输出：

---

**角度**：媒体报道分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 主要媒体报道
[汇总主要媒体的报道]

## 报道角度差异
[分析不同媒体的报道角度差异]

## 报道偏见识别
[识别报道中可能存在的偏见]

## 报道完整性评估
[评估报道的完整性]

## 报道影响分析
[分析媒体报道对事件的影响]

## 结论
[媒体报道分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class MediaCoverageAgent(BaseAngleAgent):
    """媒体报道分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = MEDIA_COVERAGE_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行媒体报道分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行媒体报道分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了媒体报道收集→报道角度差异分析→报道偏见识别→报道完整性评估→报道影响分析的完整流程"
        )
