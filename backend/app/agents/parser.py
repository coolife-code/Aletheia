import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
import openai
from anthropic import Anthropic
import hashlib

from app.core.config import settings


class ParserAgent:
    """搜索策略师 Agent - 情报分析与搜索方案设计"""

    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        ) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None

    def _get_cache_key(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    async def parse(self, content: str) -> Dict[str, Any]:
        """分析查询并生成搜索方案"""
        task_id = str(uuid.uuid4())

        cache_key = self._get_cache_key(content)
        if cache_key in self._cache:
            cached_result = self._cache[cache_key].copy()
            cached_result["task_id"] = task_id
            return cached_result

        analysis = await self._analyze_query(content)

        result = {
            "task_id": task_id,
            "original_query": content,
            "analysis": analysis,
            "search_queries": analysis.get("search_queries", []),
            "metadata": {
                "source_type": "user_input",
                "content_length": len(content),
                "timestamp": str(uuid.uuid1())
            }
        }

        self._cache[cache_key] = result.copy()
        return result

    async def parse_stream(self, content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式分析查询"""
        task_id = str(uuid.uuid4())

        cache_key = self._get_cache_key(content)
        if cache_key in self._cache:
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": "缓存命中",
                "content": "发现缓存数据，直接使用历史分析结果"
            }
            cached_result = self._cache[cache_key].copy()
            cached_result["task_id"] = task_id
            yield {
                "type": "result",
                "agent": "parser",
                "data": cached_result
            }
            return

        # 问题分析 - 详细推理过程
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "问题分析",
            "content": "🧠 开始分析问题...\n"
                       "   1. 提取核心实体：识别人物、组织、事件、地点等关键要素\n"
                       "   2. 理解查询意图：判断用户想要验证什么信息\n"
                       "   3. 确定信息类型：事实验证 / 背景信息 / 数据 / 人物传记\n"
                       "   4. 评估验证需求：是否需要多源交叉验证"
        }

        analysis = await self._analyze_query(content)

        # 输出详细分析结果
        core_entities = analysis.get('core_entities', [])
        core_question = analysis.get('core_question', '')
        query_intent = analysis.get('query_intent', '')
        info_types = analysis.get('info_types', [])
        need_cross = analysis.get('need_cross_validation', False)

        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "实体识别",
            "content": f"🔍 核心实体识别:\n" +
                       chr(10).join([f"   • {e}" for e in core_entities])
        }

        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "问题提炼",
            "content": f"🎯 核心问题:\n   {core_question}\n\n" +
                       f"💭 查询意图:\n   {query_intent}"
        }

        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "信息类型",
            "content": f"📋 信息类型分析:\n" +
                       chr(10).join([f"   • {t}" for t in info_types]) +
                       f"\n\n🔗 多源交叉验证: {'需要' if need_cross else '不需要'}"
        }

        # 搜索策略 - 详细说明
        search_strategy = analysis.get('search_strategy', '')
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "搜索策略",
            "content": f"📊 搜索策略规划:\n   {search_strategy}\n\n" +
                       "   策略原则:\n" +
                       "   • 从宽泛到具体：先了解整体背景，再深入细节\n" +
                       "   • 多语言覆盖：中英文结合，获取更全面信息\n" +
                       "   • 多角度验证：官方、媒体、社交平台多方印证\n" +
                       "   • 时效性优先：优先获取最新、最权威的信息"
        }

        # 搜索查询 - 逐个说明
        queries = analysis.get("search_queries", [])
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "查询生成",
            "content": f"📝 生成 {len(queries)} 条精准搜索查询:"
        }

        for i, query in enumerate(queries, 1):
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": f"查询{i}",
                "content": f"   {i}. {query}\n" +
                           f"      目的: 从不同角度收集信息，确保全面覆盖"
            }

        result = {
            "task_id": task_id,
            "original_query": content,
            "analysis": analysis,
            "search_queries": queries,
            "metadata": {
                "source_type": "user_input",
                "content_length": len(content),
                "timestamp": str(uuid.uuid1())
            }
        }

        self._cache[cache_key] = result.copy()
        yield {
            "type": "result",
            "agent": "parser",
            "data": result
        }

    async def _analyze_query(self, content: str) -> Dict[str, Any]:
        """分析查询并生成搜索方案"""
        prompt = f"""你是一位专业的情报分析师和搜索策略师。请对以下事实性查询进行完整的搜索前分析，并设计搜索方案。

查询内容：{content}

请严格按照以下结构输出（JSON格式）：

{{
    "core_entities": ["核心实体1", "核心实体2", ...],
    "core_question": "提炼后的核心问题（一句话）",
    "query_intent": "查询意图说明",
    "info_types": ["事实验证", "背景信息", "数据", "人物传记"],
    "need_cross_validation": true/false,
    "search_strategy": "搜索策略规划（原则：从宽泛到具体、多语言、多角度、可验证）",
    "search_queries": [
        "查询1（精准聚焦）",
        "查询2（精准聚焦）",
        "查询3（精准聚焦）",
        ...
    ]
}}

要求：
1. 核心实体：提取查询中的关键人物、组织、事件、地点等
2. 核心问题：用一句话精准概括用户想问什么
3. 查询意图：说明用户想要得到什么信息
4. 信息类型：从 [事实验证, 背景信息, 数据, 人物传记] 中选择
5. 多源交叉验证：判断是否需要多个独立信源验证
6. 搜索策略：说明搜索思路，如从宽泛到具体、多语言、多角度等
7. 搜索查询：生成3-6条精准搜索查询，中英文都可，每条聚焦不同角度

注意：
- 搜索查询要具体、可执行，包含关键实体
- 查询之间要有差异化，覆盖不同角度
- 优先使用中文查询，必要时补充英文"""

        result_text = await self._call_llm(prompt)

        try:
            text = self._clean_json_text(result_text)
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"[ParserAgent] Analysis error: {e}")
            # 返回默认分析
            return {
                "core_entities": [content[:20]],
                "core_question": content,
                "query_intent": "事实验证",
                "info_types": ["事实验证"],
                "need_cross_validation": True,
                "search_strategy": "直接搜索查询内容",
                "search_queries": [content, f"{content} 官方通报", f"{content} 最新消息"]
            }

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一位专业的情报分析师和搜索策略师，擅长设计精准的搜索方案。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                content = response.choices[0].message.content
                print(f"[ParserAgent] LLM Response: {content[:100]}...")
                return content
            elif self.llm_provider == "claude" and self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=2000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text
                print(f"[ParserAgent] LLM Response: {content[:100]}...")
                return content
            else:
                print(f"[ParserAgent] Warning: No LLM client available")
                return "{}"
        except Exception as e:
            print(f"[ParserAgent] LLM Error: {str(e)}")
            return "{}"

    def _clean_json_text(self, text: str) -> str:
        """清理JSON文本"""
        if not text:
            return "{}"

        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return text.strip()
