'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ExternalLink, Newspaper, Info, Star, AlertTriangle, ChevronDown, ChevronUp, Scale, Eye } from 'lucide-react';
import { Evidence, SourceCredibility } from '../types';

interface EvidenceListProps {
  evidenceList: Evidence[];
  keySourcesCited?: Array<{
    evidence_id: string;
    title: string;
    domain: string;
    credibility: string;
    key_insight: string;
    why_important: string;
  }>;
  searchAnalysis?: {
    key_findings: string[];
    conflict_points: string[];
    evidence_gaps: string[];
    perspectives: {
      supporting?: string;
      opposing?: string;
      neutral?: string;
    };
  };
}

const CREDIBILITY_LABELS: Record<SourceCredibility, { label: string; color: string; bgColor: string }> = {
  high: { label: '高可信度', color: 'text-green-700', bgColor: 'bg-green-100' },
  medium: { label: '中等可信度', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  low: { label: '低可信度', color: 'text-gray-700', bgColor: 'bg-gray-100' },
};

const STANCE_LABELS: Record<string, { label: string; color: string }> = {
  neutral: { label: '中立', color: 'bg-blue-100 text-blue-700' },
  supportive: { label: '支持', color: 'bg-green-100 text-green-700' },
  opposing: { label: '反对', color: 'bg-red-100 text-red-700' },
  unclear: { label: '立场不明', color: 'bg-gray-100 text-gray-700' },
};

export function EvidenceList({ evidenceList, keySourcesCited, searchAnalysis }: EvidenceListProps) {
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
  const [showKeyFindings, setShowKeyFindings] = useState(true);
  const [showAllSources, setShowAllSources] = useState(true);

  if (!evidenceList || evidenceList.length === 0) {
    return null;
  }

  // 分离关键信源和普通信源
  const keySources = evidenceList.filter(e => e.is_key_source);
  const regularSources = evidenceList.filter(e => !e.is_key_source);

  const toggleSource = (id: string) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  return (
    <div className="space-y-6">
      {/* 分析洞察卡片 */}
      {searchAnalysis && (
        <Card className="border-0 shadow-sm bg-gradient-to-br from-purple-50 to-blue-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <Eye className="w-5 h-5 text-purple-600" />
              Search Agent 分析洞察
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 核心发现 */}
            {searchAnalysis.key_findings && searchAnalysis.key_findings.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500" />
                  核心发现
                </h4>
                <ul className="space-y-1.5">
                  {searchAnalysis.key_findings.slice(0, 4).map((finding, idx) => (
                    <li key={idx} className="text-sm text-gray-600 pl-5 relative">
                      <span className="absolute left-0 text-purple-500">•</span>
                      {finding}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 信息冲突 */}
            {searchAnalysis.conflict_points && searchAnalysis.conflict_points.length > 0 && (
              <div className="pt-2 border-t border-purple-100">
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                  信息冲突点
                </h4>
                <ul className="space-y-1.5">
                  {searchAnalysis.conflict_points.slice(0, 3).map((conflict, idx) => (
                    <li key={idx} className="text-sm text-gray-600 pl-5 relative">
                      <span className="absolute left-0 text-orange-500">!</span>
                      {conflict}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 不同立场 */}
            {searchAnalysis.perspectives && (
              <div className="pt-2 border-t border-purple-100">
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Scale className="w-4 h-4 text-blue-500" />
                  多方观点
                </h4>
                <div className="grid grid-cols-1 gap-2">
                  {searchAnalysis.perspectives.supporting && (
                    <div className="p-2 bg-green-50 rounded border border-green-100">
                      <span className="text-xs font-medium text-green-700">支持方：</span>
                      <span className="text-xs text-gray-600">{searchAnalysis.perspectives.supporting}</span>
                    </div>
                  )}
                  {searchAnalysis.perspectives.opposing && (
                    <div className="p-2 bg-red-50 rounded border border-red-100">
                      <span className="text-xs font-medium text-red-700">反对方：</span>
                      <span className="text-xs text-gray-600">{searchAnalysis.perspectives.opposing}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 关键信源 */}
      {keySources.length > 0 && (
        <Card className="border-0 shadow-sm border-l-4 border-l-amber-400">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
              关键信源 ({keySources.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {keySources.map((evidence, index) => (
                <EvidenceCard 
                  key={evidence.evidence_id || index}
                  evidence={evidence}
                  isExpanded={expandedSources.has(evidence.evidence_id)}
                  onToggle={() => toggleSource(evidence.evidence_id)}
                  isKeySource={true}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 所有信源 */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-gray-600" />
            全部信源 ({evidenceList.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* 提示信息 */}
          <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-blue-700">
              点击下方"查看原文"链接将在新标签页打开信源页面。点击信源卡片可查看深度分析。
            </p>
          </div>

          <div className="space-y-3">
            {regularSources.map((evidence, index) => (
              <EvidenceCard 
                key={evidence.evidence_id || index}
                evidence={evidence}
                isExpanded={expandedSources.has(evidence.evidence_id)}
                onToggle={() => toggleSource(evidence.evidence_id)}
                isKeySource={false}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// 单个信源卡片组件
function EvidenceCard({ 
  evidence, 
  isExpanded, 
  onToggle,
  isKeySource 
}: { 
  evidence: Evidence; 
  isExpanded: boolean;
  onToggle: () => void;
  isKeySource: boolean;
}) {
  const credibility = CREDIBILITY_LABELS[evidence.source_credibility];
  const stance = STANCE_LABELS[evidence.source_stance || 'neutral'];

  return (
    <div 
      className={`p-4 rounded-lg border transition-all cursor-pointer ${
        isKeySource 
          ? 'bg-amber-50/50 border-amber-200 hover:border-amber-300' 
          : 'bg-gray-50 border-gray-100 hover:border-gray-200'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start gap-3">
        {/* 图标 */}
        <div className="flex-shrink-0 mt-1">
          {isKeySource ? (
            <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
          ) : (
            <Newspaper className="w-5 h-5 text-gray-400" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          {/* 来源信息行 */}
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-medium text-gray-800 text-sm">
              {evidence.source_domain}
            </span>
            <Badge 
              variant="secondary" 
              className={`text-xs ${credibility.bgColor} ${credibility.color}`}
            >
              {credibility.label}
            </Badge>
            {evidence.source_stance && evidence.source_stance !== 'neutral' && (
              <Badge 
                variant="secondary" 
                className={`text-xs ${stance.color}`}
              >
                {stance.label}
              </Badge>
            )}
            {evidence.publish_time && (
              <span className="text-xs text-gray-400">
                {new Date(evidence.publish_time).toLocaleDateString('zh-CN')}
              </span>
            )}
          </div>

          {/* 标题 */}
          <h4 className="text-sm font-medium text-gray-900 mb-1 line-clamp-1">
            {evidence.title}
          </h4>

          {/* 关键洞察（如果有） */}
          {evidence.key_insight && (
            <p className="text-xs text-purple-700 mb-2 bg-purple-50 p-2 rounded">
              <span className="font-medium">关键信息：</span>
              {evidence.key_insight}
            </p>
          )}

          {/* 摘要 */}
          <p className="text-xs text-gray-500 line-clamp-2 mb-2">
            {evidence.content_snippet}
          </p>

          {/* 展开后的详细内容 */}
          {isExpanded && (
            <div className="mt-3 pt-3 border-t border-gray-200 space-y-3">
              {/* 重要性说明 */}
              {evidence.importance_note && (
                <div className="p-2 bg-amber-50 rounded border border-amber-100">
                  <span className="text-xs font-medium text-amber-700">重要性：</span>
                  <span className="text-xs text-gray-700">{evidence.importance_note}</span>
                </div>
              )}

              {/* 深度分析 */}
              {evidence.deep_analysis && (
                <div>
                  <span className="text-xs font-medium text-gray-700">深度分析：</span>
                  <p className="text-xs text-gray-600 mt-1">{evidence.deep_analysis}</p>
                </div>
              )}

              {/* 独特价值 */}
              {evidence.unique_value && (
                <div>
                  <span className="text-xs font-medium text-gray-700">独特价值：</span>
                  <p className="text-xs text-gray-600 mt-1">{evidence.unique_value}</p>
                </div>
              )}

              {/* 潜在偏见 */}
              {evidence.potential_bias && (
                <div className="p-2 bg-orange-50 rounded border border-orange-100">
                  <span className="text-xs font-medium text-orange-700">潜在偏见：</span>
                  <span className="text-xs text-gray-700">{evidence.potential_bias}</span>
                </div>
              )}
            </div>
          )}

          {/* 底部操作栏 */}
          <div className="flex items-center justify-between mt-2">
            {/* 相关度 */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">相关度</span>
              <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${isKeySource ? 'bg-amber-500' : 'bg-blue-500'}`}
                  style={{ width: `${evidence.relevance_score * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-500">
                {Math.round(evidence.relevance_score * 100)}%
              </span>
            </div>

            {/* 展开/收起 和 查看原文 */}
            <div className="flex items-center gap-3">
              <button 
                className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggle();
                }}
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="w-3 h-3" />
                    收起
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3" />
                    展开详情
                  </>
                )}
              </button>

              <a
                href={evidence.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 transition-colors"
                onClick={(e) => e.stopPropagation()}
              >
                查看原文
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
