# poker_engine.py
# 德州扑克游戏引擎

import random
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from game_info import GameAction,GameInfoState


class Suit(Enum):
    """花色枚举"""
    SPADE = "♠"  # 黑桃
    HEART = "♥"  # 红桃
    CLUB = "♣"   # 梅花
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


class GameStage(Enum):
    """游戏阶段枚举"""
    PREFLOP = "preflop"  # 翻牌前
    FLOP = "flop"  # 翻牌
    TURN = "turn"  # 转牌
    RIVER = "river"  # 河牌
    SHOWDOWN = "showdown"  # 摊牌


class HandRank(Enum):
    """牌型大小枚举"""
    HIGH_CARD = 1  # 高牌
    ONE_PAIR = 2  # 一对
    TWO_PAIR = 3  # 两对
    THREE_OF_A_KIND = 4  # 三条
    STRAIGHT = 5  # 顺子
    FLUSH = 6  # 同花
    FULL_HOUSE = 7  # 葫芦
    FOUR_OF_A_KIND = 8  # 四条
    STRAIGHT_FLUSH = 9  # 同花顺
    ROYAL_FLUSH = 10  # 皇家同花顺


class Player:
    """玩家类"""
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        self.id = player_id
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
            "id": self.id,
            "name": self.name,
            "chips": self.chips,
            "hand": [str(card) for card in self.hand],
            "bet_in_round": self.bet_in_round,
            "total_bet": self.total_bet,
            "folded": self.folded,
            "all_in": self.all_in,
            "is_active": self.is_active
        }


