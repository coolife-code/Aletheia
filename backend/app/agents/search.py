import json
import uuid
from typing import List, Dict, Any
import httpx
from datetime import datetime

from app.core.config import settings


class SearchAgent:
    """搜索 Agent - 执行定制化全网检索"""

    def __init__(self):
        self.search_provider = settings.SEARCH_PROVIDER
        self.serpapi_key = settings.SERPAPI_KEY
        self.google_api_key = settings.GOOGLE_SEARCH_API_KEY
        self.google_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.bing_api_key = settings.BING_SEARCH_API_KEY
        self.newsapi_key = settings.NEWSAPI_KEY
        print(f"[SearchAgent] Initialized with provider: {self.search_provider}")
        print(f"[SearchAgent] API Keys - NewsAPI: {'set' if self.newsapi_key else 'not set'}, SerpAPI: {'set' if self.serpapi_key else 'not set'}")

    async def search(self, parser_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行搜索，收集证据

        Args:
            parser_result: Parser Agent 的输出

        Returns:
            结构化的证据数据集
        """
        search_id = str(uuid.uuid4())
        queries = parser_result.get("search_queries", [])

        print(f"[SearchAgent] Starting search with {len(queries)} queries")

        all_sources = []

        # 对每个查询执行搜索
        for i, query_item in enumerate(queries[:2]):  # 限制查询数量
            query_text = query_item.get("query_text", "")
            print(f"[SearchAgent] Query {i+1}: {query_text}")
            if not query_text:
                print(f"[SearchAgent] Query {i+1} is empty, skipping")
                continue

            sources = await self._execute_search(query_text)
            print(f"[SearchAgent] Query {i+1} returned {len(sources)} sources")
            all_sources.extend(sources)

        # 去重和排序
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = self._rank_sources(unique_sources)

        # 增加返回数量到30条
        return_count = min(30, len(ranked_sources))
        print(f"[SearchAgent] Search complete: {len(all_sources)} total, {len(unique_sources)} unique, returning {return_count}")

        return {
            "search_id": search_id,
            "parser_task_ref": parser_result.get("task_id"),
            "query_sources": ranked_sources[:return_count],  # 增加到30条
            "search_metadata": {
                "total_queries": len(queries),
                "sources_found": len(all_sources),
                "sources_after_dedup": len(unique_sources),
                "coverage_score": min(0.95, 0.5 + len(unique_sources) * 0.05),
                "completeness_score": min(0.95, 0.5 + len(unique_sources) * 0.03),
                "search_duration_ms": 3500
            }
        }

    async def _execute_search(self, query: str) -> List[Dict[str, Any]]:
        """执行搜索 - 优先使用真实API"""
        print(f"[SearchAgent] _execute_search called")

        # 优先顺序：NewsAPI > SerpAPI > Google > Bing
        if self.newsapi_key:
            print(f"[SearchAgent] Using NewsAPI (API key available)")
            return await self._search_newsapi(query)
        elif self.serpapi_key:
            print(f"[SearchAgent] Using SerpAPI (API key available)")
            return await self._search_serpapi(query)
        elif self.google_api_key:
            print(f"[SearchAgent] Using Google")
            return await self._search_google(query)
        elif self.bing_api_key:
            print(f"[SearchAgent] Using Bing")
            return await self._search_bing(query)
        else:
            print(f"[SearchAgent] No API key configured, returning empty results")
            return []  # 没有API Key时返回空列表

    async def _search_newsapi(self, query: str) -> List[Dict[str, Any]]:
        """使用 NewsAPI 搜索新闻 - 获取更多结果"""
        print(f"[SearchAgent] Calling NewsAPI with query: {query[:50]}...")
        all_sources = []

        async with httpx.AsyncClient() as client:
            try:
                # 第一页：获取最新新闻
                response1 = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": query,
                        "apiKey": self.newsapi_key,
                        "language": "zh",
                        "sortBy": "publishedAt",
                        "pageSize": 20,
                        "page": 1
                    },
                    timeout=10.0
                )
                print(f"[SearchAgent] NewsAPI (recent) response status: {response1.status_code}")

                if response1.status_code == 200:
                    data1 = response1.json()
                    if data1.get("status") == "ok":
                        articles1 = data1.get("articles", [])
                        print(f"[SearchAgent] NewsAPI (recent) returned {len(articles1)} articles")
                        for article in articles1:
                            url = article.get("url", "")
                            domain = self._extract_domain(url)
                            all_sources.append({
                                "evidence_id": str(uuid.uuid4()),
                                "source_url": url,
                                "source_domain": domain,
                                "source_credibility": self._evaluate_credibility(url),
                                "source_category": "news",
                                "publish_time": article.get("publishedAt"),
                                "title": article.get("title", ""),
                                "content_snippet": article.get("description", "") or article.get("content", "")[:200],
                                "full_text": "",
                                "relevance_score": 0.9,
                                "evidence_type": "primary"
                            })

                # 第二页：获取相关度最高的新闻
                response2 = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": query,
                        "apiKey": self.newsapi_key,
                        "language": "zh",
                        "sortBy": "relevancy",
                        "pageSize": 20,
                        "page": 1
                    },
                    timeout=10.0
                )
                print(f"[SearchAgent] NewsAPI (relevancy) response status: {response2.status_code}")

                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get("status") == "ok":
                        articles2 = data2.get("articles", [])
                        print(f"[SearchAgent] NewsAPI (relevancy) returned {len(articles2)} articles")
                        for article in articles2:
                            url = article.get("url", "")
                            domain = self._extract_domain(url)
                            all_sources.append({
                                "evidence_id": str(uuid.uuid4()),
                                "source_url": url,
                                "source_domain": domain,
                                "source_credibility": self._evaluate_credibility(url),
                                "source_category": "news",
                                "publish_time": article.get("publishedAt"),
                                "title": article.get("title", ""),
                                "content_snippet": article.get("description", "") or article.get("content", "")[:200],
                                "full_text": "",
                                "relevance_score": 0.85,
                                "evidence_type": "primary"
                            })

                # 第三页：英文新闻补充
                response3 = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": query,
                        "apiKey": self.newsapi_key,
                        "language": "en",
                        "sortBy": "relevancy",
                        "pageSize": 10,
                        "page": 1
                    },
                    timeout=10.0
                )
                print(f"[SearchAgent] NewsAPI (english) response status: {response3.status_code}")

                if response3.status_code == 200:
                    data3 = response3.json()
                    if data3.get("status") == "ok":
                        articles3 = data3.get("articles", [])
                        print(f"[SearchAgent] NewsAPI (english) returned {len(articles3)} articles")
                        for article in articles3:
                            url = article.get("url", "")
                            domain = self._extract_domain(url)
                            all_sources.append({
                                "evidence_id": str(uuid.uuid4()),
                                "source_url": url,
                                "source_domain": domain,
                                "source_credibility": self._evaluate_credibility(url),
                                "source_category": "news",
                                "publish_time": article.get("publishedAt"),
                                "title": article.get("title", ""),
                                "content_snippet": article.get("description", "") or article.get("content", "")[:200],
                                "full_text": "",
                                "relevance_score": 0.8,
                                "evidence_type": "primary"
                            })

                print(f"[SearchAgent] NewsAPI total sources collected: {len(all_sources)}")

                if len(all_sources) > 0:
                    return all_sources
                else:
                    print(f"[SearchAgent] NewsAPI returned no results")
                    return []  # 返回空列表，不使用模拟数据

            except Exception as e:
                print(f"[SearchAgent] NewsAPI search error: {e}")
                return []  # 返回空列表，不使用模拟数据

    async def _search_serpapi(self, query: str) -> List[Dict[str, Any]]:
        """使用 SerpAPI 搜索"""
        print(f"[SearchAgent] Calling SerpAPI with query: {query[:50]}...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "num": 5
                    },
                    timeout=10.0
                )
                print(f"[SearchAgent] SerpAPI response status: {response.status_code}")

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    print(f"[SearchAgent] SerpAPI error: HTTP {response.status_code}")
                    if response.status_code == 401:
                        print(f"[SearchAgent] SerpAPI 401: API Key 无效或已过期")
                    return []  # 返回空列表，不使用模拟数据

                data = response.json()

                sources = []
                organic_results = data.get("organic_results", [])
                print(f"[SearchAgent] SerpAPI returned {len(organic_results)} organic results")
                for result in organic_results:
                    sources.append({
                        "evidence_id": str(uuid.uuid4()),
                        "source_url": result.get("link", ""),
                        "source_domain": self._extract_domain(result.get("link", "")),
                        "source_credibility": self._evaluate_credibility(result.get("link", "")),
                        "source_category": "news",
                        "publish_time": None,
                        "title": result.get("title", ""),
                        "content_snippet": result.get("snippet", ""),
                        "full_text": "",
                        "relevance_score": 0.8,
                        "evidence_type": "secondary"
                    })
                return sources
            except Exception as e:
                print(f"[SearchAgent] SerpAPI search error: {e}")
                return []  # 返回空列表，不使用模拟数据

    async def _search_google(self, query: str) -> List[Dict[str, Any]]:
        """使用 Google Custom Search API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "q": query,
                        "key": self.google_api_key,
                        "cx": self.google_engine_id,
                        "num": 5
                    },
                    timeout=10.0
                )

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    print(f"[SearchAgent] Google search error: HTTP {response.status_code}")
                    return []  # 返回空列表，不使用模拟数据

                data = response.json()

                sources = []
                for item in data.get("items", []):
                    sources.append({
                        "evidence_id": str(uuid.uuid4()),
                        "source_url": item.get("link", ""),
                        "source_domain": self._extract_domain(item.get("link", "")),
                        "source_credibility": self._evaluate_credibility(item.get("link", "")),
                        "source_category": "news",
                        "publish_time": None,
                        "title": item.get("title", ""),
                        "content_snippet": item.get("snippet", ""),
                        "full_text": "",
                        "relevance_score": 0.8,
                        "evidence_type": "secondary"
                    })
                return sources
            except Exception as e:
                print(f"[SearchAgent] Google search error: {e}")
                return []  # 返回空列表，不使用模拟数据

    async def _search_bing(self, query: str) -> List[Dict[str, Any]]:
        """使用 Bing Search API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.bing.microsoft.com/v7.0/search",
                    headers={"Ocp-Apim-Subscription-Key": self.bing_api_key},
                    params={"q": query, "count": 5},
                    timeout=10.0
                )

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    print(f"[SearchAgent] Bing search error: HTTP {response.status_code}")
                    return []  # 返回空列表，不使用模拟数据

                data = response.json()

                sources = []
                for item in data.get("webPages", {}).get("value", []):
                    sources.append({
                        "evidence_id": str(uuid.uuid4()),
                        "source_url": item.get("url", ""),
                        "source_domain": self._extract_domain(item.get("url", "")),
                        "source_credibility": self._evaluate_credibility(item.get("url", "")),
                        "source_category": "news",
                        "publish_time": None,
                        "title": item.get("name", ""),
                        "content_snippet": item.get("snippet", ""),
                        "full_text": "",
                        "relevance_score": 0.8,
                        "evidence_type": "secondary"
                    })
                return sources
            except Exception as e:
                print(f"[SearchAgent] Bing search error: {e}")
                return []  # 返回空列表，不使用模拟数据

    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url

    def _evaluate_credibility(self, url: str) -> str:
        """评估信源可信度"""
        high_credibility_domains = [
            "xinhuanet.com", "people.com.cn", "gov.cn",
            "bbc.com", "reuters.com", "apnews.com",
            "nature.com", "science.org"
        ]

        domain = self._extract_domain(url).lower()

        for high_domain in high_credibility_domains:
            if high_domain in domain:
                return "high"

        return "medium"

    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重 - 按URL去重，同时限制每个域名的文章数量"""
        seen_urls = set()
        domain_counts = {}
        unique_sources = []
        
        # 限制每个域名最多保留5篇文章
        MAX_PER_DOMAIN = 5

        for source in sources:
            url = source.get("source_url", "")
            domain = source.get("source_domain", "")
            
            # 跳过重复URL
            if url in seen_urls:
                continue
            
            # 检查该域名是否已达到上限
            domain_count = domain_counts.get(domain, 0)
            if domain_count >= MAX_PER_DOMAIN:
                continue
            
            seen_urls.add(url)
            domain_counts[domain] = domain_count + 1
            unique_sources.append(source)

        return unique_sources

    def _rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按可信度排序"""
        credibility_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            sources,
            key=lambda x: (credibility_order.get(x.get("source_credibility", "low"), 3), -x.get("relevance_score", 0))
        )
