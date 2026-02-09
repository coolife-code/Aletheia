"""
Aletheia Gradio前端应用 - 简化稳定版
"""
import asyncio
import gradio as gr
from openai import AsyncOpenAI

from aletheia.system import AletheiaSystem
from aletheia.core.config import settings


# 初始化
llm_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY or "your-api-key",
    base_url=settings.OPENAI_BASE_URL
)
aletheia = AletheiaSystem(llm_client)

# 角度中文名映射
ANGLE_NAMES = {
    "CoreFactChecker": "核心事实核查",
    "TimelineBuilder": "时间线构建",
    "StakeholderMapper": "利益相关方分析",
    "SentimentAnalyzer": "舆论情绪分析",
    "DataVerifier": "数据验证",
    "SourceCredibility": "信源可信度",
    "ContextAnalyzer": "背景语境分析",
    "TechnicalAnalyzer": "技术细节分析",
    "LegalAnalyzer": "法律合规分析",
    "PsychologicalAnalyzer": "心理动机分析",
    "EconomicAnalyzer": "经济影响分析",
    "MediaCoverage": "媒体报道分析",
    "SocialImpact": "社会影响分析",
    "CausalityAnalyzer": "因果逻辑分析",
    "ComparisonAnalyzer": "对比参照分析"
}


async def typewriter_effect(text: str, chunk_size: int = 4, delay: float = 0.02):
    """生成打字机效果的分块"""
    if not text:
        yield ""
        return
    for i in range(0, len(text), chunk_size):
        yield text[:i + chunk_size]
        await asyncio.sleep(delay)


