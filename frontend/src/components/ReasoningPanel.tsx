'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';

interface ReasoningPanelProps {
  reasoningChain: string[];
}

export function ReasoningPanel({ reasoningChain }: ReasoningPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!reasoningChain || reasoningChain.length === 0) {
    return null;
  }

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-left"
        >
          <CardTitle className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            推理过程
          </CardTitle>
          <span className="text-gray-400">
            {isExpanded ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </span>
        </button>
      </CardHeader>
      
      {isExpanded && (
        <CardContent>
          <div className="space-y-3">
            {reasoningChain.map((step, index) => (
              <div key={index} className="flex gap-3">
                <div className="flex-shrink-0">
                  <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                </div>
                <div className="flex-1 pt-0.5">
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {step}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      )}
      
      {!isExpanded && (
        <CardContent className="pt-0">
          <p className="text-sm text-gray-400">
            点击展开查看详细推理过程
          </p>
        </CardContent>
      )}
    </Card>
  );
}
