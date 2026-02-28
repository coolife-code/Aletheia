import json
import uuid
from typing import Dict, Any
import openai
from anthropic import Anthropic

from app.core.config import settings


class ArticleAgent:
    """
    新闻稿生成 Agent - 专业新闻工作者
    
    职责：
    1. 基于鉴定结果生成专业新闻稿
    2. 以新闻工作者视角撰写
    3. 充分利用搜索和推理材料
    4. 避免过度 AI 化的表达
    5. 采用标准新闻稿结构
    """

    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        model = settings.ARTICLE_LLM_MODEL or settings.OPENAI_MODEL
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=60.0
        ) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
        self.model = model
        self.temperature = settings.ARTICLE_LLM_TEMPERATURE if hasattr(settings, 'ARTICLE_LLM_TEMPERATURE') else 0.7

    async def generate_article(self, verify_result: Dict[str, Any], original_content: str) -> Dict[str, Any]:
        """
        基于鉴定结果生成新闻稿
        """
        article_id = str(uuid.uuid4())
        
        print(f"[ArticleAgent] Generating news article for verdict: {verify_result.get('conclusion')}")

        # 提取关键信息
        conclusion = verify_result.get('conclusion', 'uncertain')
        confidence_score = verify_result.get('confidence_score', 0.5)
        summary = verify_result.get('summary', '')
        evidence_list = verify_result.get('evidence_list', [])
        dimensional_analysis = verify_result.get('dimensional_analysis', {})
        multi_angle_reasoning = verify_result.get('multi_angle_reasoning', {})
        search_analysis = verify_result.get('search_analysis', {})
        findings = verify_result.get('findings', {})
        key_sources_cited = verify_result.get('key_sources_cited', [])

        # 准备新闻稿素材
        article_materials = self._prepare_article_materials(
            original_content, conclusion, confidence_score, summary,
            evidence_list, dimensional_analysis, multi_angle_reasoning,
            search_analysis, findings, key_sources_cited
        )

        # 生成新闻稿
        article = await self._write_news_article(article_materials)

        return {
            "article_id": article_id,
            "verdict_ref": verify_result.get('verdict_id'),
            "article": article,
            "metadata": {
                "conclusion": conclusion,
                "confidence_score": confidence_score,
                "evidence_count": len(evidence_list),
                "key_sources_count": len(key_sources_cited),
                "generated_at": str(uuid.uuid1())
            }
        }

    def _prepare_article_materials(self, original_content: str, conclusion: str, 
                                    confidence_score: float, summary: str,
                                    evidence_list: list, dimensional_analysis: dict,
                                    multi_angle_reasoning: dict, search_analysis: dict,
                                    findings: dict, key_sources_cited: list) -> Dict[str, Any]:
        """
        准备新闻稿素材
        """
        # 结论映射
        conclusion_map = {
            'true': '经核实属实',
            'false': '经证实为虚假信息',
            'uncertain': '尚无法确定真伪',
            'unverifiable': '缺乏可验证依据',
            'partially_true': '部分属实但存在夸大',
            'misleading': '具有误导性'
        }
        
        conclusion_text = conclusion_map.get(conclusion, '需进一步核实')

        # 提取关键证据
        key_evidences = []
        for evidence in evidence_list[:8]:
            if evidence.get('is_key_source') or evidence.get('source_credibility') == 'high':
                key_evidences.append({
                    'source': evidence.get('source_domain', ''),
                    'title': evidence.get('title', ''),
                    'snippet': evidence.get('content_snippet', '')[:150],
                    'credibility': evidence.get('source_credibility', ''),
                    'key_insight': evidence.get('key_insight', '')
                })

        # 提取多维度分析要点
        dimension_points = []
        for dim_name, dim_data in dimensional_analysis.items():
            if dim_data and isinstance(dim_data, dict):
                analysis = dim_data.get('analysis', '')
                key_points = dim_data.get('key_points', [])
                if analysis or key_points:
                    dimension_points.append({
                        'dimension': dim_name,
                        'analysis': analysis[:200],
                        'key_points': key_points[:3]
                    })

        # 提取搜索分析发现
        key_findings = search_analysis.get('key_findings', [])[:5]
        conflict_points = search_analysis.get('conflict_points', [])[:3]

        # 提取发现分类
        verified_claims = findings.get('verified_claims', [])
        refuted_claims = findings.get('refuted_claims', [])
        uncertain_claims = findings.get('uncertain_claims', [])

        # 提取多角度推理
        angle_summaries = []
        for angle_name, angle_content in multi_angle_reasoning.items():
            if angle_content:
                angle_summaries.append({
                    'angle': angle_name,
                    'content': angle_content[:150]
                })

        return {
            'original_content': original_content,
            'conclusion': conclusion,
            'conclusion_text': conclusion_text,
            'confidence_score': confidence_score,
            'summary': summary,
            'key_evidences': key_evidences,
            'dimension_points': dimension_points,
            'key_findings': key_findings,
            'conflict_points': conflict_points,
            'verified_claims': verified_claims,
            'refuted_claims': refuted_claims,
            'uncertain_claims': uncertain_claims,
            'angle_summaries': angle_summaries,
            'key_sources': key_sources_cited[:5]
        }

    async def _write_news_article(self, materials: Dict[str, Any]) -> Dict[str, str]:
        """
        撰写新闻稿
        """
        original_content = materials['original_content']
        conclusion_text = materials['conclusion_text']
        confidence_score = materials['confidence_score']
        summary = materials['summary']
        
        # 构建证据引用
        evidence_refs = []
        for ev in materials['key_evidences'][:5]:
            evidence_refs.append(
                f"• {ev['source']}：{ev['key_insight'] or ev['snippet']}"
            )
        
        # 构建多维度分析摘要
        dimension_summary = []
        for dp in materials['dimension_points']:
            dim_name_map = {
                'factual_dimension': '事实层面',
                'contextual_dimension': '背景层面',
                'motivational_dimension': '动机层面',
                'impact_dimension': '影响层面'
            }
            dim_name = dim_name_map.get(dp['dimension'], dp['dimension'])
            dimension_summary.append(f"{dim_name}：{dp['analysis'][:100]}")

        # 构建发现摘要
        findings_parts = []
        if materials['verified_claims']:
            findings_parts.append(f"已核实内容：{', '.join(materials['verified_claims'][:2])}")
        if materials['refuted_claims']:
            findings_parts.append(f"不实内容：{', '.join(materials['refuted_claims'][:2])}")

        prompt = f"""你是一位资深新闻工作者，擅长撰写客观、准确、有深度的新闻稿。请基于以下材料撰写一篇标准新闻稿。

【待报道内容】
{original_content}

【核实结论】
{conclusion_text}（可信度：{confidence_score:.0%}）

【核心发现】
{summary}

【关键证据来源】
{chr(10).join(evidence_refs[:4])}

【多维度分析要点】
{chr(10).join(dimension_summary[:3])}

【具体发现】
{chr(10).join(findings_parts[:2]) if findings_parts else '暂无'}

【关键信源】
{chr(10).join([f"• {ks['domain']} - {ks['title']}" for ks in materials['key_sources'][:3]])}

请撰写一篇标准新闻稿，要求：

1. **标题**：简洁有力，准确概括核心事实，避免标题党
2. **导语**：第一段即交代最重要的信息（5W1H），吸引读者继续阅读
3. **正文结构**：
   - 事实陈述：客观描述事件经过和核心信息
   - 核实过程：说明如何进行调查和核实
   - 证据呈现：引用关键信源，注明来源
   - 多维分析：从不同角度分析事件背景、影响等
4. **结尾**：总结要点，必要时提出展望或建议
5. **写作风格**：
   - 客观中立，避免主观臆断
   - 语言简洁明了，避免冗长句式
   - 避免使用"AI分析"、"智能判断"等术语
   - 使用新闻常用表达，如"据了解"、"经核实"、"相关人士表示"等
   - 适当使用引语增强可信度
6. **避免**：
   - 过度使用"综上所述"、"值得注意的是"等AI常用连接词
   - 过于机械的结构化表达
   - 缺乏人情味的表述

请返回JSON格式：
{{
    "headline": "新闻标题",
    "lead": "导语段落",
    "body": "正文内容（包含事实陈述、核实过程、证据呈现、多维分析等）",
    "conclusion": "结尾段落",
    "sources": "信源说明"
}}"""

        try:
            result_text = await self._call_llm(prompt)
            result = self._parse_llm_response(result_text)
            
            # 确保所有字段都存在
            if not result.get('headline'):
                result['headline'] = self._generate_headline(materials)
            if not result.get('lead'):
                result['lead'] = self._generate_lead(materials)
            if not result.get('body'):
                result['body'] = summary
            if not result.get('conclusion'):
                result['conclusion'] = conclusion_text
            if not result.get('sources'):
                result['sources'] = chr(10).join(evidence_refs[:4])
            
            return result
            
        except Exception as e:
            print(f"[ArticleAgent] Article generation error: {e}")
            # 降级处理：使用模板生成
            return self._generate_fallback_article(materials)

    def _generate_headline(self, materials: Dict[str, Any]) -> str:
        """生成标题"""
        conclusion = materials['conclusion']
        content = materials['original_content'][:50]
        
        if conclusion == 'true':
            return f"经多方核实：{content}属实"
        elif conclusion == 'false':
            return f"调查发现：{content}不实"
        elif conclusion == 'uncertain':
            return f"{content}：真相仍待查明"
        elif conclusion == 'partially_true':
            return f"{content}：部分属实但存在夸大"
        elif conclusion == 'misleading':
            return f"{content}：具有误导性"
        else:
            return f"{content}：相关情况调查"

    def _generate_lead(self, materials: Dict[str, Any]) -> str:
        """生成导语"""
        content = materials['original_content'][:100]
        conclusion = materials['conclusion_text']
        confidence = materials['confidence_score']
        
        return f'针对近期流传的"{content}"，经多方调查核实，{conclusion}。调查可信度达到{confidence:.0%}。'

    def _generate_fallback_article(self, materials: Dict[str, Any]) -> Dict[str, str]:
        """降级生成新闻稿"""
        headline = self._generate_headline(materials)
        lead = self._generate_lead(materials)
        
        body_parts = []
        body_parts.append("【调查背景】")
        body_parts.append(f"近期，{materials['original_content'][:100]}引起广泛关注。为核实相关信息真实性，调查团队进行了深入调查。")
        
        if materials['key_findings']:
            body_parts.append("\n【核心发现】")
            body_parts.append("\n".join([f"• {f}" for f in materials['key_findings'][:3]]))
        
        if materials['key_evidences']:
            body_parts.append("\n【证据来源】")
            for ev in materials['key_evidences'][:4]:
                body_parts.append(f"• {ev['source']}：{ev['key_insight'] or ev['snippet']}")
        
        if materials['dimension_points']:
            body_parts.append("\n【多维分析】")
            for dp in materials['dimension_points'][:3]:
                body_parts.append(f"• {dp['analysis'][:150]}")
        
        conclusion = materials['conclusion_text']
        sources = chr(10).join([f"• {ev['source']}" for ev in materials['key_evidences'][:4]])
        
        return {
            'headline': headline,
            'lead': lead,
            'body': '\n'.join(body_parts),
            'conclusion': conclusion,
            'sources': sources
        }

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        if self.llm_provider == 'anthropic' and self.anthropic_client:
            message = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        elif self.openai_client:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        else:
            raise Exception("No LLM client available")

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            print(f"[ArticleAgent] JSON parse error: {e}")
        
        # 解析失败，返回空字典
        return {}
