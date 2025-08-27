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
    """使用LLM路由器调用大语言模型（简单单轮接口）

    注意：该方法为无状态HTTP调用，模型不会记住上下文。
    为了让模型拿到完整信息，请在 user 参数中携带棋盘与走子历史。
    本文件已提供 format_user_prompt() 组装完整信息。
    """
    try:
        # 使用简单聊天接口（单轮）
        response = llm_router.simple_chat(system=system, user=user, temperature=0.2, max_tokens=128)
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
        "你是五子棋AI对手。棋盘15×15，列A–O，行1–15。黑先，目标是五连。"
        "必须输出严格JSON：{\"move\":\"<列行>\"}，例如 {\"move\":\"H8\"}。"
        "不要输出任何解释或多余文本，不要换行，不要添加其他字段。"
    )

def format_user_prompt(board: Board, ai_player: int) -> str:
    """构造包含完整上下文的提示（无状态HTTP，每次携带全部信息）。"""
    turn = "Black" if next_player(board) == BLACK else "White"
    you = "Black" if ai_player == BLACK else "White"
    last = idx_to_coord(*board.moves[-1][1]) if board.moves else "None"
    # 将上下文用结构化JSON嵌入，便于模型解析
    context = {
        "size": SIZE,
        "you_are": you,
        "turn": turn,
        "last_move": last,
        "moves": [
            {
                "player": ("B" if p == BLACK else "W"),
                "coord": idx_to_coord(r, c),
            }
            for p, (r, c) in board.moves
        ],
    }
    ctx_json = json.dumps(context, ensure_ascii=False)
    return (
        "下面给出完整对局上下文(JSON)。请基于该上下文选择下一步。\n"
        "要求：只能在空位落子，且坐标合法；只输出严格JSON {\"move\":\"<列行>\"}。\n"
        f"上下文: {ctx_json}"
    )

def build_messages_for_move(board: Board, ai_player: int) -> List[LLMMessage]:
    """构造一轮落子的对话消息（包含系统+用户，内含完整上下文）。"""
    return [
        LLMMessage(role="system", content=format_system_prompt()),
        LLMMessage(role="user", content=format_user_prompt(board, ai_player)),
    ]

def ask_ai_move_with_retry(board: Board, ai_player: int, retries: int = 2) -> Tuple[Optional[Tuple[int,int]], str]:
    """在无状态HTTP下，采用“每次携带上下文 + 错误纠正重试”的策略获取AI走子。

    返回：(rc, raw_text)，若rc为None表示最终仍未解析出有效走子。
    """
    messages = build_messages_for_move(board, ai_player)
    last_raw = ""
    for attempt in range(retries + 1):
        try:
            resp = llm_router.chat_completion(messages=messages, temperature=0.2, max_tokens=128)
            raw = resp.content or ""
            last_raw = raw
            mv = parse_move_from_json(raw)
            rc = coord_to_idx(mv) if mv else None
            # 校验合法性（坐标+空位）
            if rc and board.in_bounds(*rc) and board.cell(*rc) == EMPTY:
                return rc, raw
            # 将错误反馈回模型，并要求修正
            reason = "坐标非法或位置已被占用" if rc else "输出不是规定的严格JSON或坐标非法"
            messages.append(LLMMessage(role="assistant", content=raw))
            messages.append(LLMMessage(
                role="user",
                content=(
                    f"刚才的答案有误：{reason}。请基于相同上下文，重新输出严格JSON，"
                    f"只包含一个字段 move，例如 {{\"move\":\"H8\"}}。不要输出任何其他内容。"
                )
            ))
        except Exception as e:
            logger.error(f"LLM调用失败（第{attempt+1}次）：{e}")
            break
    return None, last_raw

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
            # AI走：每次携带完整上下文 + 失败纠正重试
            rc, raw = ask_ai_move_with_retry(b, ai_player, retries=2)
            logger.info(f"AI 输出：{raw}")
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
