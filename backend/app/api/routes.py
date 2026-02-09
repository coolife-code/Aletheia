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
    1. Parser Agent 解析内容，生成搜索策略
    2. Search Agent 深度搜索和分析证据
    3. Verdict Agent 多维度鉴定结论
    """
    try:
        # Step 1: 解析内容
        parser_result = await parser_agent.parse(request.content)
        
        if parser_result.get("needs_clarification"):
            return VerifyResponse(
                verdict_id="",
                conclusion="unverifiable",
                confidence_score=0.0,
                summary=parser_result.get("clarification_prompt", "请提供更多具体信息"),
                evidence_list=[],
                reasoning_chain=[]
            )
        
        # Step 2: 深度搜索和分析（传入原始内容）
        search_result = await search_agent.search(parser_result, request.content)
        
        # Step 3: 多维度鉴定结论
        verdict_result = await verdict_agent.verdict(search_result, request.content)
        
        # 构建响应 - 合并关键信源和普通信源
        all_sources = search_result.get("all_sources", [])
        
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
                "is_key_source": s.get("is_key_source", False),
                "key_insight": s.get("key_insight", ""),
                "importance_note": s.get("importance_note", ""),
                "source_stance": s.get("source_stance", "neutral"),
                "potential_bias": s.get("potential_bias", ""),
                "supports": True
            }
            for s in all_sources
        ]
        
        return VerifyResponse(
            verdict_id=verdict_result.get("verdict_id"),
            conclusion=verdict_result.get("conclusion"),
            confidence_score=verdict_result.get("confidence_score"),
            summary=verdict_result.get("conclusion_summary"),
            evidence_list=evidence_list,
            reasoning_chain=verdict_result.get("reasoning_chain", []),
            # 扩展字段
            dimensional_analysis=verdict_result.get("dimensional_analysis", {}),
            multi_angle_reasoning=verdict_result.get("multi_angle_reasoning", {}),
            key_sources_cited=verdict_result.get("key_sources_cited", []),
            search_analysis=search_result.get("analysis", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"鉴定过程出错: {str(e)}")


@router.post("/verify/stream")
async def verify_content_stream(request: VerifyRequest):
    """
    流式鉴定舆情内容，实时返回每个 Agent 的详细推理过程
    
    返回格式：
    {
        "type": "reasoning" | "result" | "complete" | "error",
        "agent": "parser" | "search" | "verdict",
        "step": "步骤名称",
        "content": "推理内容",
        "data": {}  // 最终结果时包含
    }
    """
    async def event_generator():
        try:
            # ==================== Step 1: Parser Agent ====================
            parser_result_data = None
            async for parser_event in parser_agent.parse_stream(request.content):
                yield f"data: {json.dumps(parser_event, ensure_ascii=False)}\n\n"
                if parser_event.get("type") == "result":
                    parser_result_data = parser_event.get("data")
                await asyncio.sleep(0.05)
            
            # 检查是否需要澄清
            if parser_result_data and parser_result_data.get("needs_clarification"):
                clarification_response = {
                    'type': 'complete',
                    'needs_clarification': True,
                    'clarification_prompt': parser_result_data.get('clarification_prompt')
                }
                yield f"data: {json.dumps(clarification_response, ensure_ascii=False)}\n\n"
                return
            
            if not parser_result_data:
                yield f"data: {json.dumps({'type': 'error', 'message': '解析失败'}, ensure_ascii=False)}\n\n"
                return
            
            # ==================== Step 2: Search Agent (深度搜索分析) ====================
            search_result_data = None
            async for search_event in search_agent.search_stream(parser_result_data, request.content):
                yield f"data: {json.dumps(search_event, ensure_ascii=False)}\n\n"
                if search_event.get("type") == "result":
                    search_result_data = search_event.get("data")
                await asyncio.sleep(0.05)
            
            if not search_result_data:
                yield f"data: {json.dumps({'type': 'error', 'message': '搜索失败'}, ensure_ascii=False)}\n\n"
                return
            
            # ==================== Step 3: Verdict Agent (多维度鉴定) ====================
            verdict_result_data = None
            async for verdict_event in verdict_agent.verdict_stream(search_result_data, request.content):
                yield f"data: {json.dumps(verdict_event, ensure_ascii=False)}\n\n"
                if verdict_event.get("type") == "result":
                    verdict_result_data = verdict_event.get("data")
                await asyncio.sleep(0.05)
            
            # ==================== 最终结果 ====================
            if verdict_result_data:
                # 构建完整的证据列表
                all_sources = search_result_data.get("all_sources", [])
                
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
                        "is_key_source": s.get("is_key_source", False),
                        "key_insight": s.get("key_insight", ""),
                        "importance_note": s.get("importance_note", ""),
                        "source_stance": s.get("source_stance", "neutral"),
                        "potential_bias": s.get("potential_bias", ""),
                        "deep_analysis": s.get("deep_analysis", ""),
                        "unique_value": s.get("unique_value", ""),
                        "supports": True
                    }
                    for s in all_sources
                ]
                
                # 构建完整的最终结果
                final_result = {
                    "verdict_id": verdict_result_data.get("verdict_id"),
                    "conclusion": verdict_result_data.get("conclusion"),
                    "confidence_score": verdict_result_data.get("confidence_score"),
                    "summary": verdict_result_data.get("conclusion_summary"),
                    "evidence_list": evidence_list,
                    "reasoning_chain": verdict_result_data.get("reasoning_chain", []),
                    
                    # Search Agent 的深度分析结果
                    "search_analysis": {
                        "key_findings": search_result_data.get("analysis", {}).get("key_findings", []),
                        "conflict_points": search_result_data.get("analysis", {}).get("conflict_points", []),
                        "evidence_gaps": search_result_data.get("analysis", {}).get("evidence_gaps", []),
                        "analysis_reasoning": search_result_data.get("analysis", {}).get("analysis_reasoning", ""),
                        "perspectives": search_result_data.get("analysis", {}).get("perspectives", {}),
                        "search_reasoning_chain": search_result_data.get("analysis", {}).get("search_reasoning_chain", [])
                    },
                    
                    # Verdict Agent 的多维度分析
                    "dimensional_analysis": verdict_result_data.get("dimensional_analysis", {}),
                    "multi_angle_reasoning": verdict_result_data.get("multi_angle_reasoning", {}),
                    "evidence_evaluation": verdict_result_data.get("evidence_evaluation", {}),
                    
                    # 关键信源引用
                    "key_sources_cited": verdict_result_data.get("key_sources_cited", []),
                    
                    # 发现分类
                    "findings": verdict_result_data.get("findings", {}),
                    
                    # 证据链
                    "evidence_chain": verdict_result_data.get("evidence_chain", []),
                    
                    # 元数据
                    "metadata": {
                        "parser_task_id": parser_result_data.get("task_id"),
                        "search_task_id": search_result_data.get("search_id"),
                        "verdict_task_id": verdict_result_data.get("verdict_id"),
                        "total_sources": len(all_sources),
                        "key_sources_count": len(search_result_data.get("key_sources", [])),
                        "analysis_depth": "deep"
                    }
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
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "aletheia"}
