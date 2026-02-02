'use client';

import React, { useState, useRef } from 'react';
import { Textarea } from '@/components/ui/textarea';

interface InputBoxProps {
  value: string;
  onChange: (value: string) => void;
  maxLength?: number;
  placeholder?: string;
  disabled?: boolean;
}

export function InputBox({
  value,
  onChange,
  maxLength = 2000,
  placeholder = '粘贴或输入舆情内容...',
  disabled = false
}: InputBoxProps) {
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      onChange(newValue);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    // 处理拖拽的文件
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      // 这里可以处理图片上传
      console.log('Dropped files:', files);
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    // 处理粘贴的图片
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const blob = items[i].getAsFile();
        if (blob) {
          console.log('Pasted image:', blob);
        }
      }
    }
  };

  return (
    <div
      className={`
        relative rounded-xl border-2 transition-all duration-200
        ${isDragging 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* 头部标签 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <span className="text-sm font-medium text-gray-700">
          输入要鉴定的内容（支持文本、链接、图片）
        </span>
        <span className="text-gray-400">📎</span>
      </div>

      {/* 文本输入区 */}
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onPaste={handlePaste}
        placeholder={placeholder}
        disabled={disabled}
        className="
          min-h-[150px] resize-none border-0 focus-visible:ring-0
          text-base leading-relaxed placeholder:text-gray-400
          px-4 py-3
        "
      />

      {/* 底部工具栏 */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-100">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>支持拖拽上传图片</span>
        </div>
        <div className="flex items-center gap-2">
          {value.length > 0 && (
            <button
              onClick={() => onChange('')}
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
              disabled={disabled}
            >
              清空
            </button>
          )}
          <span className={`text-xs ${value.length >= maxLength ? 'text-red-500' : 'text-gray-400'}`}>
            {value.length}/{maxLength}字
          </span>
        </div>
      </div>

      {/* 拖拽提示遮罩 */}
      {isDragging && (
        <div className="absolute inset-0 bg-blue-50/90 rounded-xl flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-2">📎</div>
            <div className="text-blue-600 font-medium">释放以上传图片</div>
          </div>
        </div>
      )}
    </div>
  );
}
