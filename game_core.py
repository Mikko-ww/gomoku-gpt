"""五子棋游戏的核心类和常量定义"""

SIZE = 15
COLS = [chr(ord('A') + i) for i in range(SIZE)]
COL_TO_IDX = {c: i for i, c in enumerate(COLS)}

EMPTY, BLACK, WHITE = 0, 1, 2

class Board:
    def __init__(self):
        self.g = [[EMPTY]*SIZE for _ in range(SIZE)]
        self.moves = []  # list of (player, (r,c)), player in {BLACK, WHITE}

    def in_bounds(self, r, c):
        return 0 <= r < SIZE and 0 <= c < SIZE

    def cell(self, r, c):
        """返回位置 (r,c) 的棋子：EMPTY, BLACK, WHITE"""
        if not self.in_bounds(r, c):
            return None
        return self.g[r][c]

    def place(self, player, pos):
        """在位置 pos=(r,c) 放置玩家 player 的棋子"""
        r, c = pos
        if not self.in_bounds(r, c) or self.g[r][c] != EMPTY:
            return False
        self.g[r][c] = player
        self.moves.append((player, (r, c)))
        return True

    def render(self):
        """渲染棋盘（ASCII格式）"""
        lines = ["   " + " ".join(COLS)]
        for r in range(SIZE):
            row_str = f"{r+1:2} "
            for c in range(SIZE):
                if self.g[r][c] == BLACK:
                    row_str += "● "
                elif self.g[r][c] == WHITE:
                    row_str += "○ "
                else:
                    row_str += ". "
            lines.append(row_str)
        return "\n".join(lines)

    def check_last_win(self):
        """检查最后一步是否获胜（五子连成一线）"""
        if not self.moves:
            return False
        
        player, (r, c) = self.moves[-1]
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        
        for dr, dc in directions:
            # 向两个方向计数
            count = 1  # 包括当前位置
            
            # 向前计数
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc) and self.cell(nr, nc) == player:
                count += 1
                nr, nc = nr + dr, nc + dc
            
            # 向后计数
            nr, nc = r - dr, c - dc
            while self.in_bounds(nr, nc) and self.cell(nr, nc) == player:
                count += 1
                nr, nc = nr - dr, nc - dc
            
            if count >= 5:
                return True
        
        return False

    def is_full(self):
        """检查棋盘是否已满"""
        for r in range(SIZE):
            for c in range(SIZE):
                if self.g[r][c] == EMPTY:
                    return False
        return True

def next_player(board: Board):
    """根据棋盘状态确定下一个该走的玩家"""
    black_count = sum(1 for r in range(SIZE) for c in range(SIZE) if board.cell(r, c) == BLACK)
    white_count = sum(1 for r in range(SIZE) for c in range(SIZE) if board.cell(r, c) == WHITE)
    
    # 黑棋先手，子数相等时轮到黑棋
    return BLACK if black_count == white_count else WHITE

def coord_to_idx(coord_str):
    """将棋盘坐标（如'H8'）转换为索引(r,c)"""
    if len(coord_str) < 2:
        return None
    
    col_char = coord_str[0].upper()
    if col_char not in COL_TO_IDX:
        return None
    
    try:
        row_num = int(coord_str[1:])
        if 1 <= row_num <= SIZE:
            return (row_num - 1, COL_TO_IDX[col_char])
    except ValueError:
        pass
    
    return None

def idx_to_coord(r, c):
    """将索引(r,c)转换为棋盘坐标（如'H8'）"""
    if 0 <= r < SIZE and 0 <= c < SIZE:
        return f"{COLS[c]}{r+1}"
    return None