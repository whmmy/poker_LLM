# ai_player.py
# AI玩家接口和实现

import random
from typing import List, Dict, Any, Tuple, Optional
from poker_engine import Player, Action, Card, GameStage
from openai import OpenAI

class AIPlayer:
    """AI玩家基类，定义AI玩家接口"""
    def __init__(self, player: Player):
        self.player = player
        self.name = player.name
    
    def make_decision(self, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """根据游戏状态做出决策
        
        Args:
            game_state: 游戏状态信息，包括：
                - hand: 手牌
                - community_cards: 公共牌
                - pot: 底池
                - current_bet: 当前最高下注
                - min_raise: 最小加注额
                - stage: 当前游戏阶段
                - players_info: 其他玩家信息
                - position: 自己的位置
                - dealer_position: 庄家位置
                - action_history: 行动历史
        
        Returns:
            Tuple[Action, int]: 行动类型和下注金额
        """
        raise NotImplementedError("子类必须实现此方法")
    def reflect_on_game(self, game_result: Dict[str, Any]):
        """在游戏结束后，根据游戏结果进行反思和学习"""
        raise NotImplementedError("子类必须实现此方法")


class RandomAIPlayer(AIPlayer):
    """随机行动的AI玩家，用于测试"""
    def make_decision(self, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        # 获取可用行动
        available_actions = []
        current_bet = game_state['current_bet']
        my_bet = self.player.bet_in_round
        
        # 检查可用行动
        if current_bet == 0 or current_bet == my_bet:
            available_actions.append(Action.CHECK)
        
        if current_bet > my_bet:
            available_actions.append(Action.CALL)
        
        available_actions.append(Action.FOLD)
        
        # 如果还有足够的筹码，可以加注或全押
        if self.player.chips > 0:
            available_actions.append(Action.RAISE)
            available_actions.append(Action.ALL_IN)
        
        # 随机选择一个行动
        action = random.choice(available_actions)
        
        # 根据行动确定金额
        amount = 0
        if action == Action.CALL:
            amount = current_bet - my_bet
        elif action == Action.RAISE:
            min_raise = max(game_state['min_raise'], current_bet * 2)
            max_raise = self.player.chips
            amount = random.randint(min_raise, max_raise) if max_raise > min_raise else min_raise
        elif action == Action.ALL_IN:
            amount = self.player.chips
        
        return action, amount

    def reflect_on_game(self, game_result: Dict[str, Any]):
        # 随机AI玩家不需要反思和学习
        pass


class LLMPlayer(AIPlayer):
    """由大语言模型驱动的AI玩家"""
    def __init__(self, player: Player, model_name: str, api_key: Optional[str] = None,base_url: Optional[str] = None):
        super().__init__(player)
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.context_history = []  # 存储对话历史，用于提供上下文
        self.last_play_reason = ""  # 存储最近一次决策的理由
        self.last_behavior = ""  # 存储最近一次决策的行为描述
        self.client = OpenAI(api_key=self.api_key,base_url=self.base_url)
        self.opinions = {}

    def make_decision(self, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        # 构建提示信息
        prompt = self._build_prompt(game_state)
        
        # 调用大语言模型获取决策
        # 注意：这里需要根据实际使用的大语言模型API进行实现
        # 以下是一个示例实现，实际使用时需要替换为真实的API调用
        response = self._call_llm_api(prompt)
        
        # 解析响应获取行动和金额
        action, amount = self._parse_response(response, game_state)
        
        # 更新对话历史
        self.context_history.append({"prompt": prompt, "response": response})
        
        return action, amount
    
    def _build_prompt(self, game_state: Dict[str, Any]) -> str:
        """构建提示信息"""
        from prompts import get_decision_prompt
        
        hand = game_state['hand']
        community_cards = game_state['community_cards']
        pot = game_state['pot']
        current_bet = game_state['current_bet']
        min_raise = game_state['min_raise']
        stage = game_state['stage']
        players_info = game_state['players_info']
        position = game_state['position']
        dealer_position = game_state['dealer_position']
        action_history = game_state['action_history']
        
        # 使用prompts模块中的函数构建提示信息
        return get_decision_prompt(
            hand, community_cards, pot, current_bet, 
            self.player.bet_in_round, self.player.chips, 
            min_raise, stage, players_info, position, 
            dealer_position, action_history
        )
    
    def _call_llm_api(self, prompt: str) -> str:
        """调用大语言模型API获取响应"""
        # 这里需要根据实际使用的大语言模型API进行实现
        # 以下是一个示例，实际使用时需要替换为真实的API调用
        




        # 临时使用随机响应进行测试
        actions = ["FOLD", "CHECK", "CALL", f"RAISE {random.randint(50, 200)}", "ALL_IN"]
        return random.choice(actions)
    
    def _parse_response(self, response: str, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """解析大语言模型的响应"""
        import json
        
        # 尝试解析JSON响应
        try:
            # 提取JSON部分（防止模型输出额外文本）
            response = response.strip()
            # 查找第一个{和最后一个}之间的内容
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end+1]
                data = json.loads(json_str)
                
                # 提取action和amount
                action_str = data.get('action', '').strip().upper()
                amount = data.get('amount', 0)
                
                # 存储决策理由和行为描述
                self.last_play_reason = data.get('play_reason', '')
                self.last_behavior = data.get('behavior', '')
                
                # 解析行动
                if action_str == 'FOLD':
                    return Action.FOLD, 0
                elif action_str == 'CHECK':
                    return Action.CHECK, 0
                elif action_str == 'CALL':
                    return Action.CALL, game_state['current_bet'] - self.player.bet_in_round
                elif action_str == 'ALL_IN':
                    return Action.ALL_IN, self.player.chips
                elif action_str == 'RAISE':
                    # 确保加注金额合法
                    min_raise = max(game_state['min_raise'], game_state['current_bet'] * 2)
                    amount = max(min_raise, amount)  # 确保金额不小于最小加注
                    amount = min(amount, self.player.chips)  # 确保金额不超过玩家筹码
                    return Action.RAISE, amount
        except Exception as e:
            # 如果JSON解析失败，尝试使用旧方法解析
            print(f"JSON解析失败: {e}，尝试使用旧方法解析")
            response = response.strip().upper()
            
            # 解析行动和金额
            if "FOLD" in response:
                return Action.FOLD, 0
            elif "CHECK" in response:
                return Action.CHECK, 0
            elif "CALL" in response:
                return Action.CALL, game_state['current_bet'] - self.player.bet_in_round
            elif "ALL_IN" in response:
                return Action.ALL_IN, self.player.chips
            elif "RAISE" in response:
                # 尝试从响应中提取金额
                try:
                    amount = int(response.split("RAISE")[1].strip())
                    min_raise = max(game_state['min_raise'], game_state['current_bet'] * 2)
                    amount = max(min_raise, amount)  # 确保金额不小于最小加注
                    amount = min(amount, self.player.chips)  # 确保金额不超过玩家筹码
                    return Action.RAISE, amount
                except:
                    # 如果无法解析金额，默认使用最小加注
                    return Action.RAISE, max(game_state['min_raise'], game_state['current_bet'] * 2)
        
        # 默认弃牌
        return Action.FOLD, 0

    def reflect_on_game(self, game_result: Dict[str, Any]):
        # 实现游戏结束后的反思和学习
        pass