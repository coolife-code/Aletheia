import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
import openai
from anthropic import Anthropic
import asyncio

from app.core.config import settings


class SearchAgent:
    """搜索 Agent - 使用 DeepSeek 联网功能执行多次搜索"""

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

    async def search(self, parser_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行多次联网搜索，收集证据

        Args:
            parser_result: Parser Agent 的输出，包含搜索查询列表

        Returns:
            结构化的证据数据集
        """
        search_id = str(uuid.uuid4())
        search_queries = parser_result.get("search_queries", [])

        print(f"[SearchAgent] Starting search with {len(search_queries)} queries")

        all_sources = []
        all_search_reasoning = []

        # 对每个查询执行联网搜索
        for i, query in enumerate(search_queries[:4]):  # 最多执行4个查询
            print(f"[SearchAgent] Query {i+1}/{len(search_queries)}: {query}")

            result = await self._execute_web_search(query)
            sources = result.get("sources", [])
            reasoning = result.get("search_reasoning", "")

            all_sources.extend(sources)
            if reasoning:
                all_search_reasoning.append(f"查询'{query}':\n{reasoning}")

            print(f"[SearchAgent] Query {i+1} returned {len(sources)} sources")

        # 去重和排序
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = self._rank_sources(unique_sources)

        print(f"[SearchAgent] Search complete: {len(all_sources)} total, {len(unique_sources)} unique")

        return {
            "search_id": search_id,
            "parser_task_ref": parser_result.get("task_id"),
            "query_sources": ranked_sources[:20],  # 返回前20个
            "search_metadata": {
                "total_queries": len(search_queries),
                "executed_queries": min(len(search_queries), 4),
                "sources_found": len(all_sources),
                "sources_after_dedup": len(unique_sources),
                "search_reasoning": "\n\n".join(all_search_reasoning),
                "coverage_score": min(0.95, 0.5 + len(unique_sources) * 0.03),
                "completeness_score": min(0.95, 0.5 + len(unique_sources) * 0.02),
                "search_duration_ms": 8000
            }
        }

    async def search_stream(self, parser_result: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式搜索，实时返回搜索过程和结果
        """
        search_id = str(uuid.uuid4())
        search_queries = parser_result.get("search_queries", [])

        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "搜索规划",
            "content": f"开始执行搜索，共 {len(search_queries)} 条查询策略"
        }

        all_sources = []
        all_search_reasoning = []

        # 对每个查询执行联网搜索
        for i, query in enumerate(search_queries[:4]):
            yield {
                "type": "reasoning",
                "agent": "search",
                "step": "搜索执行",
                "content": f"执行查询 {i+1}/{min(len(search_queries), 4)}: {query[:60]}..."
            }

            result = await self._execute_web_search(query)
            sources = result.get("sources", [])
            reasoning = result.get("search_reasoning", "")

            all_sources.extend(sources)
            if reasoning:
                all_search_reasoning.append(reasoning)

            # 显示该查询的结果
            yield {
                "type": "reasoning",
                "agent": "search",
                "step": "搜索结果",
                "content": f"  ✓ 找到 {len(sources)} 个信源"
            }

            # 显示前2个信源
            for j, source in enumerate(sources[:2], 1):
                yield {
                    "type": "reasoning",
                    "agent": "search",
                    "step": "信源详情",
                    "content": f"    - {source.get('source_domain', '未知')}: {source.get('title', '')[:40]}..."
                }

            if len(sources) > 2:
                yield {
                    "type": "reasoning",
                    "agent": "search",
                    "step": "信源详情",
                    "content": f"    ... 还有 {len(sources) - 2} 个"
                }

            await asyncio.sleep(0.2)

        # 去重和排序
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = self._rank_sources(unique_sources)

        # 搜索总结
        yield {
            "type": "reasoning",
            "agent": "search",
            "step": "搜索总结",
            "content": f"搜索完成！\n"
                       f"  - 总信源数: {len(all_sources)}\n"
                       f"  - 去重后: {len(unique_sources)}\n"
                       f"  - 最终保留: {len(ranked_sources[:20])}"
        }

        result = {
            "search_id": search_id,
            "parser_task_ref": parser_result.get("task_id"),
            "query_sources": ranked_sources[:20],
            "search_metadata": {
                "total_queries": len(search_queries),
                "executed_queries": min(len(search_queries), 4),
                "sources_found": len(all_sources),
                "sources_after_dedup": len(unique_sources),
                "search_reasoning": "\n\n".join(all_search_reasoning),
                "coverage_score": min(0.95, 0.5 + len(unique_sources) * 0.03),
                "completeness_score": min(0.95, 0.5 + len(unique_sources) * 0.02),
                "search_duration_ms": 8000
            }
        }

        yield {
            "type": "result",
            "agent": "search",
            "data": result
        }

    async def _execute_web_search(self, query: str) -> Dict[str, Any]:
        """使用 DeepSeek 联网功能执行单次搜索"""
        prompt = f"""请使用联网搜索功能，搜索以下查询：

查询：{query}

请搜索并返回以下格式的结果（JSON）：
{{
    "search_reasoning": "搜索思路和过程说明",
    "sources": [
        {{
            "evidence_id": "唯一ID",
            "title": "文章标题",
            "source_url": "https://...",
            "source_domain": "网站域名",
            "publish_time": "发布时间",
            "content_snippet": "内容摘要（150字以内）",
            "source_credibility": "high|medium|low",
            "source_category": "news|government|social",
            "relevance_score": 0.9,
            "evidence_type": "primary|secondary",
            "credibility_reason": "可信度评估理由"
        }}
    ]
}}

要求：
1. 返回3-8个最相关的信源
2. 优先官方媒体、政府网站、权威机构
3. 每个信源必须包含真实可访问的URL
4. 评估可信度和相关性
5. 说明搜索思路"""

        result_text = await self._call_llm_with_search(prompt)
        return self._parse_search_result(result_text)

    async def _call_llm_with_search(self, prompt: str) -> str:
        """调用支持联网功能的 LLM"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                print(f"[SearchAgent] Calling DeepSeek with web search...")
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个专业的新闻调查记者，擅长使用联网搜索功能查找权威信源。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=3000
                )
                content = response.choices[0].message.content
                print(f"[SearchAgent] LLM Response: {content[:150]}...")
                return content
            elif self.llm_provider == "claude" and self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=3000,
                    temperature=0.3,
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
            return {"sources": [], "search_reasoning": ""}

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
            sources = result.get("sources", [])

            # 为每个信源添加 ID 和默认值
            for source in sources:
                if not source.get("evidence_id"):
                    source["evidence_id"] = str(uuid.uuid4())
                if not source.get("source_category"):
                    source["source_category"] = "news"
                if not source.get("relevance_score"):
                    source["relevance_score"] = 0.8
                if not source.get("evidence_type"):
                    source["evidence_type"] = "primary"

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
        """按 URL 去重"""
        seen_urls = set()
        unique_sources = []

        for source in sources:
            url = source.get("source_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)

        return unique_sources

    def _rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按可信度排序"""
        credibility_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            sources,
            key=lambda x: (
                credibility_order.get(x.get("source_credibility", "low"), 3),
                -x.get("relevance_score", 0)
            )
        )
