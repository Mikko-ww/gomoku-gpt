#!/usr/bin/env python3
"""
五子棋智能分析模块
提供棋型识别、威胁检测、机会分析等功能
"""

from typing import List, Tuple, Dict, Set, Optional
from enum import Enum

from game_core import Board, SIZE, BLACK, WHITE, EMPTY

class PatternType(Enum):
    """棋型类型"""
    FIVE = "连五"          # 已胜
    LIVE_FOUR = "活四"     # 必胜
    RUSH_FOUR = "冲四"     # 冲四
    LIVE_THREE = "活三"    # 活三
    SLEEP_THREE = "眠三"   # 眠三
    LIVE_TWO = "活二"      # 活二
    SLEEP_TWO = "眠二"     # 眠二

class ThreatLevel(Enum):
    """威胁等级"""
    CRITICAL = 5    # 立即致胜
    URGENT = 4      # 必须防守
    HIGH = 3        # 重要威胁
    MEDIUM = 2      # 一般威胁  
    LOW = 1         # 轻微威胁

class ChessAnalyzer:
    """五子棋智能分析器"""
    
    def __init__(self):
        # 八个方向：水平、垂直、两个对角线
        self.directions = [
            (0, 1),   # 水平
            (1, 0),   # 垂直
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]
    
    def analyze_board(self, board: Board, player: int) -> Dict:
        """全面分析棋盘状态"""
        opponent = WHITE if player == BLACK else BLACK
        
        analysis = {
            "player_patterns": self.find_all_patterns(board, player),
            "opponent_patterns": self.find_all_patterns(board, opponent),
            "threats": self.detect_threats(board, opponent),
            "opportunities": self.find_opportunities(board, player),
            "critical_points": self.get_critical_points(board, player),
            "board_visual": self.create_visual_board(board),
            "recommendation": self.get_move_recommendation(board, player)
        }
        
        return analysis
    
    def find_all_patterns(self, board: Board, player: int) -> Dict[PatternType, List[List[Tuple]]]:
        """找出所有棋型"""
        patterns = {pattern: [] for pattern in PatternType}
        
        # 遍历每个位置的每个方向
        for r in range(SIZE):
            for c in range(SIZE):
                if board.cell(r, c) == player:
                    for dr, dc in self.directions:
                        pattern_info = self.analyze_line(board, r, c, dr, dc, player)
                        if pattern_info:
                            pattern_type, positions = pattern_info
                            patterns[pattern_type].append(positions)
        
        return patterns
    
    def analyze_line(self, board: Board, r: int, c: int, dr: int, dc: int, player: int) -> Optional[Tuple[PatternType, List[Tuple]]]:
        """分析一条线上的棋型"""
        # 向两个方向扩展，找出完整的棋子序列
        positions = [(r, c)]
        
        # 向前扩展
        nr, nc = r + dr, c + dc
        while self.in_bounds(nr, nc) and board.cell(nr, nc) == player:
            positions.append((nr, nc))
            nr, nc = nr + dr, nc + dc
        
        # 向后扩展  
        nr, nc = r - dr, c - dc
        while self.in_bounds(nr, nc) and board.cell(nr, nc) == player:
            positions.insert(0, (nr, nc))
            nr, nc = nr - dr, nc - dc
        
        # 分析棋型
        return self.classify_pattern(board, positions, dr, dc, player)
    
    def classify_pattern(self, board: Board, positions: List[Tuple], dr: int, dc: int, player: int) -> Optional[Tuple]:
        """分类棋型"""
        length = len(positions)
        if length < 2:
            return None
        
        # 检查两端的情况
        start_r, start_c = positions[0]
        end_r, end_c = positions[-1]
        
        # 前端空位
        front_r, front_c = start_r - dr, start_c - dc
        front_free = self.in_bounds(front_r, front_c) and board.cell(front_r, front_c) == EMPTY
        
        # 后端空位
        back_r, back_c = end_r + dr, end_c + dc
        back_free = self.in_bounds(back_r, back_c) and board.cell(back_r, back_c) == EMPTY
        
        # 分类逻辑
        if length >= 5:
            return (PatternType.FIVE, positions)
        elif length == 4:
            if front_free and back_free:
                return (PatternType.LIVE_FOUR, positions)
            elif front_free or back_free:
                return (PatternType.RUSH_FOUR, positions)
        elif length == 3:
            if front_free and back_free:
                # 检查是否真正的活三（两端都能延伸）
                if self.check_extendable(board, positions, dr, dc, player, 2):
                    return (PatternType.LIVE_THREE, positions)
            elif front_free or back_free:
                return (PatternType.SLEEP_THREE, positions)
        elif length == 2:
            if front_free and back_free:
                return (PatternType.LIVE_TWO, positions)
            elif front_free or back_free:
                return (PatternType.SLEEP_TWO, positions)
        
        return None
    
    def check_extendable(self, board: Board, positions: List[Tuple], dr: int, dc: int, player: int, extend_len: int) -> bool:
        """检查是否可以向两端延伸指定长度"""
        start_r, start_c = positions[0]
        end_r, end_c = positions[-1]
        
        # 检查前端
        can_extend_front = True
        for i in range(1, extend_len + 1):
            nr, nc = start_r - dr * i, start_c - dc * i
            if not self.in_bounds(nr, nc) or board.cell(nr, nc) != EMPTY:
                can_extend_front = False
                break
        
        # 检查后端
        can_extend_back = True
        for i in range(1, extend_len + 1):
            nr, nc = end_r + dr * i, end_c + dc * i
            if not self.in_bounds(nr, nc) or board.cell(nr, nc) != EMPTY:
                can_extend_back = False
                break
        
        return can_extend_front and can_extend_back
    
    def detect_threats(self, board: Board, opponent: int) -> List[Dict]:
        """检测对手威胁"""
        threats = []
        patterns = self.find_all_patterns(board, opponent)
        
        # 致命威胁：连五、活四
        for pos_list in patterns[PatternType.FIVE]:
            threats.append({
                "type": PatternType.FIVE,
                "level": ThreatLevel.CRITICAL,
                "positions": pos_list,
                "defense_points": []  # 已经无法防守
            })
        
        for pos_list in patterns[PatternType.LIVE_FOUR]:
            defense_points = self.find_defense_points(board, pos_list, opponent)
            threats.append({
                "type": PatternType.LIVE_FOUR,
                "level": ThreatLevel.CRITICAL,
                "positions": pos_list,
                "defense_points": defense_points
            })
        
        # 紧急威胁：冲四
        for pos_list in patterns[PatternType.RUSH_FOUR]:
            defense_points = self.find_defense_points(board, pos_list, opponent)
            threats.append({
                "type": PatternType.RUSH_FOUR,
                "level": ThreatLevel.URGENT,
                "positions": pos_list,
                "defense_points": defense_points
            })
        
        # 重要威胁：活三
        for pos_list in patterns[PatternType.LIVE_THREE]:
            defense_points = self.find_defense_points(board, pos_list, opponent)
            threats.append({
                "type": PatternType.LIVE_THREE,
                "level": ThreatLevel.HIGH,
                "positions": pos_list,
                "defense_points": defense_points
            })
        
        return sorted(threats, key=lambda x: x["level"].value, reverse=True)
    
    def find_defense_points(self, board: Board, positions: List[Tuple], player: int) -> List[Tuple]:
        """找出防守点"""
        defense_points = []
        
        if not positions:
            return defense_points
        
        # 对于每个方向，检查可能的防守点
        for dr, dc in self.directions:
            # 检查这些位置是否在同一条线上
            if self.are_positions_aligned(positions, dr, dc):
                start_r, start_c = positions[0]
                end_r, end_c = positions[-1]
                
                # 检查两端的防守点
                front_r, front_c = start_r - dr, start_c - dc
                if self.in_bounds(front_r, front_c) and board.cell(front_r, front_c) == EMPTY:
                    defense_points.append((front_r, front_c))
                
                back_r, back_c = end_r + dr, end_c + dc
                if self.in_bounds(back_r, back_c) and board.cell(back_r, back_c) == EMPTY:
                    defense_points.append((back_r, back_c))
        
        return list(set(defense_points))  # 去重
    
    def are_positions_aligned(self, positions: List[Tuple], dr: int, dc: int) -> bool:
        """检查位置是否在指定方向上对齐"""
        if len(positions) < 2:
            return True
        
        start_r, start_c = positions[0]
        for i, (r, c) in enumerate(positions[1:], 1):
            expected_r = start_r + dr * i
            expected_c = start_c + dc * i
            if r != expected_r or c != expected_c:
                return False
        return True
    
    def find_opportunities(self, board: Board, player: int) -> List[Dict]:
        """找出进攻机会"""
        opportunities = []
        patterns = self.find_all_patterns(board, player)
        
        # 寻找可以形成更高级棋型的机会
        for pattern_type, pos_lists in patterns.items():
            for pos_list in pos_lists:
                upgrade_points = self.find_upgrade_points(board, pos_list, player, pattern_type)
                if upgrade_points:
                    opportunities.append({
                        "current_pattern": pattern_type,
                        "positions": pos_list,
                        "upgrade_points": upgrade_points,
                        "priority": self.get_opportunity_priority(pattern_type)
                    })
        
        return sorted(opportunities, key=lambda x: x["priority"], reverse=True)
    
    def find_upgrade_points(self, board: Board, positions: List[Tuple], player: int, current_type: PatternType) -> List[Tuple]:
        """找出可以升级棋型的点"""
        upgrade_points = []
        
        # 对于每个方向检查延伸点
        for dr, dc in self.directions:
            if self.are_positions_aligned(positions, dr, dc):
                start_r, start_c = positions[0]
                end_r, end_c = positions[-1]
                
                # 检查延伸点
                for extend_r, extend_c in [(start_r - dr, start_c - dc), (end_r + dr, end_c + dc)]:
                    if (self.in_bounds(extend_r, extend_c) and 
                        board.cell(extend_r, extend_c) == EMPTY):
                        # 模拟放子，检查是否能升级
                        board.g[extend_r][extend_c] = player
                        new_pattern = self.get_pattern_at_position(board, extend_r, extend_c, player)
                        board.g[extend_r][extend_c] = EMPTY  # 恢复
                        
                        if self.is_pattern_upgrade(current_type, new_pattern):
                            upgrade_points.append((extend_r, extend_c))
        
        return upgrade_points
    
    def get_pattern_at_position(self, board: Board, r: int, c: int, player: int) -> Optional[PatternType]:
        """获取指定位置的最高棋型"""
        best_pattern = None
        best_priority = 0
        
        for dr, dc in self.directions:
            pattern_info = self.analyze_line(board, r, c, dr, dc, player)
            if pattern_info:
                pattern_type, _ = pattern_info
                priority = self.get_pattern_priority(pattern_type)
                if priority > best_priority:
                    best_pattern = pattern_type
                    best_priority = priority
        
        return best_pattern
    
    def is_pattern_upgrade(self, old_pattern: PatternType, new_pattern: Optional[PatternType]) -> bool:
        """判断是否为棋型升级"""
        if not new_pattern:
            return False
        
        old_priority = self.get_pattern_priority(old_pattern)
        new_priority = self.get_pattern_priority(new_pattern)
        
        return new_priority > old_priority
    
    def get_pattern_priority(self, pattern: PatternType) -> int:
        """获取棋型优先级"""
        priority_map = {
            PatternType.FIVE: 10,
            PatternType.LIVE_FOUR: 9,
            PatternType.RUSH_FOUR: 8,
            PatternType.LIVE_THREE: 7,
            PatternType.SLEEP_THREE: 6,
            PatternType.LIVE_TWO: 5,
            PatternType.SLEEP_TWO: 4
        }
        return priority_map.get(pattern, 0)
    
    def get_opportunity_priority(self, pattern: PatternType) -> int:
        """获取机会优先级"""
        return self.get_pattern_priority(pattern)
    
    def get_critical_points(self, board: Board, player: int) -> List[Tuple]:
        """获取关键点位"""
        critical_points = []
        opponent = WHITE if player == BLACK else BLACK
        
        # 收集所有威胁的防守点
        threats = self.detect_threats(board, opponent)
        for threat in threats:
            if threat["level"] in [ThreatLevel.CRITICAL, ThreatLevel.URGENT]:
                critical_points.extend(threat["defense_points"])
        
        # 收集最佳进攻点
        opportunities = self.find_opportunities(board, player)
        for opp in opportunities[:3]:  # 只取前3个机会
            critical_points.extend(opp["upgrade_points"])
        
        return list(set(critical_points))  # 去重
    
    def create_visual_board(self, board: Board) -> str:
        """创建可视化棋盘"""
        lines = []
        
        # 表头
        header = "   " + " ".join([chr(ord('A') + i) for i in range(SIZE)])
        lines.append(header)
        
        # 棋盘内容
        for r in range(SIZE):
            row_items = [str(r + 1).rjust(2)]
            for c in range(SIZE):
                cell = board.cell(r, c)
                if cell == BLACK:
                    row_items.append('●')
                elif cell == WHITE:
                    row_items.append('○')
                else:
                    row_items.append('·')
            lines.append(" ".join(row_items))
        
        return "\n".join(lines)
    
    def get_move_recommendation(self, board: Board, player: int) -> Dict:
        """获取移动推荐"""
        threats = self.detect_threats(board, WHITE if player == BLACK else BLACK)
        opportunities = self.find_opportunities(board, player)
        
        # 决策逻辑
        if threats and threats[0]["level"] in [ThreatLevel.CRITICAL, ThreatLevel.URGENT]:
            # 优先防守
            defense_points = threats[0]["defense_points"]
            if defense_points:
                return {
                    "action": "防守",
                    "reason": f"必须防守对手的{threats[0]['type'].value}",
                    "recommended_moves": defense_points[:3],
                    "priority": "紧急"
                }
        
        if opportunities:
            # 进攻机会
            best_opp = opportunities[0]
            return {
                "action": "进攻",
                "reason": f"可以形成{best_opp['current_pattern'].value}",
                "recommended_moves": best_opp["upgrade_points"][:3],
                "priority": "重要"
            }
        
        # 默认建议
        return {
            "action": "发展",
            "reason": "寻找发展机会",
            "recommended_moves": self.get_development_moves(board),
            "priority": "一般"
        }
    
    def get_development_moves(self, board: Board) -> List[Tuple]:
        """获取发展性移动"""
        center = SIZE // 2
        development_moves = []
        
        # 优先考虑中心区域
        for offset in range(1, 4):
            for dr in [-offset, 0, offset]:
                for dc in [-offset, 0, offset]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = center + dr, center + dc
                    if (self.in_bounds(r, c) and 
                        board.cell(r, c) == EMPTY and
                        (r, c) not in development_moves):
                        development_moves.append((r, c))
        
        return development_moves[:5]
    
    def in_bounds(self, r: int, c: int) -> bool:
        """检查坐标是否在棋盘范围内"""
        return 0 <= r < SIZE and 0 <= c < SIZE

# 创建全局分析器实例
chess_analyzer = ChessAnalyzer()