# game_controller.py
# 德州扑克游戏控制器，用于管理多个AI玩家之间的对战

import os
import time
import uuid
from typing import List, Dict, Any, Optional
from poker_engine import PokerTable, Player, GameStage, Action
from ai_player import AIPlayer, LLMPlayer
from game_info import GameInfoState


class GameController:
    """德州扑克游戏控制器，管理多个AI玩家之间的对战"""

    def __init__(self, small_blind: int = 5, big_blind: int = 10, initial_chips: int = 1000):
        self.table = PokerTable(small_blind=small_blind, big_blind=big_blind)
        self.ai_players: List[AIPlayer] = []
        self.initial_chips = initial_chips
        self.game_id = str(uuid.uuid4())[:8]  # 生成一个唯一的游戏ID
        self.log_dir = "game_logs"

        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def add_player(self, ai_player: AIPlayer) -> bool:
        """添加AI玩家到游戏"""
        if len(self.ai_players) >= self.table.max_players:
            return False
        self.ai_players.append(ai_player)
        return self.table.add_player(ai_player.player)

    def prepare_game_state(self, current_player: Player) -> GameInfoState:
        """准备当前游戏状态信息，用于AI决策"""
        # 找出当前玩家在牌桌中的位置
        position = -1
        for i, player in enumerate(self.table.players):
            if player.name == current_player.name:
                position = i
                break

        # 准备其他玩家信息
        players_info = []
        # for player in self.table.players:
        # 对于其他玩家，不显示手牌
        # player_info = player.to_dict()
        # if player.name != current_player.name:
        #     player_info["hand"] = ["??", "??"]
        # players_info.append(player_info)

        # 获取当前对局的行动历史
        recent_actions = [action for action in self.table.action_history if
                          action.hand_number == self.table.hand_number]
        # 计算最小加注额
        min_raise = max(self.table.big_blind, self.table.current_bet * 2)
        game_state = GameInfoState(
            hand=current_player.hand,
            community_cards=self.table.community_cards,
            pot=self.table.pot,
            current_bet=self.table.current_bet,
            min_raise=min_raise,
            stage=self.table.stage,
            players_info=self.table.players,
            position=position,
            dealer_position=self.table.dealer_position,
            action_history=recent_actions,
            small_blind=self.table.small_blind,
            big_blind=self.table.big_blind,
            hand_num=self.table.hand_number
        )

        return game_state

    def run_hand(self, verbose: bool = True):
        """运行一手牌"""
        # 开始新的一手牌
        self.table.start_new_hand()

        if verbose:
            print(f"\n开始第 {self.table.hand_number} 手牌")
            print(f"庄家位置: {self.table.dealer_position}")
            print("玩家信息:")
            for player in self.table.players:
                print(f"{player.name}:\n 手牌:{', '.join(str(card) for card in player.hand)}, 筹码:{player.chips}")

        # 进行翻牌前的下注
        self.run_betting_round(verbose)

        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.table.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.table.award_pot(active_players)
            return

        # 进行翻牌
        self.table.move_to_next_stage()  # 进入翻牌阶段
        if verbose:
            print(f"在场玩家：{', '.join(f'{p.name}, 筹码:{p.chips}' for p in active_players)}")
            print(f"\n翻牌: {', '.join(str(card) for card in self.table.community_cards)}")
        self.run_betting_round(verbose)

        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.table.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.table.award_pot(active_players)
            return

        # 进行转牌
        self.table.move_to_next_stage()  # 进入转牌阶段
        if verbose:
            print(f"在场玩家：{', '.join(f'{p.name}, 筹码:{p.chips}' for p in active_players)}")
            print(f"\n转牌: {', '.join(str(card) for card in self.table.community_cards)}")
        self.run_betting_round(verbose)

        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.table.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.table.award_pot(active_players)
            return

        # 进行河牌
        self.table.move_to_next_stage()  # 进入河牌阶段
        if verbose:
            print(f"在场玩家：{', '.join(f'{p.name}, 筹码:{p.chips}' for p in active_players)}")
            print(f"\n河牌: {', '.join(str(card) for card in self.table.community_cards)}")
        self.run_betting_round(verbose)

        # 进行摊牌
        self.table.move_to_next_stage()  # 进入摊牌阶段

        # 显示摊牌结果
        if verbose:
            active_players = [p for p in self.table.players if p.is_active and not p.folded]
            print("\n摊牌:")
            for player in active_players:
                print(f"在场玩家：{', '.join(f'{p.name}, 筹码:{p.chips}' for p in active_players)}")
                print(f"  {player.name}: {', '.join(str(card) for card in player.hand)}\n")
            print(f"公共牌: {', '.join(str(card) for card in self.table.community_cards)}")

    def run_betting_round(self, verbose: bool = True):
        """运行一轮下注"""
        # 如果只有一个或没有玩家，直接结束
        active_players = [p for p in self.table.players if p.is_active and not p.folded and not p.all_in]
        if len(active_players) <= 1:
            return

        # 记录当前阶段开始
        if verbose:
            print(f"\n开始 {self.table.stage.value} 阶段下注")

        # 玩家轮流行动，直到回合结束
        first_action = True
        while not self.table.is_round_complete():
            # 获取下一个行动的玩家
            if first_action:
                if self.table.stage == GameStage.PREFLOP:
                    # 翻牌前从大盲注后的玩家开始
                    bb_pos = (self.table.dealer_position + 2) % len(self.table.players)
                    self.table.current_player_idx = bb_pos  # 修改：不要+1，因为next_player会+1
                    print(f'翻牌前下注,从{(bb_pos + 1) % len(self.table.players)}开始')
                else:
                    # 翻牌后从庄家后第一个玩家开始
                    self.table.current_player_idx = self.table.dealer_position  # 修改：不要+1，因为next_player会+1
                first_action = False

            current_player = self.table.next_player()
            if not current_player:
                break  # 没有可行动的玩家，结束回合

            # 找到对应的AI玩家
            ai_player = next((ai for ai in self.ai_players if ai.player.name == current_player.name), None)
            if not ai_player:
                continue  # 找不到对应的AI玩家，跳过

            # 准备游戏状态
            game_state = self.prepare_game_state(current_player)

            # 获取AI决策
            playerAction = ai_player.make_decision(game_state)

            # 处理玩家行动
            success = self.table.process_action(current_player, playerAction.action, playerAction.amount,
                                                playerAction.behavior)

            if verbose:
                action_str = f"{current_player.name} 选择 {playerAction.action.value}"
                if playerAction.action in [Action.CALL, Action.RAISE, Action.ALL_IN]:
                    action_str += f" {playerAction.amount}"
                print(f"  {action_str}")
                if playerAction.behavior:
                    print(f" 他的表现: {playerAction.behavior}")
                print(f'理由是：{playerAction.play_reason}')
                print(f"  底池: {self.table.pot}")

    def run_tournament(self, num_hands: int = 100, verbose: bool = True):
        """运行一场锦标赛"""
        if len(self.ai_players) < 2:
            print("至少需要2名玩家才能开始游戏")
            return

        # 为玩家设置相同的初始筹码
        for p in self.ai_players:
            p.player.chips = self.initial_chips
        start_time = time.time()

        if verbose:
            print(f"开始德州扑克锦标赛 (游戏ID: {self.game_id})")
            print(f"参赛玩家: {', '.join(ai.name for ai in self.ai_players)}")
            print(f"初始筹码: {self.initial_chips}")
            print(f"盲注结构: 小盲 {self.table.small_blind}, 大盲 {self.table.big_blind}")
            print(f"计划进行 {num_hands} 手牌\n")

        # 运行指定数量的牌局
        for i in range(num_hands):
            # 检查是否只剩一名玩家
            active_players = [p for p in self.table.players if p.is_active]
            if len(active_players) <= 1:
                if verbose:
                    if active_players:
                        print(f"\n游戏结束! {active_players[0].name} 获胜!")
                    else:
                        print("\n游戏结束! 没有玩家剩余。")
                break

            # 运行一手牌
            self.run_hand(verbose)
            # 添加当局游戏结果汇报
            if verbose:
                print(f"\n第 {i + 1} 手牌结束")
                game_result = self.table.game_result_log.get(i + 1)
                print(game_result.get_result_info())

            # 按照上一局的运行结果各个active_players进行反思
            self.handle_reflection()
            # 每10手牌保存一次日志
            if i % 10 == 0:
                self.save_game_log()

        # 保存最终游戏日志
        self.save_game_log()

        # 显示最终结果
        if verbose:
            print("\n锦标赛结束!")
            print("最终排名:")
            sorted_players = sorted(self.table.players, key=lambda p: p.chips, reverse=True)
            for i, player in enumerate(sorted_players):
                print(f"{i + 1}. {player.name}: {player.chips} 筹码")

            print(f"\n游戏用时: {time.time() - start_time:.2f} 秒")
            print(f"游戏日志已保存到: {self.get_log_filename()}")

    def get_log_filename(self) -> str:
        """获取日志文件名"""
        return os.path.join(self.log_dir, f"poker_game_{self.game_id}.json")

    def save_game_log(self):
        """保存游戏日志"""
        self.table.save_game_log(self.get_log_filename())

    def replay_game(self, game_id: Optional[str] = None):
        """重放游戏"""
        if game_id:
            filename = os.path.join(self.log_dir, f"poker_game_{game_id}.json")
        else:
            filename = self.get_log_filename()

        if not os.path.exists(filename):
            print(f"找不到游戏日志文件: {filename}")
            return

        # 加载游戏日志
        self.table.load_game_log(filename)

        # 重放游戏
        self.table.replay_game()

    def handle_reflection(self):
        game_result = self.table.game_result_log[self.table.hand_number]
        for p in self.ai_players:
            if p.player.is_active:
                p.reflect_on_game(self.prepare_game_state(p.player), game_result)
