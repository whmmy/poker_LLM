# analyze_logs.py
# 增强日志分析工具

import json
import os
from typing import Dict, List, Any
from collections import defaultdict


class LogAnalyzer:
    """增强日志分析器"""

    def __init__(self, log_dir: str = "game_logs"):
        self.log_dir = log_dir

    def list_enhanced_logs(self) -> List[str]:
        """列出所有增强日志文件"""
        if not os.path.exists(self.log_dir):
            return []

        logs = []
        for file in os.listdir(self.log_dir):
            if file.startswith("enhanced_poker_game_") and file.endswith(".json"):
                logs.append(os.path.join(self.log_dir, file))
        return logs

    def load_log(self, game_id: str) -> Dict[str, Any]:
        """加载指定游戏的增强日志"""
        filename = os.path.join(self.log_dir, f"enhanced_poker_game_{game_id}.json")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"找不到日志文件: {filename}")

        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_game_summary(self, game_id: str) -> Dict[str, Any]:
        """获取游戏摘要"""
        log = self.load_log(game_id)

        return {
            "game_id": log["game_id"],
            "start_time": log["start_time"],
            "end_time": log.get("end_time", "进行中"),
            "players": log["players"],
            "total_decisions": len(log["llm_decisions"]),
            "total_reflections": len(log["llm_reflections"]),
            "final_rankings": log.get("final_rankings", []),
            "total_hands": max([e.get("hand_number", 0) for e in log["events"]], default=0)
        }

    def get_player_decisions(self, game_id: str, player_name: str) -> List[Dict[str, Any]]:
        """获取指定玩家的所有决策"""
        log = self.load_log(game_id)
        return [
            decision for decision in log["llm_decisions"]
            if decision["player_name"] == player_name
        ]

    def get_player_reflections(self, game_id: str, player_name: str) -> List[Dict[str, Any]]:
        """获取指定玩家的所有反思"""
        log = self.load_log(game_id)
        return [
            reflection for reflection in log["llm_reflections"]
            if reflection["player_name"] == player_name
        ]

    def analyze_decision_patterns(self, game_id: str, player_name: str) -> Dict[str, Any]:
        """分析玩家的决策模式"""
        decisions = self.get_player_decisions(game_id, player_name)

        action_counts = defaultdict(int)
        stage_action_counts = defaultdict(lambda: defaultdict(int))
        total_response_time = 0
        fold_count = 0
        raise_count = 0
        call_count = 0
        all_in_count = 0

        for decision in decisions:
            action = decision["parsed_action"]
            action_counts[action] += 1
            stage_action_counts[decision["stage"]][action] += 1
            total_response_time += decision.get("response_time", 0)

            if action == "FOLD":
                fold_count += 1
            elif action == "RAISE":
                raise_count += 1
            elif action == "CALL":
                call_count += 1
            elif action == "ALL_IN":
                all_in_count += 1

        total_decisions = len(decisions)

        return {
            "player_name": player_name,
            "total_decisions": total_decisions,
            "action_distribution": dict(action_counts),
            "stage_action_distribution": {
                stage: dict(actions)
                for stage, actions in stage_action_counts.items()
            },
            "avg_response_time": total_response_time / total_decisions if total_decisions > 0 else 0,
            "aggression_score": (raise_count + all_in_count) / total_decisions if total_decisions > 0 else 0,
            "fold_rate": fold_count / total_decisions if total_decisions > 0 else 0,
            "call_rate": call_count / total_decisions if total_decisions > 0 else 0
        }

    def get_decision_by_stage(self, game_id: str, hand_number: int, stage: str, player_name: str = None) -> List[Dict[str, Any]]:
        """获取特定阶段的所有决策"""
        log = self.load_log(game_id)

        decisions = [
            decision for decision in log["llm_decisions"]
            if decision["hand_number"] == hand_number and decision["stage"] == stage
        ]

        if player_name:
            decisions = [d for d in decisions if d["player_name"] == player_name]

        return decisions

    def compare_models(self, game_id: str) -> Dict[str, Any]:
        """对比不同模型的表现"""
        log = self.load_log(game_id)

        model_stats = defaultdict(lambda: {
            "decisions": 0,
            "total_response_time": 0,
            "fold_count": 0,
            "raise_count": 0,
            "call_count": 0
        })

        for decision in log["llm_decisions"]:
            model_name = decision["model_name"]
            stats = model_stats[model_name]
            stats["decisions"] += 1
            stats["total_response_time"] += decision.get("response_time", 0)

            action = decision["parsed_action"]
            if action == "FOLD":
                stats["fold_count"] += 1
            elif action == "RAISE":
                stats["raise_count"] += 1
            elif action == "CALL":
                stats["call_count"] += 1

        # 计算统计数据
        comparison = {}
        for model_name, stats in model_stats.items():
            comparison[model_name] = {
                "total_decisions": stats["decisions"],
                "avg_response_time": stats["total_response_time"] / stats["decisions"] if stats["decisions"] > 0 else 0,
                "aggression_rate": (stats["raise_count"] / stats["decisions"]) if stats["decisions"] > 0 else 0,
                "fold_rate": (stats["fold_count"] / stats["decisions"]) if stats["decisions"] > 0 else 0,
                "call_rate": (stats["call_count"] / stats["decisions"]) if stats["decisions"] > 0 else 0
            }

        return comparison

    def export_decision_timeline(self, game_id: str, output_file: str = None) -> str:
        """导出决策时间线（用于Web展示）"""
        log = self.load_log(game_id)

        timeline = []
        for decision in log["llm_decisions"]:
            timeline.append({
                "time": decision["timestamp"],
                "hand_number": decision["hand_number"],
                "stage": decision["stage"],
                "player": decision["player_name"],
                "model": decision["model_name"],
                "action": decision["parsed_action"],
                "amount": decision["action_amount"],
                "reason": decision["play_reason"],
                "behavior": decision["behavior"],
                "hand": decision["game_state"]["hand"],
                "community_cards": decision["game_state"]["community_cards"],
                "pot": decision["game_state"]["pot"]
            })

        # 按时间排序
        timeline.sort(key=lambda x: x["time"])

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(timeline, f, ensure_ascii=False, indent=2)
            return output_file

        return json.dumps(timeline, ensure_ascii=False, indent=2)


