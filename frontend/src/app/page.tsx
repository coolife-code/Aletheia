'use client';

import React, { useState, useCallback } from 'react';
import { InputBox } from '../components/InputBox';
import { VerifyButton } from '../components/VerifyButton';
import { ResultCard } from '../components/ResultCard';
import { EvidenceList } from '../components/EvidenceList';
import ReasoningPanel from '../components/ReasoningPanel';
import { verifyContentStream, generateArticle } from '../lib/api';
import { VerifyResponse, StreamEvent, LoadingStepType, ArticleResponse } from '../types';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [inputContent, setInputContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<LoadingStepType>('parsing');
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([]);
  const [articleData, setArticleData] = useState<ArticleResponse | null>(null);
  const [isGeneratingArticle, setIsGeneratingArticle] = useState(false);

  const handleVerify = async () => {
    if (!inputContent.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);
    setStreamEvents([]);

    try {
      // 使用流式 API，实时接收推理过程
      const finalResult = await verifyContentStream(
        { content: inputContent },
        (event: StreamEvent) => {
          // 实时更新推理事件
          setStreamEvents(prev => [...prev, event]);

          // 更新加载步骤
          if (event.agent === 'parser') {
            setLoadingStep('parsing');
          } else if (event.agent === 'search') {
            setLoadingStep('searching');
          } else if (event.agent === 'verdict') {
            setLoadingStep('verifying');
          }
        }
      );

      if (finalResult) {
        setResult(finalResult);
        setLoadingStep('complete');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '网络错误，请稍后重试');
      setLoadingStep('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInputContent('');
    setResult(null);
    setError(null);
    setStreamEvents([]);
    setLoadingStep('parsing');
    setArticleData(null);
  };

  const handleGenerateArticle = async () => {
    if (!result || !inputContent) return;

    setIsGeneratingArticle(true);
    try {
      const article = await generateArticle({
        verify_result: result,
        original_content: inputContent
      });
      setArticleData(article);
    } catch (err) {
      setError(err instanceof Error ? err.message : '新闻稿生成失败');
    } finally {
      setIsGeneratingArticle(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12 md:py-16">
        {/* 头部 */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Aletheia
          </h1>
          <p className="text-lg text-gray-500">
            AI 舆情谎言鉴定系统
          </p>
          <p className="text-sm text-gray-400 mt-2">
            Parser + Search Analyst + Verdict Expert
          </p>
        </div>

        {/* 输入区域 */}
        <div className="space-y-6">
          <InputBox
            value={inputContent}
            onChange={setInputContent}
            disabled={isLoading}
            placeholder="粘贴或输入舆情内容，支持文本、链接、图片..."
          />

          <VerifyButton
            onClick={result ? handleReset : handleVerify}
            isLoading={isLoading}
            loadingStep={loadingStep}
            disabled={!inputContent.trim() && !result}
            hasResult={!!result}
          />
        </div>

        {/* 加载状态提示 */}
        {isLoading && (
          <div className="mt-8 text-center space-y-2">
            <div className="flex items-center justify-center gap-2 text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <p className="text-sm text-gray-400">
              {loadingStep === 'parsing' && '🔄 Parser Agent 正在分析查询并设计搜索策略...'}
              {loadingStep === 'searching' && '🔍 Search Agent 正在深度搜索和分析信源...'}
              {loadingStep === 'verifying' && '🧠 Verdict Agent 正在进行多维度鉴定...'}
            </p>
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <div>
                <h3 className="font-medium text-red-800">鉴定失败</h3>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* 实时推理过程 - 突出显示 */}
        {(isLoading || streamEvents.length > 0) && (
          <div className="mt-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="mb-4 text-center">
              <span className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full border">
                🤖 AI 正在深度思考中...
              </span>
            </div>
            <ReasoningPanel events={streamEvents} isLoading={isLoading} />
          </div>
        )}

        {/* 结果展示区域 */}
        {result && (
          <div className="mt-10 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* 分隔线 */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-4 bg-gradient-to-b from-gray-50 to-white text-sm text-gray-400">
                  鉴定结果
                </span>
              </div>
            </div>

            {/* 结论卡片 - 包含多维度分析 */}
            <ResultCard
              conclusion={result.conclusion}
              confidenceScore={result.confidence_score}
              summary={result.summary}
              dimensionalAnalysis={result.dimensional_analysis}
              multiAngleReasoning={result.multi_angle_reasoning}
              findings={result.findings}
              onGenerateArticle={handleGenerateArticle}
              articleData={articleData}
              isGeneratingArticle={isGeneratingArticle}
              verifyResult={result}
              originalContent={inputContent}
            />

            {/* 证据列表 - 包含 Search Agent 分析洞察 */}
            <EvidenceList 
              evidenceList={result.evidence_list}
              keySourcesCited={result.key_sources_cited}
              searchAnalysis={result.search_analysis}
            />

            {/* 推理过程回顾 */}
            {streamEvents.length > 0 && (
              <div className="mt-8 pt-8 border-t border-gray-200">
                <div className="text-center mb-4">
                  <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    🔍 查看完整推理过程
                  </span>
                </div>
                <ReasoningPanel events={streamEvents} isLoading={false} />
              </div>
            )}
          </div>
        )}

        {/* 初始状态提示 */}
        {!result && !isLoading && !error && streamEvents.length === 0 && (
          <div className="mt-12 text-center text-gray-400">
            <p className="text-sm">👆 输入内容，点击鉴定按钮开始分析</p>
            <p className="text-xs mt-2 text-gray-300">
              系统将依次调用 Parser、Search Analyst 和 Verdict Expert 三个 Agent 进行深度分析
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
