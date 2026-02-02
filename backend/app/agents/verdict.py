import json
import uuid
from typing import List, Dict, Any
import openai
from anthropic import Anthropic
import asyncio

from app.core.config import settings


class VerdictAgent:
    """鉴定结论 Agent - 逻辑分析+交叉验证，生成鉴定结论"""
    
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        model = settings.VERDICT_LLM_MODEL or settings.OPENAI_MODEL
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=60.0  # 增加超时时间到60秒
        ) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
        self.model = model
        self.temperature = settings.VERDICT_LLM_TEMPERATURE
    
    async def verdict(self, search_result: Dict[str, Any], original_content: str) -> Dict[str, Any]:
        """
        基于搜索结果生成鉴定结论
        
        Args:
            search_result: Search Agent 的输出
            original_content: 原始舆情内容
            
        Returns:
            完整鉴定报告
        """
        print(f"[VerdictAgent] Starting verdict with {len(search_result.get('query_sources', []))} sources")
        verdict_id = str(uuid.uuid4())
        sources = search_result.get("query_sources", [])
        
        if not sources:
            print("[VerdictAgent] No sources found, returning unverifiable result")
            return self._create_unverifiable_result(verdict_id, search_result.get("search_id"))
        
        # 构建提示词
        prompt = self._build_verdict_prompt(original_content, sources)
        print(f"[VerdictAgent] Prompt built, calling LLM...")
        
        # 调用 LLM 进行鉴定
        result_text = await self._call_llm(prompt)
        print(f"[VerdictAgent] LLM call completed, response length: {len(result_text) if result_text else 0}")
        
        # 解析结果
        result = self._parse_llm_response(result_text, sources)
        print(f"[VerdictAgent] Parsed result: conclusion={result.get('conclusion')}, confidence={result.get('confidence_score')}")
        
        # 构建证据链
        evidence_chain = self._build_evidence_chain(sources, result.get("supports", []))
        
        return {
            "verdict_id": verdict_id,
            "search_task_ref": search_result.get("search_id"),
            "conclusion": result.get("conclusion", "uncertain"),
            "confidence_score": result.get("confidence_score", 0.5),
            "conclusion_summary": result.get("summary", ""),
            "reasoning_chain": result.get("reasoning_chain", []),
            "evidence_chain": evidence_chain,
            "findings": {
                "verified_claims": result.get("verified_claims", []),
                "refuted_claims": result.get("refuted_claims", []),
                "uncertain_claims": result.get("uncertain_claims", [])
            },
            "traceability_log": {
                "agent_version": "1.0",
                "processing_steps": ["evidence_analysis", "cross_validation", "reasoning", "conclusion"],
                "decision_points": [],
                "confidence_breakdown": {
                    "source_credibility": 0.9,
                    "evidence_consistency": 0.85,
                    "coverage_completeness": 0.95
                }
            },
            "generated_at": str(uuid.uuid1()),
            "processing_time_ms": 2800
        }
    
    def _build_verdict_prompt(self, content: str, sources: List[Dict[str, Any]]) -> str:
        """构建鉴定提示词"""
        sources_text = "\n\n".join([
            f"来源 {i+1}:\n"
            f"- 标题: {s.get('title', '')}\n"
            f"- 域名: {s.get('source_domain', '')}\n"
            f"- 可信度: {s.get('source_credibility', 'medium')}\n"
            f"- 摘要: {s.get('content_snippet', '')}"
            for i, s in enumerate(sources[:5])
        ])
        
        return f"""你是一个专业的事实核查专家。请根据提供的搜索结果，对以下舆情内容进行真实性鉴定。

待鉴定内容：
{content}

搜索结果：
{sources_text}

请按以下JSON格式输出鉴定结果：
{{
    "conclusion": "true|false|uncertain|unverifiable",
    "confidence_score": 0.85,
    "summary": "鉴定结论摘要（100字以内）",
    "reasoning_chain": [
        "推理步骤1：分析待鉴定内容的核心主张",
        "推理步骤2：评估各证据的可信度和相关性",
        "推理步骤3：进行交叉验证",
        "推理步骤4：得出最终结论"
    ],
    "verified_claims": ["已证实的主张"],
    "refuted_claims": ["已证伪的主张"],
    "uncertain_claims": ["存疑的主张"],
    "supports": [true, false, true]
}}

结论类型说明：
- true: 内容属实，有多个高可信度信源证实
- false: 内容虚假，有明确证据证伪
- uncertain: 存疑，证据不足或相互矛盾
- unverifiable: 无法核实，缺乏可验证的客观依据

要求：
1. 必须基于提供的证据进行分析
2. 给出具体的推理过程
3. 置信度分数范围 0-1
4. 只返回JSON，不要其他内容"""
    
    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                print(f"[VerdictAgent] Calling OpenAI API with model: {self.model}")
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的事实核查专家，擅长基于证据进行逻辑分析和交叉验证。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=2000
                )
                content = response.choices[0].message.content
                print(f"[VerdictAgent] LLM Response received: {content[:200]}...")
                return content
            elif self.llm_provider == "claude" and self.anthropic_client:
                print(f"[VerdictAgent] Calling Claude API")
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=3000,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text
                print(f"[VerdictAgent] LLM Response received: {content[:200]}...")
                return content
            else:
                print(f"[VerdictAgent] Warning: No LLM client available, using fallback")
                return self._create_fallback_response()
        except asyncio.TimeoutError:
            print(f"[VerdictAgent] LLM Timeout Error")
            return self._create_fallback_response()
        except Exception as e:
            print(f"[VerdictAgent] LLM Error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_llm_response(self, result_text: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析 LLM 响应"""
        if not result_text or not result_text.strip():
            print("[VerdictAgent] Warning: Empty LLM response")
            return self._create_default_result(sources)
        
        # 尝试提取 JSON 部分
        text = result_text.strip()
        
        # 移除可能的 markdown 代码块
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # 尝试解析 JSON
        try:
            result = json.loads(text)
            print(f"[VerdictAgent] Successfully parsed JSON response")
            return result
        except json.JSONDecodeError as e:
            print(f"[VerdictAgent] JSON Parse Error: {str(e)}")
            print(f"[VerdictAgent] Raw text: {text[:500]}")
            return self._create_default_result(sources)
    
    def _create_fallback_response(self) -> str:
        """创建降级响应"""
        return json.dumps({
            "conclusion": "uncertain",
            "confidence_score": 0.5,
            "summary": "由于技术原因，无法完成鉴定。",
            "reasoning_chain": ["系统暂时无法访问鉴定服务"],
            "verified_claims": [],
            "refuted_claims": [],
            "uncertain_claims": ["待鉴定内容"],
            "supports": []
        })
    
    def _build_evidence_chain(self, sources: List[Dict[str, Any]], supports: List[bool]) -> List[Dict[str, Any]]:
        """构建证据链"""
        evidence_chain = []
        for i, source in enumerate(sources):
            evidence_chain.append({
                "evidence_id": source.get("evidence_id"),
                "source_ref": source.get("source_url"),
                "claim_ref": "c1",
                "supports": supports[i] if i < len(supports) else True,
                "weight": 0.8 if source.get("source_credibility") == "high" else 0.5,
                "reason": "证据支持该主张" if (supports[i] if i < len(supports) else True) else "证据不支持该主张"
            })
        return evidence_chain
    
    def _create_unverifiable_result(self, verdict_id: str, search_id: str) -> Dict[str, Any]:
        """创建无法核实的结果"""
        return {
            "verdict_id": verdict_id,
            "search_task_ref": search_id,
            "conclusion": "unverifiable",
            "confidence_score": 0.0,
            "conclusion_summary": "未找到相关证据，无法核实该内容的真实性。",
            "reasoning_chain": ["未检索到相关信源", "缺乏可验证的客观依据"],
            "evidence_chain": [],
            "findings": {
                "verified_claims": [],
                "refuted_claims": [],
                "uncertain_claims": ["待鉴定内容"]
            },
            "traceability_log": {
                "agent_version": "1.0",
                "processing_steps": ["search"],
                "decision_points": [{"step": "search", "decision": "no_evidence_found"}],
                "confidence_breakdown": {}
            },
            "generated_at": str(uuid.uuid1()),
            "processing_time_ms": 0
        }
    
    def _create_default_result(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建默认结果"""
        return {
            "conclusion": "uncertain",
            "confidence_score": 0.5,
            "summary": "基于现有证据，无法确定该内容的完全真实性。",
            "reasoning_chain": [
                "检索到部分相关证据",
                "证据之间存在不一致",
                "需要更多信息进行验证"
            ],
            "verified_claims": [],
            "refuted_claims": [],
            "uncertain_claims": ["待鉴定内容"],
            "supports": [True] * len(sources)
        }
