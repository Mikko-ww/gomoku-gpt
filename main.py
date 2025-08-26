import random
import re
from typing import List, Optional, Tuple
import requests
import json

from logger import logger
from llm_router import LLMRouter, LLMMessage, get_llm_router

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

SIZE = 15
COLS = [chr(ord('A') + i) for i in range(SIZE)]
COL_TO_IDX = {c: i for i, c in enumerate(COLS)}

EMPTY, BLACK, WHITE = 0, 1, 2

def call_llm(system: str, user: str) -> str:
    """使用LLM路由器调用大语言模型"""
    try:
        # 使用简单聊天接口
        response = llm_router.simple_chat(system=system, user=user)
        logger.info(f"LLM响应成功: {response[:100]}...")
        return response
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        return ""


class Board:
    def __init__(self):
        self.g = [[EMPTY]*SIZE for _ in range(SIZE)]
        self.moves = []  # list of (player, (r,c)), player in {BLACK, WHITE}

    def in_bounds(self, r, c):
        return 0 <= r < SIZE and 0 <= c < SIZE

    def cell(self, r, c):
        return self.g[r][c]

    def place(self, player: int, rc: Tuple[int,int]) -> bool:
        r, c = rc
        if not self.in_bounds(r, c): return False
        if self.g[r][c] != EMPTY: return False
        self.g[r][c] = player
        self.moves.append((player, (r,c)))
        return True

    def is_full(self) -> bool:
        return all(self.g[r][c] != EMPTY for r in range(SIZE) for c in range(SIZE))

    def check_win_from(self, r, c) -> bool:
        player = self.g[r][c]
        if player == EMPTY: return False
        dirs = [(1,0),(0,1),(1,1),(1,-1)]
        for dr, dc in dirs:
            count = 1
            for sgn in (1, -1):
                nr, nc = r, c
                while True:
                    nr += dr*sgn; nc += dc*sgn
                    if not self.in_bounds(nr, nc): break
                    if self.g[nr][nc] == player:
                        count += 1
                    else:
                        break
            if count >= 5:
                return True
        return False

    def check_last_win(self) -> bool:
        if not self.moves: return False
        _, (r, c) = self.moves[-1]
        return self.check_win_from(r, c)

    def to_compact_moves(self) -> str:
        parts = []
        for i, (p, (r, c)) in enumerate(self.moves):
            who = 'B' if p == BLACK else 'W'
            parts.append(f"{who}:{idx_to_coord(r, c)}")
        return ", ".join(parts)

    def render(self) -> str:
        # ASCII board for terminal
        s = []
        header = "   " + " ".join(COLS)
        s.append(header)
        for r in range(SIZE):
            row = [str(r+1).rjust(2)]
            for c in range(SIZE):
                v = self.g[r][c]
                ch = '.'
                if v == BLACK: ch = '●'
                elif v == WHITE: ch = '○'
                row.append(ch)
            s.append(" ".join(row))
        return "\n".join(s)

def coord_to_idx(coord: str) -> Optional[Tuple[int,int]]:
    m = re.fullmatch(r"([A-Oa-o])\s*([1-9]|1[0-5])", coord.strip())
    if not m: return None
    col = m.group(1).upper(); row = int(m.group(2))
    c = COL_TO_IDX[col]; r = row - 1
    return (r, c)

def idx_to_coord(r: int, c: int) -> str:
    return f"{COLS[c]}{r+1}"

def format_system_prompt() -> str:
    return (
        "你正在扮演五子棋对手。棋盘15×15，列A–O，行1–15。黑先，目标是五连。"
        "禁止走出棋盘或落在已有棋子上。只输出JSON：{\"move\":\"<列行>\"}，例如 {\"move\":\"H8\"}。"
        "你的输出格式必须是严格的JSON，不能有多余内容。"
    )

def format_user_prompt(board: Board, ai_player: int) -> str:
    turn = "Black" if next_player(board) == BLACK else "White"
    you = "Black" if ai_player == BLACK else "White"
    last = idx_to_coord(*board.moves[-1][1]) if board.moves else "None"
    return (
        f"当前对局：\n"
        f"- 轮到：{turn}（你是 {you}）\n"
        f"- 已着法：{board.to_compact_moves() or 'None'}\n"
        f"- 上一手：{last}\n"
        f"请给出你的下一步，输出JSON，字段为 move，仅一个坐标，例如 {{\"move\":\"H8\"}}。"
    )

def next_player(board: Board) -> int:
    return BLACK if len(board.moves) % 2 == 0 else WHITE

# TODO: 将此函数替换为你的大模型API调用，确保只返回如 {"move":"H8"} 的字符串
# def call_llm(system: str, user: str) -> str:
#     # 占位：随机合法点，便于你先跑通回路
#     legal = [(r,c) for r in range(SIZE) for c in range(SIZE) if b.cell(r,c)==EMPTY]
#     r, c = random.choice(legal)
#     return f'{{"move":"{idx_to_coord(r,c)}"}}'

def parse_move_from_json(s: str) -> Optional[str]:
    m = re.search(r'\"move\"\s*:\s*\"([A-Oa-o]\s*(?:[1-9]|1[0-5]))\"', s)
    return m.group(1).upper() if m else None

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
            # AI走
            sys_prompt = format_system_prompt()
            usr_prompt = format_user_prompt(b, ai_player)
            resp = call_llm(sys_prompt, usr_prompt)
            logger.info(f"AI 输出：{resp}")
            mv = parse_move_from_json(resp or "")
            rc = coord_to_idx(mv) if mv else None
            if not rc or not b.place(player, rc):
                # 回退：强制改走一个随机合法点
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
