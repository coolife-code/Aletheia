"""
角度Agent包

包含15个独立的角度Agent，每个Agent专注于一个特定的调查角度
"""

from .core_fact_checker import CoreFactCheckerAgent
from .timeline_builder import TimelineBuilderAgent
from .stakeholder_mapper import StakeholderMapperAgent
from .sentiment_analyzer import SentimentAnalyzerAgent
from .data_verifier import DataVerifierAgent
from .source_credibility import SourceCredibilityAgent
from .context_analyzer import ContextAnalyzerAgent
from .technical_analyzer import TechnicalAnalyzerAgent
from .legal_analyzer import LegalAnalyzerAgent
from .psychological_analyzer import PsychologicalAnalyzerAgent
from .economic_analyzer import EconomicAnalyzerAgent
from .media_coverage import MediaCoverageAgent
from .social_impact import SocialImpactAgent
from .causality_analyzer import CausalityAnalyzerAgent
from .comparison_analyzer import ComparisonAnalyzerAgent

__all__ = [
    'CoreFactCheckerAgent',
    'TimelineBuilderAgent',
    'StakeholderMapperAgent',
    'SentimentAnalyzerAgent',
    'DataVerifierAgent',
    'SourceCredibilityAgent',
    'ContextAnalyzerAgent',
    'TechnicalAnalyzerAgent',
    'LegalAnalyzerAgent',
    'PsychologicalAnalyzerAgent',
    'EconomicAnalyzerAgent',
    'MediaCoverageAgent',
    'SocialImpactAgent',
    'CausalityAnalyzerAgent',
    'ComparisonAnalyzerAgent',
]
