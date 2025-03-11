# prompts.py
# 存储德州扑克AI玩家的提示语模板

def get_decision_prompt(hand, community_cards, pot, current_bet, player_bet, player_chips, 
                       min_raise, stage, players_info, position, dealer_position, action_history):
    """
    构建提示信息，用于让大语言模型做出德州扑克决策
    
    Returns:
        str: 格式化的提示语
    """
    # 构建提示信息
    prompt = f"""你是一名德州扑克玩家，需要根据当前游戏状态做出决策。

当前游戏信息：
- 你的手牌：{', '.join(str(card) for card in hand)}
- 公共牌：{', '.join(str(card) for card in community_cards) if community_cards else '暂无'}
- 当前阶段：{stage.value}
- 底池：{pot}
- 当前最高下注：{current_bet}
- 你已下注：{player_bet}
- 你的剩余筹码：{player_chips}
- 最小加注额：{min_raise}

玩家信息：
"""
    
    for i, player_info in enumerate(players_info):
        is_self = player_info['id'] == players_info[position]['id']
        position_str = "(你)" if is_self else ""
        dealer_str = "(庄家)" if i == dealer_position else ""
        prompt += f"- 玩家{i+1}{position_str}{dealer_str}: {player_info['name']}, 筹码: {player_info['chips']}, 已下注: {player_info['bet_in_round']}, {'已弃牌' if player_info['folded'] else '未弃牌'}, {'已全押' if player_info['all_in'] else '未全押'}\n"
    
    prompt += "\n最近的行动历史：\n"
    recent_actions = action_history[-10:] if len(action_history) > 10 else action_history
    for action_record in recent_actions:
        prompt += f"- 玩家 {action_record['player_name']} 执行 {action_record['action']}"
        if action_record['amount'] > 0:
            prompt += f", 金额: {action_record['amount']}"
        prompt += "\n"
    
    prompt += """\n请根据以上信息，选择一个行动：
1. FOLD (弃牌)
2. CHECK (过牌，仅当没有人下注或你已经跟注时可用)
3. CALL (跟注)
4. RAISE (加注，需指定金额)
5. ALL_IN (全押)

你的决策是什么？请以JSON格式回复，包含以下字段：
- action: 行动类型 (FOLD/CHECK/CALL/RAISE/ALL_IN)
- amount: 下注金额 (如果需要)
- play_reason: 选择这个行动和金额的理由
- behavior: 一段没有主语的行为/表情/发言等描写，用于给其他玩家观察和分析

例如：
{
  "action": "RAISE",
  "amount": 100,
  "play_reason": "手牌较强，试图增加底池价值",
  "behavior": "微微皱眉，思考片刻后推出筹码，眼神坚定地扫视其他玩家"
}

或者：
{
  "action": "FOLD",
  "amount": 0,
  "play_reason": "手牌较弱，不值得继续投入",
  "behavior": "叹了口气，将牌面朝下推向荷官"
}
"""
    
    return prompt