# Poker LLM

中文 | [English](README_EN.md)

一个由大语言模型驱动的AI版德州扑克对战框架

## 项目介绍

本项目是一个德州扑克AI对战框架，使用大语言模型(LLM)作为AI玩家进行德州扑克游戏对战。框架模拟了完整的德州扑克游戏流程，包括发牌、下注、翻牌、转牌、河牌和摊牌等环节，并支持多个AI玩家同时参与游戏。每个AI玩家由大语言模型驱动，能够根据当前游戏状态做出决策，并在游戏结束后进行反思学习。

## 运行方式

### 环境要求

- Python 3.10+
- 安装依赖：`pip install -r requirements.txt`（主要依赖openai库）

### 配置API密钥

在运行前，需要在`main.py`中配置大语言模型的API密钥和基础URL：

```python
players.append(LLMPlayer(name="玩家名称", model_name="模型名称", api_key='YOUR_API_KEY', base_url="YOUR_BASE_URL"))
```

### 开始游戏

直接运行`main.py`文件即可开始游戏：

```bash
python main.py
```

### 游戏回放

可以使用以下命令查看已保存的游戏列表：
直接使用replay_game.py：

```bash
python replay_game.py
```

可以通过修改`main.py`中的参数来调整游戏设置：

```python
start_game(players, hands=10, chips=1000, small_blind=5, big_blind=10)
```

- `hands`: 要进行的手牌数量
- `chips`: 初始每位玩家筹码数量
- `small_blind`: 小盲注金额
- `big_blind`: 大盲注金额

## 文件结构说明

- `main.py`: 主程序入口，用于配置和启动游戏
- `game_controller.py`: 游戏控制器，管理多个AI玩家之间的对战
- `poker_engine.py`: 德州扑克游戏引擎，实现游戏规则和逻辑
- `ai_player.py`: AI玩家接口和实现，包含基于大语言模型的玩家实现
- `engine_info.py`: 游戏基础数据结构，如牌、花色、行动类型等
- `game_info.py`: 游戏状态信息结构，用于AI决策和游戏记录
- `prompt/`: 提示词目录
  - `decision_prompt.txt`: 用于AI决策的提示词模板
  - `reflect_prompt.txt`: 用于AI反思的提示词模板
  - `reflect_all_prompt.txt`: 用于AI对所有玩家进行反思的提示词模板
- `replay_game.py`: 游戏回放工具
- `prompts.py`: 提示词管理
- `requirements.txt`: 项目依赖

## 游戏流程

1. 初始化游戏，设置盲注和初始筹码
2. 为每个玩家发放底牌
3. 进行翻牌前下注
4. 发放翻牌并进行下注
5. 发放转牌并进行下注
6. 发放河牌并进行下注
7. 进行摊牌并确定赢家
8. 分配筹码并记录游戏结果
9. AI玩家对本局游戏进行反思
10. 开始新一轮游戏

## 已知问题

1. ~~**边池计算问题**: 当前版本在计算赢家筹码时未按照边池进行计算。在`poker_engine.py`中已有`award_pot_new`方法实现了边池计算，但当前使用的是简化版的`award_pot`方法，未考虑边池情况。~~

2. **内容输出不完善**: 游戏过程中的信息输出不够完整，部分关键信息可能未显示。


## 扩展功能

- 支持游戏日志记录和回放
- AI玩家可以对其他玩家进行分析和反思
- 可以自定义不同的大语言模型作为AI玩家
- 支持调整游戏参数，如盲注大小、初始筹码等