'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ConfidenceRing } from './ConfidenceRing';
import { ConclusionType, CONCLUSION_CONFIG, MultiDimensionalAnalysis, MultiAngleReasoning, Findings } from '../types';
import { ChevronDown, ChevronUp, Layers, Lightbulb, CheckCircle, XCircle, HelpCircle, AlertCircle, Download, FileJson, FileText, File, PenTool } from 'lucide-react';
import { Button } from './ui/button';
import { ArticlePanel } from './ArticlePanel';
import { VerifyResponse, ArticleResponse } from '../types';

interface ResultCardProps {
  conclusion: ConclusionType;
  confidenceScore: number;
  summary: string;
  dimensionalAnalysis?: MultiDimensionalAnalysis;
  multiAngleReasoning?: MultiAngleReasoning;
  findings?: Findings;
  onGenerateArticle?: () => void;
  articleData?: ArticleResponse | null;
  isGeneratingArticle?: boolean;
  verifyResult?: VerifyResponse;
  originalContent?: string;
}

export function ResultCard({
  conclusion,
  confidenceScore,
  summary,
  dimensionalAnalysis,
  multiAngleReasoning,
  findings,
  onGenerateArticle,
  articleData,
  isGeneratingArticle = false,
  verifyResult,
  originalContent
}: ResultCardProps) {
  const config = CONCLUSION_CONFIG[conclusion];
  const [showDimensions, setShowDimensions] = useState(true);
  const [showAngles, setShowAngles] = useState(false);
  const [showFindings, setShowFindings] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showArticle, setShowArticle] = useState(false);

  const exportToJSON = () => {
    const data = {
      conclusion,
      confidenceScore,
      summary,
      dimensionalAnalysis,
      multiAngleReasoning,
      findings,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aletheia-report-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  };

  const exportToMarkdown = () => {
    let markdown = `# Aletheia 舆情鉴定报告\n\n`;
    markdown += `**导出时间**: ${new Date().toLocaleString('zh-CN')}\n\n`;
    markdown += `---\n\n`;
    
    markdown += `## 鉴定结论\n\n`;
    markdown += `${config.icon} **${config.label}**\n\n`;
    markdown += `**可信度评分**: ${(confidenceScore * 100).toFixed(1)}%\n\n`;
    markdown += `**结论描述**:\n${summary}\n\n`;
    
    if (dimensionalAnalysis) {
      markdown += `---\n\n## 多维度分析\n\n`;
      
      if (dimensionalAnalysis.factual_dimension) {
        markdown += `### 事实维度\n\n`;
        if (dimensionalAnalysis.factual_dimension.analysis) {
          markdown += `${dimensionalAnalysis.factual_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.factual_dimension.key_points?.length) {
          markdown += `**关键点**:\n`;
          dimensionalAnalysis.factual_dimension.key_points.forEach(point => {
            markdown += `- ${point}\n`;
          });
          markdown += `\n`;
        }
      }
      
      if (dimensionalAnalysis.contextual_dimension) {
        markdown += `### 背景维度\n\n`;
        if (dimensionalAnalysis.contextual_dimension.analysis) {
          markdown += `${dimensionalAnalysis.contextual_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.contextual_dimension.key_points?.length) {
          markdown += `**关键点**:\n`;
          dimensionalAnalysis.contextual_dimension.key_points.forEach(point => {
            markdown += `- ${point}\n`;
          });
          markdown += `\n`;
        }
      }
      
      if (dimensionalAnalysis.motivational_dimension) {
        markdown += `### 动机维度\n\n`;
        if (dimensionalAnalysis.motivational_dimension.analysis) {
          markdown += `${dimensionalAnalysis.motivational_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.motivational_dimension.key_points?.length) {
          markdown += `**关键点**:\n`;
          dimensionalAnalysis.motivational_dimension.key_points.forEach(point => {
            markdown += `- ${point}\n`;
          });
          markdown += `\n`;
        }
      }
      
      if (dimensionalAnalysis.impact_dimension) {
        markdown += `### 影响维度\n\n`;
        if (dimensionalAnalysis.impact_dimension.analysis) {
          markdown += `${dimensionalAnalysis.impact_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.impact_dimension.key_points?.length) {
          markdown += `**关键点**:\n`;
          dimensionalAnalysis.impact_dimension.key_points.forEach(point => {
            markdown += `- ${point}\n`;
          });
          markdown += `\n`;
        }
      }
    }
    
    if (multiAngleReasoning && Object.keys(multiAngleReasoning).length > 0) {
      markdown += `---\n\n## 多角度推理\n\n`;
      
      if (multiAngleReasoning.literal_meaning) {
        markdown += `### 字面意思\n${multiAngleReasoning.literal_meaning}\n\n`;
      }
      if (multiAngleReasoning.deep_implication) {
        markdown += `### 深层含义\n${multiAngleReasoning.deep_implication}\n\n`;
      }
      if (multiAngleReasoning.direct_evidence) {
        markdown += `### 直接证据\n${multiAngleReasoning.direct_evidence}\n\n`;
      }
      if (multiAngleReasoning.indirect_evidence) {
        markdown += `### 间接证据\n${multiAngleReasoning.indirect_evidence}\n\n`;
      }
      if (multiAngleReasoning.short_term) {
        markdown += `### 短期影响\n${multiAngleReasoning.short_term}\n\n`;
      }
      if (multiAngleReasoning.long_term) {
        markdown += `### 长期影响\n${multiAngleReasoning.long_term}\n\n`;
      }
    }
    
    if (findings) {
      markdown += `---\n\n## 发现分类\n\n`;
      
      if (findings.verified_claims?.length) {
        markdown += `### ✅ 已验证的主张\n\n`;
        findings.verified_claims.forEach(claim => {
          markdown += `- ${claim}\n`;
        });
        markdown += `\n`;
      }
      
      if (findings.refuted_claims?.length) {
        markdown += `### ❌ 已证伪的主张\n\n`;
        findings.refuted_claims.forEach(claim => {
          markdown += `- ${claim}\n`;
        });
        markdown += `\n`;
      }
      
      if (findings.nuanced_claims?.length) {
        markdown += `### ⚠️ 需要 nuanced 理解\n\n`;
        findings.nuanced_claims.forEach(claim => {
          markdown += `- ${claim}\n`;
        });
        markdown += `\n`;
      }
      
      if (findings.uncertain_claims?.length) {
        markdown += `### ❓ 不确定的主张\n\n`;
        findings.uncertain_claims.forEach(claim => {
          markdown += `- ${claim}\n`;
        });
        markdown += `\n`;
      }
    }
    
    markdown += `---\n\n*本报告由 Aletheia AI 舆情谎言鉴定系统生成*`;
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aletheia-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  };

  const exportToTXT = () => {
    let text = `Aletheia 舆情鉴定报告\n`;
    text += `${'='.repeat(50)}\n\n`;
    text += `导出时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
    text += `${'='.repeat(50)}\n\n`;
    
    text += `【鉴定结论】\n\n`;
    text += `${config.icon} ${config.label}\n\n`;
    text += `可信度评分: ${(confidenceScore * 100).toFixed(1)}%\n\n`;
    text += `结论描述:\n${summary}\n\n`;
    
    if (dimensionalAnalysis) {
      text += `${'='.repeat(50)}\n\n`;
      text += `【多维度分析】\n\n`;
      
      if (dimensionalAnalysis.factual_dimension) {
        text += `--- 事实维度 ---\n\n`;
        if (dimensionalAnalysis.factual_dimension.analysis) {
          text += `${dimensionalAnalysis.factual_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.factual_dimension.key_points?.length) {
          text += `关键点:\n`;
          dimensionalAnalysis.factual_dimension.key_points.forEach(point => {
            text += `  - ${point}\n`;
          });
          text += `\n`;
        }
      }
      
      if (dimensionalAnalysis.contextual_dimension) {
        text += `--- 背景维度 ---\n\n`;
        if (dimensionalAnalysis.contextual_dimension.analysis) {
          text += `${dimensionalAnalysis.contextual_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.contextual_dimension.key_points?.length) {
          text += `关键点:\n`;
          dimensionalAnalysis.contextual_dimension.key_points.forEach(point => {
            text += `  - ${point}\n`;
          });
          text += `\n`;
        }
      }
      
      if (dimensionalAnalysis.motivational_dimension) {
        text += `--- 动机维度 ---\n\n`;
        if (dimensionalAnalysis.motivational_dimension.analysis) {
          text += `${dimensionalAnalysis.motivational_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.motivational_dimension.key_points?.length) {
          text += `关键点:\n`;
          dimensionalAnalysis.motivational_dimension.key_points.forEach(point => {
            text += `  - ${point}\n`;
          });
          text += `\n`;
        }
      }
      
      if (dimensionalAnalysis.impact_dimension) {
        text += `--- 影响维度 ---\n\n`;
        if (dimensionalAnalysis.impact_dimension.analysis) {
          text += `${dimensionalAnalysis.impact_dimension.analysis}\n\n`;
        }
        if (dimensionalAnalysis.impact_dimension.key_points?.length) {
          text += `关键点:\n`;
          dimensionalAnalysis.impact_dimension.key_points.forEach(point => {
            text += `  - ${point}\n`;
          });
          text += `\n`;
        }
      }
    }
    
    if (multiAngleReasoning && Object.keys(multiAngleReasoning).length > 0) {
      text += `${'='.repeat(50)}\n\n`;
      text += `【多角度推理】\n\n`;
      
      if (multiAngleReasoning.literal_meaning) {
        text += `字面意思:\n${multiAngleReasoning.literal_meaning}\n\n`;
      }
      if (multiAngleReasoning.deep_implication) {
        text += `深层含义:\n${multiAngleReasoning.deep_implication}\n\n`;
      }
      if (multiAngleReasoning.direct_evidence) {
        text += `直接证据:\n${multiAngleReasoning.direct_evidence}\n\n`;
      }
      if (multiAngleReasoning.indirect_evidence) {
        text += `间接证据:\n${multiAngleReasoning.indirect_evidence}\n\n`;
      }
      if (multiAngleReasoning.short_term) {
        text += `短期影响:\n${multiAngleReasoning.short_term}\n\n`;
      }
      if (multiAngleReasoning.long_term) {
        text += `长期影响:\n${multiAngleReasoning.long_term}\n\n`;
      }
    }
    
    if (findings) {
      text += `${'='.repeat(50)}\n\n`;
      text += `【发现分类】\n\n`;
      
      if (findings.verified_claims?.length) {
        text += `[已验证的主张]\n\n`;
        findings.verified_claims.forEach(claim => {
          text += `  [√] ${claim}\n`;
        });
        text += `\n`;
      }
      
      if (findings.refuted_claims?.length) {
        text += `[已证伪的主张]\n\n`;
        findings.refuted_claims.forEach(claim => {
          text += `  [×] ${claim}\n`;
        });
        text += `\n`;
      }
      
      if (findings.nuanced_claims?.length) {
        text += `[需要 nuanced 理解]\n\n`;
        findings.nuanced_claims.forEach(claim => {
          text += `  [◆] ${claim}\n`;
        });
        text += `\n`;
      }
      
      if (findings.uncertain_claims?.length) {
        text += `[不确定的主张]\n\n`;
        findings.uncertain_claims.forEach(claim => {
          text += `  [?] ${claim}\n`;
        });
        text += `\n`;
      }
    }
    
    text += `${'='.repeat(50)}\n\n`;
    text += `本报告由 Aletheia AI 舆情谎言鉴定系统生成\n`;
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aletheia-report-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  };

  return (
    <div className="space-y-4">
      {/* 新闻稿面板 */}
      {(showArticle || isGeneratingArticle) && (
        <ArticlePanel
          article={articleData}
          isLoading={isGeneratingArticle}
          onClose={() => setShowArticle(false)}
          onCopy={() => {}}
          onDownload={() => {}}
        />
      )}

      {/* 主要结论卡片 */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-gray-800">
              鉴定结论
            </CardTitle>
            <div className="flex items-center gap-2">
              {onGenerateArticle && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowArticle(true);
                    onGenerateArticle();
                  }}
                  disabled={isGeneratingArticle}
                  className="h-8 px-3 gap-2"
                >
                  <PenTool className="w-4 h-4" />
                  <span className="text-sm">写稿</span>
                </Button>
              )}
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  className="h-8 px-3 gap-2"
                >
                  <Download className="w-4 h-4" />
                  <span className="text-sm">导出报告</span>
                </Button>
                {showExportMenu && (
                  <div className="absolute right-0 top-full mt-2 z-10 bg-white rounded-lg shadow-lg border border-gray-200 py-1 min-w-[180px]">
                    <button
                      onClick={exportToJSON}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 whitespace-nowrap"
                    >
                      <FileJson className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <span>导出 JSON</span>
                    </button>
                    <button
                      onClick={exportToMarkdown}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 whitespace-nowrap"
                    >
                      <FileText className="w-4 h-4 text-green-600 flex-shrink-0" />
                      <span>导出 Markdown</span>
                    </button>
                    <button
                      onClick={exportToTXT}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 whitespace-nowrap"
                    >
                      <File className="w-4 h-4 text-gray-600 flex-shrink-0" />
                      <span>导出 TXT</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
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
