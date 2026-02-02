'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ConfidenceRing } from './ConfidenceRing';
import { ConclusionType, CONCLUSION_CONFIG } from '@/types';

interface ResultCardProps {
  conclusion: ConclusionType;
  confidenceScore: number;
  summary: string;
}

export function ResultCard({
  conclusion,
  confidenceScore,
  summary
}: ResultCardProps) {
  const config = CONCLUSION_CONFIG[conclusion];

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold text-gray-800">
          鉴定结论
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-6">
          {/* 可信度环形图 */}
          <div className="flex-shrink-0">
            <ConfidenceRing 
              score={confidenceScore} 
              color={config.color}
              size={100}
              strokeWidth={6}
            />
          </div>

          {/* 结论信息 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-3xl">{config.icon}</span>
              <div>
                <div 
                  className="text-xl font-bold"
                  style={{ color: config.color }}
                >
                  {config.label}
                </div>
                <div className="text-sm text-gray-500">
                  可信度评分
                </div>
              </div>
            </div>
            
            {/* 结论描述 */}
            <p className="text-gray-600 text-sm leading-relaxed">
              {summary}
            </p>
          </div>
        </div>

        {/* 可信度进度条 */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>可信度</span>
            <span>{confidenceScore >= 0.8 ? '高' : confidenceScore >= 0.5 ? '中' : '低'}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000"
              style={{ 
                width: `${confidenceScore * 100}%`,
                backgroundColor: config.color
              }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
