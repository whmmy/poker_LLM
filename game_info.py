from dataclasses import dataclass, field
from engine_info import Card,Action,GameStage,Player
from typing import List, Dict, Optional

import prompts



@dataclass
class GameAction:
    """游戏动作"""
    hand_number: int = 0
    stage:GameStage = GameStage.PREFLOP
    player_name: str = ''
    action: Action = Action.CHECK
    amount: int = 0
    pot: int = 0
    player_chips: int = 0
    behavior:str = ''



@dataclass
class GameInfoState:
    """游戏状态信息 用于给ai进行决策用的基础信息"""
    hand: List[Card] = field(default_factory=list)
    community_cards: List[Card] = field(default_factory=list)
    pot: int = 0
    current_bet: int = 0
    min_raise: int = 0
    stage: GameStage = GameStage.PREFLOP
    players_info: List[Player] = field(default_factory=list)
    position: Optional[int] = 0
    dealer_position: Optional[int] = 0
    action_history:List[GameAction] = field(default_factory=list)
    small_blind:int=0
    big_blind:int=0
    hand_num:int=0
    
    def get_common_game_info(self):
        return f"""
        - 当前是第{self.hand_num}轮
        - 小盲/大盲:{self.small_blind}/{self.big_blind}
        - 公共牌：{', '.join(str(card) for card in self.community_cards) if self.community_cards else '暂无'}
        - 当前阶段：{self.stage.value}
        - 底池：{self.pot}
        - 当前最高下注：{self.current_bet}
        - 最小加注额：{self.min_raise}
        - 庄家位置：{self.dealer_position}
        """

    def get_simple_game_info(self):
       return f"""
        - 当前是第{self.hand_num}轮
        - 小盲/大盲:{self.small_blind}/{self.big_blind}
        - 公共牌：{', '.join(str(card) for card in self.community_cards) if self.community_cards else '暂无'}
        - 当前阶段：{self.stage.value}
        - 庄家位置：{self.dealer_position}
        """ 

@dataclass
class GamePlayerAction:
    action: Action = Action.FOLD
    amount: int = 0
    play_reason: str = ''
    behavior:str=''

@dataclass
class GameWinnerInfo:
    player_name: str =''
    amount:int = 0
    hand:List[Card] = field(default_factory=list)

@dataclass
class GameResult:
    hand_number:int = 0
    pot:int = 0
    community_cards:List[Card] = field(default_factory=list)
    winners:List[GameWinnerInfo] = field(default_factory=list)

    def get_result_info(self):
        prompt = f"""
        - 最终底池：{self.pot}
        获胜玩家:\n
        """
        for winner in self.winners:
            prompt += f'''
                玩家 {winner.player_name} 获胜，赢得筹码:{winner.amount},手牌信息为：{', '.join(str(card) for card in winner.hand)} \n
            '''