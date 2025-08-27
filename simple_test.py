#!/usr/bin/env python3
"""
简单的token优化功能验证脚本
"""

from main import *

def test_compact_format():
    """测试紧凑格式的效果"""
    print("🎯 Token优化验证测试\n")
    
    # 创建一个测试棋盘
    board = Board()
    board.place(BLACK, (7, 7))  # 中心
    board.place(WHITE, (7, 8))  # 旁边
    board.place(BLACK, (8, 8))  # 对角
    board.place(WHITE, (8, 7))  # 阻挡
    
    print("当前棋盘:")
    print(board.render())
    
    # 生成紧凑格式
    system_prompt = format_system_prompt()
    user_prompt = format_user_prompt(board, BLACK)
    
    print(f"\n📦 系统提示 ({len(system_prompt)} 字符):")
    print(system_prompt)
    
    print(f"\n📦 用户提示 ({len(user_prompt)} 字符):")
    print(user_prompt)
    
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"\n📊 总字符数: {total_chars}")
    print(f"💰 相比旧格式(~2000字符)节省: {((2000-total_chars)/2000)*100:.1f}%")
    
    # 测试解析
    test_responses = [
        "[7,6]", 
        "[9,9]", 
        '{"row": 6, "col": 6}',
        "[0,0]"
    ]
    
    print(f"\n🔍 解析测试:")
    for response in test_responses:
        parsed = parse_move_from_json(response)
        valid = parsed and board.in_bounds(*parsed) and board.cell(*parsed) == EMPTY
        status = "✅" if valid else "❌"
        print(f"   {status} {response} -> {parsed} {'(可用)' if valid else '(无效/已占用)'}")

if __name__ == "__main__":
    test_compact_format()