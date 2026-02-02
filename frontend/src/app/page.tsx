'use client';

import React, { useState } from 'react';
import { InputBox } from '@/components/InputBox';
import { VerifyButton } from '@/components/VerifyButton';
import { ResultCard } from '@/components/ResultCard';
import { EvidenceList } from '@/components/EvidenceList';
import { ReasoningPanel } from '@/components/ReasoningPanel';
import { verifyContent, verifyContentStream } from '@/lib/api';
import { VerifyResponse, LoadingStepType } from '@/types';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [inputContent, setInputContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<LoadingStepType>('parsing');
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (!inputContent.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // 使用流式 API 获取进度更新
      for await (const data of verifyContentStream({ content: inputContent })) {
        if (data.step === 'parsing') {
          setLoadingStep('parsing');
        } else if (data.step === 'searching') {
          setLoadingStep('searching');
        } else if (data.step === 'verifying') {
          setLoadingStep('verifying');
        } else if (data.step === 'complete' && data.result) {
          setResult(data.result);
        } else if (data.step === 'error') {
          setError(data.message || '鉴定过程出错');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '网络错误，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInputContent('');
    setResult(null);
    setError(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-3xl mx-auto px-4 py-12 md:py-16">
        {/* 头部 */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Aletheia
          </h1>
          <p className="text-lg text-gray-500">
            AI 舆情谎言鉴定系统
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
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <p className="text-sm text-gray-400">
              {loadingStep === 'parsing' && '正在解析内容，提取关键主张...'}
              {loadingStep === 'searching' && '正在全网搜索相关证据...'}
              {loadingStep === 'verifying' && '正在进行交叉验证和逻辑分析...'}
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

            {/* 结论卡片 */}
            <ResultCard
              conclusion={result.conclusion}
              confidenceScore={result.confidence_score}
              summary={result.summary}
            />

            {/* 证据列表 */}
            <EvidenceList evidenceList={result.evidence_list} />

            {/* 推理过程 */}
            <ReasoningPanel reasoningChain={result.reasoning_chain} />
          </div>
        )}

        {/* 初始状态提示 */}
        {!result && !isLoading && !error && (
          <div className="mt-12 text-center text-gray-400">
            <p className="text-sm">👆 输入内容，点击鉴定按钮开始分析</p>
          </div>
        )}
      </div>
    </main>
  );
}
