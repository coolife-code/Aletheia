"""
Aletheia主系统 - Orchestrator
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .agents import (
    DirectionAgent,
    JudgmentAgent,
    AngleReport,
    DirectionResult,
    JudgmentResult,
    CoreFactCheckerAgent,
    TimelineBuilderAgent,
    StakeholderMapperAgent,
    SentimentAnalyzerAgent,
    DataVerifierAgent,
    SourceCredibilityAgent,
    ContextAnalyzerAgent,
    TechnicalAnalyzerAgent,
    LegalAnalyzerAgent,
    PsychologicalAnalyzerAgent,
    EconomicAnalyzerAgent,
    MediaCoverageAgent,
    SocialImpactAgent,
    CausalityAnalyzerAgent,
    ComparisonAnalyzerAgent,
)
from .core.config import settings


@dataclass
class AnalysisResult:
    """分析结果"""
    direction: DirectionResult
    angle_reports: List[AngleReport]
    judgment: JudgmentResult
    raw_output: Dict[str, Any]


class AletheiaSystem:
    """Aletheia主系统"""
    
    def __init__(self, llm_client, search_client=None):
        self.llm = llm_client
        self.search = search_client
        
        # 初始化核心Agent
        self.direction_agent = DirectionAgent(llm_client)
        self.judgment_agent = JudgmentAgent(llm_client)
        
        # 初始化角度Agent池
        self.angle_agents = {
            "core_fact_checker": CoreFactCheckerAgent(llm_client, search_client),
            "timeline_builder": TimelineBuilderAgent(llm_client, search_client),
            "stakeholder_mapper": StakeholderMapperAgent(llm_client, search_client),
            "sentiment_analyzer": SentimentAnalyzerAgent(llm_client, search_client),
            "data_verifier": DataVerifierAgent(llm_client, search_client),
            "source_credibility": SourceCredibilityAgent(llm_client, search_client),
            "context_analyzer": ContextAnalyzerAgent(llm_client, search_client),
            "technical_analyzer": TechnicalAnalyzerAgent(llm_client, search_client),
            "legal_analyzer": LegalAnalyzerAgent(llm_client, search_client),
            "psychological_analyzer": PsychologicalAnalyzerAgent(llm_client, search_client),
            "economic_analyzer": EconomicAnalyzerAgent(llm_client, search_client),
            "media_coverage": MediaCoverageAgent(llm_client, search_client),
            "social_impact": SocialImpactAgent(llm_client, search_client),
            "causality_analyzer": CausalityAnalyzerAgent(llm_client, search_client),
            "comparison_analyzer": ComparisonAnalyzerAgent(llm_client, search_client),
        }
        
        # 最大并发角度数
        self.max_concurrent_angles = settings.MAX_CONCURRENT_ANGLES
    
    async def analyze(self, content: str) -> AnalysisResult:
        """
        执行完整分析流程
        
        Args:
            content: 待分析的舆情内容
            
        Returns:
            AnalysisResult: 分析结果
        """
        print("[System] 开始分析...")
        
        # Step 1: Direction Agent分析
        print("[System] Direction Agent分析中...")
        direction_result = await self.direction_agent.analyze(content)
        print(f"[System] 事件类型: {direction_result.event_type}")
        print(f"[System] 激活角度: {direction_result.activated_angles}")
        
        # Step 2: 并行执行角度Agent
        print("[System] 角度Agent并行调查中...")
        angle_reports = await self._run_angle_agents(
            content, 
            direction_result.activated_angles
        )
        print(f"[System] 完成{len(angle_reports)}个角度调查")
        
        # Step 3: Judgment Agent综合研判
        print("[System] Judgment Agent综合研判中...")
        judgment_result = await self.judgment_agent.judge(content, angle_reports)
        print("[System] 分析完成")
        
        # 构建最终结果
        raw_output = {
            "direction": {
                "event_type": direction_result.event_type,
                "activated_angles": direction_result.activated_angles,
                "reasoning": direction_result.reasoning,
                "priority_focus": direction_result.priority_focus
            },
            "angle_reports": [
                {
                    "angle_name": r.angle_name,
                    "confidence": r.confidence,
                    "key_sources": r.key_sources,
                    "report": r.report,
                    "reasoning_process": r.reasoning_process
                }
                for r in angle_reports
            ],
            "judgment": {
                "conclusion": judgment_result.conclusion,
                "confidence": judgment_result.confidence,
                "summary": judgment_result.summary,
                "detailed_judgment": judgment_result.detailed_judgment,
                "reasoning_process": judgment_result.reasoning_process
            }
        }
        
        return AnalysisResult(
            direction=direction_result,
            angle_reports=angle_reports,
            judgment=judgment_result,
            raw_output=raw_output
        )
    
    async def _run_angle_agents(self, content: str, angle_names: List[str]) -> List[AngleReport]:
        """
        并行执行角度Agent
        
        Args:
            content: 待分析内容
            angle_names: 角度名称列表
            
        Returns:
            List[AngleReport]: 角度报告列表
        """
        # 限制并发数量
        semaphore = asyncio.Semaphore(self.max_concurrent_angles)
        
        async def run_agent_with_semaphore(angle_name: str):
            async with semaphore:
                return await self._run_single_agent(content, angle_name)
        
        # 创建任务
        tasks = [
            run_agent_with_semaphore(angle_name)
            for angle_name in angle_names
            if angle_name in self.angle_agents
        ]
        
        # 并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉异常结果
        valid_reports = []
        for i, result in enumerate(results):
            angle_name = angle_names[i] if i < len(angle_names) else "unknown"
            if isinstance(result, Exception):
                print(f"[Warning] Agent '{angle_name}' 执行失败: {result}")
            elif result is not None:
                valid_reports.append(result)
        
        return valid_reports
    
    async def _run_single_agent(self, content: str, angle_name: str) -> Optional[AngleReport]:
        """
        执行单个角度Agent
        
        Args:
            content: 待分析内容
            angle_name: 角度名称
            
        Returns:
            Optional[AngleReport]: 角度报告或None
        """
        if angle_name not in self.angle_agents:
            print(f"[Warning] 未知的角度Agent: {angle_name}")
            return None
        
        agent = self.angle_agents[angle_name]
        
        try:
            # 设置超时
            report = await asyncio.wait_for(
                agent.investigate(content),
                timeout=settings.ANGLE_TIMEOUT
            )
            print(f"[System] Agent '{angle_name}' 完成")
            return report
        except asyncio.TimeoutError:
            print(f"[Warning] Agent '{angle_name}' 执行超时")
            return None
        except Exception as e:
            print(f"[Warning] Agent '{angle_name}' 执行失败: {e}")
            return None
    
    async def analyze_stream(self, content: str):
        """
        流式分析，实时返回各阶段结果
        
        Args:
            content: 待分析的舆情内容
            
        Yields:
            Dict: 阶段结果
        """
        # Step 1: Direction Agent
        yield {"stage": "direction", "status": "started"}
        direction_result = await self.direction_agent.analyze(content)
        yield {
            "stage": "direction", 
            "status": "completed",
            "data": {
                "event_type": direction_result.event_type,
                "activated_angles": direction_result.activated_angles,
                "reasoning": direction_result.reasoning
            }
        }
        
        # Step 2: Angle Agents（流式返回每个Agent的结果）
        yield {"stage": "angles", "status": "started"}
        angle_reports = []
        
        for angle_name in direction_result.activated_angles:
            yield {"stage": "angles", "status": "processing", "angle": angle_name}
            
            if angle_name in self.angle_agents:
                agent = self.angle_agents[angle_name]
                try:
                    report = await asyncio.wait_for(
                        agent.investigate(content),
                        timeout=settings.ANGLE_TIMEOUT
                    )
                    angle_reports.append(report)
                    yield {
                        "stage": "angles",
                        "status": "completed",
                        "angle": angle_name,
                        "data": {
                            "angle_name": report.angle_name,
                            "confidence": report.confidence,
                            "report": report.report
                        }
                    }
                except Exception as e:
                    yield {
                        "stage": "angles",
                        "status": "error",
                        "angle": angle_name,
                        "error": str(e)
                    }
        
        # Step 3: Judgment Agent
        yield {"stage": "judgment", "status": "started"}
        judgment_result = await self.judgment_agent.judge(content, angle_reports)
        yield {
            "stage": "judgment",
            "status": "completed",
            "data": {
                "conclusion": judgment_result.conclusion,
                "confidence": judgment_result.confidence,
                "summary": judgment_result.summary,
                "detailed_judgment": judgment_result.detailed_judgment
            }
        }
    
    def get_available_angles(self) -> List[str]:
        """
        获取所有可用的角度Agent
        
        Returns:
            List[str]: 角度Agent名称列表
        """
        return list(self.angle_agents.keys())
    
    def get_angle_info(self, angle_name: str) -> Optional[Dict[str, Any]]:
        """
        获取角度Agent信息
        
        Args:
            angle_name: 角度名称
            
        Returns:
            Optional[Dict[str, Any]]: 角度信息
        """
        if angle_name not in self.angle_agents:
            return None
        
        agent = self.angle_agents[angle_name]
        return {
            "name": angle_name,
            "class_name": agent.__class__.__name__,
            "description": agent.prompt[:200] + "..." if hasattr(agent, 'prompt') else "No description"
        }
