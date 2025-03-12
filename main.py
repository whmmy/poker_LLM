# main.py
# 德州扑克AI对战框架的主程序入口

import argparse
import os
from typing import Optional,List
from ai_player import AIPlayer,LLMPlayer
from game_controller import GameController
from poker_engine import Player

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
        print(f"{i+1}. 游戏ID: {game_id}")
    
    print("\n使用 --replay 参数后跟游戏ID来重放游戏，例如: python main.py --replay 12345678")




"""
开始对局
args:
    players: 玩家列表
    hands: 要进行的手牌数量
    chips: 初始每一位玩家筹码数量
    small_blind: 小盲注金额
    big_blind: 大盲注金额;
"""
def start_game(players:List[AIPlayer], hands, chips, small_blind, big_blind):
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
    players = []
    # start_game
    pass