"""
Parser Agent V2 测试程序
测试新的事件判断和标准化功能
"""
import asyncio
import json
from aletheia_backend.agents.parser import ParserAgent


async def test_parser_v2():
    """测试优化后的 Parser Agent"""
    parser = ParserAgent()

    # 测试案例
    test_cases = [
        {
            "name": "科技公司破产（事件）",
            "content": "近日网传消息称，某知名科技公司宣布破产，数千名员工失业。这一消息在社交媒体上迅速传播，引发广泛关注。"
        },
        {
            "name": "明星吸毒（事件）",
            "content": "网传某明星因吸毒被捕，警方已介入调查。该消息在微博热搜榜排名第一。"
        },
        {
            "name": "医院过期药品（事件）",
            "content": "有传言称某知名医院使用过期药品，导致多名患者出现不良反应。"
        },
        {
            "name": "非事件-观点",
            "content": "我觉得现在的科技公司都太不靠谱了"
        },
        {
            "name": "非事件-问题",
            "content": "请问最近有什么科技新闻吗？"
        }
    ]

    for case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"测试案例: {case['name']}")
        print(f"{'=' * 80}")
        print(f"输入内容: {case['content']}\n")

        result = await parser.parse(case['content'])

        print(f"【解析结果】")
        print(f"\n1. 是否是事件: {result.get('is_event', False)}")
        print(f"2. 需要澄清: {result.get('needs_clarification', False)}")

        if result.get('needs_clarification'):
            print(f"\n3. 澄清提示: {result.get('clarification_prompt', 'N/A')}")
        else:
            print(f"\n3. 标准化事件:")
            event = result.get('standardized_event', {})
            print(f"   - 时间: {event.get('time', 'N/A')}")
            print(f"   - 地点: {event.get('location', 'N/A')}")
            print(f"   - 人物: {', '.join(event.get('people', []))}")
            print(f"   - 起因: {event.get('cause', 'N/A')}")
            print(f"   - 经过: {event.get('process', 'N/A')}")
            print(f"   - 结果: {event.get('result', 'N/A')}")

            print(f"\n4. 内容摘要: {result.get('content_summary', 'N/A')}")

            print(f"\n5. 关键主张 ({len(result.get('key_claims', []))} 个):")
            for i, claim in enumerate(result.get('key_claims', []), 1):
                print(f"   {i}. {claim.get('claim_text', 'N/A')}")
                print(f"      - 类型: {claim.get('claim_type', 'N/A')}")
                print(f"      - 实体: {', '.join(claim.get('entities', []))}")

            print(f"\n6. 搜索查询 ({len(result.get('search_queries', []))} 个):")
            for i, query in enumerate(result.get('search_queries', []), 1):
                print(f"   {i}. {query.get('query_text', 'N/A')}")
                print(f"      - 优先级: {query.get('priority', 'N/A')}")
                print(f"      - 目标信源: {', '.join(query.get('target_sources', []))}")

        print(f"\n完整JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_parser_v2())
