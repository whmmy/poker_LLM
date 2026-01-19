# Poker LLM

[中文](README.md) | English

An AI-powered Texas Hold'em Poker framework driven by Large Language Models

## Project Introduction

This project is a Texas Hold'em Poker AI battle framework that uses Large Language Models (LLMs) as AI players to compete in poker games. The framework simulates the complete Texas Hold'em poker game process, including dealing cards, betting, flop, turn, river, and showdown phases, and supports multiple AI players participating simultaneously.

### Key Features

- Complete Texas Hold'em poker game engine
- Support for multiple LLMs (OpenAI, Claude, DeepSeek, QWen, etc.)
- Web-based visual replay system (Vue 3 + Vite + Element Plus)
- Comprehensive logging system
- AI player reflection and analysis functionality
- Flexible configuration management

## Project Structure

```
poker-llm/
├── frontend/              # Frontend project (Vue 3)
│   └── poker_llm_web/    # Game replay web application
├── prompt/               # Prompt templates
├── game_logs/            # Game log storage
├── doc/                  # Documentation and screenshots
├── ai_player.py          # AI player implementation
├── game_controller.py    # Game controller
├── poker_engine.py       # Texas Hold'em engine
├── game_logger.py        # Logging system
├── prompts.py            # Prompt management
├── replay_game.py        # Game replay tool
├── analyze_logs.py       # Log analysis tool
└── main.py               # Main program entry
```

## Quick Start

### Backend Setup

#### Requirements

- Python 3.10+

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:

```env
# OpenAI compatible API (DeepSeek, QWen, etc.)
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Game configuration
INITIAL_CHIPS=1000
SMALL_BLIND=5
BIG_BLIND=10
NUM_HANDS=10
```

#### Start the Game

Run the main program:

```bash
python main.py
```

### Frontend Setup (Web Replay)

#### Requirements

- Node.js 16+
- npm or yarn

#### Install Dependencies

```bash
cd frontend/poker_llm_web
npm install
```

#### Development Mode

```bash
npm run dev
```

#### Build Production Version

```bash
npm run build
```

#### Tech Stack

- Vue 3 - Progressive JavaScript framework
- Vite - Next generation frontend build tool
- Element Plus - Vue 3 UI component library
- Pinia - Vue state management
- Vue Router - Router management
- GSAP - High-performance animation library

## Game Replay

### Method 1: Command Line Replay

```bash
python replay_game.py
```

### Method 2: Web Replay

1. Start the frontend development server
2. Open `http://localhost:5173` in your browser
3. Select a saved game record to replay

## Configuration Guide

### AI Player Configuration

You can add different types of AI players in `main.py`:

```python
# OpenAI compatible API
players.append(OpenAiLLMUser(
    name="Player Name",
    model_name="Model Name",
    api_key='YOUR_API_KEY',
    base_url="YOUR_BASE_URL"
))

# Anthropic Claude
players.append(AnthropicLLMUser(
    name="Player Name",
    model_name="Model Name",
    api_key='YOUR_API_KEY',
    base_url="YOUR_BASE_URL"
))
```

### Game Parameters

You can adjust game settings by modifying parameters in `main.py`:

```python
start_game(
    players,
    hands=10,        # Number of hands to play
    chips=1000,      # Initial chips for each player
    small_blind=5,   # Small blind amount
    big_blind=10     # Big blind amount
)
```

## Game Process

1. Initialize the game, set blinds and initial chips
2. Deal hole cards to each player
3. Pre-flop betting round
4. Deal the flop and betting round
5. Deal the turn and betting round
6. Deal the river and betting round
7. Showdown and determine the winner
8. Distribute chips and record game results
9. AI players reflect on the current game
10. Start a new round

## Extended Features

- Support for game log recording and replay
- AI players can analyze and reflect on other players
- Different large language models can be customized as AI players
- Support for adjusting game parameters, such as blind size, initial chips, etc.
- Web-based visual interface

## Program Screenshots

Showing LLM call results and reasoning process
![Program Screenshot](./doc/img/1.png)

Showing the process of LLM analyzing other players' behavior
![Program Screenshot](./doc/img/2.png)

## License

This project is open-source, see [LICENSE](LICENSE) file for details.
