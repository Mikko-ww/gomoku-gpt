#!/usr/bin/env python3
"""测试改进后AI的实际对战表现"""

from game_core import Board, BLACK, WHITE, next_player
from main import ask_ai_move_single_call, format_user_prompt, format_system_prompt
from logger import logger

def quick_ai_test():
    """快速测试AI的智能决策"""
    logger.info("开始测试AI智能决策...")
    
    # 创建一个有威胁的局面
    board = Board()
    
    # 设置一个白棋即将获胜的局面
    board.place(WHITE, (7, 7))
    board.place(WHITE, (7, 8))
    board.place(WHITE, (7, 9))
    board.place(WHITE, (7, 10))
    # 白棋有四连，下一步(7, 6)或(7, 11)就能获胜
    
    # 黑棋的防御位置
    board.place(BLACK, (8, 7))
    board.place(BLACK, (6, 8))
    
    logger.info("测试局面:")
    logger.print(board.render())
    
    logger.info("当前轮到黑棋，必须防守白棋的获胜威胁")
    
    # 测试AI决策（应该选择防守点 (7, 6) 或 (7, 11)）
    rc, raw_response = ask_ai_move_single_call(board, BLACK)
    
    logger.info(f"AI原始响应: {raw_response}")
    logger.info(f"AI解析位置: {rc}")
    
    expected_defense_positions = [(7, 6), (7, 11)]
    if rc in expected_defense_positions:
        logger.success(f"✓ AI正确识别并防守了威胁位置: {rc}")
        return True
    else:
        logger.error(f"✗ AI未能正确防守，选择了: {rc}，期望: {expected_defense_positions}")
        return False

def test_opportunity_detection():
    """测试AI机会识别"""
    logger.info("\n测试AI机会识别...")
    
    board = Board()
    
    # 创建一个黑棋有进攻机会的局面
    board.place(BLACK, (7, 7))
    board.place(BLACK, (7, 8))
    board.place(BLACK, (7, 9))
    # 黑棋三连，可以在(7, 6)或(7, 10)形成活四
    
    # 白棋的一些干扰子
    board.place(WHITE, (8, 8))
    board.place(WHITE, (6, 9))
    
    logger.info("测试局面:")
    logger.print(board.render())
    
    logger.info("当前轮到黑棋，应该抓住进攻机会")
    
    # 测试AI决策
    rc, raw_response = ask_ai_move_single_call(board, BLACK)
    
    logger.info(f"AI原始响应: {raw_response}")
    logger.info(f"AI解析位置: {rc}")
    
    expected_attack_positions = [(7, 6), (7, 10)]
    if rc in expected_attack_positions:
        logger.success(f"✓ AI正确识别了进攻机会: {rc}")
        return True
    else:
        logger.error(f"✗ AI未能抓住进攻机会，选择了: {rc}，期望: {expected_attack_positions}")
        return False

def test_prompt_format():
    """测试新的prompt格式"""
    logger.info("\n测试新的prompt格式...")
    
    board = Board()
    board.place(BLACK, (7, 7))
    board.place(WHITE, (8, 8))
    board.place(BLACK, (7, 8))
    
    system_prompt = format_system_prompt()
    user_prompt = format_user_prompt(board, WHITE)
    
    logger.info("=== System Prompt ===")
    logger.info(system_prompt)
    logger.info("\n=== User Prompt ===")
    logger.info(user_prompt)
    
    logger.info(f"System prompt长度: {len(system_prompt)} 字符")
    logger.info(f"User prompt长度: {len(user_prompt)} 字符")
    
    return True

def main():
    """运行所有测试"""
    logger.info("开始测试改进后的AI系统实际表现...")
    
    try:
        # 运行测试
        test1 = test_prompt_format()
        test2 = quick_ai_test()
        test3 = test_opportunity_detection()
        
        # 总结结果
        logger.info("\n=== 实战测试结果 ===")
        logger.success(f"Prompt格式测试: {'通过' if test1 else '失败'}")
        logger.success(f"防守决策测试: {'通过' if test2 else '失败'}")
        logger.success(f"进攻机会测试: {'通过' if test3 else '失败'}")
        
        if all([test1, test2, test3]):
            logger.success("所有测试通过！AI智能决策系统表现良好。")
            logger.info("可以开始与改进后的AI对战了！")
        else:
            logger.warning("部分测试失败，但基本功能应该已经有显著改善。")
            
    except Exception as e:
        logger.error(f"测试过程出错: {e}")

if __name__ == "__main__":
    main()