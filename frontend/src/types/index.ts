export type ConclusionType = 'true' | 'false' | 'uncertain' | 'unverifiable';
export type SourceCredibility = 'high' | 'medium' | 'low';
export type EvidenceType = 'primary' | 'secondary' | 'hearsay';
export type LoadingStepType = 'parsing' | 'searching' | 'verifying' | 'complete' | 'error';

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
}

export interface VerifyRequest {
  content: string;
  image_url?: string;
}

export interface VerifyResponse {
  verdict_id: string;
  conclusion: ConclusionType;
  confidence_score: number;
  summary: string;
  evidence_list: Evidence[];
  reasoning_chain: string[];
}

export interface LoadingStep {
  step: LoadingStepType;
  message: string;
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
    description: '内容属实'
  },
  false: {
    label: '虚假',
    icon: '❌',
    color: '#ef4444',
    bgColor: 'bg-red-50',
    description: '内容虚假'
  },
  uncertain: {
    label: '存疑',
    icon: '⚠️',
    color: '#eab308',
    bgColor: 'bg-yellow-50',
    description: '证据不足'
  },
  unverifiable: {
    label: '无法核实',
    icon: '❓',
    color: '#6b7280',
    bgColor: 'bg-gray-50',
    description: '缺乏依据'
  }
};
