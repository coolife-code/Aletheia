'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { FileText, Copy, Download, X, Loader2 } from 'lucide-react';
import { ArticleResponse } from '../types';

interface ArticlePanelProps {
  article: ArticleResponse | null;
  isLoading: boolean;
  onClose: () => void;
  onCopy: () => void;
  onDownload: () => void;
}

export function ArticlePanel({ article, isLoading, onClose, onCopy, onDownload }: ArticlePanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!article) return;
    
    const fullText = `${article.article.headline}\n\n${article.article.lead}\n\n${article.article.body}\n\n${article.article.conclusion}\n\n【信源】\n${article.article.sources}`;
    
    navigator.clipboard.writeText(fullText).then(() => {
      setCopied(true);
      onCopy();
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownload = () => {
    if (!article) return;
    
    const fullText = `${article.article.headline}\n\n${article.article.lead}\n\n${article.article.body}\n\n${article.article.conclusion}\n\n【信源】\n${article.article.sources}`;
    
    const blob = new Blob([fullText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `新闻稿-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    onDownload();
  };

  if (isLoading) {
    return (
      <Card className="border-0 shadow-sm bg-gradient-to-br from-amber-50 to-orange-50">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <FileText className="w-5 h-5 text-amber-600" />
              新闻稿生成中
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-3">
              <Loader2 className="w-8 h-8 text-amber-600 animate-spin mx-auto" />
              <p className="text-sm text-gray-600">正在撰写新闻稿...</p>
              <p className="text-xs text-gray-400">基于搜索和推理材料</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!article) {
    return null;
  }

  return (
    <Card className="border-0 shadow-sm bg-gradient-to-br from-amber-50 to-orange-50">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <FileText className="w-5 h-5 text-amber-600" />
            新闻稿
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-8 px-2"
              title="复制"
            >
              <Copy className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownload}
              className="h-8 px-2"
              title="下载"
            >
              <Download className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 px-2"
              title="关闭"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 标题 */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            {article.article.headline}
          </h3>
        </div>

        {/* 导语 */}
        <div className="bg-white/50 rounded-lg p-4">
          <p className="text-sm font-semibold text-gray-700 mb-1">导语</p>
          <p className="text-gray-700 leading-relaxed">
            {article.article.lead}
          </p>
        </div>

        {/* 正文 */}
        <div className="bg-white/50 rounded-lg p-4">
          <p className="text-sm font-semibold text-gray-700 mb-1">正文</p>
          <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {article.article.body}
          </div>
        </div>

        {/* 结论 */}
        <div className="bg-white/50 rounded-lg p-4">
          <p className="text-sm font-semibold text-gray-700 mb-1">结论</p>
          <p className="text-gray-700 leading-relaxed">
            {article.article.conclusion}
          </p>
        </div>

        {/* 信源 */}
        <div className="bg-white/50 rounded-lg p-4">
          <p className="text-sm font-semibold text-gray-700 mb-1">信源</p>
          <div className="text-gray-700 leading-relaxed whitespace-pre-wrap text-sm">
            {article.article.sources}
          </div>
        </div>

        {/* 元数据 */}
        <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
          <div className="flex flex-wrap gap-4">
            <span>证据数量: {article.metadata.evidence_count}</span>
            <span>关键信源: {article.metadata.key_sources_count}</span>
            <span>可信度: {(article.metadata.confidence_score * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* 复制成功提示 */}
        {copied && (
          <div className="fixed bottom-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg animate-in fade-in slide-in-from-bottom-2">
            已复制到剪贴板
          </div>
        )}
      </CardContent>
    </Card>
  );
}