# main.py
# 德州扑克AI对战框架的主程序入口

import os
from typing import List
from dotenv import load_dotenv

from ai_player import AIPlayer, OpenAiLLMUser, AnthropicLLMUser
from game_controller import GameController

# 加载环境变量
load_dotenv()


def list_games():
    """列出所有已保存的游戏"""
    log_dir = "game_logs"
    if not os.path.exists(log_dir):
        print("没有找到任何已保存的游戏")
        return

    game_files = [f for f in os.listdir(log_dir) if f.startswith("poker_game_") and f.endswith(".json")]
    if not game_files:
        print("没有找到任何已保存的游戏")
        return

    print("已保存的游戏列表:")
    for i, file in enumerate(game_files):
        game_id = file.replace("poker_game_", "").replace(".json", "")
        print(f"{i + 1}. 游戏ID: {game_id}")


"""
开始对局
args:
    players: 玩家列表
    hands: 要进行的手牌数量
    chips: 初始每一位玩家筹码数量
    small_blind: 小盲注金额
    big_blind: 大盲注金额;
"""


def start_game(players: List[AIPlayer], hands, chips, small_blind, big_blind):
    """开始新的游戏"""
    controller = GameController(
        small_blind=small_blind,
        big_blind=big_blind,
        initial_chips=chips
    )
    for player in players:
        controller.add_player(player)

    controller.run_tournament(num_hands=hands, verbose=True)


if __name__ == "__main__":
    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

    # 游戏配置
    initial_chips = int(os.getenv("INITIAL_CHIPS", "1000"))
    small_blind = int(os.getenv("SMALL_BLIND", "5"))
    big_blind = int(os.getenv("BIG_BLIND", "10"))
    num_hands = int(os.getenv("NUM_HANDS", "10"))

    # 验证必要的环境变量
    if not openai_api_key and not anthropic_api_key:
        raise ValueError("请至少配置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")

    # 配置玩家 - 根据实际拥有的 API 密钥来配置
    players = []

    # OpenAI 兼容接口玩家示例 (DeepSeek, QWen, Gork 等)
    if openai_api_key:
        players.extend([
            OpenAiLLMUser(name="DeepSeek-V3", model_name="deepseek-v3",
                         api_key=openai_api_key, base_url=openai_base_url),
            OpenAiLLMUser(name="DeepSeek-R1", model_name="deepseek-r1",
                         api_key=openai_api_key, base_url=openai_base_url),
            # 可根据需要添加更多玩家
            # OpenAiLLMUser(name="QWen", model_name="qwen-plus",
            #              api_key=openai_api_key, base_url=openai_base_url),
        ])

    # Anthropic Claude 玩家示例
    if anthropic_api_key:
        players.append(
            AnthropicLLMUser(name="Claude", model_name="claude-3-5-sonnet-20241022",
                           api_key=anthropic_api_key, base_url=anthropic_base_url)
        )

    if not players:
        raise ValueError("请至少配置一个 AI 玩家")

    start_game(players, hands=num_hands, chips=initial_chips,
               small_blind=small_blind, big_blind=big_blind)
