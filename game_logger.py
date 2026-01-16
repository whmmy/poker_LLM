# game_logger.py
# 增强的游戏日志系统，用于支持web端对局复现和展示模型思考过程

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from engine_info import Card, Action, GameStage


@dataclass
class PlayerInfo:
    """玩家信息"""
    name: str
    model_name: str = ""  # LLM模型名称
    chips: int = 0
    hand: List[str] = field(default_factory=list)
    bet_in_round: int = 0
    total_bet: int = 0
    folded: bool = False
    all_in: bool = False
    is_active: bool = True


@dataclass
class LLMDecisionLog:
    """LLM决策日志"""
    player_name: str
    model_name: str
    hand_number: int
    stage: str
    timestamp: str

    # 输入信息
    prompt: str  # 发送给LLM的完整prompt
    game_state: Dict[str, Any]  # 当时的游戏状态

    # 输出信息
    raw_response: str  # LLM的原始响应
    reasoning_content: str = ""  # 推理内容（如果模型支持，如DeepSeek-R1）
    parsed_action: str = ""  # 解析后的行动
    action_amount: int = 0  # 行动金额
    play_reason: str = ""  # 决策理由
    behavior: str = ""  # 行为描述

    # 元信息
    response_time: float = 0.0  # 响应时间（秒）
    error: str = ""  # 错误信息（如果有）


@dataclass
class LLMReflectionLog:
    """LLM反思日志"""
    player_name: str
    model_name: str
    hand_number: int
    timestamp: str

    # 输入信息
    prompt: str  # 发送给LLM的完整prompt
    game_result: str  # 游戏结果描述

    # 输出信息
    raw_response: str  # LLM的原始响应
    updated_opinions: Dict[str, str] = field(default_factory=dict)  # 更新后的对其他玩家的评估


@dataclass
class GameEventLog:
    """游戏事件日志（用于保持向后兼容）"""
    type: int
    hand_number: int = 0
    stage: str = ""
    player_name: str = ""
    action: str = ""
    amount: int = 0
    pot: int = 0
    player_chips: int = 0
    behavior: str = ""


@dataclass
class HandStartLog:
    """一手牌开始的日志"""
    type: int = 1
    hand_number: int = 0
    dealer: int = 0
    small_blind: int = 0
    big_blind: int = 0
    players: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CommunityCardsLog:
    """公共牌日志"""
    type: int = 2
    hand_number: int = 0
    stage: str = ""  # flop, turn, river
    community_cards: List[str] = field(default_factory=list)


@dataclass
class PlayerActionLog:
    """玩家行动日志"""
    type: int = 3
    hand_number: int = 0
    stage: str = ""
    player_name: str = ""
    action: str = ""
    amount: int = 0
    pot: int = 0
    player_chips: int = 0
    behavior: str = ""
    play_reason: str = ""  # 新增：决策理由


@dataclass
class ShowdownLog:
    """摊牌日志"""
    type: int = 4
    hand_number: int = 0
    community_cards: List[str] = field(default_factory=list)
    players: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PotAwardLog:
    """奖池分配日志"""
    type: int = 5
    hand_number: int = 0
    pot: int = 0
    side_pots: List[Dict[str, Any]] = field(default_factory=list)
    winners: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HandResultLog:
    """一手牌的结算日志（增强版）"""
    type: int = 6
    hand_number: int = 0
    pot: int = 0
    stage: str = ""  # 结束阶段：showdown 或其他
    community_cards: List[str] = field(default_factory=list)

    # 所有未弃牌玩家的信息（包括赢家和输家）
    players: List[Dict[str, Any]] = field(default_factory=list)

    # 赢家详情
    winners: List[Dict[str, Any]] = field(default_factory=list)

    # 边池信息（如果有）
    side_pots: List[Dict[str, Any]] = field(default_factory=list)

    # 时间戳
    timestamp: str = ""


