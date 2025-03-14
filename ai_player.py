# ai_player.py
# AI玩家接口和实现

import random
from typing import List, Dict, Any, Tuple, Optional
from engine_info import Card, Action, GameStage, Player
from openai import OpenAI
from game_info import GameAction, GameInfoState, GamePlayerAction, GameResult
import re

DESISION_PROMPT_PATH = "prompt/decision_prompt.txt"
REFLECT_PROMPT_PATH = "prompt/reflect_prompt.txt"
REFLECT_ALL_PROMPT_PATH = "prompt/reflect_all_prompt.txt"
RED = '\033[31m'
RESET = '\033[0m'


class AIPlayer:
    """AI玩家基类,定义AI玩家接口"""

    def __init__(self, player: Player):
        self.player = player
        self.name = player.name

    def make_decision(self, game_state: GameInfoState) -> GamePlayerAction:
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

    def reflect_on_game(self, game_state: GameInfoState, game_result: GameResult):
        """在游戏结束后，根据游戏结果进行反思和学习"""
        raise NotImplementedError("子类必须实现此方法")


class LLMPlayer(AIPlayer):
    """由大语言模型驱动的AI玩家"""

    def __init__(self, name: str, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(Player(name=name))
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.opinions = {}
        self.all_player_previous = '对他们还不了解'

    def make_decision(self, game_state: GameInfoState) -> GamePlayerAction:
        print(f'玩家 {self.name} 正在思考...')
        print(f"他的手牌是：{', '.join(str(card) for card in self.player.hand)}")
        print(f"他的筹码量：{self.player.chips}")
        for i in range(3):
            try:
                # 构建提示信息
                prompt = self._build_prompt(game_state)

                # 调用大语言模型获取决策
                response = self._call_llm_api(prompt)

                return self._parse_response(response, game_state)
            except Exception as e:
                print(e)
        return GamePlayerAction(
            action=Action.FOLD,
            amount=0,
            play_reason='大模型操作错误，直接弃牌',
            behavior='无表情'
        )

    def _build_prompt(self, game_state: GameInfoState) -> str:
        """构建提示信息"""
        basePrompt = self._read_file(DESISION_PROMPT_PATH)

        # 生成游戏游戏相关信息
        game_info = game_state.get_common_game_info()

        # 生成玩家当前信息
        self_info = self.get_self_current_round_info(game_state)

        # 生成所有玩家信息
        player_info = self.get_all_player_info(game_state)

        # 生成当前轮次的对局历史
        action_history = self.get_action_history(game_state.action_history)

        # 生成当前玩家对其他人物的评估
        player_performance = self.get_player_performance(game_state.players_info)

        prompt = basePrompt.format(
            game_info=game_info,
            self_info=self_info,
            player_info=player_info,
            action_history=action_history,
            player_performance=self.all_player_previous
        )

        return prompt

    def _call_llm_api(self, prompt: str) -> str:
        """调用大语言模型API获取响应"""
        # 每次都发送相同的原始prompt
        messages = [
            {"role": "user", "content": prompt}
        ]

        # print(f"玩家 LLM请求的提示语信息: {prompt}")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        if response.choices:
            message = response.choices[0].message
            content = message.content if message.content else ""
            reasoning_content = getattr(message, "reasoning_content", "")
            if reasoning_content != '':
                print(f"{RED} LLM推理内容: {reasoning_content} {RESET}")
            print(f"{RED} LLM推理内容: {content} {RESET}")
            return content

        # 临时使用随机响应进行测试
        actions = ["FOLD", "CHECK", "CALL", f"RAISE {random.randint(50, 200)}", "ALL_IN"]
        return random.choice(actions)

    def _parse_response(self, response: str, game_state: GameInfoState) -> GamePlayerAction:
        """解析大语言模型的响应"""
        import json

        # 提取JSON部分（防止模型输出额外文本）
        response = response.strip()

        json_match = re.search(r'({[\s\S]*})', response)

        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)

            # 提取action和amount
            action_str = data.get('action', '').strip().upper()
            amount = data.get('amount', 0)

            # 存储决策理由和行为描述
            play_reason = data.get('play_reason', '')
            behavior = data.get('behavior', '')
            action = Action.FOLD
            # 解析行动
            if action_str == 'FOLD':
                action = Action.FOLD
                amount = 0
            elif action_str == 'CHECK':
                action = Action.CHECK
                amount = 0
            elif action_str == 'CALL':
                action = Action.CALL
                amount = game_state.current_bet - self.player.bet_in_round
            elif action_str == 'ALL_IN':
                action = Action.ALL_IN
                amount = self.player.chips
            elif action_str == 'RAISE':
                # 确保加注金额合法
                min_raise = max(game_state.min_raise, game_state.current_bet * 2)
                amount = max(min_raise, amount)  # 确保金额不小于最小加注
                amount = min(amount, self.player.chips)  # 确保金额不超过玩家筹码
                action = Action.RAISE

            return GamePlayerAction(
                action=action,
                amount=amount,
                play_reason=play_reason,
                behavior=behavior
            )
        else:
            raise ValueError("无法从响应中提取有效数据")

    def reflect_on_game(self, game_state: GameInfoState, game_result: GameResult):
        print(f'玩家 {self.name} 正在反思和总结...')
        # 生成当前轮次的对局历史
        action_history = self.get_action_history(game_state.action_history)
        # 生成结果信息
        result_str = game_result.get_result_info()
        # 生成所有玩家信息
        player_info = self.get_all_player_info(game_state)

        # 使用一次调用为所有玩家进行分析
        basePrompt = self._read_file(REFLECT_ALL_PROMPT_PATH)
        try:
            prompt = basePrompt.format(
                self_name=self.player.name,
                user_info=player_info,
                action_history=action_history,
                game_result=result_str,
                previous_opinion=self.all_player_previous
            )
            content = self._call_llm_api(prompt=prompt)
            # 更新对其他玩家的印象
            self.all_player_previous = content.strip()
            print(f"{self.name} 更新了对其他玩家的印象: {content}")
        except Exception as e:
            print(f"反思自己时出错: {str(e)}")
        # 使用多轮调用给每一位玩家进行分析
        # basePrompt = self._read_file(REFLECT_PROMPT_PATH)
        # for player in game_state.players_info:
        #     if player.is_active and player.name != self.player.name:
        #         try:
        #             prompt = basePrompt.format(
        #                 self_name=self.player.name,
        #                 user_info=player_info,
        #                 action_history=action_history,
        #                 game_result=result_str,
        #                 player=player.name,
        #                 previous_opinion=self.opinions.get(player.name, "还不了解这个玩家")
        #             )
        #
        #             content = self._call_llm_api(prompt=prompt)
        #             # 更新对该玩家的印象
        #             self.opinions[player.name] = content.strip()
        #             print(f"{self.name} 更新了对 {player.name} 的印象: {content}")
        #         except Exception as e:
        #             print(f"反思玩家 {player.name} 时出错: {str(e)}")

    def _read_file(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取文件 {filepath} 失败: {str(e)}")
            return ""

    def get_self_current_round_info(self, game_state: GameInfoState) -> str:
        return f"""
        - 你的手牌：{', '.join(str(card) for card in self.player.hand)}
        - 你已下注：{self.player.bet_in_round}
        - 你的剩余筹码：{self.player.chips}
        - 你的位置：{game_state.position}
        """

    def get_all_player_info(self, game_state: GameInfoState) -> str:
        prompt = ''
        for i, player_info in enumerate(game_state.players_info):
            is_self = player_info.name == self.player.name
            position_str = "(你)" if is_self else ""
            dealer_str = "(庄家)" if i == game_state.dealer_position else ""
            prompt += f"- 玩家{position_str}{dealer_str}: {player_info.name},位置：{i}, 剩余筹码: {player_info.chips}, 已下注: {player_info.bet_in_round}, {'已弃牌' if player_info.folded else '未弃牌'}, {'已全押' if player_info.all_in else '未全押'}\n"
        return prompt

    def get_action_history(self, action_history: List[GameAction]) -> str:
        """获取当前轮次的对局历史"""
        action_history_str = ""
        for action in action_history:
            action_history_str += f"牌局阶段 {action.stage.value} 玩家 {action.player_name} 执行 {action.action.value}"
            if action.amount > 0:
                action_history_str += f", 金额: {action.amount}"
            action_history_str += f"\n玩家 {action.player_name} 的表现:{action.behavior}\n"
        return action_history_str

    def get_player_performance(self, players_info: List[Player]) -> str:
        prompt = ''
        for player in players_info:
            if player.name == self.player.name:
                continue
            previous_opinion = self.opinions.get(player.name, "还不了解这个玩家")
            prompt += f'玩家 {player.name}:{previous_opinion}\n'

        return prompt
