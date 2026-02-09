from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum


class ConclusionType(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNCERTAIN = "uncertain"
    UNVERIFIABLE = "unverifiable"
    PARTIALLY_TRUE = "partially_true"
    MISLEADING = "misleading"


class SourceCredibility(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HEARSAY = "hearsay"


class SourceStance(str, Enum):
    NEUTRAL = "neutral"
    SUPPORTIVE = "supportive"
    OPPOSING = "opposing"
    UNCLEAR = "unclear"


class VerifyRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="待鉴定的舆情内容")
    image_url: Optional[str] = Field(None, description="图片URL（可选）")


class Evidence(BaseModel):
    evidence_id: str
    source_url: str
    source_domain: str
    source_credibility: SourceCredibility
    source_category: str
    publish_time: Optional[str] = None
    title: str
    content_snippet: str
    relevance_score: float = Field(..., ge=0, le=1)
    evidence_type: EvidenceType
    supports: bool
    
    # 新增字段
    is_key_source: bool = Field(default=False, description="是否为关键信源")
    key_insight: str = Field(default="", description="关键信息或观点")
    importance_note: str = Field(default="", description="重要性说明")
    source_stance: str = Field(default="neutral", description="信源立场")
    potential_bias: str = Field(default="", description="潜在偏见")
    deep_analysis: str = Field(default="", description="深度分析")
    unique_value: str = Field(default="", description="独特价值")


class KeySourceCited(BaseModel):
    """被引用的关键信源"""
    evidence_id: str
    title: str
    domain: str
    credibility: str
    key_insight: str
    why_important: str


class DimensionalAnalysis(BaseModel):
    """多维度分析"""
    analysis: str
    key_points: List[str]
    confidence: float


class MultiDimensionalAnalysis(BaseModel):
    """多维度分析结果"""
    factual_dimension: Dict[str, Any] = Field(default_factory=dict, description="事实维度")
    contextual_dimension: Dict[str, Any] = Field(default_factory=dict, description="背景维度")
    motivational_dimension: Dict[str, Any] = Field(default_factory=dict, description="动机维度")
    impact_dimension: Dict[str, Any] = Field(default_factory=dict, description="影响维度")


class SearchAnalysis(BaseModel):
    """Search Agent 的深度分析结果"""
    key_findings: List[str] = Field(default_factory=list, description="核心发现")
    conflict_points: List[str] = Field(default_factory=list, description="信息冲突点")
    evidence_gaps: List[str] = Field(default_factory=list, description="证据缺口")
    analysis_reasoning: str = Field(default="", description="分析推理过程")
    perspectives: Dict[str, str] = Field(default_factory=dict, description="不同立场观点")
    search_reasoning_chain: List[Dict[str, str]] = Field(default_factory=list, description="搜索推理链")


class ReasoningStep(BaseModel):
    step_id: int
    reasoning: str
    basis: List[str]


class VerifyResponse(BaseModel):
    verdict_id: str
    conclusion: ConclusionType
    confidence_score: float = Field(..., ge=0, le=1)
    summary: str
    evidence_list: List[Evidence]
    reasoning_chain: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 新增扩展字段
    dimensional_analysis: Optional[MultiDimensionalAnalysis] = None
    multi_angle_reasoning: Optional[Dict[str, str]] = None
    key_sources_cited: Optional[List[KeySourceCited]] = None
    search_analysis: Optional[SearchAnalysis] = None


class LoadingStep(BaseModel):
    step: Literal["parsing", "searching", "verifying"]
    message: str