@dataclass
class EnhancedGameLog:
    """增强的游戏日志"""
    # 游戏元信息
    game_id: str
    start_time: str
    end_time: str = ""
    initial_chips: int = 0
    small_blind: int = 0
    big_blind: int = 0

    # 玩家信息
    players: List[Dict[str, Any]] = field(default_factory=list)

    # 游戏事件（保持向后兼容）
    events: List[Dict[str, Any]] = field(default_factory=list)

    # LLM决策日志（新增）
    llm_decisions: List[Dict[str, Any]] = field(default_factory=list)

    # LLM反思日志（新增）
    llm_reflections: List[Dict[str, Any]] = field(default_factory=list)

    # 最终结果
    final_rankings: List[Dict[str, Any]] = field(default_factory=list)


class GameLogger:
    """增强的游戏日志记录器"""

    def __init__(self, game_id: str, log_dir: str = "game_logs"):
        self.game_id = game_id
        self.log_dir = log_dir
        self.log_data = EnhancedGameLog(
            game_id=game_id,
            start_time=datetime.now().isoformat()
        )

        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def set_game_config(self, initial_chips: int, small_blind: int, big_blind: int):
        """设置游戏配置"""
        self.log_data.initial_chips = initial_chips
        self.log_data.small_blind = small_blind
        self.log_data.big_blind = big_blind

    def set_players(self, players: List[Any]):
        """设置玩家信息"""
        self.log_data.players = []
        for player in players:
            player_info = {
                "name": player.name,
                "model_name": getattr(player, "model_name", "unknown"),
                "initial_chips": player.player.chips if hasattr(player, 'player') else player.chips
            }
            self.log_data.players.append(player_info)

    def log_event(self, event: Any):
        """记录游戏事件（保持向后兼容）"""
        if hasattr(event, 'type'):
            self.log_data.events.append(asdict(event))
        else:
            self.log_data.events.append(event)

    def log_llm_decision(
        self,
        player_name: str,
        model_name: str,
        hand_number: int,
        stage: GameStage,
        prompt: str,
        game_state: Dict[str, Any],
        raw_response: str,
        parsed_action: Action,
        action_amount: int,
        play_reason: str,
        behavior: str,
        reasoning_content: str = "",
        response_time: float = 0.0,
        error: str = ""
    ):
        """记录LLM决策过程"""
        decision_log = LLMDecisionLog(
            player_name=player_name,
            model_name=model_name,
            hand_number=hand_number,
            stage=stage.value,
            timestamp=datetime.now().isoformat(),
            prompt=prompt,
            game_state=game_state,
            raw_response=raw_response,
            reasoning_content=reasoning_content,
            parsed_action=parsed_action.value if isinstance(parsed_action, Action) else str(parsed_action),
            action_amount=action_amount,
            play_reason=play_reason,
            behavior=behavior,
            response_time=response_time,
            error=error
        )
        self.log_data.llm_decisions.append(asdict(decision_log))

    def log_llm_reflection(
        self,
        player_name: str,
        model_name: str,
        hand_number: int,
        prompt: str,
        game_result: str,
        raw_response: str,
        updated_opinions: Dict[str, str]
    ):
        """记录LLM反思过程"""
        reflection_log = LLMReflectionLog(
            player_name=player_name,
            model_name=model_name,
            hand_number=hand_number,
            timestamp=datetime.now().isoformat(),
            prompt=prompt,
            game_result=game_result,
            raw_response=raw_response,
            updated_opinions=updated_opinions
        )
        self.log_data.llm_reflections.append(asdict(reflection_log))

    def log_community_cards(self, hand_number: int, stage: str, community_cards: List[Any]):
        """记录公共牌出现"""
        cards_log = CommunityCardsLog(
            type=2,
            hand_number=hand_number,
            stage=stage,
            community_cards=[str(card) for card in community_cards]
        )
        self.log_data.events.append(asdict(cards_log))

    def log_showdown(self, hand_number: int, community_cards: List[Any], players: List[Any]):
        """记录摊牌"""
        showdown_log = ShowdownLog(
            type=4,
            hand_number=hand_number,
            community_cards=[str(card) for card in community_cards],
            players=[
                {
                    "name": p.name,
                    "hand": [str(card) for card in p.hand],
                    "chips": p.chips,
                    "folded": p.folded
                }
                for p in players if not p.folded
            ]
        )
        self.log_data.events.append(asdict(showdown_log))

    def log_hand_result(
        self,
        hand_number: int,
        pot: int,
        stage: str,
        community_cards: List[Any],
        all_players: List[Any],
        winners: List[Any],
        side_pots: List[Any] = None
    ):
        """记录一手牌的结算结果"""
        # 记录所有未弃牌玩家的信息
        active_players = []
        for player in all_players:
            if not player.folded:
                player_info = {
                    "name": player.name,
                    "hand": [str(card) for card in player.hand],
                    "chips_before": player.chips + player.total_bet,  # 结束前的筹码
                    "chips_after": player.chips,  # 结束后的筹码
                    "total_bet": player.total_bet,  # 本局下注总额
                    "net_result": player.chips - (player.chips + player.total_bet)  # 净赢/输
                }
                active_players.append(player_info)

        # 记录赢家详情
        winners_info = []
        for winner in winners:
            winner_info = {
                "name": winner.name,
                "hand": [str(card) for card in winner.hand],
                "amount": 0  # 将在后面计算
            }
            # 计算实际赢得的金额（需要从side_pots或总池中获取）
            winners_info.append(winner_info)

        result_log = HandResultLog(
            type=6,
            hand_number=hand_number,
            pot=pot,
            stage=stage,
            community_cards=[str(card) for card in community_cards],
            players=active_players,
            winners=winners_info,
            side_pots=side_pots or [],
            timestamp=datetime.now().isoformat()
        )
        self.log_data.events.append(asdict(result_log))

    def set_final_rankings(self, players: List[Any]):
        """设置最终排名"""
        self.log_data.final_rankings = []
        sorted_players = sorted(
            players,
            key=lambda p: p.player.chips if hasattr(p, 'player') else p.chips,
            reverse=True
        )
        for i, player in enumerate(sorted_players):
            chips = player.player.chips if hasattr(player, 'player') else player.chips
            self.log_data.final_rankings.append({
                "rank": i + 1,
                "name": player.name,
                "final_chips": chips,
                "model_name": getattr(player, "model_name", "unknown")
            })

    def finish_game(self):
        """结束游戏记录"""
        self.log_data.end_time = datetime.now().isoformat()

    def save(self) -> str:
        """保存日志到文件"""
        filename = os.path.join(self.log_dir, f"enhanced_poker_game_{self.game_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.log_data), f, ensure_ascii=False, indent=2)
        return filename

    def get_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        return {
            "game_id": self.game_id,
            "start_time": self.log_data.start_time,
            "end_time": self.log_data.end_time,
            "total_hands": max(
                [e.get("hand_number", 0) for e in self.log_data.events],
                default=0
            ),
            "total_decisions": len(self.log_data.llm_decisions),
            "total_reflections": len(self.log_data.llm_reflections),
            "players": self.log_data.players,
            "final_rankings": self.log_data.final_rankings
        }


def convert_legacy_log(legacy_log: List[Dict[str, Any]], game_id: str) -> EnhancedGameLog:
    """将旧版日志转换为新格式（用于向后兼容）"""
    enhanced_log = EnhancedGameLog(
        game_id=game_id,
        start_time=datetime.now().isoformat(),
        events=legacy_log
    )

    # 从日志中提取游戏配置
    for event in legacy_log:
        if event.get("type") == 1:  # HandStartLog
            enhanced_log.small_blind = event.get("small_blind", 0)
            enhanced_log.big_blind = event.get("big_blind", 0)
            if event.get("players"):
                enhanced_log.players = [
                    {
                        "name": p.get("name"),
                        "model_name": "unknown",
                        "initial_chips": p.get("chips", 0)
                    }
                    for p in event["players"]
                ]
            break

    return enhanced_log