# test_side_pot.py
# 测试边池计算逻辑

from poker_engine import PokerTable, Player, Action, Suit, Card
from engine_info import GameStage


def test_side_pot_scenario_1():
    """
    测试场景1：简单边池
    - 玩家A: 100筹码，全押
    - 玩家B: 500筹码，跟注
    - 玩家C: 500筹码，跟注
    - 玩家B弃牌，A和C摊牌，C获胜
    期望：C赢得全部底池
    """
    print("\n=== 测试场景1：简单边池 ===")
    table = PokerTable(small_blind=5, big_blind=10)

    # 添加玩家
    player_a = Player(name="玩家A", chips=100)
    player_b = Player(name="玩家B", chips=500)
    player_c = Player(name="玩家C", chips=500)

    table.add_player(player_a)
    table.add_player(player_b)
    table.add_player(player_c)

    # 设置下注（使用place_bet方法）
    table.hand_number = 1

    # A全押100
    player_a.place_bet(100)
    player_a.all_in = True

    # B跟注500
    player_b.place_bet(500)
    player_b.all_in = True

    # C跟注500
    player_c.place_bet(500)
    player_c.all_in = True

    table.pot = 100 + 500 + 500  # 总共1100

    print(f"初始底池: {table.pot}")
    print(f"玩家A总下注: {player_a.total_bet}, 剩余筹码: {player_a.chips}")
    print(f"玩家B总下注: {player_b.total_bet}, 剩余筹码: {player_b.chips}")
    print(f"玩家C总下注: {player_c.total_bet}, 剩余筹码: {player_c.chips}")

    # 玩家B弃牌，A和C摊牌，C获胜
    player_b.folded = True
    winners = [player_c]

    # 分配奖池
    table.award_pot(winners)

    print(f"\n最终结果:")
    print(f"玩家A筹码: {player_a.chips}")
    print(f"玩家B筹码: {player_b.chips}")
    print(f"玩家C筹码: {player_c.chips}")

    # 验证结果
    # A下注100后剩余0，B下注500后剩余0且弃牌，C下注500后剩余0，赢得全部1100
    assert player_a.chips == 0, f"玩家A应该有0筹码，实际有{player_a.chips}"
    assert player_b.chips == 0, f"玩家B应该有0筹码，实际有{player_b.chips}"
    assert player_c.chips == 1100, f"玩家C应该有1100筹码，实际有{player_c.chips}"
    print("✓ 测试场景1通过")


def test_side_pot_scenario_2():
    """
    测试场景2：多个边池
    - 玩家A: 50筹码，全押
    - 玩家B: 100筹码，全押
    - 玩家C: 200筹码，跟注
    - 玩家D: 200筹码，跟注
    - A、B、C、D都进入摊牌，B获胜
    期望：
    - 主池(50*4=200): A、B、C、D都参与，B获胜
    - 边池1(50*3=150): B、C、D参与，B获胜
    - 边池2(100*2=200): C、D参与，无人获胜（B无法参与）
    """
    print("\n=== 测试场景场景2：多个边池 ===")
    table = PokerTable(small_blind=5, big_blind=10)

    # 添加玩家
    player_a = Player(name="玩家A", chips=50)
    player_b = Player(name="玩家B", chips=100)
    player_c = Player(name="玩家C", chips=200)
    player_d = Player(name="玩家D", chips=200)

    table.add_player(player_a)
    table.add_player(player_b)
    table.add_player(player_c)
    table.add_player(player_d)

    # 设置下注
    table.hand_number = 1

    # A全押50
    player_a.place_bet(50)
    player_a.all_in = True

    # B全押100
    player_b.place_bet(100)
    player_b.all_in = True

    # C跟注200
    player_c.place_bet(200)
    player_c.all_in = True

    # D跟注200
    player_d.place_bet(200)
    player_d.all_in = True

    table.pot = 50 + 100 + 200 + 200  # 总共550

    print(f"初始底池: {table.pot}")
    print(f"玩家A总下注: {player_a.total_bet}")
    print(f"玩家B总下注: {player_b.total_bet}")
    print(f"玩家C总下注: {player_c.total_bet}")
    print(f"玩家D总下注: {player_d.total_bet}")

    # B获胜
    winners = [player_b]

    # 分配奖池
    table.award_pot(winners)

    print(f"\n最终结果:")
    print(f"玩家A筹码: {player_a.chips}")
    print(f"玩家B筹码: {player_b.chips}")
    print(f"玩家C筹码: {player_c.chips}")
    print(f"玩家D筹码: {player_d.chips}")

    # 验证结果
    # 主池50*4=200，边池1(100-50)*3=150，边池2(200-100)*2=200
    # B只能参与主池和边池1，总共200+150=350
    # 边池2的200需要退还给C和D
    expected_b = 350  # B赢得主池和边池1
    expected_c = 100  # C拿回边池2的一半
    expected_d = 100  # D拿回边池2的一半

    assert player_a.chips == 0, f"玩家A应该有0筹码，实际有{player_a.chips}"
    assert player_b.chips == expected_b, f"玩家B应该有{expected_b}筹码，实际有{player_b.chips}"
    assert player_c.chips == expected_c, f"玩家C应该有{expected_c}筹码，实际有{player_c.chips}"
    assert player_d.chips == expected_d, f"玩家D应该有{expected_d}筹码，实际有{player_d.chips}"
    print("✓ 测试场景2通过")


