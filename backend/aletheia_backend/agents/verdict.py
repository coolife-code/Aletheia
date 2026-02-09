import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
import openai
from anthropic import Anthropic
import asyncio

from aletheia_backend.core.config import settings


class VerdictAgent:
    """
    鉴定结论 Agent - 多维度深度分析专家
    
    职责：
    1. 从多角度审视问题，不局限于字面意思
    2. 深度分析关键信源和普通信源
    3. 识别问题的多个层面（事实、背景、动机、影响）
    4. 综合 Search Agent 的分析结果
    5. 得出有说服力、令人信服的结论
    """

    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        model = settings.VERDICT_LLM_MODEL or settings.OPENAI_MODEL
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=60.0
        ) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
        self.model = model
        self.temperature = settings.VERDICT_LLM_TEMPERATURE

    async def verdict(self, search_result: Dict[str, Any], original_content: str) -> Dict[str, Any]:
        """
        基于 Search Agent 的深度分析结果，生成多维度鉴定结论
        """
        print(f"[VerdictAgent] Starting multi-dimensional verdict")
        verdict_id = str(uuid.uuid4())

        # 提取 Search Agent 的分析结果
        key_sources = search_result.get("key_sources", [])
        regular_sources = search_result.get("regular_sources", [])
        all_sources = search_result.get("all_sources", [])
        search_analysis = search_result.get("analysis", {})
        query_analysis = search_result.get("query_analysis", {})

        if not all_sources:
            print("[VerdictAgent] No sources found, returning unverifiable result")
            return self._create_unverifiable_result(verdict_id, search_result.get("search_id"))

        # 阶段1: 多维度问题分解
        print("[VerdictAgent] Performing multi-dimensional analysis...")
        dimensions = await self._analyze_dimensions(
            original_content, query_analysis, search_analysis
        )

        # 阶段2: 深度证据评估
        print("[VerdictAgent] Evaluating evidence...")
        evidence_evaluation = await self._evaluate_evidence_comprehensive(
            key_sources, regular_sources, search_analysis, original_content
        )

        # 阶段3: 多角度综合判断
        print("[VerdictAgent] Synthesizing multi-angle judgment...")
        final_judgment = await self._synthesize_judgment(
            original_content, dimensions, evidence_evaluation, search_analysis
        )

        # 构建证据链
        evidence_chain = self._build_comprehensive_evidence_chain(
            key_sources, regular_sources, final_judgment.get("supporting_sources", [])
        )

        print(f"[VerdictAgent] Verdict complete: {final_judgment.get('conclusion')} with confidence {final_judgment.get('confidence_score')}")

        return {
            "verdict_id": verdict_id,
            "search_task_ref": search_result.get("search_id"),
            
            # 鉴定结论
            "conclusion": final_judgment.get("conclusion", "uncertain"),
            "confidence_score": final_judgment.get("confidence_score", 0.5),
            "conclusion_summary": final_judgment.get("summary", ""),
            
            # 多维度分析
            "dimensional_analysis": {
                "factual_dimension": dimensions.get("factual", {}),
                "contextual_dimension": dimensions.get("contextual", {}),
                "motivational_dimension": dimensions.get("motivational", {}),
                "impact_dimension": dimensions.get("impact", {})
            },
            
            # 详细推理链
            "reasoning_chain": final_judgment.get("reasoning_chain", []),
            "multi_angle_reasoning": final_judgment.get("multi_angle_reasoning", {}),
            
            # 证据评估
            "evidence_evaluation": evidence_evaluation,
            
            # 证据链
            "evidence_chain": evidence_chain,
            
            # 发现分类
            "findings": {
                "verified_claims": final_judgment.get("verified_claims", []),
                "refuted_claims": final_judgment.get("refuted_claims", []),
                "uncertain_claims": final_judgment.get("uncertain_claims", []),
                "nuanced_claims": final_judgment.get("nuanced_claims", [])  # 新增： nuanced 结论
            },
            
            # 重要信源引用
            "key_sources_cited": [
                {
                    "evidence_id": s.get("evidence_id"),
                    "title": s.get("title"),
                    "domain": s.get("source_domain"),
                    "credibility": s.get("source_credibility"),
                    "key_insight": s.get("key_insight", "")[:100],
                    "why_important": s.get("importance_note", "")
                }
                for s in key_sources[:5]
            ],
            
            # 可追溯日志
            "traceability_log": {
                "agent_version": "2.0",
                "processing_steps": [
                    "multi_dimensional_decomposition",
                    "evidence_comprehensive_evaluation",
                    "conflict_resolution",
                    "multi_angle_synthesis",
                    "conclusion_generation"
                ],
                "decision_points": final_judgment.get("decision_points", []),
                "confidence_breakdown": final_judgment.get("confidence_breakdown", {})
            },
            
            "generated_at": str(uuid.uuid1()),
            "processing_time_ms": 3500
        }

    async def verdict_stream(self, search_result: Dict[str, Any], original_content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式鉴定，实时返回多维度推理过程
        """
        verdict_id = str(uuid.uuid4())

        key_sources = search_result.get("key_sources", [])
        regular_sources = search_result.get("regular_sources", [])
        all_sources = search_result.get("all_sources", [])
        search_analysis = search_result.get("analysis", {})
        query_analysis = search_result.get("query_analysis", {})

        # 开始鉴定
        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "鉴定启动",
            "content": f"🎯 启动多维度深度鉴定\n"
                       f"   📌 关键信源: {len(key_sources)} 个\n"
                       f"   📄 普通信源: {len(regular_sources)} 个\n"
                       f"   🔍 Search Agent 已识别 {len(search_analysis.get('key_findings', []))} 个核心发现"
        }

        if not all_sources:
            yield {
                "type": "reasoning",
                "agent": "verdict",
                "step": "证据检查",
                "content": "⚠️ 未找到任何相关信源，无法完成鉴定"
            }
            result = self._create_unverifiable_result(verdict_id, search_result.get("search_id"))
            yield {"type": "result", "agent": "verdict", "data": result}
            return

        # 阶段1: 多维度问题分解
        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "多维度分析",
            "content": "🔬 从多维度审视问题...\n"
                       "   - 事实维度：核心主张是否属实\n"
                       "   - 背景维度：事件的前因后果\n"
                       "   - 动机维度：信息传播的可能动机\n"
                       "   - 影响维度：该信息的潜在影响"
        }

        dimensions = await self._analyze_dimensions(
            original_content, query_analysis, search_analysis
        )

        for dim_name, dim_data in dimensions.items():
            yield {
                "type": "reasoning",
                "agent": "verdict",
                "step": f"{dim_name}维度",
                "content": f"📊 {dim_name}维度分析:\n{dim_data.get('analysis', '')}"
            }

        # 阶段2: 证据评估
        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "证据评估",
            "content": f"🧩 深度评估证据...\n"
                       f"   - 评估 {len(key_sources)} 个关键信源\n"
                       f"   - 评估 {len(regular_sources)} 个普通信源\n"
                       f"   - 分析 Search Agent 识别的 {len(search_analysis.get('conflict_points', []))} 个冲突点"
        }

        evidence_evaluation = await self._evaluate_evidence_comprehensive(
            key_sources, regular_sources, search_analysis, original_content
        )

        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "证据权重",
            "content": "⚖️ 证据权重分析:\n" +
                       "\n".join([f"   • {e}" for e in evidence_evaluation.get("weight_analysis", [])])
        }

        # 阶段3: 多角度综合
        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "综合判断",
            "content": "🎭 从多角度综合判断...\n"
                       "   - 字面意思 vs 深层含义\n"
                       "   - 直接证据 vs 间接证据\n"
                       "   - 短期影响 vs 长期影响\n"
                       "   - 表面现象 vs 本质问题"
        }

        final_judgment = await self._synthesize_judgment(
            original_content, dimensions, evidence_evaluation, search_analysis
        )

        # 输出多角度推理 - 详细分析
        multi_angle = final_judgment.get("multi_angle_reasoning", {})

        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "多角度分析",
            "content": "🎭 从多角度审视问题...\n\n"
                       "   分析维度:\n"
                       "   • 字面意思 vs 深层含义\n"
                       "   • 直接证据 vs 间接证据\n"
                       "   • 短期影响 vs 长期影响\n"
                       "   • 表面现象 vs 本质问题"
        }

        angle_names = {
            "literal_meaning": "字面意思",
            "deep_implication": "深层含义",
            "direct_evidence": "直接证据",
            "indirect_evidence": "间接证据",
            "short_term": "短期影响",
            "long_term": "长期影响"
        }

        for angle, reasoning in multi_angle.items():
            angle_name = angle_names.get(angle, angle)
            yield {
                "type": "reasoning",
                "agent": "verdict",
                "step": f"角度-{angle_name}",
                "content": f"📐 {angle_name}:\n   {reasoning}"
            }

        # 输出详细推理链
        reasoning_chain = final_judgment.get("reasoning_chain", [])
        if reasoning_chain:
            yield {
                "type": "reasoning",
                "agent": "verdict",
                "step": "推理链条",
                "content": "🧠 详细推理过程:\n\n" +
                           "\n".join([f"   步骤 {i+1}:\n      {r}\n" for i, r in enumerate(reasoning_chain)])
            }

        # 发现分类
        findings = {
            "verified_claims": final_judgment.get("verified_claims", []),
            "refuted_claims": final_judgment.get("refuted_claims", []),
            "uncertain_claims": final_judgment.get("uncertain_claims", []),
            "nuanced_claims": final_judgment.get("nuanced_claims", [])
        }

        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "发现分类",
            "content": "📊 发现分类:\n" +
                       f"   ✅ 已验证: {len(findings['verified_claims'])} 项\n" +
                       f"   ❌ 已证伪: {len(findings['refuted_claims'])} 项\n" +
                       f"   ⚠️ 需 nuanced 理解: {len(findings['nuanced_claims'])} 项\n" +
                       f"   ❓ 不确定: {len(findings['uncertain_claims'])} 项"
        }

        # 结论生成 - 详细说明
        conclusion = final_judgment.get("conclusion", "uncertain")
        confidence = final_judgment.get("confidence_score", 0.5)
        summary = final_judgment.get("summary", "")

        conclusion_emoji = {
            "true": "✅",
            "false": "❌",
            "uncertain": "⚠️",
            "unverifiable": "❓",
            "partially_true": "🟨",
            "misleading": "🟧"
        }.get(conclusion, "❓")

        conclusion_labels = {
            "true": "真实",
            "false": "虚假",
            "uncertain": "存疑",
            "unverifiable": "无法核实",
            "partially_true": "部分真实",
            "misleading": "误导性"
        }

        yield {
            "type": "reasoning",
            "agent": "verdict",
            "step": "结论生成",
            "content": f"🎯 最终鉴定结论\n\n"
                       f"   {conclusion_emoji} 结论: {conclusion_labels.get(conclusion, conclusion)}\n"
                       f"   📊 置信度: {confidence:.0%}\n"
                       f"   📝 结论摘要:\n      {summary}\n\n"
                       f"   💡 结论依据:\n"
                       f"      • 基于 {len(key_sources)} 个关键信源\n"
                       f"      • 综合 {len(regular_sources)} 个普通信源\n"
                       f"      • 多维度交叉验证"
        }

        # 构建最终结果
        evidence_chain = self._build_comprehensive_evidence_chain(
            key_sources, regular_sources, final_judgment.get("supporting_sources", [])
        )

        final_result = {
            "verdict_id": verdict_id,
            "search_task_ref": search_result.get("search_id"),
            "conclusion": conclusion,
            "confidence_score": confidence,
            "conclusion_summary": summary,
            "dimensional_analysis": {
                "factual_dimension": dimensions.get("factual", {}),
                "contextual_dimension": dimensions.get("contextual", {}),
                "motivational_dimension": dimensions.get("motivational", {}),
                "impact_dimension": dimensions.get("impact", {})
            },
            "reasoning_chain": reasoning_chain,
            "multi_angle_reasoning": multi_angle,
            "evidence_evaluation": evidence_evaluation,
            "evidence_chain": evidence_chain,
            "findings": {
                "verified_claims": final_judgment.get("verified_claims", []),
                "refuted_claims": final_judgment.get("refuted_claims", []),
                "uncertain_claims": final_judgment.get("uncertain_claims", []),
                "nuanced_claims": final_judgment.get("nuanced_claims", [])
            },
            "key_sources_cited": [
                {
                    "evidence_id": s.get("evidence_id"),
                    "title": s.get("title"),
                    "domain": s.get("source_domain"),
                    "credibility": s.get("source_credibility"),
                    "key_insight": s.get("key_insight", "")[:100],
                    "why_important": s.get("importance_note", "")
                }
                for s in key_sources[:5]
            ],
            "traceability_log": {
                "agent_version": "2.0",
                "processing_steps": [
                    "multi_dimensional_decomposition",
                    "evidence_comprehensive_evaluation",
                    "conflict_resolution",
                    "multi_angle_synthesis",
                    "conclusion_generation"
                ],
                "decision_points": final_judgment.get("decision_points", []),
                "confidence_breakdown": final_judgment.get("confidence_breakdown", {})
            },
            "generated_at": str(uuid.uuid1()),
            "processing_time_ms": 3500
        }

        yield {
            "type": "result",
            "agent": "verdict",
            "data": final_result
        }

    async def _analyze_dimensions(self, original_content: str, query_analysis: Dict, search_analysis: Dict) -> Dict[str, Any]:
        """
        多维度问题分解分析
        """
        key_findings = search_analysis.get("key_findings", [])
        perspectives = search_analysis.get("perspectives", {})

        prompt = f"""你是一位多维度分析专家。请从以下四个维度深度分析这个问题：

【待分析内容】
{original_content}

【核心问题】
{query_analysis.get('core_question', '')}

【Search Agent 的核心发现】
{chr(10).join(['- ' + f for f in key_findings[:5]])}

【不同立场的观点】
支持方: {perspectives.get('supporting', '无')}
反对方: {perspectives.get('opposing', '无')}
中立方: {perspectives.get('neutral', '无')}

请从以下四个维度进行分析，返回JSON格式：
{{
    "factual": {{
        "analysis": "事实维度分析：核心主张的事实基础、可验证性、证据强度",
        "key_points": ["关键点1", "关键点2"],
        "confidence": 0.85
    }},
    "contextual": {{
        "analysis": "背景维度分析：事件的前因后果、历史背景、相关事件",
        "key_points": ["背景点1", "背景点2"],
        "confidence": 0.75
    }},
    "motivational": {{
        "analysis": "动机维度分析：信息传播的可能动机、利益相关方、叙事目的",
        "key_points": ["动机点1", "动机点2"],
        "confidence": 0.60
    }},
    "impact": {{
        "analysis": "影响维度分析：该信息的潜在社会影响、情绪影响、行为影响",
        "key_points": ["影响点1", "影响点2"],
        "confidence": 0.70
    }}
}}

要求：
1. 每个维度都要有深入的分析
2. 指出该维度的关键证据支撑
3. 给出该维度的置信度评估
4. 思考维度之间的关联"""

        try:
            result_text = await self._call_llm(prompt)
            return self._parse_llm_response(result_text)
        except Exception as e:
            print(f"[VerdictAgent] Dimension analysis error: {e}")
            return {
                "factual": {"analysis": "分析失败", "key_points": [], "confidence": 0.5},
                "contextual": {"analysis": "分析失败", "key_points": [], "confidence": 0.5},
                "motivational": {"analysis": "分析失败", "key_points": [], "confidence": 0.5},
                "impact": {"analysis": "分析失败", "key_points": [], "confidence": 0.5}
            }

    async def _evaluate_evidence_comprehensive(self, key_sources: List[Dict], regular_sources: List[Dict], 
                                                search_analysis: Dict, original_content: str) -> Dict[str, Any]:
        """
        综合评估所有证据
        """
        conflict_points = search_analysis.get("conflict_points", [])
        evidence_gaps = search_analysis.get("evidence_gaps", [])

        # 准备信源摘要
        key_sources_summary = []
        for s in key_sources[:6]:
            key_sources_summary.append({
                "domain": s.get("source_domain", ""),
                "credibility": s.get("source_credibility", "medium"),
                "stance": s.get("source_stance", "neutral"),
                "insight": s.get("key_insight", "")[:120],
                "deep_analysis": s.get("deep_analysis", "")[:80]
            })

        prompt = f"""你是一位证据评估专家。请对以下证据进行综合评估。

【待核实内容】
{original_content}

【关键信源】
{json.dumps(key_sources_summary, ensure_ascii=False, indent=2)}

【Search Agent 识别的冲突点】
{chr(10).join(['- ' + c for c in conflict_points[:4]])}

【证据缺口】
{chr(10).join(['- ' + g for g in evidence_gaps[:3]])}

请返回JSON格式：
{{
    "key_sources_assessment": [
        {{
            "domain": "信源域名",
            "assessment": "对该信源的评估",
            "weight": 0.9,
            "reliability_concerns": "可靠性担忧（如有）"
        }}
    ],
    "conflict_resolution": "如何处理信源之间的冲突",
    "weight_analysis": [
        "证据权重分析点1",
        "证据权重分析点2"
    ],
    "evidence_strength": 0.75,
    "coverage_assessment": "证据覆盖度评估",
    "overall_quality": "整体证据质量评价"
}}

要求：
1. 详细评估每个关键信源
2. 说明如何处理冲突信息
3. 评估证据的整体强度和覆盖度
4. 指出任何可靠性担忧"""

        try:
            result_text = await self._call_llm(prompt)
            return self._parse_llm_response(result_text)
        except Exception as e:
            print(f"[VerdictAgent] Evidence evaluation error: {e}")
            return {
                "key_sources_assessment": [],
                "conflict_resolution": "评估失败",
                "weight_analysis": [],
                "evidence_strength": 0.5,
                "coverage_assessment": "评估失败",
                "overall_quality": "评估失败"
            }

    async def _synthesize_judgment(self, original_content: str, dimensions: Dict, 
                                   evidence_evaluation: Dict, search_analysis: Dict) -> Dict[str, Any]:
        """
        综合多角度判断，生成最终结论
        """
        key_findings = search_analysis.get("key_findings", [])
        analysis_reasoning = search_analysis.get("analysis_reasoning", "")
        perspectives = search_analysis.get("perspectives", {})

        prompt = f"""你是一位资深的事实核查专家。请基于多维度分析和证据评估，生成最终的综合判断。

【待核实内容】
{original_content}

【多维度分析结果】
事实维度置信度: {dimensions.get('factual', {}).get('confidence', 0.5)}
背景维度置信度: {dimensions.get('contextual', {}).get('confidence', 0.5)}
动机维度置信度: {dimensions.get('motivational', {}).get('confidence', 0.5)}
影响维度置信度: {dimensions.get('impact', {}).get('confidence', 0.5)}

【证据评估】
整体证据强度: {evidence_evaluation.get('evidence_strength', 0.5)}
证据质量: {evidence_evaluation.get('overall_quality', '未知')}

【Search Agent 的分析推理】
{analysis_reasoning[:500]}

【核心发现】
{chr(10).join(['- ' + f for f in key_findings[:5]])}

【不同立场观点】
支持方: {perspectives.get('supporting', '无')[:200]}
反对方: {perspectives.get('opposing', '无')[:200]}

请返回JSON格式：
{{
    "conclusion": "true|false|uncertain|unverifiable|partially_true|misleading",
    "confidence_score": 0.85,
    "summary": "鉴定结论摘要（150字以内，要有说服力）",
    "reasoning_chain": [
        "推理步骤1：从事实维度的分析",
        "推理步骤2：如何处理证据冲突",
        "推理步骤3：多角度综合判断",
        "推理步骤4：最终结论的形成"
    ],
    "multi_angle_reasoning": {{
        "literal_meaning": "字面意思的分析",
        "deep_implication": "深层含义的挖掘",
        "direct_evidence": "直接证据的评估",
        "indirect_evidence": "间接证据的评估",
        "short_term": "短期影响分析",
        "long_term": "长期影响分析"
    }},
    "verified_claims": ["已验证的具体主张"],
    "refuted_claims": ["已证伪的具体主张"],
    "uncertain_claims": ["不确定的主张"],
    "nuanced_claims": ["需要 nuanced 理解的主张，如'部分真实但有误导性'"],
    "supporting_sources": ["evidence_id1", "evidence_id2"],
    "decision_points": [
        {{"step": "证据评估", "decision": "高可信度信源占主导"}},
        {{"step": "冲突处理", "decision": "采用多数高可信度信源的观点"}}
    ],
    "confidence_breakdown": {{
        "factual_basis": 0.9,
        "evidence_quality": 0.85,
        "source_credibility": 0.88,
        "consistency": 0.82
    }}
}}

结论类型说明：
- true: 内容属实，有多个高可信度信源证实
- false: 内容虚假，有明确证据证伪
- uncertain: 存疑，证据不足或相互矛盾
- unverifiable: 无法核实，缺乏可验证的客观依据
- partially_true: 部分真实，但存在夸大或遗漏
- misleading: 具有误导性，虽然字面可能正确但引导错误结论

要求：
1. 结论要有说服力，基于充分的证据
2. 不要局限于字面意思，要挖掘深层含义
3. 承认不确定性，不要过度自信
4. 给出详细的推理过程
5. 考虑不同角度的观点"""

        try:
            result_text = await self._call_llm(prompt)
            return self._parse_llm_response(result_text)
        except Exception as e:
            print(f"[VerdictAgent] Judgment synthesis error: {e}")
            return {
                "conclusion": "uncertain",
                "confidence_score": 0.5,
                "summary": "综合判断过程中出现错误",
                "reasoning_chain": ["错误: " + str(e)],
                "multi_angle_reasoning": {},
                "verified_claims": [],
                "refuted_claims": [],
                "uncertain_claims": [original_content],
                "nuanced_claims": [],
                "supporting_sources": [],
                "decision_points": [],
                "confidence_breakdown": {}
            }

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                print(f"[VerdictAgent] Calling OpenAI API with model: {self.model}")
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位资深的事实核查专家和批判性思维导师。你擅长多维度分析、多角度思考，不局限于表面现象。你总是基于证据说话，善于发现问题的复杂性，给出 nuanced 的结论。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=3000
                )
                content = response.choices[0].message.content
                print(f"[VerdictAgent] LLM Response received: {content[:200]}...")
                return content
            elif self.llm_provider == "claude" and self.anthropic_client:
                print(f"[VerdictAgent] Calling Claude API")
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=3500,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                print(f"[VerdictAgent] LLM Response received: {content[:200]}...")
                return content
            else:
                print(f"[VerdictAgent] Warning: No LLM client available")
                return self._create_fallback_response()
        except asyncio.TimeoutError:
            print(f"[VerdictAgent] LLM Timeout Error")
            return self._create_fallback_response()
        except Exception as e:
            print(f"[VerdictAgent] LLM Error: {str(e)}")
            return self._create_fallback_response()

    def _parse_llm_response(self, result_text: str) -> Dict[str, Any]:
        """解析 LLM 响应"""
        if not result_text or not result_text.strip():
            return {}

        text = result_text.strip()

        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            print(f"[VerdictAgent] JSON Parse Error: {str(e)}")
            # 尝试提取 JSON
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
            except:
                pass
            return {}

    def _create_fallback_response(self) -> str:
        """创建降级响应"""
        return json.dumps({
            "conclusion": "uncertain",
            "confidence_score": 0.5,
            "summary": "由于技术原因，无法完成鉴定。",
            "reasoning_chain": ["系统暂时无法访问鉴定服务"],
            "multi_angle_reasoning": {},
            "verified_claims": [],
            "refuted_claims": [],
            "uncertain_claims": ["待鉴定内容"],
            "nuanced_claims": [],
            "supporting_sources": [],
            "decision_points": [],
            "confidence_breakdown": {}
        })

    def _build_comprehensive_evidence_chain(self, key_sources: List[Dict], regular_sources: List[Dict], 
                                            supporting_ids: List[str]) -> List[Dict[str, Any]]:
        """构建综合证据链"""
        evidence_chain = []
        all_sources = key_sources + regular_sources

        for source in all_sources:
            evidence_id = source.get("evidence_id")
            supports = evidence_id in supporting_ids if supporting_ids else True

            evidence_chain.append({
                "evidence_id": evidence_id,
                "source_ref": source.get("source_url"),
                "source_domain": source.get("source_domain"),
                "source_credibility": source.get("source_credibility"),
                "is_key_source": source.get("is_key_source", False),
                "claim_ref": "c1",
                "supports": supports,
                "weight": self._calculate_weight(source),
                "reason": source.get("key_insight", "")[:100] if supports else source.get("deep_analysis", "")[:100]
            })

        return evidence_chain

    def _calculate_weight(self, source: Dict) -> float:
        """计算证据权重"""
        weight = 0.5

        # 可信度权重
        credibility_scores = {"high": 0.9, "medium": 0.6, "low": 0.3}
        weight *= credibility_scores.get(source.get("source_credibility", "medium"), 0.5)

        # 相关度权重
        weight *= source.get("relevance_score", 0.8)

        # 关键信源加成
        if source.get("is_key_source"):
            weight *= 1.2

        return min(1.0, weight)

    def _create_unverifiable_result(self, verdict_id: str, search_id: str) -> Dict[str, Any]:
        """创建无法核实的结果"""
        return {
            "verdict_id": verdict_id,
            "search_task_ref": search_id,
            "conclusion": "unverifiable",
            "confidence_score": 0.0,
            "conclusion_summary": "未找到相关证据，无法核实该内容的真实性。",
            "dimensional_analysis": {},
            "reasoning_chain": ["未检索到相关信源", "缺乏可验证的客观依据"],
            "multi_angle_reasoning": {},
            "evidence_evaluation": {},
            "evidence_chain": [],
            "findings": {
                "verified_claims": [],
                "refuted_claims": [],
                "uncertain_claims": ["待鉴定内容"],
                "nuanced_claims": []
            },
            "key_sources_cited": [],
            "traceability_log": {
                "agent_version": "2.0",
                "processing_steps": ["search"],
                "decision_points": [{"step": "search", "decision": "no_evidence_found"}],
                "confidence_breakdown": {}
            },
            "generated_at": str(uuid.uuid1()),
            "processing_time_ms": 0
        }
