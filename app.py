"""
Aletheia - AI舆情谎言鉴定系统
Gradio版本主入口文件
部署到魔搭社区创空间
"""

import os
import sys
import asyncio
import json
from typing import AsyncGenerator

# 将backend添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import gradio as gr
from app.agents.parser import ParserAgent
from app.agents.search import SearchAgent
from app.agents.verdict import VerdictAgent

# 初始化Agents
parser_agent = ParserAgent()
search_agent = SearchAgent()
verdict_agent = VerdictAgent()


def get_conclusion_emoji(conclusion: str) -> str:
    """根据结论类型返回对应的emoji"""
    return {
        "true": "✅",
        "false": "❌",
        "uncertain": "⚠️",
        "unverifiable": "❓",
        "partially_true": "🟨",
        "misleading": "🟧"
    }.get(conclusion, "❓")


def get_conclusion_label(conclusion: str) -> str:
    """根据结论类型返回中文标签"""
    return {
        "true": "真实",
        "false": "虚假",
        "uncertain": "存疑",
        "unverifiable": "无法核实",
        "partially_true": "部分真实",
        "misleading": "误导性"
    }.get(conclusion, "未知")


async def verify_content_stream(content: str):
    """
    流式鉴定舆情内容，实时返回每个Agent的推理过程
    """
    if not content or not content.strip():
        yield "请输入需要鉴定的舆情内容", "", "", ""
        return

    reasoning_text = ""
    result_text = ""
    evidence_text = ""

    try:
        # ==================== Step 1: Parser Agent ====================
        reasoning_text += "## 🔍 Parser Agent - 问题分析\n\n"
        yield reasoning_text, result_text, evidence_text, "正在分析问题..."

        parser_result_data = None
        async for parser_event in parser_agent.parse_stream(content):
            event_type = parser_event.get("type")
            step = parser_event.get("step", "")
            event_content = parser_event.get("content", "")

            if event_type == "reasoning":
                reasoning_text += f"**{step}**: {event_content}\n\n"
                yield reasoning_text, result_text, evidence_text, f"Parser: {step}..."
            elif event_type == "result":
                parser_result_data = parser_event.get("data")

        # 检查是否需要澄清
        if parser_result_data and parser_result_data.get("needs_clarification"):
            clarification = parser_result_data.get("clarification_prompt", "请提供更多具体信息")
            result_text = f"## ⚠️ 需要补充信息\n\n{clarification}"
            yield reasoning_text, result_text, evidence_text, "需要补充信息"
            return

        if not parser_result_data:
            result_text = "## ❌ 解析失败\n\n无法解析输入内容，请重试。"
            yield reasoning_text, result_text, evidence_text, "解析失败"
            return

        # ==================== Step 2: Search Agent ====================
        reasoning_text += "\n---\n\n## 🔎 Search Agent - 深度搜索\n\n"
        yield reasoning_text, result_text, evidence_text, "正在搜索相关信息..."

        search_result_data = None
        async for search_event in search_agent.search_stream(parser_result_data, content):
            event_type = search_event.get("type")
            step = search_event.get("step", "")
            event_content = search_event.get("content", "")

            if event_type == "reasoning":
                reasoning_text += f"**{step}**: {event_content}\n\n"
                yield reasoning_text, result_text, evidence_text, f"Search: {step}..."
            elif event_type == "result":
                search_result_data = search_event.get("data")

        if not search_result_data:
            result_text = "## ❌ 搜索失败\n\n无法获取相关信息，请重试。"
            yield reasoning_text, result_text, evidence_text, "搜索失败"
            return

        # ==================== Step 3: Verdict Agent ====================
        reasoning_text += "\n---\n\n## 🎯 Verdict Agent - 多维度鉴定\n\n"
        yield reasoning_text, result_text, evidence_text, "正在进行多维度鉴定..."

        verdict_result_data = None
        async for verdict_event in verdict_agent.verdict_stream(search_result_data, content):
            event_type = verdict_event.get("type")
            step = verdict_event.get("step", "")
            event_content = verdict_event.get("content", "")

            if event_type == "reasoning":
                reasoning_text += f"**{step}**: {event_content}\n\n"
                yield reasoning_text, result_text, evidence_text, f"Verdict: {step}..."
            elif event_type == "result":
                verdict_result_data = verdict_event.get("data")

        # ==================== 最终结果 ====================
        if verdict_result_data:
            conclusion = verdict_result_data.get("conclusion", "uncertain")
            confidence = verdict_result_data.get("confidence_score", 0.5)
            summary = verdict_result_data.get("conclusion_summary", "")

            emoji = get_conclusion_emoji(conclusion)
            label = get_conclusion_label(conclusion)

            # 构建结果展示
            result_text = f"""## {emoji} 鉴定结论: {label}

**置信度**: {confidence:.0%}

### 结论摘要
{summary}

### 多维度分析
"""

            # 添加多维度分析
            dimensional = verdict_result_data.get("dimensional_analysis", {})
            for dim_name, dim_data in dimensional.items():
                dim_labels = {
                    "factual": "📊 事实维度",
                    "contextual": "📋 背景维度",
                    "motivational": "💭 动机维度",
                    "impact": "🌟 影响维度"
                }
                label_text = dim_labels.get(dim_name, dim_name)
                analysis = dim_data.get("analysis", "")[:200]
                conf = dim_data.get("confidence", 0.5)
                result_text += f"\n**{label_text}**: {analysis} (置信度: {conf:.0%})\n"

            # 添加发现分类
            findings = verdict_result_data.get("findings", {})
            result_text += f"""
### 发现分类
- ✅ 已验证: {len(findings.get('verified_claims', []))} 项
- ❌ 已证伪: {len(findings.get('refuted_claims', []))} 项
- ⚠️ 需 nuanced 理解: {len(findings.get('nuanced_claims', []))} 项
- ❓ 不确定: {len(findings.get('uncertain_claims', []))} 项
"""

            # 构建证据列表
            all_sources = search_result_data.get("all_sources", [])
            evidence_text = f"## 📚 证据列表 (共 {len(all_sources)} 个信源)\n\n"

            # 关键信源
            key_sources = [s for s in all_sources if s.get("is_key_source", False)]
            if key_sources:
                evidence_text += "### 🔑 关键信源\n\n"
                for i, source in enumerate(key_sources[:5], 1):
                    credibility = source.get("source_credibility", "medium")
                    cred_emoji = "🟢" if credibility == "high" else "🟡" if credibility == "medium" else "🔴"
                    evidence_text += f"**{i}. {source.get('title', '未知标题')}**\n"
                    evidence_text += f"- 来源: {source.get('source_domain', '未知')}\n"
                    evidence_text += f"- 可信度: {cred_emoji} {credibility}\n"
                    evidence_text += f"- 关键信息: {source.get('key_insight', '')[:100]}...\n\n"

            # 普通信源
            regular_sources = [s for s in all_sources if not s.get("is_key_source", False)]
            if regular_sources:
                evidence_text += "### 📄 其他信源\n\n"
                for i, source in enumerate(regular_sources[:5], 1):
                    credibility = source.get("source_credibility", "medium")
                    cred_emoji = "🟢" if credibility == "high" else "🟡" if credibility == "medium" else "🔴"
                    evidence_text += f"**{i}. {source.get('title', '未知标题')}** ({cred_emoji} {credibility})\n"
                    evidence_text += f"   来源: {source.get('source_domain', '未知')}\n\n"

            yield reasoning_text, result_text, evidence_text, "鉴定完成"
        else:
            result_text = "## ❌ 鉴定未完成\n\n鉴定过程未能完成，请重试。"
            yield reasoning_text, result_text, evidence_text, "鉴定失败"

    except Exception as e:
        error_msg = f"## ❌ 错误\n\n鉴定过程出错: {str(e)}"
        yield reasoning_text, error_msg, evidence_text, "出错"


