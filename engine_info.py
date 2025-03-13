from enum import Enum
from typing import List, Dict, Any, Tuple, Optional

class Suit(Enum):
    """花色枚举"""
    SPADE = "♠"  # 黑桃
    HEART = "♥"  # 红桃
    CLUB = "♣"  # 梅花
    DIAMOND = "♦"  # 方块


class Card:
    """扑克牌类"""

    def __init__(self, suit: Suit, value: int):
        self.suit = suit
        self.value = value  # 2-14, 其中11=J, 12=Q, 13=K, 14=A

    def __str__(self):
        value_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        value_str = value_map.get(self.value, str(self.value))
        return f"{self.suit.value}{value_str}"

    def __repr__(self):
        return self.__str__()


class Action(Enum):
    """玩家行动枚举"""
    FOLD = "fold"  # 弃牌
    CHECK = "check"  # 过牌
    CALL = "call"  # 跟注
    RAISE = "raise"  # 加注
    ALL_IN = "all-in"  # 全押
    BIG_BLIND = "big-blind"  # 大盲注
    SMALL_BLIND = "small-blind"  # 小盲注


class GameStage(Enum):
    """游戏阶段枚举"""
    PREFLOP = "preflop"  # 翻牌前
    FLOP = "flop"  # 翻牌
    TURN = "turn"  # 转牌
    RIVER = "river"  # 河牌
    SHOWDOWN = "showdown"  # 摊牌


class Player:
    """玩家类"""

    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.bet_in_round = 0  # 当前回合已下注额
        self.total_bet = 0  # 当前牌局总下注额
        self.folded = False  # 是否弃牌
        self.all_in = False  # 是否全押
        self.is_active = True  # 是否还在游戏中

    def reset_for_new_hand(self):
        """为新的一手牌重置状态"""
        self.hand = []
        self.bet_in_round = 0
        self.total_bet = 0
        self.folded = False
        self.all_in = False
        self.is_active = self.chips > 0

    def receive_card(self, card: Card):
        """接收一张牌"""
        self.hand.append(card)

    def place_bet(self, amount: int) -> int:
        """下注"""
        amount = min(amount, self.chips)
        self.chips -= amount
        self.bet_in_round += amount
        self.total_bet += amount
        if self.chips == 0:
            self.all_in = True
        return amount

    def to_dict(self) -> Dict[str, Any]:
        """将玩家信息转换为字典，用于记录和显示"""
        return {
            "name": self.name,
            "chips": self.chips,
            "hand": [str(card) for card in self.hand],
            "bet_in_round": self.bet_in_round,
            "total_bet": self.total_bet,
            "folded": self.folded,
            "all_in": self.all_in,
            "is_active": self.is_active
        }