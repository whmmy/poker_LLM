from dataclasses import dataclass, field
from poker_engine import Player, Card, GameStage,Action
from typing import List, Dict, Optional



@dataclass
class GameAction:
    """游戏动作"""
    hand_number: int = 0
    stage:GameStage = GameStage.PREFLOP
    player_id: str = ''
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
    players_info: Optional[List[Player]] = None
    position: Optional[int] = 0
    dealer_position: Optional[int] = 0
    action_history:Optional[List[GameAction]] = []
    
