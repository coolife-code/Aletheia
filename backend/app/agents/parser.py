import json
import uuid
from typing import List, Dict, Any, Tuple, Optional, AsyncGenerator
import openai
from anthropic import Anthropic
import hashlib

from app.core.config import settings


class ParserAgent:
    """解析预处理 Agent - 提取舆情核心信息并标准化"""

    # 类级别的缓存
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
        """生成缓存键"""
        return hashlib.md5(content.encode()).hexdigest()

    async def parse(self, content: str) -> Dict[str, Any]:
        """
        解析舆情内容（非流式版本）
        """
        task_id = str(uuid.uuid4())

        # 检查缓存
        cache_key = self._get_cache_key(content)
        if cache_key in self._cache:
            print(f"[ParserAgent] Cache hit for content")
            cached_result = self._cache[cache_key].copy()
            cached_result["task_id"] = task_id
            return cached_result

        # 第一步：判断是否是事件并提取要素
        is_event, event_info = await self._analyze_event(content)

        if not is_event:
            result = {
                "task_id": task_id,
                "is_event": False,
                "needs_clarification": True,
                "clarification_prompt": event_info.get("suggestion", "请提供更多具体信息"),
                "content_summary": content[:50],
                "key_claims": [],
                "search_queries": [],
                "metadata": {
                    "source_type": "user_input",
                    "content_length": len(content),
                    "timestamp": str(uuid.uuid1())
                }
            }
            self._cache[cache_key] = result.copy()
            return result

        # 第二步：生成搜索查询
        search_queries = await self._generate_search_queries(event_info)
        search_queries = sorted(search_queries, key=lambda x: x.get("priority", 99))[:2]

        result = {
            "task_id": task_id,
            "is_event": True,
            "needs_clarification": False,
            "standardized_event": event_info,
            "content_summary": self._generate_summary(event_info),
            "key_claims": self._generate_key_claims(event_info),
            "search_queries": search_queries,
            "metadata": {
                "source_type": "user_input",
                "content_length": len(content),
                "timestamp": str(uuid.uuid1())
            },
            "parser_log": {
                "version": "2.1",
                "processing_time_ms": 0,
                "confidence": 0.95
            }
        }

        self._cache[cache_key] = result.copy()
        return result

    async def parse_stream(self, content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式解析舆情内容，实时返回推理过程
        
        Yields:
            {
                "type": "reasoning" | "result",
                "agent": "parser",
                "step": "事件分析" | "查询生成",
                "content": "推理内容",
                "data": {}  # 最终结果时包含
            }
        """
        task_id = str(uuid.uuid4())

        # 检查缓存
        cache_key = self._get_cache_key(content)
        if cache_key in self._cache:
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": "缓存命中",
                "content": "发现缓存数据，直接使用历史解析结果"
            }
            cached_result = self._cache[cache_key].copy()
            cached_result["task_id"] = task_id
            yield {
                "type": "result",
                "agent": "parser",
                "data": cached_result
            }
            return

        # 第一步：事件分析（流式）
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "事件分析",
            "content": "正在分析内容类型，判断是否为可验证的事件..."
        }

        is_event, event_info, reasoning_text = await self._analyze_event_stream(content)

        # 输出推理过程
        if reasoning_text:
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": "事件分析",
                "content": reasoning_text
            }

        if not is_event:
            result = {
                "task_id": task_id,
                "is_event": False,
                "needs_clarification": True,
                "clarification_prompt": event_info.get("suggestion", "请提供更多具体信息"),
                "content_summary": content[:50],
                "key_claims": [],
                "search_queries": [],
                "metadata": {
                    "source_type": "user_input",
                    "content_length": len(content),
                    "timestamp": str(uuid.uuid1())
                }
            }
            self._cache[cache_key] = result.copy()
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": "事件分析",
                "content": f"分析完成：这不是一个可验证的事件。{event_info.get('suggestion', '')}"
            }
            yield {
                "type": "result",
                "agent": "parser",
                "data": result
            }
            return

        # 输出标准化事件信息
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "事件分析",
            "content": f"✓ 识别为有效事件\n"
                       f"  - 时间: {event_info.get('time', '未明确')}\n"
                       f"  - 人物: {', '.join(event_info.get('people', []))}\n"
                       f"  - 起因: {event_info.get('cause', '')}"
        }

        # 第二步：生成搜索查询（流式）
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "查询生成",
            "content": "正在基于标准化事件生成精准搜索查询..."
        }

        search_queries, query_reasoning = await self._generate_search_queries_stream(event_info)
        search_queries = sorted(search_queries, key=lambda x: x.get("priority", 99))[:2]

        if query_reasoning:
            yield {
                "type": "reasoning",
                "agent": "parser",
                "step": "查询生成",
                "content": query_reasoning
            }

        # 输出生成的查询
        queries_text = "\n".join([f"  {i+1}. {q.get('query_text')}" 
                                  for i, q in enumerate(search_queries)])
        yield {
            "type": "reasoning",
            "agent": "parser",
            "step": "查询生成",
            "content": f"✓ 生成 {len(search_queries)} 个搜索查询:\n{queries_text}"
        }

        result = {
            "task_id": task_id,
            "is_event": True,
            "needs_clarification": False,
            "standardized_event": event_info,
            "content_summary": self._generate_summary(event_info),
            "key_claims": self._generate_key_claims(event_info),
            "search_queries": search_queries,
            "metadata": {
                "source_type": "user_input",
                "content_length": len(content),
                "timestamp": str(uuid.uuid1())
            },
            "parser_log": {
                "version": "2.1",
                "processing_time_ms": 0,
                "confidence": 0.95
            }
        }

        self._cache[cache_key] = result.copy()
        yield {
            "type": "result",
            "agent": "parser",
            "data": result
        }

    async def _analyze_event(self, content: str) -> Tuple[bool, Dict[str, Any]]:
        """非流式事件分析"""
        prompt = f"""分析以下内容是否是"事件"。事件指发生了具体的、可验证的事情。

内容：{content}

按JSON格式输出：
{{
    "is_event": true/false,
    "time": "时间（可推断为现在）",
    "location": "地点（如有）",
    "people": ["涉及的人物/组织"],
    "cause": "起因",
    "process": "经过",
    "result": "结果（如有）",
    "suggestion": "如果不是事件，提示用户补充什么信息"
}}

要求：
- 即使时间不明确，AI可推断为"现在/近日"也算事件
- 地点、结果缺失不影响判断为事件
- 必须包含具体发生的事情"""

        result_text = await self._call_llm(prompt)

        try:
            text = self._clean_json_text(result_text)
            result = json.loads(text)
            return result.get("is_event", False), result
        except Exception as e:
            print(f"[ParserAgent] Event analysis error: {e}")
            return True, {
                "time": "近日",
                "location": "",
                "people": [],
                "cause": content,
                "process": "",
                "result": ""
            }

    async def _analyze_event_stream(self, content: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        流式事件分析，返回推理过程文本
        """
        prompt = f"""分析以下内容是否是"事件"。事件指发生了具体的、可验证的事情。

内容：{content}

按JSON格式输出：
{{
    "is_event": true/false,
    "time": "时间（可推断为现在）",
    "location": "地点（如有）",
    "people": ["涉及的人物/组织"],
    "cause": "起因",
    "process": "经过",
    "result": "结果（如有）",
    "suggestion": "如果不是事件，提示用户补充什么信息",
    "reasoning": "分析推理过程的简要说明"
}}

要求：
- 即使时间不明确，AI可推断为"现在/近日"也算事件
- 地点、结果缺失不影响判断为事件
- 必须包含具体发生的事情
- 请提供reasoning字段说明分析思路"""

        result_text = await self._call_llm(prompt)

        try:
            text = self._clean_json_text(result_text)
            result = json.loads(text)
            reasoning = result.get("reasoning", "")
            return result.get("is_event", False), result, reasoning
        except Exception as e:
            print(f"[ParserAgent] Event analysis error: {e}")
            return True, {
                "time": "近日",
                "location": "",
                "people": [],
                "cause": content,
                "process": "",
                "result": ""
            }, "解析失败，使用默认处理"

    async def _generate_search_queries(self, event_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """非流式查询生成"""
        event_desc = self._build_event_description(event_info)

        prompt = f"""基于以下标准化事件，生成2-3个最核心、最精准的搜索查询：

事件：{event_desc}

按JSON格式输出：
{{
    "queries": [
        {{
            "query_text": "搜索语句（包含关键实体+动作+信源类型）",
            "priority": 1,
            "target_sources": ["news"]
        }}
    ]
}}

要求：
- 只生成2-3个最核心的查询
- 优先级1：官方通报类（包含"官方声明/警方通报/政府回应"）
- 优先级2：事件核心事实类（实体+动作）
- 优先级3：辟谣/核实类（如有必要）
- 每个查询必须包含具体实体和动作关键词"""

        result_text = await self._call_llm(prompt)

        try:
            text = self._clean_json_text(result_text)
            result = json.loads(text)
            queries = result.get("queries", [])
            for i, q in enumerate(queries):
                q["query_id"] = f"q{i+1}"
            return queries
        except Exception as e:
            print(f"[ParserAgent] Query generation error: {e}")
            return self._fallback_queries(event_info)

    async def _generate_search_queries_stream(self, event_info: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
        """
        流式查询生成，返回推理过程
        """
        event_desc = self._build_event_description(event_info)

        prompt = f"""基于以下标准化事件，生成2-3个最核心、最精准的搜索查询：

事件：{event_desc}

按JSON格式输出：
{{
    "queries": [
        {{
            "query_text": "搜索语句（包含关键实体+动作+信源类型）",
            "priority": 1,
            "target_sources": ["news"]
        }}
    ],
    "reasoning": "生成这些查询的思路说明"
}}

要求：
- 只生成2-3个最核心的查询
- 优先级1：官方通报类（包含"官方声明/警方通报/政府回应"）
- 优先级2：事件核心事实类（实体+动作）
- 优先级3：辟谣/核实类（如有必要）
- 每个查询必须包含具体实体和动作关键词
- 请提供reasoning字段说明查询设计思路"""

        result_text = await self._call_llm(prompt)

        try:
            text = self._clean_json_text(result_text)
            result = json.loads(text)
            queries = result.get("queries", [])
            reasoning = result.get("reasoning", "")
            for i, q in enumerate(queries):
                q["query_id"] = f"q{i+1}"
            return queries, reasoning
        except Exception as e:
            print(f"[ParserAgent] Query generation error: {e}")
            return self._fallback_queries(event_info), "生成失败，使用默认查询"

    def _build_event_description(self, event_info: Dict[str, Any]) -> str:
        """构建事件描述"""
        parts = []
        if event_info.get("time"):
            parts.append(event_info["time"])
        if event_info.get("location"):
            parts.append(event_info["location"])
        if event_info.get("people"):
            parts.append("、".join(event_info["people"]))
        if event_info.get("cause"):
            parts.append(event_info["cause"])
        if event_info.get("process"):
            parts.append(event_info["process"])
        if event_info.get("result"):
            parts.append(event_info["result"])
        return "，".join(parts)

    def _generate_summary(self, event_info: Dict[str, Any]) -> str:
        """生成内容摘要"""
        return self._build_event_description(event_info)[:50]

    def _generate_key_claims(self, event_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成关键主张"""
        claims = []

        main_claim = event_info.get("cause", "")
        if main_claim:
            claims.append({
                "claim_id": "c1",
                "claim_text": main_claim,
                "claim_type": "fact",
                "entities": event_info.get("people", [])
            })

        result = event_info.get("result", "")
        if result:
            claims.append({
                "claim_id": "c2",
                "claim_text": result,
                "claim_type": "fact",
                "entities": event_info.get("people", [])
            })

        return claims

    def _fallback_queries(self, event_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """降级查询生成"""
        queries = []
        people = event_info.get("people", [])
        cause = event_info.get("cause", "")

        if people:
            queries.append({
                "query_id": "q1",
                "query_text": f"{people[0]} {cause} 官方声明 通报",
                "target_sources": ["news"],
                "priority": 1
            })

        if cause:
            person = people[0] if people else ""
            queries.append({
                "query_id": f"q{len(queries)+1}",
                "query_text": f"{person} {cause} 最新消息" if person else f"{cause} 最新消息",
                "target_sources": ["news"],
                "priority": 2
            })

        return queries

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            if self.llm_provider == "openai" and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个舆情分析专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
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
