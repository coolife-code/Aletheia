from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer
from sqlalchemy.sql import func
from aletheia_backend.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class VerificationTask(Base):
    """鉴定任务表"""
    __tablename__ = "verification_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False, comment="待鉴定内容")
    content_hash = Column(String(64), index=True, comment="内容哈希")
    
    # 任务状态
    status = Column(String(20), default="pending", comment="pending/processing/completed/failed")
    
    # 鉴定结果
    conclusion = Column(String(20), nullable=True, comment="true/false/uncertain/unverifiable")
    confidence_score = Column(Float, nullable=True, comment="可信度评分 0-1")
    summary = Column(Text, nullable=True, comment="结论摘要")
    reasoning_chain = Column(JSON, default=list, comment="推理过程")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 错误信息
    error_message = Column(Text, nullable=True)


class Evidence(Base):
    """证据表"""
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, index=True, comment="关联的任务ID")
    
    # 来源信息
    source_url = Column(String(2048), nullable=False)
    source_domain = Column(String(255), index=True)
    source_credibility = Column(String(20), comment="high/medium/low")
    source_category = Column(String(50))
    
    # 内容
    title = Column(String(500))
    content_snippet = Column(Text)
    relevance_score = Column(Float)
    evidence_type = Column(String(20), comment="primary/secondary/hearsay")
    supports = Column(Integer, default=1, comment="1支持/0不支持")
    
    # 元数据
    publish_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentLog(Base):
    """Agent 执行日志表"""
    __tablename__ = "agent_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, index=True)
    agent_type = Column(String(50), comment="parser/search/verdict")
    
    # 输入输出
    input_data = Column(JSON)
    output_data = Column(JSON)
    
    # 执行信息
    status = Column(String(20), comment="success/failed")
    processing_time_ms = Column(Integer)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