class PokerTable:
    """德州扑克牌桌类"""
    def __init__(self, small_blind: int = 5, big_blind: int = 10, max_players: int = 10):
        self.players: List[Player] = []
        self.deck: List[Card] = []
        self.community_cards: List[Card] = []
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.max_players = max_players
        self.pot = 0  # 底池
        self.current_bet = 0  # 当前回合最高下注额
        self.dealer_position = 0  # 庄家位置
        self.current_player_idx = 0  # 当前行动玩家索引
        self.stage = GameStage.PREFLOP  # 当前游戏阶段
        self.hand_number = 0  # 当前是第几手牌
        self.action_history: List[GameAction] = []  # 行动历史
        self.game_log: List[Dict[str, Any]] = []  # 游戏日志
    
    def add_player(self, player: Player) -> bool:
        """添加玩家到牌桌"""
        if len(self.players) >= self.max_players:
            return False
        self.players.append(player)
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """从牌桌移除玩家"""
        for i, player in enumerate(self.players):
            if player.id == player_id:
                self.players.pop(i)
                return True
        return False
    
    def initialize_deck(self):
        """初始化一副牌"""
        self.deck = []
        for suit in Suit:
            for value in range(2, 15):  # 2-14 (2-A)
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)
    
    def deal_hole_cards(self):
        """发放底牌给每个玩家"""
        for _ in range(2):  # 每个玩家发2张底牌
            for player in self.players:
                if player.is_active and not player.folded:
                    player.receive_card(self.deck.pop())
    
    def deal_community_cards(self, count: int):
        """发放公共牌"""
        for _ in range(count):
            self.community_cards.append(self.deck.pop())
    
    def post_blinds(self):
        """下盲注"""
        if len(self.players) < 2:
            return
        
        # 确定小盲和大盲位置
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)
        
        # 下小盲注
        sb_player = self.players[sb_pos]
        sb_amount = sb_player.place_bet(self.small_blind)
        self.pot += sb_amount
        self.log_action(sb_player, Action.RAISE, sb_amount, "")
        
        # 下大盲注
        bb_player = self.players[bb_pos]
        bb_amount = bb_player.place_bet(self.big_blind)
        self.pot += bb_amount
        self.current_bet = self.big_blind
        self.log_action(bb_player, Action.RAISE, bb_amount, "")
        
        # 设置当前行动玩家为大盲注后的玩家
        self.current_player_idx = (bb_pos + 1) % len(self.players)
    
    def next_player(self) -> Optional[Player]:
        """获取下一个应该行动的玩家"""
        active_players = [p for p in self.players if p.is_active and not p.folded and not p.all_in]
        if not active_players:
            return None
        
        start_idx = self.current_player_idx
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            current_player = self.players[self.current_player_idx]
            if current_player.is_active and not current_player.folded and not current_player.all_in:
                return current_player
            if self.current_player_idx == start_idx:
                break
        return None
    
    def process_action(self, player: Player, action: Action, amount: int = 0, behavior: str = "") -> bool:
        """处理玩家行动"""
        if player.folded or not player.is_active or player.all_in:
            return False
        
        if action == Action.FOLD:
            player.folded = True
            self.log_action(player, action, 0, behavior)
            return True
        
        elif action == Action.CHECK:
            if self.current_bet > player.bet_in_round:
                return False  # 不能过牌，必须跟注或弃牌
            self.log_action(player, action, 0, behavior)
            return True
        
        elif action == Action.CALL:
            call_amount = min(self.current_bet - player.bet_in_round, player.chips)
            if call_amount <= 0:
                return False  # 没有可跟的注
            
            bet_amount = player.place_bet(call_amount)
            self.pot += bet_amount
            self.log_action(player, action, bet_amount, behavior)
            return True
        
        elif action == Action.RAISE:
            min_raise = self.current_bet * 2
            if amount < min_raise or amount > player.chips:
                return False  # 加注金额无效
            
            bet_amount = player.place_bet(amount)
            self.pot += bet_amount
            self.current_bet = player.bet_in_round
            self.log_action(player, action, bet_amount, behavior)
            return True
        
        elif action == Action.ALL_IN:
            bet_amount = player.place_bet(player.chips)
            self.pot += bet_amount
            if player.bet_in_round > self.current_bet:
                self.current_bet = player.bet_in_round
            self.log_action(player, action, bet_amount, behavior)
            return True
        
        return False
    
    def log_action(self, player: Player, action: Action, amount: int = 0, behavior: str = ""):
        """记录玩家行动"""
        gameAction = GameAction(
            hand_number=self.hand_number,
            stage= self.stage,
            player_id= player.id,
            player_name= player.name,
            action= action,
            amount= amount,
            pot=self.pot,
            player_chips= player.chips,
            behavior=behavior
        )
        self.action_history.append(gameAction)
    
    def is_round_complete(self) -> bool:
        """检查当前回合是否结束"""
        active_players = [p for p in self.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            return True  # 只剩一个玩家，回合结束
        
        # 检查所有未弃牌的玩家是否都已经行动并且下注相等或全押
        bet_amounts = set()
        for player in active_players:
            if player.all_in:
                continue  # 全押玩家不需要下注相等
            bet_amounts.add(player.bet_in_round)
        
        return len(bet_amounts) <= 1  # 如果所有玩家下注相等或全押，回合结束
    
    def move_to_next_stage(self):
        """进入下一个游戏阶段"""
        # 重置玩家当前回合下注
        for player in self.players:
            player.bet_in_round = 0
        self.current_bet = 0
        
        # 根据当前阶段进入下一阶段
        if self.stage == GameStage.PREFLOP:
            self.stage = GameStage.FLOP
            self.deal_community_cards(3)  # 发放3张翻牌
        elif self.stage == GameStage.FLOP:
            self.stage = GameStage.TURN
            self.deal_community_cards(1)  # 发放1张转牌
        elif self.stage == GameStage.TURN:
            self.stage = GameStage.RIVER
            self.deal_community_cards(1)  # 发放1张河牌
        elif self.stage == GameStage.RIVER:
            self.stage = GameStage.SHOWDOWN
            self.showdown()  # 进行摊牌
        
        # 设置行动顺序，从庄家后第一个玩家开始
        if len(self.players) > 0:
            self.current_player_idx = (self.dealer_position + 1) % len(self.players)
    
    def evaluate_hand(self, player: Player) -> Tuple[HandRank, List[int]]:
        """评估玩家的最佳牌型"""
        all_cards = player.hand + self.community_cards
        return self.find_best_hand(all_cards)
    
    def find_best_hand(self, cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """从给定的牌中找出最佳牌型"""
        # 检查是否有皇家同花顺
        royal_flush = self.check_royal_flush(cards)
        if royal_flush:
            return (HandRank.ROYAL_FLUSH, royal_flush)
        
        # 检查是否有同花顺
        straight_flush = self.check_straight_flush(cards)
        if straight_flush:
            return (HandRank.STRAIGHT_FLUSH, straight_flush)
        
        # 检查是否有四条
        four_of_a_kind = self.check_four_of_a_kind(cards)
        if four_of_a_kind:
            return (HandRank.FOUR_OF_A_KIND, four_of_a_kind)
        
        # 检查是否有葫芦
        full_house = self.check_full_house(cards)
        if full_house:
            return (HandRank.FULL_HOUSE, full_house)
        
        # 检查是否有同花
        flush = self.check_flush(cards)
        if flush:
            return (HandRank.FLUSH, flush)
        
        # 检查是否有顺子
        straight = self.check_straight(cards)
        if straight:
            return (HandRank.STRAIGHT, straight)
        
        # 检查是否有三条
        three_of_a_kind = self.check_three_of_a_kind(cards)
        if three_of_a_kind:
            return (HandRank.THREE_OF_A_KIND, three_of_a_kind)
        
        # 检查是否有两对
        two_pair = self.check_two_pair(cards)
        if two_pair:
            return (HandRank.TWO_PAIR, two_pair)
        
        # 检查是否有一对
        one_pair = self.check_one_pair(cards)
        if one_pair:
            return (HandRank.ONE_PAIR, one_pair)
        
        # 高牌
        high_card = self.check_high_card(cards)
        return (HandRank.HIGH_CARD, high_card)
    
    def check_royal_flush(self, cards: List[Card]) -> List[int]:
        """检查是否有皇家同花顺"""
        for suit in Suit:
            suit_cards = [card for card in cards if card.suit == suit]
            if len(suit_cards) >= 5:
                values = [card.value for card in suit_cards]
                if all(v in values for v in [10, 11, 12, 13, 14]):
                    return [14, 13, 12, 11, 10]  # A, K, Q, J, 10
        return []
    
    def check_straight_flush(self, cards: List[Card]) -> List[int]:
        """检查是否有同花顺"""
        for suit in Suit:
            suit_cards = [card for card in cards if card.suit == suit]
            if len(suit_cards) >= 5:
                values = sorted([card.value for card in suit_cards], reverse=True)
                # 检查A-5顺子
                if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
                    return [5, 4, 3, 2, 1]  # 5高顺子
                
                # 检查常规顺子
                for i in range(len(values) - 4):
                    if values[i] - values[i+4] == 4 and len(set(values[i:i+5])) == 5:
                        return values[i:i+5]
        return []
    
    def check_four_of_a_kind(self, cards: List[Card]) -> List[int]:
        """检查是否有四条"""
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        
        quads = [v for v, count in value_count.items() if count == 4]
        if quads:
            quad = max(quads)
            kickers = [v for v in value_count.keys() if v != quad]
            kickers.sort(reverse=True)
            return [quad] * 4 + [kickers[0] if kickers else 0]
        return []
    
    def check_full_house(self, cards: List[Card]) -> List[int]:
        """检查是否有葫芦"""
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        
        trips = [v for v, count in value_count.items() if count >= 3]
        pairs = [v for v, count in value_count.items() if count >= 2]
        
        if trips and pairs:
            best_trip = max(trips)
            pairs = [p for p in pairs if p != best_trip]
            if pairs:
                best_pair = max(pairs)
                return [best_trip] * 3 + [best_pair] * 2
            elif len([v for v, count in value_count.items() if count >= 3 and v != best_trip]) > 0:
                second_trip = max([v for v, count in value_count.items() if count >= 3 and v != best_trip])
                return [best_trip] * 3 + [second_trip] * 2
        return []
    
    def check_flush(self, cards: List[Card]) -> List[int]:
        """检查是否有同花"""
        for suit in Suit:
            suit_cards = [card for card in cards if card.suit == suit]
            if len(suit_cards) >= 5:
                values = sorted([card.value for card in suit_cards], reverse=True)
                return values[:5]
        return []
    
    def check_straight(self, cards: List[Card]) -> List[int]:
        """检查是否有顺子"""
        values = sorted(set(card.value for card in cards), reverse=True)
        
        # 检查A-5顺子
        if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
            return [5, 4, 3, 2, 1]  # 5高顺子
        
        # 检查常规顺子
        for i in range(len(values) - 4):
            if values[i] - values[i+4] == 4 and len(set(values[i:i+5])) == 5:
                return values[i:i+5]
        return []
    
    def check_three_of_a_kind(self, cards: List[Card]) -> List[int]:
        """检查是否有三条"""
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        
        trips = [v for v, count in value_count.items() if count == 3]
        if trips:
            trip = max(trips)
            kickers = [v for v in value_count.keys() if v != trip]
            kickers.sort(reverse=True)
            return [trip] * 3 + kickers[:2]
        return []
    
    def check_two_pair(self, cards: List[Card]) -> List[int]:
        """检查是否有两对"""
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        
        pairs = [v for v, count in value_count.items() if count == 2]
        if len(pairs) >= 2:
            pairs.sort(reverse=True)
            top_pairs = pairs[:2]
            kickers = [v for v in value_count.keys() if v not in top_pairs]
            kickers.sort(reverse=True)
            return [top_pairs[0]] * 2 + [top_pairs[1]] * 2 + [kickers[0] if kickers else 0]
        return []
    
    def check_one_pair(self, cards: List[Card]) -> List[int]:
        """检查是否有一对"""
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        
        pairs = [v for v, count in value_count.items() if count == 2]
        if pairs:
            pair = max(pairs)
            kickers = [v for v in value_count.keys() if v != pair]
            kickers.sort(reverse=True)
            return [pair] * 2 + kickers[:3]
        return []
    
    def check_high_card(self, cards: List[Card]) -> List[int]:
        """返回高牌"""
        values = sorted([card.value for card in cards], reverse=True)
        return values[:5]
    
    def compare_hands(self, hand1: Tuple[HandRank, List[int]], hand2: Tuple[HandRank, List[int]]) -> int:
        """比较两手牌的大小，返回1表示hand1大，-1表示hand2大，0表示相等"""
        rank1, values1 = hand1
        rank2, values2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        
        # 牌型相同，比较牌值
        for v1, v2 in zip(values1, values2):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        
        return 0  # 完全相同
    
    def showdown(self):
        """摊牌并确定赢家"""
        active_players = [p for p in self.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            # 只有一个玩家，直接获胜
            winner = active_players[0]
            self.award_pot([winner])
            return
        
        # 评估每个玩家的牌型
        player_hands = {}
        for player in active_players:
            player_hands[player.id] = self.evaluate_hand(player)
        
        # 找出最佳牌型的玩家
        best_players = []
        best_hand = None
        
        for player in active_players:
            hand = player_hands[player.id]
            if not best_hand or self.compare_hands(hand, best_hand) > 0:
                best_hand = hand
                best_players = [player]
            elif self.compare_hands(hand, best_hand) == 0:
                best_players.append(player)
        
        # 记录摊牌结果
        showdown_record = {
            "hand_number": self.hand_number,
            "community_cards": [str(card) for card in self.community_cards],
            "players": []
        }
        
        for player in active_players:
            player_record = {
                "player_id": player.id,
                "player_name": player.name,
                "hand": [str(card) for card in player.hand],
                "hand_rank": player_hands[player.id][0].name,
                "is_winner": player in best_players
            }
            showdown_record["players"].append(player_record)
        
        self.game_log.append(showdown_record)
        
        # 分配奖池
        self.award_pot(best_players)
    
    def award_pot(self, winners: List[Player]):
        """将奖池分配给赢家"""
        if not winners:
            return
        
        # 平分奖池
        award_per_player = self.pot // len(winners)
        remainder = self.pot % len(winners)
        
        for player in winners:
            player.chips += award_per_player
        
        # 将余数给第一个玩家
        if remainder > 0 and winners:
            winners[0].chips += remainder
        
        # 记录奖池分配
        pot_award_record = {
            "hand_number": self.hand_number,
            "pot": self.pot,
            "winners": [{
                "player_id": player.id,
                "player_name": player.name,
                "amount": award_per_player + (remainder if player == winners[0] else 0)
            } for player in winners]
        }
        
        self.game_log.append(pot_award_record)
        self.pot = 0
    
    def start_new_hand(self):
        """开始新的一手牌"""
        # 移动庄家位置
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.hand_number += 1
        
        # 重置牌桌状态
        self.pot = 0
        self.current_bet = 0
        self.community_cards = []
        self.stage = GameStage.PREFLOP
        
        # 重置玩家状态
        for player in self.players:
            player.reset_for_new_hand()
        
        # 初始化牌组并洗牌
        self.initialize_deck()
        
        # 下盲注
        self.post_blinds()
        
        # 发底牌
        self.deal_hole_cards()
        
        # 记录新一手牌开始
        hand_start_record = {
            "hand_number": self.hand_number,
            "dealer": self.dealer_position,
            "small_blind": self.small_blind,
            "big_blind": self.big_blind,
            "players": [player.to_dict() for player in self.players]
        }
        self.game_log.append(hand_start_record)
    
    def play_hand(self):
        """进行一手牌的游戏"""
        # 开始新的一手牌
        self.start_new_hand()
        
        # 进行翻牌前的下注
        self.play_betting_round()
        
        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.award_pot(active_players)
            return
        
        # 进行翻牌
        self.move_to_next_stage()  # 进入翻牌阶段
        self.play_betting_round()
        
        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.award_pot(active_players)
            return
        
        # 进行转牌
        self.move_to_next_stage()  # 进入转牌阶段
        self.play_betting_round()
        
        # 如果只剩一个玩家，直接结束
        active_players = [p for p in self.players if p.is_active and not p.folded]
        if len(active_players) <= 1:
            self.award_pot(active_players)
            return
        
        # 进行河牌
        self.move_to_next_stage()  # 进入河牌阶段
        self.play_betting_round()
        
        # 进行摊牌
        self.move_to_next_stage()  # 进入摊牌阶段
    
    def play_betting_round(self):
        """进行一轮下注"""
        # 如果只有一个或没有玩家，直接结束
        active_players = [p for p in self.players if p.is_active and not p.folded and not p.all_in]
        if len(active_players) <= 1:
            return
        
        # 记录当前阶段开始
        stage_start_record = {
            "hand_number": self.hand_number,
            "stage": self.stage.value,
            "community_cards": [str(card) for card in self.community_cards]
        }
        self.game_log.append(stage_start_record)
        
        # 玩家轮流行动，直到回合结束
        first_action = True
        while not self.is_round_complete():
            # 获取下一个行动的玩家
            if first_action and self.stage != GameStage.PREFLOP:
                # 翻牌后从庄家后第一个玩家开始
                self.current_player_idx = (self.dealer_position + 1) % len(self.players)
                first_action = False
            
            current_player = self.next_player()
            if not current_player:
                break  # 没有可行动的玩家，结束回合
            
            # 这里应该由AI决策引擎决定行动，暂时用随机行动代替
            action, amount = self.get_player_action(current_player)
            
            # 处理玩家行动
            self.process_action(current_player, action, amount)
    
    def get_player_action(self, player: Player) -> Tuple[Action, int]:
        """获取玩家行动，这里应该由AI决策引擎实现"""
        # 临时使用随机行动，实际应该由AI决策引擎实现
        available_actions = []
        
        # 检查可用行动
        if self.current_bet == 0 or self.current_bet == player.bet_in_round:
            available_actions.append(Action.CHECK)
        
        if self.current_bet > player.bet_in_round:
            available_actions.append(Action.CALL)
        
        available_actions.append(Action.FOLD)
        available_actions.append(Action.RAISE)
        available_actions.append(Action.ALL_IN)
        
        # 随机选择一个行动
        action = random.choice(available_actions)
        
        # 根据行动确定金额
        amount = 0
        if action == Action.CALL:
            amount = self.current_bet - player.bet_in_round
        elif action == Action.RAISE:
            min_raise = self.current_bet * 2
            amount = min(min_raise, player.chips)
        elif action == Action.ALL_IN:
            amount = player.chips
        
        return action, amount
    
    def save_game_log(self, filename: str):
        """保存游戏日志到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, ensure_ascii=False, indent=2)
    
    def load_game_log(self, filename: str) -> bool:
        """从文件加载游戏日志"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.game_log = json.load(f)
            return True
        except Exception as e:
            print(f"加载游戏日志失败: {e}")
            return False
    
    def replay_game(self):
        """根据游戏日志重放游戏"""
        if not self.game_log:
            print("没有游戏日志可供重放")
            return
        
        print("开始重放游戏...")
        for record in self.game_log:
            if "stage" in record:
                # 阶段记录
                print(f"\n阶段: {record['stage']}")
                if "community_cards" in record:
                    print(f"公共牌: {', '.join(record['community_cards'])}")
            
            elif "action" in record:
                # 行动记录
                print(f"玩家 {record['player_name']} 执行 {record['action']}")
                if record['amount'] > 0:
                    print(f"金额: {record['amount']}")
                print(f"底池: {record['pot']}")
            
            elif "players" in record and "community_cards" in record:
                # 摊牌记录
                print("\n摊牌:")
                print(f"公共牌: {', '.join(record['community_cards'])}")
                for player in record["players"]:
                    winner_mark = "(赢家)" if player.get("is_winner", False) else ""
                    print(f"玩家 {player['player_name']} {winner_mark}")
                    print(f"手牌: {', '.join(player['hand'])}")
                    print(f"牌型: {player['hand_rank']}")
            
            elif "winners" in record:
                # 奖池分配记录
                print("\n奖池分配:")
                print(f"底池: {record['pot']}")
                for winner in record["winners"]:
                    print(f"玩家 {winner['player_name']} 获得 {winner['amount']} 筹码")
            
            elif "dealer" in record:
                # 新一手牌开始记录
                print(f"\n新一手牌 #{record['hand_number']}")
                print(f"庄家位置: {record['dealer']}")
                print(f"小盲: {record['small_blind']}, 大盲: {record['big_blind']}")
                print("玩家筹码:")
                for player in record["players"]:
                    print(f"玩家 {player['name']}: {player['chips']} 筹码")
            
            # 暂停一下，便于观察
            input("按Enter键继续...")