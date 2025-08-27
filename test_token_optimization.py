#!/usr/bin/env python3
"""
Token优化测试脚本
验证新的紧凑prompt格式的token节省效果和解析准确性
"""

import os
import sys
import json
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    Board, SIZE, BLACK, WHITE, EMPTY,
    format_system_prompt, format_user_prompt, 
    parse_move_from_json, build_messages_for_move
)
from llm_router import LLMRouter

def create_test_board():
    """创建一个测试棋盘，包含几步棋"""
    board = Board()
    # 模拟几步棋
    moves = [
        (BLACK, (7, 7)),   # 黑棋中心
        (WHITE, (7, 8)),   # 白棋旁边
        (BLACK, (8, 8)),   # 黑棋对角
        (WHITE, (8, 7)),   # 白棋阻挡
        (BLACK, (6, 6)),   # 黑棋扩展
    ]
    
    for player, (r, c) in moves:
        board.place(player, (r, c))  # 使用place方法而不是make_move
    
    return board

def test_format_comparison():
    """对比新旧格式的差异"""
    print("🔍 格式对比测试")
    print("=" * 50)
    
    board = create_test_board()
    
    # 新的紧凑格式
    compact_prompt = format_user_prompt(board, BLACK)
    system_prompt = format_system_prompt()
    
    print("📦 新的紧凑格式:")
    print(f"系统提示 ({len(system_prompt)} 字符):")
    print(system_prompt)
    print(f"\n用户提示 ({len(compact_prompt)} 字符):")
    print(compact_prompt)
    print(f"\n总字符数: {len(system_prompt) + len(compact_prompt)}")
    
    # 估算老格式的字符数（基于之前的观察）
    estimated_old_format = 2000  # 之前JSON格式大约的字符数
    savings = estimated_old_format - (len(system_prompt) + len(compact_prompt))
    savings_percentage = (savings / estimated_old_format) * 100
    
    print(f"\n💰 预估节省效果:")
    print(f"   旧格式估算: ~{estimated_old_format} 字符")
    print(f"   新格式实际: {len(system_prompt) + len(compact_prompt)} 字符")
    print(f"   节省字符: {savings}")
    print(f"   节省比例: {savings_percentage:.1f}%")

def test_parsing_accuracy():
    """测试解析准确性"""
    print("\n🎯 解析准确性测试")
    print("=" * 50)
    
    test_cases = [
        # 新的数组格式
        ("[7, 8]", (7, 8)),
        ("[12,3]", (12, 3)),
        ("[0, 14]", (0, 14)),
        
        # 直接JSON数组
        ("[5, 9]", (5, 9)),
        
        # 兼容旧格式
        ('{"row": 7, "col": 8}', (7, 8)),
        ('{"col": 3, "row": 12}', (12, 3)),
        
        # 边界情况
        ("[14, 0]", (14, 0)),
        ("[0, 0]", (0, 0)),
    ]
    
    success_count = 0
    for i, (input_str, expected) in enumerate(test_cases, 1):
        result = parse_move_from_json(input_str)
        success = result == expected
        success_count += success
        
        status = "✅" if success else "❌"
        print(f"   {status} 测试 {i}: {input_str} -> {result} (期望: {expected})")
    
    accuracy = (success_count / len(test_cases)) * 100
    print(f"\n📊 解析成功率: {success_count}/{len(test_cases)} ({accuracy:.1f}%)")
    
    return accuracy >= 90

def test_board_state_representation():
    """测试棋盘状态表示的正确性"""
    print("\n🏁 棋盘状态表示测试")
    print("=" * 50)
    
    board = create_test_board()
    prompt = format_user_prompt(board, BLACK)
    
    print("当前棋盘:")
    print(board.render())  # 使用render方法而不是ascii
    print(f"\n紧凑表示: {prompt}")
    
    # 验证是否包含了所有必要信息
    checks = [
        ("包含黑棋位置" if "B:" in prompt else "❌缺少黑棋位置", "B:" in prompt),
        ("包含白棋位置" if "W:" in prompt else "❌缺少白棋位置", "W:" in prompt),  
        ("包含历史记录" if "H:" in prompt else "❌缺少历史记录", "H:" in prompt),
        ("包含当前轮次" if "T:" in prompt else "❌缺少当前轮次", "T:" in prompt),
        ("包含最后一步" if "L:" in prompt else "❌缺少最后一步", "L:" in prompt),
    ]
    
    all_good = True
    for check_msg, check_result in checks:
        print(f"   {'✅' if check_result else '❌'} {check_msg}")
        all_good = all_good and check_result
    
    return all_good

def test_token_usage_with_api():
    """测试实际API调用的token使用情况"""
    print("\n🌐 实际API Token测试")
    print("=" * 50)
    
    try:
        from llm_router import get_llm_router
        
        # 创建LLM路由器
        router = get_llm_router()
        
        # 创建测试棋盘
        board = create_test_board()
        messages = build_messages_for_move(board, BLACK)
        
        print("发送消息到AI...")
        print(f"系统消息长度: {len(messages[0].content)} 字符")
        print(f"用户消息长度: {len(messages[1].content)} 字符")
        
        # 调用API
        start_time = time.time()
        response = router.chat_completion(messages=messages, temperature=0.3, max_tokens=50)
        end_time = time.time()
        
        # 显示结果
        print(f"\n⏱️ 响应时间: {end_time - start_time:.2f}秒")
        print(f"🤖 AI回复: {response.content}")
        
        if response.usage:
            usage = response.usage
            print(f"\n📊 Token使用统计:")
            print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
            print(f"   模型: {response.model}")
            
            # 验证解析
            parsed = parse_move_from_json(response.content)
            if parsed:
                print(f"✅ 成功解析移动: {parsed}")
                return True, usage.get('total_tokens', 0)
            else:
                print("❌ 解析失败")
                return False, usage.get('total_tokens', 0)
        else:
            print("⚠️ 未获取到token统计信息")
            return False, 0
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False, 0

def main():
    """运行所有测试"""
    print("🚀 Token优化全面测试")
    print("=" * 60)
    
    # 1. 格式对比
    test_format_comparison()
    
    # 2. 解析准确性
    parsing_ok = test_parsing_accuracy()
    
    # 3. 棋盘状态表示
    state_ok = test_board_state_representation()
    
    # 4. 实际API测试
    api_ok, token_count = test_token_usage_with_api()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print(f"   ✅ 解析准确性: {'通过' if parsing_ok else '失败'}")
    print(f"   ✅ 状态表示: {'通过' if state_ok else '失败'}")
    print(f"   ✅ API调用: {'通过' if api_ok else '失败'}")
    
    if token_count > 0:
        print(f"   📊 实际token消耗: {token_count}")
        
    all_passed = parsing_ok and state_ok and api_ok
    
    print(f"\n🏆 总体结果: {'全部测试通过！' if all_passed else '存在问题，需要修复'}")
    
    if all_passed:
        print("\n🎉 优化成功！新格式已准备就绪，可以大幅减少token消耗。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)