def test_side_pot_scenario_3():
    """
    测试场景3：赢家是全押玩家
    - 玩家A: 100筹码，全押
    - 玩家B: 500筹码，跟注
    - 玩家C: 500筹码，跟注
    - A获胜
    期望：A只能赢主池(300)，边池(800)由B和C争夺
    """
    print("\n=== 测试场景3：全押玩家获胜 ===")
    table = PokerTable(small_blind=5, big_blind=10)

    # 添加玩家
    player_a = Player(name="玩家A", chips=100)
    player_b = Player(name="玩家B", chips=500)
    player_c = Player(name="玩家C", chips=500)

    table.add_player(player_a)
    table.add_player(player_b)
    table.add_player(player_c)

    # 设置下注
    table.hand_number = 1

    # A全押100
    player_a.place_bet(100)
    player_a.all_in = True

    # B跟注500
    player_b.place_bet(500)
    player_b.all_in = True

    # C跟注500
    player_c.place_bet(500)
    player_c.all_in = True

    table.pot = 100 + 500 + 500  # 总共1100

    print(f"初始底池: {table.pot}")
    print(f"玩家A总下注: {player_a.total_bet}")
    print(f"玩家B总下注: {player_b.total_bet}")
    print(f"玩家C总下注: {player_c.total_bet}")

    # A获胜
    winners = [player_a]

    # 分配奖池
    table.award_pot(winners)

    print(f"\n最终结果:")
    print(f"玩家A筹码: {player_a.chips} (应该拿回主池300)")
    print(f"玩家B筹码: {player_b.chips} (应该拿回边池的一半400)")
    print(f"玩家C筹码: {player_c.chips} (应该拿回边池的一半400)")

    # 验证结果
    # 主池100*3=300归A
    # 边池400*2=800，B和C平分，各得400
    expected_a = 300
    expected_b = 400
    expected_c = 400

    assert player_a.chips == expected_a, f"玩家A应该有{expected_a}筹码，实际有{player_a.chips}"
    assert player_b.chips == expected_b, f"玩家B应该有{expected_b}筹码，实际有{player_b.chips}"
    assert player_c.chips == expected_c, f"玩家C应该有{expected_c}筹码，实际有{player_c.chips}"
    print("✓ 测试场景3通过")


if __name__ == "__main__":
    try:
        test_side_pot_scenario_1()
        test_side_pot_scenario_2()
        test_side_pot_scenario_3()
        print("\n=== 所有边池测试通过! ===")
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        exit(1)