def create_interface():
    """创建Gradio界面"""
    
    with gr.Blocks(title="Aletheia - 舆情鉴别") as app:
        gr.Markdown("# 🔍 Aletheia 舆情鉴别系统")
        
        # ========== 输入区 ==========
        with gr.Row():
            input_text = gr.Textbox(
                label="待鉴别内容",
                placeholder="输入新闻、传言或舆情内容...",
                lines=5,
                scale=4
            )
            analyze_btn = gr.Button("开始分析", variant="primary", scale=1)
        
        # ========== 分析方向 ==========
        gr.Markdown("---")
        gr.Markdown("## 📍 分析方向")
        
        direction_text = gr.Textbox(
            label="推理过程",
            interactive=False,
            lines=8,
            value="",
            autoscroll=False  # 防止自动滚动
        )
        with gr.Row():
            event_type = gr.Textbox(label="事件类型", interactive=False)
            activated_angles = gr.Textbox(label="激活角度", interactive=False)
        
        # ========== 多角度调查 ==========
        gr.Markdown("---")
        gr.Markdown("## 🔎 多角度调查")
        
        # 角度选择下拉框
        angle_selector = gr.Dropdown(
            label="选择角度查看",
            choices=[],
            value=None,
            interactive=True
        )
        
        angle_status = gr.Textbox(label="角度状态", interactive=False)
        angle_content = gr.Textbox(
            label="分析报告",
            interactive=False,
            lines=15,
            value="",
            autoscroll=False  # 防止自动滚动
        )
        
        # 隐藏存储角度数据
        angle_data_store = gr.JSON(visible=False)
        
        # ========== 最终结论 ==========
        gr.Markdown("---")
        gr.Markdown("## 🎯 最终结论")
        
        verdict_badge = gr.HTML()
        with gr.Row():
            verdict_conclusion = gr.Textbox(label="结论", interactive=False)
            verdict_confidence = gr.Textbox(label="置信度", interactive=False)
        verdict_summary = gr.Textbox(label="结论摘要", interactive=False, lines=2)
        verdict_detail = gr.Textbox(
            label="详细研判",
            interactive=False,
            lines=10,
            value="",
            autoscroll=False  # 防止自动滚动
        )
        
        # ========== 信源列表 ==========
        gr.Markdown("---")
        gr.Markdown("## 📚 参考信源")
        sources_html = gr.HTML()
        
        # ========== 处理函数 ==========
        async def process(content):
            print(f"\n[DEBUG] 开始分析: {content[:50]}...")
            
            if not content or not content.strip():
                yield {
                    direction_text: "请输入内容",
                    event_type: "",
                    activated_angles: "",
                    angle_selector: gr.update(choices=[]),
                    angle_status: "",
                    angle_content: "",
                    angle_data_store: {},
                    verdict_badge: "",
                    verdict_conclusion: "",
                    verdict_confidence: "",
                    verdict_summary: "",
                    verdict_detail: "",
                    sources_html: ""
                }
                return
            
            # 1. 方向判定
            print("[DEBUG] 方向判定...")
            try:
                direction = await aletheia.direction_agent.analyze(content)
                reasoning = direction.reasoning or "分析完成"
                
                # 打字机效果
                async for partial in typewriter_effect(reasoning):
                    yield {
                        direction_text: partial,
                        event_type: direction.event_type,
                        activated_angles: ", ".join(direction.activated_angles),
                        angle_selector: gr.update(choices=[]),
                        angle_status: "分析中...",
                        angle_content: "",
                        angle_data_store: {},
                        verdict_badge: "",
                        verdict_conclusion: "",
                        verdict_confidence: "",
                        verdict_summary: "",
                        verdict_detail: "",
                        sources_html: ""
                    }
                
                # 2. 角度分析
                print(f"[DEBUG] 分析 {len(direction.activated_angles)} 个角度...")
                angle_results = {}
                all_sources = []
                
                for idx, angle_name in enumerate(direction.activated_angles):
                    print(f"[DEBUG] 角度 {idx+1}/{len(direction.activated_angles)}: {angle_name}")
                    
                    agent = aletheia.angle_agents.get(angle_name)
                    if not agent:
                        continue
                    
                    try:
                        report = await agent.investigate(content)
                        angle_results[angle_name] = {
                            "name": ANGLE_NAMES.get(angle_name, angle_name),
                            "report": report.report or "暂无报告",
                            "confidence": report.confidence,
                            "sources": report.key_sources
                        }
                        all_sources.extend(report.key_sources)
                        
                        # 更新下拉框选项
                        choices = [f"{v['name']} (置信度: {v['confidence']:.0%})" for v in angle_results.values()]
                        
                        yield {
                            direction_text: reasoning,
                            event_type: direction.event_type,
                            activated_angles: ", ".join(direction.activated_angles),
                            angle_selector: gr.update(choices=choices, value=choices[-1] if choices else None),
                            angle_status: f"✓ {ANGLE_NAMES.get(angle_name, angle_name)} 完成 (置信度: {report.confidence:.0%})",
                            angle_content: report.report or "暂无报告",
                            angle_data_store: angle_results,
                            verdict_badge: "",
                            verdict_conclusion: "",
                            verdict_confidence: "",
                            verdict_summary: "",
                            verdict_detail: "",
                            sources_html: ""
                        }
                        
                    except Exception as e:
                        print(f"[ERROR] 角度失败 {angle_name}: {e}")
                
                # 3. 最终结论
                print("[DEBUG] 综合研判...")
                
                angle_reports = [
                    type('obj', (object,), {
                        'angle_name': k,
                        'report': v['report'],
                        'confidence': v['confidence'],
                        'key_sources': v['sources']
                    })() for k, v in angle_results.items()
                ]
                
                judgment = await aletheia.judgment_agent.judge(content, angle_reports)
                
                # 结论颜色
                conclusion = judgment.conclusion
                if "真实" in conclusion or "属实" in conclusion:
                    color = "#4CAF50"
                elif "虚假" in conclusion or "不实" in conclusion:
                    color = "#f44336"
                else:
                    color = "#FF9800"
                
                badge = f'<div style="background:{color};color:white;padding:15px;border-radius:8px;font-size:22px;font-weight:bold;text-align:center;">{conclusion}</div>'
                
                # 打字机效果输出结论
                full_text = f"{judgment.summary}\n\n{judgment.detailed_judgment}"
                async for partial in typewriter_effect(full_text):
                    yield {
                        direction_text: reasoning,
                        event_type: direction.event_type,
                        activated_angles: ", ".join(direction.activated_angles),
                        angle_selector: gr.update(choices=[f"{v['name']} (置信度: {v['confidence']:.0%})" for v in angle_results.values()]),
                        angle_status: f"✓ 所有角度分析完成",
                        angle_content: list(angle_results.values())[-1]["report"] if angle_results else "",
                        angle_data_store: angle_results,
                        verdict_badge: badge,
                        verdict_conclusion: conclusion,
                        verdict_confidence: f"{judgment.confidence:.0%}",
                        verdict_summary: judgment.summary,
                        verdict_detail: partial,
                        sources_html: ""
                    }
                
                # 4. 信源
                if all_sources:
                    html = "<div style='display:flex;flex-wrap:wrap;gap:10px;'>"
                    for src in all_sources[:10]:
                        name = src.get("name", "未知")
                        cred = src.get("credibility", "未知")
                        url = src.get("url", "#")
                        color = "#4CAF50" if "高" in cred else "#FF9800" if "中" in cred else "#f44336"
                        html += f"""
                        <div style="border:1px solid #ddd;border-radius:8px;padding:10px;min-width:200px;background:#fafafa;">
                            <div style="font-weight:bold;">{name}</div>
                            <div style="font-size:12px;color:#666;">可信度: <span style="color:{color};font-weight:bold;">{cred}</span></div>
                            <div style="font-size:11px;margin-top:5px;"><a href="{url}" target="_blank" style="color:#2196F3;">{url[:40]}...</a></div>
                        </div>
                        """
                    html += "</div>"
                    
                    yield {
                        direction_text: reasoning,
                        event_type: direction.event_type,
                        activated_angles: ", ".join(direction.activated_angles),
                        angle_selector: gr.update(choices=[f"{v['name']} (置信度: {v['confidence']:.0%})" for v in angle_results.values()]),
                        angle_status: "✓ 所有角度分析完成",
                        angle_content: list(angle_results.values())[-1]["report"] if angle_results else "",
                        angle_data_store: angle_results,
                        verdict_badge: badge,
                        verdict_conclusion: conclusion,
                        verdict_confidence: f"{judgment.confidence:.0%}",
                        verdict_summary: judgment.summary,
                        verdict_detail: full_text,
                        sources_html: html
                    }
                
                print("[DEBUG] 分析完成")
                
            except Exception as e:
                import traceback
                error_msg = f"错误: {str(e)}"
                print(f"[ERROR] {error_msg}\n{traceback.format_exc()}")
                yield {
                    direction_text: error_msg,
                    event_type: "",
                    activated_angles: "",
                    angle_selector: gr.update(choices=[]),
                    angle_status: "",
                    angle_content: "",
                    angle_data_store: {},
                    verdict_badge: "",
                    verdict_conclusion: "",
                    verdict_confidence: "",
                    verdict_summary: "",
                    verdict_detail: "",
                    sources_html: ""
                }
        
        # 角度选择切换
        def on_angle_select(selected, angle_data):
            if not selected or not angle_data:
                return "", ""
            
            # 从选择文本中提取角度名
            for key, value in angle_data.items():
                if value['name'] in selected:
                    return f"✓ {value['name']} 完成 (置信度: {value['confidence']:.0%})", value['report']
            
            return "", ""
        
        angle_selector.change(
            fn=on_angle_select,
            inputs=[angle_selector, angle_data_store],
            outputs=[angle_status, angle_content]
        )
        
        # 绑定分析按钮
        analyze_btn.click(
            fn=process,
            inputs=input_text,
            outputs=[
                direction_text, event_type, activated_angles,
                angle_selector, angle_status, angle_content, angle_data_store,
                verdict_badge, verdict_conclusion, verdict_confidence,
                verdict_summary, verdict_detail, sources_html
            ]
        )
    
    return app


if __name__ == "__main__":
    print("[DEBUG] 启动 Aletheia 系统...")
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7861, share=False)
