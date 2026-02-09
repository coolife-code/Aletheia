"""
Agent基类模块
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import re


@dataclass
class AngleReport:
    """角度调查报告"""
    angle_name: str
    confidence: float
    key_sources: List[Dict[str, Any]]
    report: str
    reasoning_process: str


@dataclass
class DirectionResult:
    """方向判定结果"""
    event_type: str
    activated_angles: List[str]
    angle_details: List[dict]
    reasoning: str
    priority_focus: str
    raw_response: str = ""


@dataclass
class JudgmentResult:
    """研判结果"""
    conclusion: str
    confidence: float
    summary: str
    detailed_judgment: str
    reasoning_process: str


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用LLM"""
        from ..core.config import settings
        try:
            response = await self.llm.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Error] LLM调用失败: {e}")
            return ""
    
    def _extract_confidence(self, response: str) -> float:
        """从响应中提取置信度"""
        match = re.search(r'置信度[：:]\s*(0\.\d+)', response)
        if match:
            return float(match.group(1))
        return 0.5
    
    def _extract_sources(self, response: str) -> List[Dict[str, str]]:
        """从响应中提取信源"""
        sources = []
        pattern = r'-\s*(.+?)（可信度：(.+?)）：(.+)'
        matches = re.findall(pattern, response)
        for name, credibility, url in matches:
            sources.append({
                "name": name.strip(),
                "credibility": credibility.strip(),
                "url": url.strip()
            })
        return sources
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析JSON响应"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass
        
        # 尝试从markdown代码块提取
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 尝试从文本中提取JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return {}


class BaseAngleAgent(BaseAgent):
    """角度Agent基类"""
    
    def __init__(self, llm_client, search_client=None):
        super().__init__(llm_client)
        self.search = search_client
        self.angle_name = self.__class__.__name__.replace('Agent', '')
        self.prompt = ""
    
    @abstractmethod
    async def investigate(self, content: str, context: Optional[dict] = None) -> AngleReport:
        """执行调查"""
        pass
    
    def _format_output(self, report: str, confidence: float, sources: list, reasoning: str = "") -> AngleReport:
        """格式化输出"""
        return AngleReport(
            angle_name=self.angle_name,
            confidence=confidence,
            key_sources=sources,
            report=report,
            reasoning_process=reasoning
        )
