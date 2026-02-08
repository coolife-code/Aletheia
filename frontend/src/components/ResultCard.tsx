'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ConfidenceRing } from './ConfidenceRing';
import { ConclusionType, CONCLUSION_CONFIG, MultiDimensionalAnalysis, MultiAngleReasoning, Findings } from '@/types';
import { ChevronDown, ChevronUp, Layers, Lightbulb, CheckCircle, XCircle, HelpCircle, AlertCircle } from 'lucide-react';

interface ResultCardProps {
  conclusion: ConclusionType;
  confidenceScore: number;
  summary: string;
  dimensionalAnalysis?: MultiDimensionalAnalysis;
  multiAngleReasoning?: MultiAngleReasoning;
  findings?: Findings;
}

export function ResultCard({
  conclusion,
  confidenceScore,
  summary,
  dimensionalAnalysis,
  multiAngleReasoning,
  findings
}: ResultCardProps) {
  const config = CONCLUSION_CONFIG[conclusion];
  const [showDimensions, setShowDimensions] = useState(true);
  const [showAngles, setShowAngles] = useState(false);
  const [showFindings, setShowFindings] = useState(false);

  return (
    <div className="space-y-4">
      {/* 主要结论卡片 */}
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

      {/* 多维度分析 */}
      {dimensionalAnalysis && (
        <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardHeader className="pb-2">
            <CardTitle 
              className="text-lg font-semibold text-gray-800 flex items-center gap-2 cursor-pointer"
              onClick={() => setShowDimensions(!showDimensions)}
            >
              <Layers className="w-5 h-5 text-indigo-600" />
              多维度分析
              {showDimensions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </CardTitle>
          </CardHeader>
          {showDimensions && (
            <CardContent className="space-y-4">
              {/* 事实维度 */}
              {dimensionalAnalysis.factual_dimension && (
                <DimensionCard 
                  title="事实维度"
                  icon={<CheckCircle className="w-4 h-4 text-green-600" />}
                  data={dimensionalAnalysis.factual_dimension}
                  color="green"
                />
              )}
              
              {/* 背景维度 */}
              {dimensionalAnalysis.contextual_dimension && (
                <DimensionCard 
                  title="背景维度"
                  icon={<Layers className="w-4 h-4 text-blue-600" />}
                  data={dimensionalAnalysis.contextual_dimension}
                  color="blue"
                />
              )}
              
              {/* 动机维度 */}
              {dimensionalAnalysis.motivational_dimension && (
                <DimensionCard 
                  title="动机维度"
                  icon={<Lightbulb className="w-4 h-4 text-purple-600" />}
                  data={dimensionalAnalysis.motivational_dimension}
                  color="purple"
                />
              )}
              
              {/* 影响维度 */}
              {dimensionalAnalysis.impact_dimension && (
                <DimensionCard 
                  title="影响维度"
                  icon={<AlertCircle className="w-4 h-4 text-orange-600" />}
                  data={dimensionalAnalysis.impact_dimension}
                  color="orange"
                />
              )}
            </CardContent>
          )}
        </Card>
      )}

      {/* 多角度推理 */}
      {multiAngleReasoning && Object.keys(multiAngleReasoning).length > 0 && (
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle 
              className="text-lg font-semibold text-gray-800 flex items-center gap-2 cursor-pointer"
              onClick={() => setShowAngles(!showAngles)}
            >
              <Lightbulb className="w-5 h-5 text-amber-600" />
              多角度推理
              {showAngles ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </CardTitle>
          </CardHeader>
          {showAngles && (
            <CardContent className="space-y-3">
              {multiAngleReasoning.literal_meaning && (
                <AngleCard title="字面意思" content={multiAngleReasoning.literal_meaning} />
              )}
              {multiAngleReasoning.deep_implication && (
                <AngleCard title="深层含义" content={multiAngleReasoning.deep_implication} />
              )}
              {multiAngleReasoning.direct_evidence && (
                <AngleCard title="直接证据" content={multiAngleReasoning.direct_evidence} />
              )}
              {multiAngleReasoning.indirect_evidence && (
                <AngleCard title="间接证据" content={multiAngleReasoning.indirect_evidence} />
              )}
              {multiAngleReasoning.short_term && (
                <AngleCard title="短期影响" content={multiAngleReasoning.short_term} />
              )}
              {multiAngleReasoning.long_term && (
                <AngleCard title="长期影响" content={multiAngleReasoning.long_term} />
              )}
            </CardContent>
          )}
        </Card>
      )}

      {/* 发现分类 */}
      {findings && (
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle 
              className="text-lg font-semibold text-gray-800 flex items-center gap-2 cursor-pointer"
              onClick={() => setShowFindings(!showFindings)}
            >
              <CheckCircle className="w-5 h-5 text-green-600" />
              发现分类
              {showFindings ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </CardTitle>
          </CardHeader>
          {showFindings && (
            <CardContent className="space-y-3">
              {/* 已验证 */}
              {findings.verified_claims && findings.verified_claims.length > 0 && (
                <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                  <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center gap-1">
                    <CheckCircle className="w-4 h-4" />
                    已验证的主张
                  </h4>
                  <ul className="space-y-1">
                    {findings.verified_claims.map((claim, idx) => (
                      <li key={idx} className="text-sm text-gray-700 pl-5 relative">
                        <span className="absolute left-0 text-green-500">✓</span>
                        {claim}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 已证伪 */}
              {findings.refuted_claims && findings.refuted_claims.length > 0 && (
                <div className="p-3 bg-red-50 rounded-lg border border-red-100">
                  <h4 className="text-sm font-medium text-red-700 mb-2 flex items-center gap-1">
                    <XCircle className="w-4 h-4" />
                    已证伪的主张
                  </h4>
                  <ul className="space-y-1">
                    {findings.refuted_claims.map((claim, idx) => (
                      <li key={idx} className="text-sm text-gray-700 pl-5 relative">
                        <span className="absolute left-0 text-red-500">✗</span>
                        {claim}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/*  nuanced */}
              {findings.nuanced_claims && findings.nuanced_claims.length > 0 && (
                <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                  <h4 className="text-sm font-medium text-amber-700 mb-2 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    需要 nuanced 理解
                  </h4>
                  <ul className="space-y-1">
                    {findings.nuanced_claims.map((claim, idx) => (
                      <li key={idx} className="text-sm text-gray-700 pl-5 relative">
                        <span className="absolute left-0 text-amber-500">◆</span>
                        {claim}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 不确定 */}
              {findings.uncertain_claims && findings.uncertain_claims.length > 0 && (
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                    <HelpCircle className="w-4 h-4" />
                    不确定的主张
                  </h4>
                  <ul className="space-y-1">
                    {findings.uncertain_claims.map((claim, idx) => (
                      <li key={idx} className="text-sm text-gray-600 pl-5 relative">
                        <span className="absolute left-0 text-gray-400">?</span>
                        {claim}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          )}
        </Card>
      )}
    </div>
  );
}

// 维度卡片组件
function DimensionCard({ 
  title, 
  icon, 
  data, 
  color 
}: { 
  title: string; 
  icon: React.ReactNode; 
  data: { analysis?: string; key_points?: string[]; confidence?: number };
  color: string;
}) {
  const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
    green: { bg: 'bg-green-50', border: 'border-green-100', text: 'text-green-700' },
    blue: { bg: 'bg-blue-50', border: 'border-blue-100', text: 'text-blue-700' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-100', text: 'text-purple-700' },
    orange: { bg: 'bg-orange-50', border: 'border-orange-100', text: 'text-orange-700' },
  };

  const colors = colorClasses[color] || colorClasses.blue;

  return (
    <div className={`p-3 ${colors.bg} rounded-lg border ${colors.border}`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className={`font-medium ${colors.text}`}>{title}</span>
        {data.confidence !== undefined && (
          <span className="text-xs text-gray-500">
            (置信度: {Math.round(data.confidence * 100)}%)
          </span>
        )}
      </div>
      {data.analysis && (
        <p className="text-sm text-gray-700 mb-2">{data.analysis}</p>
      )}
      {data.key_points && data.key_points.length > 0 && (
        <ul className="space-y-1">
          {data.key_points.map((point, idx) => (
            <li key={idx} className="text-xs text-gray-600 pl-4 relative">
              <span className={`absolute left-0 ${colors.text}`}>•</span>
              {point}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// 角度卡片组件
function AngleCard({ title, content }: { title: string; content: string }) {
  return (
    <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
      <h4 className="text-sm font-medium text-amber-700 mb-1">{title}</h4>
      <p className="text-sm text-gray-700">{content}</p>
    </div>
  );
}
