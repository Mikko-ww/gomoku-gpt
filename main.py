import random
import re
from typing import List, Optional, Tuple
import requests
import json

from logger import logger
from llm_router import LLMRouter, LLMMessage, get_llm_router
from game_core import Board, SIZE, COLS, COL_TO_IDX, EMPTY, BLACK, WHITE, next_player, coord_to_idx, idx_to_coord
from chess_analyzer import ChessAnalyzer

# 尝试导入配置文件
try:
    from config import API_KEYS, DEFAULT_PROVIDER
    config = {
        "default_provider": DEFAULT_PROVIDER,
        "providers": API_KEYS
    }
    # 初始化LLM路由器
    llm_router = LLMRouter(config)
except ImportError:
    logger.warning("未找到config.py，将使用环境变量配置")
    llm_router = get_llm_router()

# 初始化棋类分析器
chess_analyzer = ChessAnalyzer()

# def call_llm(system: str, user: str) -> str:
#     """使用LLM路由器调用大语言模型（简单单轮接口）

#     注意：该方法为无状态HTTP调用，模型不会记住上下文。
#     为了让模型拿到完整信息，请在 user 参数中携带棋盘与走子历史。
#     本文件已提供 format_user_prompt() 组装完整信息。
#     """
#     try:
#         # 使用简单聊天接口（单轮）
#         response = llm_router.simple_chat(system=system, user=user, temperature=0.2, max_tokens=256)
#         return response
#     except Exception as e:
#         logger.error(f"LLM调用失败: {e}")
#         return ""


def format_system_prompt() -> str:
    return (
        "你是五子棋专家,15×15棋盘,行列索引0-14。\n"
        "决策优先级：\n"
        "1. 我能一步获胜→立即获胜\n"
        "2. 对手下一步获胜→必须阻止\n"
        "3. 创建活四、冲四威胁\n"
        "4. 阻止对手威胁棋型\n"
        "5. 选择最有价值位置\n\n"
        "输入格式：B:[r,c]... - 黑棋位置; W:[r,c]... - 白棋位置; T:N - 当前轮到玩家N; L:[r,c] - 最后一步\n"
        "ANALYSIS: 必防[r,c] - 必须防守点; 机会[r,c] - 进攻机会点\n\n"
        "输出要求：只输出坐标[row,col]，如：[7,8]"
    )

def format_user_prompt(board: Board, ai_player: int) -> str:
    """构造紧凑但清晰的棋盘状态提示，包含智能分析"""
    
    # 收集黑棋位置（玩家1）
    black_positions = []
    # 收集白棋位置（玩家2）  
    white_positions = []
    
    for r in range(SIZE):
        for c in range(SIZE):
            cell_value = board.cell(r, c)
            if cell_value == BLACK:
                black_positions.append(f"[{r},{c}]")
            elif cell_value == WHITE:
                white_positions.append(f"[{r},{c}]")
    
    # 构建棋盘状态字符串
    board_str = ""
    if black_positions:
        board_str += f"B:{','.join(black_positions)}"
    if white_positions:
        if board_str:
            board_str += ";"
        board_str += f"W:{','.join(white_positions)}"
    
    # 当前轮次和最后一步
    current_turn = next_player(board)
    turn_str = f"T:{current_turn}"
    
    last_move_str = ""
    if board.moves:
        last_r, last_c = board.moves[-1][1]
        last_move_str = f"L:[{last_r},{last_c}]"
    
    # 进行智能棋盘分析（简化版）
    analysis_result = chess_analyzer.analyze_board(board, ai_player)
    
    # 构建简化分析字符串
    analysis_str = "ANALYSIS:"
    
    # 威胁分析（最重要）
    if analysis_result["threats"]:
        critical_threats = [t for t in analysis_result["threats"] if t["level"].name == "CRITICAL"]
        if critical_threats:
            # 找到最紧急的威胁防守点
            for threat in critical_threats[:1]:  # 只处理第一个最紧急威胁
                if threat["defense_points"]:
                    defense_point = threat["defense_points"][0]
                    analysis_str += f" 必防[{defense_point[0]},{defense_point[1]}]"
                    break
    
    # 我方机会分析
    if analysis_result["opportunities"]:
        best_opportunity = analysis_result["opportunities"][0]  # 第一个就是最好的机会
        if best_opportunity["upgrade_points"]:
            upgrade_point = best_opportunity["upgrade_points"][0]
            analysis_str += f" 机会[{upgrade_point[0]},{upgrade_point[1]}]"
    
    # 组合所有部分
    parts = [s for s in [board_str, turn_str, last_move_str] if s]
    compact_state = ";".join(parts)
    
    # 构建最终提示
    player_color = "黑棋" if ai_player == BLACK else "白棋"
    
    # 如果分析为空，不包含ANALYSIS部分
    if analysis_str == "ANALYSIS:":
        prompt = f"{compact_state}\n你是玩家{ai_player}（{player_color}）。"
    else:
        prompt = f"{compact_state}\n{analysis_str}\n你是玩家{ai_player}（{player_color}）。"
    
    return prompt

