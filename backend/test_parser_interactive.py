"""
交互式 Parser Agent 测试程序
输入内容，查看 Parser Agent 的输出
"""
import asyncio
import json
import sys
from app.agents.parser import ParserAgent


async def test_parser_interactive():
    """交互式测试 Parser Agent"""
    parser = ParserAgent()
    
    print("=" * 80)
    print("Parser Agent 交互式测试")
    print("=" * 80)
    print("输入要测试的舆情内容（直接回车退出）：\n")
    
    while True:
        # 获取用户输入
        print("-" * 80)
        content = input("请输入内容: ").strip()
        
        if not content:
            print("\n退出测试")
            break
        
        print(f"\n处理中...\n")
        
        try:
            # 调用 Parser Agent
            result = await parser.parse(content)
            
            # 显示输出结果
            print("=" * 80)
            print("【输出结果】")
            print("=" * 80)
            
            print(f"\n1. 任务ID: {result.get('task_id', 'N/A')}")
            
            print(f"\n2. 内容摘要:")
            print(f"   {result.get('content_summary', 'N/A')}")
            
            print(f"\n3. 关键主张 ({len(result.get('key_claims', []))} 个):")
            for i, claim in enumerate(result.get('key_claims', []), 1):
                print(f"   {i}. {claim.get('claim_text', 'N/A')}")
                print(f"      - 类型: {claim.get('claim_type', 'N/A')}")
                print(f"      - 实体: {', '.join(claim.get('entities', []))}")
            
            print(f"\n4. 搜索查询 ({len(result.get('search_queries', []))} 个):")
            for i, query in enumerate(result.get('search_queries', []), 1):
                print(f"   {i}. {query.get('query_text', 'N/A')}")
                print(f"      - 优先级: {query.get('priority', 'N/A')}")
                print(f"      - 目标信源: {', '.join(query.get('target_sources', []))}")
            
            # 质量评估
            print(f"\n5. 质量评估:")
            queries = result.get('search_queries', [])
            has_entity = any(len(q.get('query_text', '')) > 10 for q in queries)
            has_action = any(keyword in ' '.join([q.get('query_text', '') for q in queries]) 
                           for keyword in ['破产', '裁员', '被捕', '过期', '宣布', '调查'])
            has_official = any(keyword in ' '.join([q.get('query_text', '') for q in queries]) 
                             for keyword in ['官方', '警方', '声明', '通报', '辟谣', '回应'])
            
            print(f"   ✓ 查询长度足够: {'是' if has_entity else '否'}")
            print(f"   ✓ 包含核心动作: {'是' if has_action else '否'}")
            print(f"   ✓ 包含官方信源: {'是' if has_official else '否'}")
            
            # 显示完整 JSON
            print(f"\n6. 完整JSON输出:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"\n错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(test_parser_interactive())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(0)
