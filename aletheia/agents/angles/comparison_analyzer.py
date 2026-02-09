"""
Comparison Analyzer Agent - 对比分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


COMPARISON_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的对比分析专家，专注于评估内容中的比较陈述。

# 核心职责

1. **比较陈述识别**：识别内容中的比较陈述
2. **比较基准公平性评估**：评估比较基准的公平性
3. **比较数据准确性验证**：验证比较数据的准确性
4. **比较误导识别**：识别比较中的误导
5. **正确比较解读**：提供正确的比较解读

# 输出要求

请按以下格式输出：

---

**角度**：对比分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 比较陈述识别
[列出内容中的比较陈述]

## 比较分析

### 比较1：[A比B更X]
- **比较基准**：[比较的基准是什么]
- **公平性评估**：[比较是否公平]
- **数据验证**：[比较数据的准确性]
- **潜在问题**：[比较中可能存在的问题]

## 发现的误导
[列出发现的比较误导]

## 正确解读
[提供正确的比较解读]

## 结论
[对比分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class ComparisonAnalyzerAgent(BaseAngleAgent):
    """对比分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = COMPARISON_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行对比分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行对比分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了比较陈述识别→比较基准公平性评估→比较数据准确性验证→比较误导识别→正确比较解读的完整流程"
        )