def build_messages_for_move(board: Board, ai_player: int) -> List[LLMMessage]:
    """构造一轮落子的对话消息（包含系统+用户，内含完整上下文）。"""
    return [
        LLMMessage(role="system", content=format_system_prompt()),
        LLMMessage(role="user", content=format_user_prompt(board, ai_player)),
    ]

def get_legal_positions(board: Board) -> List[Tuple[int, int]]:
    """获取所有合法的落子位置"""
    return [(r, c) for r in range(SIZE) for c in range(SIZE) if board.cell(r, c) == EMPTY]

def find_closest_legal_position(board: Board, target_rc: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """找到最接近目标坐标的合法位置"""
    if not target_rc:
        return None
    
    target_r, target_c = target_rc
    legal_positions = get_legal_positions(board)
    
    if not legal_positions:
        return None
    
    # 如果目标位置合法，直接返回
    if (target_r, target_c) in legal_positions:
        return (target_r, target_c)
    
    # 找到距离最近的合法位置
    min_distance = float('inf')
    closest_pos = None
    
    for r, c in legal_positions:
        distance = abs(r - target_r) + abs(c - target_c)  # 曼哈顿距离
        if distance < min_distance:
            min_distance = distance
            closest_pos = (r, c)
    
    return closest_pos

def ask_ai_move_single_call(board: Board, ai_player: int) -> Tuple[Optional[Tuple[int,int]], str]:
    """单次API调用获取AI走法，使用智能后备策略处理无效响应。
    
    核心改进：
    1. 只调用一次API，避免重复调用成本
    2. 如果AI给出无效走法，使用智能算法找到最接近的合法位置
    3. 如果完全无法解析，选择棋盘中心附近的位置
    4. 统计并显示token使用情况
    
    返回：(rc, raw_text)，若rc为None表示无合法走子可选。
    """
    messages = build_messages_for_move(board, ai_player)
    
    try:
        # 单次API调用 - 严格限制输出长度
        resp = llm_router.chat_completion(messages=messages, temperature=0.1, max_tokens=50)
        raw = resp.content or ""
        
        # 显示token统计信息
        if resp.usage:
            prompt_tokens = resp.usage.get('prompt_tokens', 0)
            completion_tokens = resp.usage.get('completion_tokens', 0)
            total_tokens = resp.usage.get('total_tokens', 0)
            
            print(f"\n📊 Token使用统计:")
            print(f"   Prompt tokens: {prompt_tokens}")
            print(f"   Completion tokens: {completion_tokens}")
            print(f"   Total tokens: {total_tokens}")
            print(f"   模型: {resp.model}")
            
            logger.info(f"Token统计 - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}, Model: {resp.model}")
        else:
            logger.warning("未获取到token使用统计信息")
        
        logger.info(f"AI原始回复: {raw}")
        
        # 检查输出长度，如果过长则警告
        if len(raw) > 20:
            logger.warning(f"AI输出过长({len(raw)}字符)，可能未遵循格式要求")
        
        # 尝试解析JSON响应
        mv = parse_move_from_json(raw)
        if mv:
            rc = mv  # mv现在直接是(row, col)元组
            if rc and board.in_bounds(*rc) and board.cell(*rc) == EMPTY:
                logger.info(f"AI选择: {rc}")
                return rc, raw
            
            # AI给出了坐标但位置无效，寻找最接近的合法位置
            closest = find_closest_legal_position(board, mv)
            if closest:
                logger.warning(f"AI坐标{mv}无效，选择最接近的合法位置: {closest}")
                return closest, raw
        
        # 无法解析坐标，使用智能后备策略
        return get_fallback_move(board), raw
        
    except Exception as e:
        logger.error(f"AI调用失败: {e}")
        return get_fallback_move(board), ""

def get_fallback_move(board: Board) -> Optional[Tuple[int, int]]:
    """智能后备策略：选择战略位置"""
    legal_positions = get_legal_positions(board)
    
    if not legal_positions:
        return None
    
    # 如果棋盘为空，选择中心位置
    if len(board.moves) == 0:
        center = SIZE // 2
        return (center, center)
    
    # 优先选择距离棋盘中心较近的位置
    center = SIZE // 2
    legal_positions.sort(key=lambda pos: abs(pos[0] - center) + abs(pos[1] - center))
    
    # 从前几个候选位置中随机选择，增加游戏变化
    candidates = legal_positions[:min(5, len(legal_positions))]
    return random.choice(candidates)

# TODO: 将此函数替换为你的大模型API调用，确保只返回如 {"move":"H8"} 的字符串
# def call_llm(system: str, user: str) -> str:
#     # 占位：随机合法点，便于你先跑通回路
#     legal = [(r,c) for r in range(SIZE) for c in range(SIZE) if b.cell(r,c)==EMPTY]
#     r, c = random.choice(legal)
#     return f'{{"move":"{idx_to_coord(r,c)}"}}'

def parse_move_from_json(s: str) -> Optional[Tuple[int, int]]:
    """解析AI返回的移动，支持多种格式"""
    try:
        # 首先尝试直接解析数组格式：[row,col]
        array_match = re.search(r'\[(\d+),\s*(\d+)\]', s)
        if array_match:
            row, col = int(array_match.group(1)), int(array_match.group(2))
            if 0 <= row < SIZE and 0 <= col < SIZE:
                return (row, col)
        
        # 尝试直接JSON解析
        try:
            data = json.loads(s.strip())
            # 如果直接是数组格式
            if isinstance(data, list) and len(data) >= 2:
                row, col = int(data[0]), int(data[1])
                if 0 <= row < SIZE and 0 <= col < SIZE:
                    return (row, col)
            # 如果是对象格式
            elif isinstance(data, dict):
                if "row" in data and "col" in data:
                    row, col = int(data["row"]), int(data["col"])
                    if 0 <= row < SIZE and 0 <= col < SIZE:
                        return (row, col)
        except:
            pass
        
        # 尝试其他模式匹配（向后兼容）
        patterns = [
            # 标准格式：{"row": 7, "col": 8}
            r'"row"\s*:\s*(\d+).*?"col"\s*:\s*(\d+)', 
            # 可能的变体：{"col": 8, "row": 7}
            r'"col"\s*:\s*(\d+).*?"row"\s*:\s*(\d+)',
            # 简单格式：row: 7, col: 8
            r'row\s*:\s*(\d+).*?col\s*:\s*(\d+)',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, s)
            if match:
                if i == 0:  # row, col格式
                    row, col = int(match.group(1)), int(match.group(2))
                elif i == 1:  # col, row格式
                    col, row = int(match.group(1)), int(match.group(2))
                else:  # 简单格式
                    row, col = int(match.group(1)), int(match.group(2))
                
                # 验证坐标范围
                if 0 <= row < SIZE and 0 <= col < SIZE:
                    return (row, col)
            
        return None
        
    except Exception as e:
        logger.error(f"解析坐标时出错: {e}")
        return None

def game_loop(human_is_black=True):
    global b
    b = Board()
    ai_player = WHITE if human_is_black else BLACK
    logger.print(b.render())

    while True:
        player = next_player(b)
        if player != ai_player:
            # 人类走
            raw = input("你的落子（如 H8）：").strip().upper()
            rc = coord_to_idx(raw)
            if not rc or not b.place(player, rc):
                logger.error("非法坐标或位置已占，用如 H8 的格式再试。")
                continue
        else:
            # AI走：单次API调用 + 智能后备策略
            rc, raw = ask_ai_move_single_call(b, ai_player)
            logger.info(f"AI输出: {raw}")
            if not rc or not b.place(player, rc):
                # 回退：强制改走一个随机合法点（兜底保证游戏可继续）
                legal = [(r,c) for r in range(SIZE) for c in range(SIZE) if b.cell(r,c)==EMPTY]
                if not legal:
                    logger.info("无合法步。和棋。")
                    break
                r,c = random.choice(legal)
                b.place(player, (r,c))
                logger.error(f"AI 非法输出，回退为随机合法点：{idx_to_coord(r,c)}")

        logger.print(b.render())

        # 胜负判定
        if b.check_last_win():
            logger.success("黑胜！" if player == BLACK else "白胜！")
            break
        if b.is_full():
            logger.success("棋满和棋。")
            break

if __name__ == "__main__":
    game_loop(human_is_black=True)
