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
    鉴定舆情内容的真实性
    
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
    流式鉴定舆情内容，实时返回进度
    """
    async def event_generator():
        try:
            # Step 1: 解析内容
            yield f"data: {json.dumps({'step': 'parsing', 'message': '正在解析内容...'})}\n\n"
            await asyncio.sleep(0.5)
            parser_result = await parser_agent.parse(request.content)
            
            # Step 2: 搜索证据
            yield f"data: {json.dumps({'step': 'searching', 'message': '正在搜索证据...'})}\n\n"
            await asyncio.sleep(0.5)
            search_result = await search_agent.search(parser_result)
            
            # Step 3: 生成鉴定结论
            yield f"data: {json.dumps({'step': 'verifying', 'message': '正在分析验证...'})}\n\n"
            await asyncio.sleep(0.5)
            verdict_result = await verdict_agent.verdict(search_result, request.content)
            
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
            
            # 返回最终结果
            result = {
                "verdict_id": verdict_result.get("verdict_id"),
                "conclusion": verdict_result.get("conclusion"),
                "confidence_score": verdict_result.get("confidence_score"),
                "summary": verdict_result.get("conclusion_summary"),
                "evidence_list": evidence_list,
                "reasoning_chain": verdict_result.get("reasoning_chain", [])
            }
            yield f"data: {json.dumps({'step': 'complete', 'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "aletheia"}
