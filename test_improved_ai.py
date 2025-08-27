#!/usr/bin/env python3
"""测试改进后的AI棋力"""

from game_core import Board, EMPTY, BLACK, WHITE
from chess_analyzer import ChessAnalyzer
from logger import logger

# 创建分析器实例
chess_analyzer = ChessAnalyzer()

def test_basic_analysis():
    """测试基础分析功能"""
    logger.info("测试基础分析功能...")
    
    # 创建一个简单的测试棋盘
    board = Board()
    
    # 设置一些棋子 - 模拟一个实际对局
    test_moves = [
        (BLACK, (7, 7)),  # 开局天元
        (WHITE, (7, 8)),  # 白棋紧贴
        (BLACK, (7, 6)),  # 黑棋延伸
        (WHITE, (8, 7)),  # 白棋阻断
        (BLACK, (7, 5)),  # 黑棋继续延伸
        (WHITE, (6, 7)),  # 白棋继续阻断
    ]
    
    for player, (r, c) in test_moves:
        board.place(player, (r, c))
    
    logger.info("测试棋盘状态:")
    logger.print(board.render())
    
    # 测试分析功能
    analysis = chess_analyzer.analyze_board(board, BLACK)
    
    logger.info("=== 黑棋分析结果 ===")
    logger.info(f"棋型分析: {analysis['player_patterns']}")
    logger.info(f"对手棋型: {analysis['opponent_patterns']}")
    logger.info(f"检测到威胁: {len(analysis['threats'])}个")
    logger.info(f"发现机会: {len(analysis['opportunities'])}个")
    
    if analysis['recommendation']:
        logger.success(f"推荐落子: {analysis['recommendation']}")
    
    return True

def test_threat_detection():
    """测试威胁检测功能"""
    logger.info("\n测试威胁检测功能...")
    
    board = Board()
    
    # 创建一个即将获胜的局面
    threat_moves = [
        (WHITE, (7, 7)),  # 中心
        (WHITE, (7, 8)),  # 向右
        (WHITE, (7, 9)),  # 向右  
        (WHITE, (7, 10)), # 向右 - 现在白棋有四连，下一步(7,6)或(7,11)就能获胜
        (BLACK, (8, 7)),  # 黑棋在下方
        (BLACK, (6, 7)),  # 黑棋在上方
    ]
    
    for player, (r, c) in threat_moves:
        board.place(player, (r, c))
    
    logger.info("威胁测试棋盘状态:")
    logger.print(board.render())
    
    # 分析黑棋面临的威胁
    analysis = chess_analyzer.analyze_board(board, BLACK)
    
    logger.info("=== 威胁检测结果 ===")
    threats = analysis['threats']
    logger.info(f"检测到 {len(threats)} 个威胁")
    
    for i, threat in enumerate(threats):
        logger.warning(f"威胁 {i+1}: {threat['type'].name} (级别: {threat['level'].name})")
        if threat['defense_points']:
            logger.info(f"  防守点: {threat['defense_points']}")
    
    return len(threats) > 0

def test_opportunity_detection():
    """测试机会检测功能"""
    logger.info("\n测试机会检测功能...")
    
    board = Board()
    
    # 创建一个有进攻机会的局面
    opportunity_moves = [
        (BLACK, (7, 7)),  # 中心
        (BLACK, (7, 8)),  # 向右
        (BLACK, (7, 9)),  # 向右 - 黑棋有机会形成更强棋型
        (WHITE, (8, 8)),  # 白棋在下方
        (WHITE, (6, 8)),  # 白棋在上方
    ]
    
    for player, (r, c) in opportunity_moves:
        board.place(player, (r, c))
    
    logger.info("机会测试棋盘状态:")
    logger.print(board.render())
    
    # 分析黑棋的进攻机会
    analysis = chess_analyzer.analyze_board(board, BLACK)
    
    logger.info("=== 机会检测结果 ===")
    opportunities = analysis['opportunities']
    logger.info(f"发现 {len(opportunities)} 个进攻机会")
    
    for i, opp in enumerate(opportunities[:3]):  # 只显示前3个
        logger.success(f"机会 {i+1}: {opp['current_pattern'].name} (优先级: {opp['priority']})")
        logger.info(f"  升级点: {opp['upgrade_points']}")
    
    return len(opportunities) > 0

def main():
    """运行所有测试"""
    logger.info("开始测试改进后的AI系统...")
    
    try:
        # 运行测试
        test1_result = test_basic_analysis()
        test2_result = test_threat_detection()
        test3_result = test_opportunity_detection()
        
        # 总结结果
        logger.info("\n=== 测试结果总结 ===")
        logger.success(f"基础分析测试: {'通过' if test1_result else '失败'}")
        logger.success(f"威胁检测测试: {'通过' if test2_result else '失败'}")
        logger.success(f"机会检测测试: {'通过' if test3_result else '失败'}")
        
        if all([test1_result, test2_result, test3_result]):
            logger.success("所有测试通过！AI智能分析系统运行正常。")
        else:
            logger.error("部分测试失败，需要进一步调试。")
            
    except Exception as e:
        logger.error(f"测试运行出错: {e}")

if __name__ == "__main__":
    main()