def print_analysis_example():
    """打印分析示例"""
    analyzer = LogAnalyzer()

    # 列出所有增强日志
    logs = analyzer.list_enhanced_logs()
    if not logs:
        print("没有找到增强日志文件")
        return

    print(f"找到 {len(logs)} 个增强日志文件")
    print("\n" + "="*80)

    # 分析第一个日志
    for log_file in logs[:1]:  # 只分析第一个作为示例
        game_id = log_file.replace("enhanced_poker_game_", "").replace(".json", "")

        print(f"\n分析游戏: {game_id}")
        print("="*80)

        # 获取游戏摘要
        summary = analyzer.get_game_summary(game_id)
        print(f"\n游戏摘要:")
        print(f"  开始时间: {summary['start_time']}")
        print(f"  结束时间: {summary['end_time']}")
        print(f"  玩家: {', '.join(p['name'] for p in summary['players'])}")
        print(f"  总手牌数: {summary['total_hands']}")
        print(f"  总决策数: {summary['total_decisions']}")
        print(f"  总反思数: {summary['total_reflections']}")

        # 分析每个玩家的决策模式
        print(f"\n玩家决策模式分析:")
        print("-"*80)
        for player in summary['players']:
            player_name = player['name']
            patterns = analyzer.analyze_decision_patterns(game_id, player_name)

            print(f"\n玩家: {player_name} (模型: {player['model_name']})")
            print(f"  总决策数: {patterns['total_decisions']}")
            print(f"  平均响应时间: {patterns['avg_response_time']:.2f}秒")
            print(f"  激进度: {patterns['aggression_score']:.2%}")
            print(f"  弃牌率: {patterns['fold_rate']:.2%}")
            print(f"  跟注率: {patterns['call_rate']:.2%}")
            print(f"\n  行动分布:")
            for action, count in patterns['action_distribution'].items():
                print(f"    {action}: {count} ({count/patterns['total_decisions']:.1%})")

        # 对比模型表现
        print(f"\n模型对比:")
        print("-"*80)
        comparison = analyzer.compare_models(game_id)
        for model_name, stats in comparison.items():
            print(f"\n模型: {model_name}")
            print(f"  总决策数: {stats['total_decisions']}")
            print(f"  平均响应时间: {stats['avg_response_time']:.2f}秒")
            print(f"  激进度: {stats['aggression_rate']:.2%}")
            print(f"  弃牌率: {stats['fold_rate']:.2%}")

        # 显示前3个决策示例
        print(f"\n决策示例 (前3个):")
        print("-"*80)
        decisions = analyzer.get_player_decisions(game_id, summary['players'][0]['name'])
        for i, decision in enumerate(decisions[:3], 1):
            print(f"\n决策 #{i}:")
            print(f"  手牌: {decision['game_state']['hand']}")
            print(f"  阶段: {decision['stage']}")
            print(f"  行动: {decision['parsed_action']} {decision['action_amount']}")
            print(f"  理由: {decision['play_reason']}")
            if decision.get('reasoning_content'):
                print(f"  推理: {decision['reasoning_content'][:100]}...")
            print(f"  响应时间: {decision['response_time']:.2f}秒")


if __name__ == "__main__":
    print_analysis_example()
