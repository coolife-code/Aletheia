from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio

from app.models.schemas import VerifyRequest, VerifyResponse, LoadingStep
from app.agents.parser import ParserAgent
from app.agents.search import SearchAgent
from app.agents.verdict import VerdictAgent

router = APIRouter()

# 初始化 Agents
parser_agent = ParserAgent()
search_agent = SearchAgent()
verdict_agent = VerdictAgent()


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """
    鉴定舆情内容的真实性（非流式版本）
    
    流程：
    1. Parser Agent 解析内容
    2. Search Agent 搜索证据
    3. Verdict Agent 生成鉴定结论
    """
    try:
        # Step 1: 解析内容
        parser_result = await parser_agent.parse(request.content)
        
        # Step 2: 搜索证据
        search_result = await search_agent.search(parser_result)
        
        # Step 3: 生成鉴定结论
        verdict_result = await verdict_agent.verdict(search_result, request.content)
        
        # 构建响应
        evidence_list = [
            {
                "evidence_id": s.get("evidence_id"),
                "source_url": s.get("source_url"),
                "source_domain": s.get("source_domain"),
                "source_credibility": s.get("source_credibility"),
                "source_category": s.get("source_category"),
                "publish_time": s.get("publish_time"),
                "title": s.get("title"),
                "content_snippet": s.get("content_snippet"),
                "relevance_score": s.get("relevance_score"),
                "evidence_type": s.get("evidence_type"),
                "supports": True
            }
            for s in search_result.get("query_sources", [])
        ]
        
        return VerifyResponse(
            verdict_id=verdict_result.get("verdict_id"),
            conclusion=verdict_result.get("conclusion"),
            confidence_score=verdict_result.get("confidence_score"),
            summary=verdict_result.get("conclusion_summary"),
            evidence_list=evidence_list,
            reasoning_chain=verdict_result.get("reasoning_chain", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"鉴定过程出错: {str(e)}")


@router.post("/verify/stream")
async def verify_content_stream(request: VerifyRequest):
    """
    流式鉴定舆情内容，实时返回每个 Agent 的推理过程
    
    返回格式：
    {
        "type": "reasoning" | "result",
        "agent": "parser" | "search" | "verdict",
        "step": "步骤名称",
        "content": "推理内容",
        "data": {}  // 最终结果时包含
    }
    """
    async def event_generator():
        try:
            # ==================== Step 1: Parser Agent ====================
            yield f"data: {json.dumps({'type': 'start', 'agent': 'parser', 'step': '开始解析', 'content': '🔄 Parser Agent 开始解析内容...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            parser_result_data = None
            async for parser_event in parser_agent.parse_stream(request.content):
                yield f"data: {json.dumps(parser_event, ensure_ascii=False)}\n\n"
                if parser_event.get("type") == "result":
                    parser_result_data = parser_event.get("data")
                await asyncio.sleep(0.1)  # 小延迟让前端有时间渲染
            
            # 检查是否需要澄清
            if parser_result_data and parser_result_data.get("needs_clarification"):
                yield f"data: {json.dumps({'type': 'complete', 'needs_clarification': True, 'clarification_prompt': parser_result_data.get('clarification_prompt')}, ensure_ascii=False)}\n\n"
                return
            
            if not parser_result_data:
                yield f"data: {json.dumps({'type': 'error', 'message': '解析失败'}, ensure_ascii=False)}\n\n"
                return
            
            # ==================== Step 2: Search Agent ====================
            yield f"data: {json.dumps({'type': 'start', 'agent': 'search', 'step': '开始搜索', 'content': '🔍 Search Agent 开始搜索证据...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            # 搜索过程状态更新
            search_queries = parser_result_data.get("search_queries", [])
            yield f"data: {json.dumps({'type': 'reasoning', 'agent': 'search', 'step': '搜索查询', 'content': f'准备执行 {len(search_queries)} 个搜索查询...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.5)
            
            # 执行搜索
            search_result = await search_agent.search(parser_result_data)
            
            sources = search_result.get("query_sources", [])
            yield f"data: {json.dumps({'type': 'reasoning', 'agent': 'search', 'step': '搜索结果', 'content': f'✓ 找到 {len(sources)} 个相关信源'}, ensure_ascii=False)}\n\n"
            
            # 显示找到的信源
            for i, source in enumerate(sources[:3], 1):
                domain = source.get("source_domain", "未知")
                title = source.get("title", "")[:40]
                yield f"data: {json.dumps({'type': 'reasoning', 'agent': 'search', 'step': '信源详情', 'content': f'  {i}. {domain} - {title}...'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
            
            if len(sources) > 3:
                yield f"data: {json.dumps({'type': 'reasoning', 'agent': 'search', 'step': '信源详情', 'content': f'  ... 还有 {len(sources) - 3} 个信源'}, ensure_ascii=False)}\n\n"
            
            await asyncio.sleep(0.3)
            
            # ==================== Step 3: Verdict Agent ====================
            yield f"data: {json.dumps({'type': 'start', 'agent': 'verdict', 'step': '开始鉴定', 'content': '🧠 Verdict Agent 开始分析鉴定...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            verdict_result_data = None
            async for verdict_event in verdict_agent.verdict_stream(search_result, request.content):
                yield f"data: {json.dumps(verdict_event, ensure_ascii=False)}\n\n"
                if verdict_event.get("type") == "result":
                    verdict_result_data = verdict_event.get("data")
                await asyncio.sleep(0.1)
            
            # ==================== 最终结果 ====================
            if verdict_result_data:
                # 构建证据列表
                evidence_list = [
                    {
                        "evidence_id": s.get("evidence_id"),
                        "source_url": s.get("source_url"),
                        "source_domain": s.get("source_domain"),
                        "source_credibility": s.get("source_credibility"),
                        "source_category": s.get("source_category"),
                        "publish_time": s.get("publish_time"),
                        "title": s.get("title"),
                        "content_snippet": s.get("content_snippet"),
                        "relevance_score": s.get("relevance_score"),
                        "evidence_type": s.get("evidence_type"),
                        "supports": True
                    }
                    for s in search_result.get("query_sources", [])
                ]
                
                final_result = {
                    "verdict_id": verdict_result_data.get("verdict_id"),
                    "conclusion": verdict_result_data.get("conclusion"),
                    "confidence_score": verdict_result_data.get("confidence_score"),
                    "summary": verdict_result_data.get("conclusion_summary"),
                    "evidence_list": evidence_list,
                    "reasoning_chain": verdict_result_data.get("reasoning_chain", [])
                }
                
                yield f"data: {json.dumps({'type': 'complete', 'result': final_result}, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '鉴定过程未完成'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            print(f"[Stream Error] {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "aletheia"}
