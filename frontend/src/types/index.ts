export type ConclusionType = 'true' | 'false' | 'uncertain' | 'unverifiable' | 'partially_true' | 'misleading';
export type SourceCredibility = 'high' | 'medium' | 'low';
export type EvidenceType = 'primary' | 'secondary' | 'hearsay';
export type SourceStance = 'neutral' | 'supportive' | 'opposing' | 'unclear';
export type LoadingStepType = 'parsing' | 'searching' | 'verifying' | 'complete' | 'error';

// 扩展 Evidence 接口
export interface Evidence {
  evidence_id: string;
  source_url: string;
  source_domain: string;
  source_credibility: SourceCredibility;
  source_category: string;
  publish_time: string | null;
  title: string;
  content_snippet: string;
  relevance_score: number;
  evidence_type: EvidenceType;
  supports: boolean;
  
  // 新增字段
  is_key_source?: boolean;
  key_insight?: string;
  importance_note?: string;
  source_stance?: SourceStance;
  potential_bias?: string;
  deep_analysis?: string;
  unique_value?: string;
}

// 关键信源引用
export interface KeySourceCited {
  evidence_id: string;
  title: string;
  domain: string;
  credibility: string;
  key_insight: string;
  why_important: string;
}

// 多维度分析
export interface DimensionalAnalysis {
  analysis: string;
  key_points: string[];
  confidence: number;
}

export interface MultiDimensionalAnalysis {
  factual_dimension: DimensionalAnalysis;
  contextual_dimension: DimensionalAnalysis;
  motivational_dimension: DimensionalAnalysis;
  impact_dimension: DimensionalAnalysis;
}

// Search Agent 分析结果
export interface SearchAnalysis {
  key_findings: string[];
  conflict_points: string[];
  evidence_gaps: string[];
  analysis_reasoning: string;
  perspectives: {
    supporting?: string;
    opposing?: string;
    neutral?: string;
  };
  search_reasoning_chain: Array<{
    query: string;
    reasoning: string;
  }>;
}

// 证据评估
export interface EvidenceEvaluation {
  key_sources_assessment: Array<{
    domain: string;
    assessment: string;
    weight: number;
    reliability_concerns?: string;
  }>;
  conflict_resolution: string;
  weight_analysis: string[];
  evidence_strength: number;
  coverage_assessment: string;
  overall_quality: string;
}

// 多角度推理
export interface MultiAngleReasoning {
  literal_meaning?: string;
  deep_implication?: string;
  direct_evidence?: string;
  indirect_evidence?: string;
  short_term?: string;
  long_term?: string;
}

// 发现分类
export interface Findings {
  verified_claims: string[];
  refuted_claims: string[];
  uncertain_claims: string[];
  nuanced_claims: string[];
}

export interface VerifyRequest {
  content: string;
  image_url?: string;
}

// 扩展 VerifyResponse
export interface VerifyResponse {
  verdict_id: string;
  conclusion: ConclusionType;
  confidence_score: number;
  summary: string;
  evidence_list: Evidence[];
  reasoning_chain: string[];
  
  // 新增扩展字段
  dimensional_analysis?: MultiDimensionalAnalysis;
  multi_angle_reasoning?: MultiAngleReasoning;
  key_sources_cited?: KeySourceCited[];
  search_analysis?: SearchAnalysis;
  evidence_evaluation?: EvidenceEvaluation;
  findings?: Findings;
  evidence_chain?: Array<{
    evidence_id: string;
    source_ref: string;
    source_domain: string;
    source_credibility: string;
    is_key_source: boolean;
    supports: boolean;
    weight: number;
    reason: string;
  }>;
  metadata?: {
    parser_task_id: string;
    search_task_id: string;
    verdict_task_id: string;
    total_sources: number;
    key_sources_count: number;
    analysis_depth: string;
  };
}

export interface LoadingStep {
  step: LoadingStepType;
  message: string;
}

// 流式事件类型
export interface StreamEvent {
  type: 'start' | 'reasoning' | 'result' | 'complete' | 'error';
  agent?: 'parser' | 'search' | 'verdict';
  step?: string;
  content?: string;
  data?: any;
  result?: VerifyResponse;
  needs_clarification?: boolean;
  clarification_prompt?: string;
  message?: string;
}

// 推理步骤类型
export interface ReasoningStep {
  id: string;
  agent: 'parser' | 'search' | 'verdict';
  step: string;
  content: string;
  timestamp: number;
}

export const CONCLUSION_CONFIG: Record<ConclusionType, {
  label: string;
  icon: string;
  color: string;
  bgColor: string;
  description: string;
}> = {
  true: {
    label: '真实',
    icon: '✅',
    color: '#22c55e',
    bgColor: 'bg-green-50',
    description: '内容属实，有多个高可信度信源证实'
  },
  false: {
    label: '虚假',
    icon: '❌',
    color: '#ef4444',
    bgColor: 'bg-red-50',
    description: '内容虚假，有明确证据证伪'
  },
  uncertain: {
    label: '存疑',
    icon: '⚠️',
    color: '#eab308',
    bgColor: 'bg-yellow-50',
    description: '证据不足或相互矛盾，无法确定'
  },
  unverifiable: {
    label: '无法核实',
    icon: '❓',
    color: '#6b7280',
    bgColor: 'bg-gray-50',
    description: '缺乏可验证的客观依据'
  },
  partially_true: {
    label: '部分真实',
    icon: '🟨',
    color: '#f59e0b',
    bgColor: 'bg-amber-50',
    description: '部分内容真实，但存在夸大或遗漏'
  },
  misleading: {
    label: '误导性',
    icon: '🟧',
    color: '#f97316',
    bgColor: 'bg-orange-50',
    description: '具有误导性，字面可能正确但引导错误结论'
  }
};

// Agent 配置
export const AGENT_CONFIG: Record<string, {
  name: string;
  icon: string;
  color: string;
  description: string;
}> = {
  parser: {
    name: 'Parser Agent',
    icon: '🔄',
    color: '#3b82f6',
    description: '搜索策略师 - 分析查询并设计搜索方案'
  },
  search: {
    name: 'Search Agent',
    icon: '🔍',
    color: '#8b5cf6',
    description: '信息分析师 - 深度搜索、分析信源、识别关键证据'
  },
  verdict: {
    name: 'Verdict Agent',
    icon: '🧠',
    color: '#10b981',
    description: '多维度鉴定专家 - 多角度分析、综合判断'
  }
};
