# main.py
# 德州扑克AI对战框架的主程序入口

import os
from typing import List

from ai_player import AIPlayer, OpenAiLLMUser, AnthropicLLMUser
from game_controller import GameController


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
    players = [
        OpenAiLLMUser(name="dsV3", model_name="deepseek-v3", api_key='USER_API_KEY', base_url="USER_BASE_URL"),
        OpenAiLLMUser(name="dsR1", model_name="deepseek-r1", api_key='USER_API_KEY', base_url="USER_BASE_URL"),
        OpenAiLLMUser(name="o3", model_name="o3-mini", api_key='USER_API_KEY', base_url="USER_BASE_URL"),
        OpenAiLLMUser(name="Gork", model_name="gork", api_key='USER_API_KEY', base_url="USER_BASE_URL"),
        AnthropicLLMUser(name="claude", model_name="claude-3-5", api_key='USER_API_KEY', base_url="USER_BASE_URL")
    ]
    start_game(players, hands=10, chips=1000, small_blind=5, big_blind=10)
