'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface VerifyButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  loadingStep?: string;
  disabled?: boolean;
  hasResult?: boolean;
}

const LOADING_MESSAGES: Record<string, string> = {
  parsing: '正在解析内容...',
  searching: '正在搜索证据...',
  verifying: '正在分析验证...',
};

export function VerifyButton({
  onClick,
  isLoading = false,
  loadingStep = 'parsing',
  disabled = false,
  hasResult = false
}: VerifyButtonProps) {
  const buttonText = isLoading 
    ? (LOADING_MESSAGES[loadingStep] || '鉴定中...')
    : (hasResult ? '重新鉴定' : '开始鉴定');

  return (
    <Button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`
        w-full max-w-md mx-auto h-12 text-base font-medium
        transition-all duration-200
        ${isLoading 
          ? 'bg-blue-400 hover:bg-blue-400 cursor-wait' 
          : 'bg-blue-600 hover:bg-blue-700'
        }
        ${disabled && !isLoading ? 'bg-gray-300 hover:bg-gray-300 cursor-not-allowed' : ''}
      `}
    >
      {isLoading ? (
        <>
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          <span>{buttonText}</span>
        </>
      ) : (
        <>
          <span className="mr-2">{hasResult ? '🔄' : '🔍'}</span>
          <span>{buttonText}</span>
        </>
      )}
    </Button>
  );
}
