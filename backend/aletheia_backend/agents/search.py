import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
import openai
from anthropic import Anthropic
import asyncio

from aletheia_backend.core.config import settings


class SearchAgent:
    """
    搜索分析 Agent - 专业的信息分析师和找茬专家
    
    职责：
    1. 深度理解问题的核心矛盾和关键点
    2. 执行精准搜索，收集多方证据
    3. 分析信源的可信度、立场和潜在偏见
    4. 识别信息冲突点和突破口
    5. 筛选最关键的信源，标记重要证据
    """

    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=120.0
        ) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
        print(f"[SearchAgent] Initialized with LLM provider: {self.llm_provider}")

    async def search(self, parser_result: Dict[str, Any], original_content: str) -> Dict[str, Any]:
        """
        执行深度搜索和分析

        Args:
            parser_result: Parser Agent 的输出，包含搜索查询列表和分析
            original_content: 用户的原始查询内容

        Returns:
            包含深度分析的信源数据集
        """
        search_id = str(uuid.uuid4())
        search_queries = parser_result.get("search_queries", [])
        query_analysis = parser_result.get("analysis", {})

        print(f"[SearchAgent] Starting deep analysis with {len(search_queries)} queries")

        # 阶段1: 执行多次搜索收集证据
        all_sources = []
        query_reasoning = []

        for i, query in enumerate(search_queries[:4]):
            print(f"[SearchAgent] Query {i+1}/{len(search_queries)}: {query}")

            result = await self._execute_web_search(query, original_content, query_analysis)
            sources = result.get("sources", [])
            reasoning = result.get("search_reasoning", "")

            all_sources.extend(sources)
            if reasoning:
                query_reasoning.append({
                    "query": query,
                    "reasoning": reasoning
                })

            print(f"[SearchAgent] Query {i+1} returned {len(sources)} sources")

        # 阶段2: 深度分析信源
        print(f"[SearchAgent] Starting source analysis...")
        analyzed_sources = await self._analyze_sources_deep(
            all_sources, original_content, query_analysis
        )

        # 阶段3: 识别关键证据和突破口
        print(f"[SearchAgent] Identifying key evidence...")
        key_findings = await self._identify_key_findings(
            analyzed_sources, original_content, query_analysis
        )

        # 阶段4: 整理输出
        unique_sources = self._deduplicate_sources(analyzed_sources)
        ranked_sources = self._rank_sources_by_importance(unique_sources, key_findings)

        # 分离关键信源和普通信源
        key_sources = [s for s in ranked_sources if s.get("is_key_source", False)][:8]
        regular_sources = [s for s in ranked_sources if not s.get("is_key_source", False)][:12]

        print(f"[SearchAgent] Analysis complete: {len(key_sources)} key sources, {len(regular_sources)} regular sources")

        return {
            "search_id": search_id,
            "parser_task_ref": parser_result.get("task_id"),
            "original_query": original_content,
            "query_analysis": query_analysis,
            
            # 关键信源（最重要的突破口）
            "key_sources": key_sources,
            
            # 普通信源
            "regular_sources": regular_sources,
            
            # 所有信源（合并）
            "all_sources": ranked_sources[:20],
            
            # 深度分析结果
            "analysis": {
                # 搜索过程推理
                "search_reasoning_chain": query_reasoning,
                
                # 核心发现
                "key_findings": key_findings.get("findings", []),
                
                # 信息冲突点
                "conflict_points": key_findings.get("conflict_points", []),
                
                # 证据缺口
                "evidence_gaps": key_findings.get("evidence_gaps", []),
                
                # 分析推理过程
                "analysis_reasoning": key_findings.get("analysis_reasoning", ""),
                
                # 多角度观点汇总
                "perspectives": key_findings.get("perspectives", {})
            },
            
            # 元数据
            "search_metadata": {
                "total_queries": len(search_queries),
                "executed_queries": min(len(search_queries), 4),
                "sources_found": len(all_sources),
                "sources_after_dedup": len(unique_sources),
                "key_sources_count": len(key_sources),
                "coverage_score": min(0.95, 0.5 + len(unique_sources) * 0.03),
                "analysis_depth": "deep",
                "search_duration_ms": 8000
            }
        }

    async def search_stream(self, parser_result: Dict[str, Any], original_content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式搜索分析，实时返回推理过程
        """
        search_id = str(uuid.uuid4())
        search_queries = parser_result.get("search_queries", [])
        query_analysis = parser_result.get("analysis", {})

        # 开始分析 - 详细推理过程
        core_entities = query_analysis.get('core_entities', [])
        core_question = query_analysis.get('core_question', '')
        info_types = query_analysis.get('info_types', [])

        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "问题理解",
            "content": f"🧠 Search Agent 开始深度分析...\n\n"
                       f"📌 核心实体识别:\n" +
                       chr(10).join([f"   • {e}" for e in core_entities]) +
                       f"\n\n🎯 核心问题:\n   {core_question}\n\n"
                       f"📋 信息类型: {', '.join(info_types)}\n\n"
                       f"💭 分析思路:\n"
                       f"   1. 理解问题的核心矛盾和关键点\n"
                       f"   2. 设计精准搜索策略，覆盖多角度\n"
                       f"   3. 评估每个信源的可信度和立场\n"
                       f"   4. 识别信息冲突和突破口"
        }

        all_sources = []
        query_reasoning = []

        # 执行多次搜索
        for i, query in enumerate(search_queries[:4]):
            yield {
                "type": "reasoning",
                "agent": "search",
                "step": f"搜索{i+1}",
                "content": f"🔍 执行第 {i+1} 轮搜索...\n\n"
                           f"📡 搜索查询:\n   {query}\n\n"
                           f"💡 搜索策略:\n"
                           f"   • 使用联网搜索获取实时信息\n"
                           f"   • 筛选高可信度信源\n"
                           f"   • 记录搜索思路和关键发现"
            }

            result = await self._execute_web_search(query, original_content, query_analysis)
            sources = result.get("sources", [])
            reasoning = result.get("search_reasoning", "")

            all_sources.extend(sources)
            if reasoning:
                query_reasoning.append({
                    "query": query,
                    "reasoning": reasoning
                })

            yield {
                "type": "reasoning",
                "agent": "search",
                "step": f"搜索{i+1}结果",
                "content": f"✓ 第 {i+1} 轮搜索完成\n"
                           f"   📊 找到 {len(sources)} 个信源\n"
                           f"   💭 搜索思路: {reasoning}"
            }

            # 显示每个信源的详细分析
            for j, source in enumerate(sources, 1):
                credibility = source.get("source_credibility", "medium")
                credibility_emoji = "🟢" if credibility == "high" else "🟡" if credibility == "medium" else "🔴"
                credibility_text = "高" if credibility == "high" else "中" if credibility == "medium" else "低"
                domain = source.get('source_domain', '未知')
                title = source.get('title', '')
                insight = source.get('key_insight', '')

                yield {
                    "type": "reasoning",
                    "agent": "search",
                    "step": f"信源{i+1}-{j}",
                    "content": f"   {credibility_emoji} 信源 {j}: [{credibility_text}可信度]\n"
                               f"      来源: {domain}\n"
                               f"      标题: {title}\n"
                               f"      关键信息: {insight}"
                }

            await asyncio.sleep(0.1)

        # 深度分析阶段 - 只分析最重要的4-5篇
        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "精选精读",
            "content": f"🎯 从 {len(all_sources)} 个信源中精选最重要的进行精读...\n"
                       f"   - 聚焦核心问题：{query_analysis.get('core_question', '')[:50]}...\n"
                       f"   - 只精读4-5篇最关键的信源\n"
                       f"   - 避免过度分析，服务于核心目标"
        }

        analyzed_sources = await self._analyze_sources_deep(
            all_sources, original_content, query_analysis
        )

        deep_analyzed_count = sum(1 for s in analyzed_sources if s.get('is_deep_analyzed'))
        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "精读完成",
            "content": f"✅ 精选精读完成:\n"
                       f"   - 精读信源: {deep_analyzed_count} 篇\n"
                       f"   - 其他信源: {len(analyzed_sources) - deep_analyzed_count} 篇（基础信息）\n"
                       f"   - 聚焦核心问题，避免发散"
        }

        # 识别关键发现
        key_findings = await self._identify_key_findings(
            analyzed_sources, original_content, query_analysis
        )

        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "关键发现",
            "content": f"🎯 关键发现:\n" +
                       "\n".join([f"   {i+1}. {f}" for i, f in enumerate(key_findings.get("findings", []))])
        }

        if key_findings.get("conflict_points"):
            yield {
                "type": "reasoning",
                "agent": "search",
                "step": "冲突识别",
                "content": f"⚠️ 发现信息冲突:\n" +
                           "\n".join([f"   • {c}" for c in key_findings.get("conflict_points", [])])
            }

        # 整理结果
        unique_sources = self._deduplicate_sources(analyzed_sources)
        ranked_sources = self._rank_sources_by_importance(unique_sources, key_findings)

        key_sources = [s for s in ranked_sources if s.get("is_key_source", False)][:8]
        regular_sources = [s for s in ranked_sources if not s.get("is_key_source", False)][:12]

        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "分析总结",
            "content": f"✅ 分析完成!\n"
                       f"   📌 关键信源: {len(key_sources)} 个\n"
                       f"   📄 普通信源: {len(regular_sources)} 个\n"
                       f"   🔍 总覆盖率: {min(95, 50 + len(unique_sources) * 3)}%"
        }

        # 最终结果
        result = {
            "search_id": search_id,
            "parser_task_ref": parser_result.get("task_id"),
            "original_query": original_content,
            "query_analysis": query_analysis,
            "key_sources": key_sources,
            "regular_sources": regular_sources,
            "all_sources": ranked_sources[:20],
            "analysis": {
                "search_reasoning_chain": query_reasoning,
                "key_findings": key_findings.get("findings", []),
                "conflict_points": key_findings.get("conflict_points", []),
                "evidence_gaps": key_findings.get("evidence_gaps", []),
                "analysis_reasoning": key_findings.get("analysis_reasoning", ""),
                "perspectives": key_findings.get("perspectives", {})
            },
            "search_metadata": {
                "total_queries": len(search_queries),
                "executed_queries": min(len(search_queries), 4),
                "sources_found": len(all_sources),
                "sources_after_dedup": len(unique_sources),
                "key_sources_count": len(key_sources),
                "coverage_score": min(0.95, 0.5 + len(unique_sources) * 0.03),
                "analysis_depth": "deep",
                "search_duration_ms": 8000
            }
        }

        yield {
            "type": "result",
            "agent": "search",
            "data": result
        }

    async def _execute_web_search(self, query: str, original_content: str, query_analysis: Dict) -> Dict[str, Any]:
        """
        使用 DeepSeek 联网功能执行单次搜索，带着对问题的理解去搜索
        """
        prompt = f"""你是一位专业的信息分析师和调查记者。请使用联网搜索功能，针对以下查询进行深度搜索。

【原始问题】
{original_content}

【当前搜索策略】
{query}

【问题背景分析】
- 核心实体: {', '.join(query_analysis.get('core_entities', []))}
- 核心问题: {query_analysis.get('core_question', '')}
- 查询意图: {query_analysis.get('query_intent', '')}
- 需要交叉验证: {'是' if query_analysis.get('need_cross_validation') else '否'}

【你的任务】
1. 执行联网搜索，收集相关信源
2. 分析每个信源的可信度、立场和潜在偏见
3. 评估信源与问题的相关性和重要性
4. 思考这个信源可能如何帮助回答问题

请返回以下格式的结果（JSON）：
{{
    "search_reasoning": "详细的搜索思路和分析过程，包括你如何选择关键词、如何评估信源价值",
    "sources": [
        {{
            "evidence_id": "唯一ID",
            "title": "文章标题",
            "source_url": "https://...",
            "source_domain": "网站域名",
            "publish_time": "发布时间",
            "content_snippet": "内容摘要（200字以内，突出与问题的关联）",
            "source_credibility": "high|medium|low",
            "credibility_reason": "可信度评估的详细理由",
            "source_category": "news|government|academic|social|blog",
            "source_stance": "neutral|supportive|opposing|unclear",
            "potential_bias": "潜在偏见说明（如有）",
            "relevance_score": 0.95,
            "evidence_type": "primary|secondary",
            "key_insight": "这个信源提供的关键信息或观点",
            "importance_note": "为什么这个信源重要"
        }}
    ]
}}

要求：
1. 返回4-10个最相关、最有价值的信源
2. 优先官方媒体、政府网站、学术机构、权威媒体
3. 注意识别可能的偏见信源，并标注
4. 每个信源必须包含真实可访问的URL
5. 详细说明搜索思路和你发现的关键信息
6. 思考不同立场的信源，确保观点多元"""

        result_text = await self._call_llm_with_search(prompt)
        return self._parse_search_result(result_text)

    async def _analyze_sources_deep(self, sources: List[Dict], original_content: str, query_analysis: Dict) -> List[Dict]:
        """
        精选4-5篇最重要信源进行精读分析，聚焦核心问题
        """
        if not sources:
            return []

        # 第一步：快速筛选出最有价值的候选信源（最多8个）
        candidates = self._select_candidate_sources(sources, query_analysis)
        
        # 准备候选信源摘要
        sources_summary = []
        for i, s in enumerate(candidates):
            sources_summary.append({
                "index": i,
                "domain": s.get("source_domain", ""),
                "title": s.get("title", "")[:80],
                "credibility": s.get("source_credibility", "medium"),
                "stance": s.get("source_stance", "neutral"),
                "insight": s.get("key_insight", "")[:150],
                "relevance_score": s.get("relevance_score", 0.5)
            })

        prompt = f"""你是一位高效的信息分析师。你的任务是：从候选信源中精选4-5篇最重要的进行精读，直接服务于核心问题的验证。

【核心任务】
{original_content}

【核心问题】
{query_analysis.get('core_question', '')}

【需要验证的关键点】
{', '.join(query_analysis.get('core_entities', []))}

【候选信源】
{json.dumps(sources_summary, ensure_ascii=False, indent=2)}

【你的分析原则】
1. **聚焦目标**：时刻记得你要证明/证伪什么，不要为了分析而分析
2. **精选精读**：只选4-5篇最能帮助回答核心问题的信源深入分析
3. **直接相关**：优先选择与核心问题直接相关、能提供关键证据的信源
4. **多元视角**：确保选取的信源覆盖不同立场（支持/反对/中立）
5. **证据价值**：评估每个信源对核心问题的证明/证伪价值

请返回JSON格式：
{{
    "selected_indices": [0, 2, 3, 5, 7],
    "selection_reasoning": "为什么选择这4-5篇信源，它们如何帮助回答核心问题",
    "source_analysis": [
        {{
            "index": 0,
            "analysis": "精读分析：这个信源对核心问题的直接贡献",
            "key_evidence": "该信源提供的关键证据（直接引用或总结）",
            "evidence_value": "high|medium|low - 对证明/证伪核心问题的价值",
            "reliability_concerns": "可靠性方面的担忧（如有）"
        }}
    ],
    "evidence_summary": "综合这4-5篇信源，对核心问题的证据支持情况总结"
}}

注意：只分析4-5篇最重要的信源，不要面面俱到。"""

        try:
            result_text = await self._call_llm_with_search(prompt)
            analysis_result = self._parse_search_result(result_text)
            
            # 将分析结果合并到原信源（只针对被选中的信源）
            selected_indices = analysis_result.get("selected_indices", [])
            source_analysis = analysis_result.get("source_analysis", [])
            
            # 标记被选中的信源
            for idx in selected_indices:
                if idx < len(candidates):
                    original_idx = candidates[idx].get("_original_index", idx)
                    if original_idx < len(sources):
                        sources[original_idx]["is_deep_analyzed"] = True
                        sources[original_idx]["selection_reasoning"] = analysis_result.get("selection_reasoning", "")
            
            # 合并深度分析结果
            for analysis in source_analysis:
                idx = analysis.get("index", 0)
                if idx < len(candidates):
                    original_idx = candidates[idx].get("_original_index", idx)
                    if original_idx < len(sources):
                        sources[original_idx]["deep_analysis"] = analysis.get("analysis", "")
                        sources[original_idx]["key_evidence"] = analysis.get("key_evidence", "")
                        sources[original_idx]["evidence_value"] = analysis.get("evidence_value", "medium")
                        sources[original_idx]["reliability_concerns"] = analysis.get("reliability_concerns", "")

            print(f"[SearchAgent] Deep analyzed {len(selected_indices)} key sources out of {len(sources)} total")
            return sources
        except Exception as e:
            print(f"[SearchAgent] Deep analysis error: {e}")
            return sources

    def _select_candidate_sources(self, sources: List[Dict], query_analysis: Dict) -> List[Dict]:
        """
        快速筛选最有价值的候选信源（最多8个）供精读
        """
        if not sources:
            return []
        
        # 计算每个信源的初始分数
        scored_sources = []
        for i, source in enumerate(sources):
            score = 0
            
            # 可信度权重（高可信度加分）
            credibility_scores = {"high": 3, "medium": 2, "low": 1}
            score += credibility_scores.get(source.get("source_credibility", "low"), 1) * 5
            
            # 相关度权重
            score += source.get("relevance_score", 0.5) * 10
            
            # 证据类型（一手证据加分）
            if source.get("evidence_type") == "primary":
                score += 5
            
            # 是否有独特见解
            if source.get("key_insight") and len(source.get("key_insight", "")) > 20:
                score += 3
            
            source["_original_index"] = i
            source["_candidate_score"] = score
            scored_sources.append(source)
        
        # 按分数排序，取前8个
        scored_sources.sort(key=lambda x: -x.get("_candidate_score", 0))
        return scored_sources[:8]

    async def _identify_key_findings(self, sources: List[Dict], original_content: str, query_analysis: Dict) -> Dict[str, Any]:
        """
        识别关键发现、冲突点和证据缺口 - 聚焦核心问题
        """
        if not sources:
            return {
                "findings": [],
                "conflict_points": [],
                "evidence_gaps": ["未找到任何相关信源"],
                "analysis_reasoning": "",
                "perspectives": {},
                "key_source_indices": []
            }

        # 优先使用已深度分析的信源，如果没有则选高可信度信源
        deep_analyzed = [s for s in sources if s.get("is_deep_analyzed")]
        if deep_analyzed:
            key_sources = deep_analyzed[:6]
        else:
            # 按可信度排序取前8个
            key_sources = sorted(
                sources, 
                key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("source_credibility", "low"), 0),
                reverse=True
            )[:8]

        # 准备关键信息摘要
        key_info = []
        key_indices = []
        for i, s in enumerate(sources):
            if s in key_sources:
                key_indices.append(i)
                key_info.append({
                    "index": i,
                    "domain": s.get("source_domain", ""),
                    "insight": s.get("key_insight", "")[:150],
                    "stance": s.get("source_stance", "neutral"),
                    "credibility": s.get("source_credibility", "medium"),
                    "is_deep_analyzed": s.get("is_deep_analyzed", False),
                    "evidence_value": s.get("evidence_value", "medium")
                })

        prompt = f"""你是一位目标导向的事实核查专家。基于精选信源，直接回答核心问题。

【核心任务 - 时刻牢记】
{original_content}

【核心问题】
{query_analysis.get('core_question', '')}

【需要验证的关键点】
{', '.join(query_analysis.get('core_entities', []))}

【精选信源（已筛选出最重要的）】
{json.dumps(key_info, ensure_ascii=False, indent=2)}

【你的分析原则】
1. **目标导向**：所有分析都服务于回答核心问题，不要发散
2. **证据说话**：基于信源中的具体证据，而非泛泛而谈
3. **聚焦关键**：只关注对核心问题有直接影响的信息
4. **快速判断**：给出明确的倾向性判断，而非模棱两可

【你的分析任务】
1. **核心发现**（2-4条）：直接回答核心问题的关键事实
2. **信息冲突**（如有）：影响判断的关键矛盾点
3. **证据缺口**：还缺少什么关键信息才能下定论
4. **初步判断**：基于现有证据，核心问题的答案倾向

请返回JSON格式：
{{
    "findings": [
        "核心发现1：直接关联核心问题的关键事实",
        "核心发现2：..."
    ],
    "conflict_points": [
        "关键冲突：直接影响判断的矛盾点"
    ],
    "evidence_gaps": [
        "缺失的关键证据"
    ],
    "analysis_reasoning": "简洁的推理过程：基于什么证据，得出什么初步判断",
    "perspectives": {{
        "supporting": "支持方的核心论据（一句话总结）",
        "opposing": "反对方的核心论据（一句话总结）"
    }},
    "key_source_indices": {key_indices[:5]}
}}

注意：保持简洁聚焦，不要过度分析。"""

        try:
            result_text = await self._call_llm_with_search(prompt)
            return self._parse_search_result(result_text)
        except Exception as e:
            print(f"[SearchAgent] Key findings error: {e}")
            return {
                "findings": ["分析过程中出现错误"],
                "conflict_points": [],
                "evidence_gaps": [],
                "analysis_reasoning": f"错误: {str(e)}",
                "perspectives": {},
                "key_source_indices": []
            }

    async def _call_llm_with_search(self, prompt: str) -> str:
        """调用支持联网功能的 LLM (DeepSeek via 阿里百炼)"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                print(f"[SearchAgent] Calling DeepSeek with web search...")
                
                # 阿里百炼 DeepSeek 联网搜索配置
                # 参考: https://help.aliyun.com/zh/model-studio/user-guide/deepseek
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一位专业的信息分析师、调查记者和事实核查专家。你擅长深度搜索、批判性思维和多角度分析。你总是基于证据说话，善于发现信息冲突和偏见。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    max_tokens=4000,
                    # 阿里百炼联网搜索配置
                    # 使用 enable_search 参数启用联网搜索（阿里百炼特定参数）
                    extra_body={
                        "enable_search": True
                    }
                )
                
                content = response.choices[0].message.content
                print(f"[SearchAgent] LLM Response: {content[:200]}...")
                
                # 检查是否有工具调用结果（搜索结果）
                if hasattr(response.choices[0], 'tool_calls') and response.choices[0].tool_calls:
                    print(f"[SearchAgent] Web search tool was used")
                
                return content
            elif self.llm_provider == "claude" and self.anthropic_client:
                # Claude 目前不直接支持联网搜索，需要配合其他搜索工具
                print(f"[SearchAgent] Claude does not support web search directly")
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=4000,
                    temperature=0.4,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                return "{}"
        except Exception as e:
            print(f"[SearchAgent] LLM Error: {str(e)}")
            return "{}"

    def _parse_search_result(self, result_text: str) -> Dict[str, Any]:
        """解析 LLM 返回的搜索结果"""
        if not result_text or not result_text.strip():
            return {"sources": [], "search_reasoning": "", "findings": [], "conflict_points": [], "evidence_gaps": []}

        text = result_text.strip()

        # 清理 markdown
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            result = json.loads(text)
            
            # 为每个信源添加 ID 和默认值
            if "sources" in result:
                for source in result["sources"]:
                    if not source.get("evidence_id"):
                        source["evidence_id"] = str(uuid.uuid4())
                    if not source.get("source_category"):
                        source["source_category"] = "news"
                    if not source.get("relevance_score"):
                        source["relevance_score"] = 0.8
                    if not source.get("evidence_type"):
                        source["evidence_type"] = "primary"
                    if not source.get("source_stance"):
                        source["source_stance"] = "neutral"
            
            return result
        except json.JSONDecodeError:
            # 尝试提取 JSON
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
            except:
                pass
            return {"sources": [], "search_reasoning": ""}

    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按 URL 去重，保留最完整的版本"""
        seen_urls = {}
        
        for source in sources:
            url = source.get("source_url", "")
            if url:
                if url not in seen_urls:
                    seen_urls[url] = source
                else:
                    # 保留更完整的版本（有更多字段的）
                    existing = seen_urls[url]
                    if len(str(source)) > len(str(existing)):
                        seen_urls[url] = source
        
        return list(seen_urls.values())

    def _rank_sources_by_importance(self, sources: List[Dict[str, Any]], key_findings: Dict) -> List[Dict[str, Any]]:
        """
        按重要性排序信源，优先展示被深度分析的关键信源
        """
        key_indices = set(key_findings.get("key_source_indices", []))
        
        # 为每个信源计算重要性分数
        for i, source in enumerate(sources):
            score = 0
            
            # 是否被深度分析（最高优先级）
            if source.get("is_deep_analyzed"):
                score += 50
                source["is_key_source"] = True
            # 是否被标记为关键信源
            elif i in key_indices:
                score += 30
                source["is_key_source"] = True
            else:
                source["is_key_source"] = False
            
            # 证据价值权重
            evidence_value_scores = {"high": 15, "medium": 8, "low": 3}
            score += evidence_value_scores.get(source.get("evidence_value", "medium"), 5)
            
            # 可信度权重
            credibility_scores = {"high": 10, "medium": 5, "low": 2}
            score += credibility_scores.get(source.get("source_credibility", "low"), 2)
            
            # 相关度权重
            score += source.get("relevance_score", 0.5) * 10
            
            # 是否有一手证据
            if source.get("evidence_type") == "primary":
                score += 8
            
            source["importance_score"] = score
        
        # 按重要性分数排序
        return sorted(sources, key=lambda x: -x.get("importance_score", 0))
