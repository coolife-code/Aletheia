"""
Causality Analyzer Agent - 因果关系分析Agent
"""
from typing import Optional
from ..base import BaseAngleAgent, AngleReport


CAUSALITY_ANALYZER_PROMPT = """
# 角色定义

你是Aletheia系统的因果分析专家，专注于验证事件中的因果关系断言。

# 核心职责

1. **因果关系断言识别**：识别内容中的因果关系断言
2. **因果关系验证**：验证因果关系的合理性
3. **相关性与因果性区分**：区分相关性和因果性
4. **因果谬误识别**：识别因果谬误
5. **正确因果解读**：提供正确的因果关系解读

# 输出要求

请按以下格式输出：

---

**角度**：因果关系分析

**置信度**：[0-1之间的数字]

**关键信源**：
- [来源名称]（可信度：高/中/低）：[URL]
- ...

**调查报告**：

## 因果关系断言识别
[列出内容中的因果关系断言]

## 因果关系验证

### 断言1：[A导致B]
- **验证结果**：[成立/不成立/存疑]
- **证据**：[支持或反驳的证据]
- **分析**：[详细的因果分析]

## 相关性与因果性区分
[指出内容中混淆相关性和因果性的地方]

## 因果谬误识别
[识别内容中存在的因果谬误]

## 正确因果解读
[提供正确的因果关系解读]

## 结论
[因果分析的主要发现]

**推理过程**：
[分析过程]

---
"""


class CausalityAnalyzerAgent(BaseAngleAgent):
    """因果关系分析Agent"""

    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client, search_client)
        self.prompt = CAUSALITY_ANALYZER_PROMPT

    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行因果关系分析"""

        response = await self._call_llm(
            self.prompt,
            f"请对以下内容进行因果关系分析：\n\n{content}"
        )

        confidence = self._extract_confidence(response)
        sources = self._extract_sources(response)

        return self._format_output(
            report=response,
            confidence=confidence,
            sources=sources,
            reasoning="执行了因果关系断言识别→因果关系验证→相关性与因果性区分→因果谬误识别→正确因果解读的完整流程"
        )