# 创建Gradio界面
def create_interface():
    with gr.Blocks(theme=gr.themes.Soft(), title="Aletheia - AI舆情谎言鉴定系统") as demo:
        # 标题区域
        gr.Markdown("""
        # 🔍 Aletheia - AI舆情谎言鉴定系统

        基于多Agent协作的智能舆情真实性鉴定系统，通过Parser、Search、Verdict三个Agent的深度协作，
        从多维度分析问题，为您提供客观、可信的鉴定结果。

        **使用说明**: 在下方输入框中输入您想要鉴定的舆情内容，点击"开始鉴定"按钮，系统将自动分析并返回鉴定结果。
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # 输入区域
                input_text = gr.Textbox(
                    label="输入舆情内容",
                    placeholder="请输入您想要鉴定的舆情内容，例如：\"某明星宣布退出娱乐圈\"...",
                    lines=5,
                    max_lines=10
                )
                submit_btn = gr.Button("🚀 开始鉴定", variant="primary", size="lg")
                status_text = gr.Textbox(label="当前状态", value="就绪", interactive=False)

            with gr.Column(scale=2):
                # 结果展示区域 - 使用标签页
                with gr.Tabs():
                    with gr.TabItem("📝 推理过程"):
                        reasoning_output = gr.Markdown(
                            value='*点击"开始鉴定"后，这里将显示详细的推理过程...*'
                        )

                    with gr.TabItem("🎯 鉴定结果"):
                        result_output = gr.Markdown(
                            value="*鉴定结果将在这里显示...*"
                        )

                    with gr.TabItem("📚 证据列表"):
                        evidence_output = gr.Markdown(
                            value="*相关证据将在这里显示...*"
                        )

        # 示例
        gr.Markdown("### 💡 示例")
        examples = [
            ["某知名科技公司CEO宣布辞职，原因是个人健康原因"],
            ["最新研究表明，每天喝一杯咖啡可以延长寿命5年"],
            ["某城市即将实施新的交通管制措施，限制外地车辆进入"]
        ]
        gr.Examples(examples=examples, inputs=input_text)

        # 绑定事件
        submit_btn.click(
            fn=verify_content_stream,
            inputs=input_text,
            outputs=[reasoning_output, result_output, evidence_output, status_text]
        )

        gr.Markdown("""
        ---
        **技术说明**: 本系统使用DeepSeek联网搜索功能获取实时信息，通过多Agent协作进行深度分析，
        包括问题解析、证据搜索、多维度鉴定三个核心步骤。
        """)

    return demo


# 启动应用
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
