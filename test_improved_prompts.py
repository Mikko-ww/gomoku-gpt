#!/usr/bin/env python3
"""
测试改进后的prompt格式控制效果
"""

from main import *

def test_improved_prompts():
    """测试改进后的prompt格式"""
    print("🔧 改进版Prompt测试")
    print("=" * 50)
    
    # 创建测试棋盘
    board = Board()
    board.place(BLACK, (6, 7))  
    board.place(WHITE, (6, 8))
    board.place(BLACK, (7, 7))
    
    print("当前棋盘:")
    print(board.render())
    
    # 生成新的prompt格式
    system_prompt = format_system_prompt()
    user_prompt = format_user_prompt(board, WHITE)
    
    print(f"\n📋 系统提示 ({len(system_prompt)} 字符):")
    print(system_prompt)
    
    print(f"\n📋 用户提示 ({len(user_prompt)} 字符):")
    print(user_prompt)
    
    print(f"\n📊 改进效果分析:")
    print(f"   ✅ 添加了格式说明 (B/W/H/T/L)")
    print(f"   ✅ 使用[row,col]格式代替裸数字")
    print(f"   ✅ 强调'只输出坐标，不要解释'")
    print(f"   ✅ 限制max_tokens=10")
    
    # 对比旧格式
    old_chars = 152  # 之前测试的字符数
    new_chars = len(system_prompt) + len(user_prompt)
    
    print(f"\n💡 长度对比:")
    print(f"   旧格式: {old_chars} 字符")
    print(f"   新格式: {new_chars} 字符")
    print(f"   变化: {'+' if new_chars > old_chars else ''}{new_chars - old_chars} 字符")
    
    # 预测改进效果
    print(f"\n🎯 预期改进:")
    print(f"   1. AI输出应该从425 tokens降到5-10 tokens")
    print(f"   2. 格式理解更清晰(有B/W/H/T/L说明)")
    print(f"   3. 坐标格式更规范([row,col])")

def test_actual_ai_call():
    """测试实际AI调用效果"""
    print("\n" + "=" * 50)
    print("🤖 实际AI调用测试")
    print("=" * 50)
    
    # 创建同样的测试场景
    board = Board()
    board.place(BLACK, (6, 7))  
    board.place(WHITE, (6, 8))
    board.place(BLACK, (7, 7))
    
    print("测试场景: 黑棋形成活二，白棋需要防守")
    print(board.render())
    
    try:
        print("\n🤖 AI思考中...")
        move, raw_response = ask_ai_move_single_call(board, WHITE)
        
        print(f"\n📋 分析结果:")
        print(f"   原始回复长度: {len(raw_response)} 字符")
        print(f"   原始回复: {raw_response}")
        print(f"   解析结果: {move}")
        
        # 判断改进效果
        if len(raw_response) <= 20:
            print(f"   ✅ 输出长度控制成功!")
        else:
            print(f"   ❌ 输出仍然过长，需要进一步调整")
            
        if move and board.in_bounds(*move) and board.cell(*move) == EMPTY:
            print(f"   ✅ 移动有效: {move}")
            board.place(WHITE, move)
            print("\n执行移动后:")
            print(board.render())
        else:
            print(f"   ❌ 移动无效: {move}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_improved_prompts()
    test_actual_ai_call()