from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ConclusionType(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNCERTAIN = "uncertain"
    UNVERIFIABLE = "unverifiable"


class SourceCredibility(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HEARSAY = "hearsay"


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


class LoadingStep(BaseModel):
    step: Literal["parsing", "searching", "verifying"]
    message: str
