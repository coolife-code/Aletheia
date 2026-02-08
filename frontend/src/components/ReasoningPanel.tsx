'use client';

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { AGENT_CONFIG, ReasoningStep, StreamEvent } from '@/types';

interface ReasoningPanelProps {
  events: StreamEvent[];
  isLoading: boolean;
}

export default function ReasoningPanel({ events, isLoading }: ReasoningPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  // 按 Agent 分组事件
  const groupedEvents = events.reduce((acc, event) => {
    if (event.agent) {
      if (!acc[event.agent]) {
        acc[event.agent] = [];
      }
      acc[event.agent].push(event);
    }
    return acc;
  }, {} as Record<string, StreamEvent[]>);

  const toggleAgent = (agent: string) => {
    setExpandedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agent)) {
        newSet.delete(agent);
      } else {
        newSet.add(agent);
      }
      return newSet;
    });
  };

  // 获取 Agent 状态
  const getAgentStatus = (agent: string) => {
    const agentEvents = groupedEvents[agent] || [];
    const hasResult = agentEvents.some(e => e.type === 'result');
    const hasStart = agentEvents.some(e => e.type === 'start');
    
    if (hasResult) return 'completed';
    if (hasStart) return 'running';
    return 'pending';
  };

  return (
    <Card className="p-4 bg-gray-50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">推理过程</h3>
        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-blue-600">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            分析中...
          </div>
        )}
      </div>

      <div 
        ref={scrollRef}
        className="space-y-3 max-h-[400px] overflow-y-auto pr-2"
        style={{ scrollBehavior: 'smooth' }}
      >
        {/* Agent 状态概览 */}
        <div className="flex gap-2 mb-4">
          {Object.entries(AGENT_CONFIG).map(([key, config]) => {
            const status = getAgentStatus(key);
            return (
              <div
                key={key}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  status === 'completed' 
                    ? 'bg-green-100 text-green-700' 
                    : status === 'running'
                    ? 'bg-blue-100 text-blue-700 animate-pulse'
                    : 'bg-gray-100 text-gray-400'
                }`}
              >
                <span>{config.icon}</span>
                <span className="hidden sm:inline">{config.name}</span>
                {status === 'completed' && <span>✓</span>}
                {status === 'running' && <span>⋯</span>}
              </div>
            );
          })}
        </div>

        {/* 详细推理步骤 */}
        {Object.entries(groupedEvents).map(([agent, agentEvents]) => {
          const config = AGENT_CONFIG[agent];
          const isExpanded = expandedAgents.has(agent);
          const reasoningEvents = agentEvents.filter(e => e.type === 'reasoning' || e.type === 'start');
          
          if (reasoningEvents.length === 0) return null;

          return (
            <div key={agent} className="border rounded-lg bg-white overflow-hidden">
              {/* Agent 标题栏 */}
              <button
                onClick={() => toggleAgent(agent)}
                className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
                style={{ borderLeft: `4px solid ${config.color}` }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{config.icon}</span>
                  <span className="font-medium text-gray-900">{config.name}</span>
                  <span className="text-xs text-gray-500">
                    ({reasoningEvents.length} 个步骤)
                  </span>
                </div>
                <span className="text-gray-400">
                  {isExpanded ? '▼' : '▶'}
                </span>
              </button>

              {/* 推理内容 */}
              {isExpanded && (
                <div className="p-3 space-y-3 border-t bg-gray-50 max-h-[500px] overflow-y-auto">
                  {reasoningEvents.map((event, index) => (
                    <div 
                      key={index}
                      className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed p-3 bg-white rounded-lg border border-gray-100 shadow-sm"
                    >
                      {event.step && (
                        <div className="flex items-center gap-2 mb-2">
                          <span 
                            className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                            style={{ backgroundColor: `${config.color}20`, color: config.color }}
                          >
                            {event.step}
                          </span>
                          <span className="text-xs text-gray-400">步骤 {index + 1}</span>
                        </div>
                      )}
                      <div className="text-gray-700 leading-relaxed">
                        {event.content}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 折叠时显示最近3条推理 */}
              {!isExpanded && reasoningEvents.length > 0 && (
                <div className="px-3 py-2 border-t bg-gray-50 space-y-2">
                  {reasoningEvents.slice(-3).map((event, idx) => (
                    <div key={idx} className="text-sm text-gray-600 line-clamp-2">
                      {event.step && (
                        <span 
                          className="inline-block px-1.5 py-0.5 rounded text-xs font-medium mr-2"
                          style={{ backgroundColor: `${config.color}15`, color: config.color }}
                        >
                          {event.step}
                        </span>
                      )}
                      <span className="truncate">{event.content}</span>
                    </div>
                  ))}
                  {reasoningEvents.length > 3 && (
                    <div className="text-xs text-gray-400 text-center">
                      还有 {reasoningEvents.length - 3} 个步骤...
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* 空状态 */}
        {events.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🤔</div>
            <p>等待开始分析...</p>
          </div>
        )}
      </div>
    </Card>
  );
}
