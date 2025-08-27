#!/usr/bin/env python3
"""
测试新的AI交互格式
验证二维数组格式和JSON坐标解析
"""
import json
from main import Board, format_system_prompt, format_user_prompt, parse_move_from_json, EMPTY, BLACK, WHITE

def test_board_representation():
    """测试棋盘的二维数组表示"""
    print("🎯 测试棋盘二维数组表示")
    print("=" * 40)
    
    board = Board()
    # 模拟几步棋
    board.place(BLACK, (7, 7))  # 中心位置
    board.place(WHITE, (7, 8))
    board.place(BLACK, (8, 7))
    
    prompt = format_user_prompt(board, WHITE)
    
    # 提取并验证JSON部分
    try:
        # 寻找JSON块的准确边界
        lines = prompt.split('\n')
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            if line.strip().startswith('{'):
                in_json = True
                brace_count += line.count('{') - line.count('}')
                json_lines.append(line)
            elif in_json:
                brace_count += line.count('{') - line.count('}')
                json_lines.append(line)
                if brace_count <= 0:
                    break
        
        json_str = '\n'.join(json_lines)
        game_data = json.loads(json_str)
        
        print("✅ JSON格式正确")
        print(f"棋盘大小: {game_data['board_size']}")
        print(f"已下棋子数: {game_data['total_moves']}")
        print(f"当前轮到: 玩家{game_data['current_turn']}")
        
        # 检查棋盘状态
        board_state = game_data['board_state']
        print(f"棋盘状态示例 (前3行):")
        for i in range(min(3, len(board_state))):
            row_display = [str(x) for x in board_state[i][:10]] + ['...'] if len(board_state[i]) > 10 else [str(x) for x in board_state[i]]
            print(f"  行{i}: {' '.join(row_display)}")
        
        # 检查历史记录
        if game_data['move_history']:
            print(f"落子历史:")
            for move in game_data['move_history']:
                color = ['', '黑', '白'][move['player']]
                print(f"  第{move['step']}步: {color}棋 [{move['row']}, {move['col']}]")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON解析失败: {e}")
        return False

def test_coordinate_parsing():
    """测试坐标解析功能"""
    print("\n🎯 测试坐标解析功能")  
    print("=" * 40)
    
    test_cases = [
        ('{"row": 7, "col": 8}', (7, 8)),
        ('{"col": 8, "row": 7}', (7, 8)),
        ('[7, 8]', (7, 8)),
        ('{"position": [7, 8]}', (7, 8)),
        ('row: 7, col: 8', (7, 8)),  # 不标准但可能的格式
        ('{"row":10,"col":5}', (10, 5)),  # 紧凑格式
        ('invalid json', None),  # 无效格式
        ('{"row": 20, "col": 5}', None),  # 超出范围
    ]
    
    passed = 0
    for test_input, expected in test_cases:
        result = parse_move_from_json(test_input)
        if result == expected:
            print(f"✅ '{test_input}' -> {result}")
            passed += 1
        else:
            print(f"❌ '{test_input}' -> {result} (期望: {expected})")
    
    print(f"\n解析测试结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)

def test_system_prompt():
    """测试系统提示词"""
    print("\n🎯 测试系统提示词")
    print("=" * 40)
    
    system_prompt = format_system_prompt()
    
    # 检查关键内容
    key_points = [
        "二维数组",
        "0=空位",
        "1=黑棋", 
        "2=白棋",
        '{"row"',
        '"col"',
        "0-14",
        "连成5子"
    ]
    
    missing_points = []
    for point in key_points:
        if point not in system_prompt:
            missing_points.append(point)
    
    if not missing_points:
        print("✅ 系统提示词包含所有关键信息")
        print("内容预览:")
        lines = system_prompt.split('\n')
        for line in lines[:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... (共{len(lines)}行)")
        return True
    else:
        print(f"❌ 缺少关键信息: {missing_points}")
        return False

def demonstrate_new_format():
    """演示新格式的完整交互"""
    print("\n🎮 演示新格式的AI交互")
    print("=" * 40)
    
    board = Board()
    # 模拟一个中局
    moves = [
        (BLACK, (7, 7)),   # 中心开局
        (WHITE, (6, 7)),   # 防守
        (BLACK, (8, 7)),   # 继续攻击
        (WHITE, (7, 6)),   # 继续防守
        (BLACK, (9, 7)),   # 形成三连
    ]
    
    for player, pos in moves:
        board.place(player, pos)
    
    print("模拟棋局状态:")
    print(board.render())
    
    print("\n发送给AI的信息格式:")
    system_msg = format_system_prompt()
    user_msg = format_user_prompt(board, WHITE)  # 假设轮到白棋
    
    print("📋 System Prompt (部分):")
    print(system_msg[:200] + "...")
    
    print("\n📋 User Prompt (部分):")
    print(user_msg[:500] + "...")
    
    print(f"\n📊 统计信息:")
    print(f"- System prompt长度: {len(system_msg)} 字符")
    print(f"- User prompt长度: {len(user_msg)} 字符")
    print(f"- 包含完整棋盘状态: ✅")
    print(f"- 包含完整历史记录: ✅")
    print(f"- 使用数字坐标系: ✅")

if __name__ == "__main__":
    print("🧪 新AI交互格式测试")
    print("=" * 50)
    
    tests = [
        ("棋盘表示", test_board_representation),
        ("坐标解析", test_coordinate_parsing),
        ("系统提示", test_system_prompt),
    ]
    
    passed_tests = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
    
    print(f"\n📊 测试总结: {passed_tests}/{len(tests)} 通过")
    
    if passed_tests == len(tests):
        print("\n✨ 所有测试通过！新格式准备就绪")
        demonstrate_new_format()
    else:
        print("\n⚠️  部分测试失败，请检查实现")