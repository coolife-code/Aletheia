'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Newspaper } from 'lucide-react';
import { Evidence, SourceCredibility } from '@/types';

interface EvidenceListProps {
  evidenceList: Evidence[];
}

const CREDIBILITY_LABELS: Record<SourceCredibility, { label: string; color: string }> = {
  high: { label: '高可信度', color: 'bg-green-100 text-green-700' },
  medium: { label: '中等可信度', color: 'bg-yellow-100 text-yellow-700' },
  low: { label: '低可信度', color: 'bg-gray-100 text-gray-700' },
};

export function EvidenceList({ evidenceList }: EvidenceListProps) {
  if (!evidenceList || evidenceList.length === 0) {
    return null;
  }

  const supportingCount = evidenceList.filter(e => e.supports).length;

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold text-gray-800">
          证据溯源
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {evidenceList.map((evidence, index) => (
            <div 
              key={evidence.evidence_id || index}
              className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  <Newspaper className="w-5 h-5 text-gray-400" />
                </div>
                <div className="flex-1 min-w-0">
                  {/* 来源信息 */}
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="font-medium text-gray-800 text-sm">
                      {evidence.source_domain}
                    </span>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${CREDIBILITY_LABELS[evidence.source_credibility].color}`}
                    >
                      {CREDIBILITY_LABELS[evidence.source_credibility].label}
                    </Badge>
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

                  {/* 摘要 */}
                  <p className="text-xs text-gray-500 line-clamp-2 mb-2">
                    {evidence.content_snippet}
                  </p>

                  {/* 相关度 */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">相关度</span>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${evidence.relevance_score * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {Math.round(evidence.relevance_score * 100)}%
                      </span>
                    </div>
                    
                    {/* 查看原文链接 */}
                    <a
                      href={evidence.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 transition-colors"
                    >
                      查看原文
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 统计信息 */}
        <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-500">
          共找到 {evidenceList.length} 个相关信源
          {supportingCount > 0 && (
            <span className="ml-2">
              ，其中 {supportingCount} 个支持该主张
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
