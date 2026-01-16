<template>
  <div class="game-state-view">
    <div class="state-section">
      <h4>手牌信息</h4>
      <div class="cards-display">
        <div
          v-for="(card, index) in gameState.hand"
          :key="index"
          class="state-card"
          :class="{ 'red': isRedCard(card) }"
        >
          {{ card }}
        </div>
      </div>
    </div>

    <div class="state-section">
      <h4>公共牌</h4>
      <div class="cards-display">
        <div
          v-if="gameState.community_cards && gameState.community_cards.length > 0"
          v-for="(card, index) in gameState.community_cards"
          :key="index"
          class="state-card"
          :class="{ 'red': isRedCard(card) }"
        >
          {{ card }}
        </div>
        <div v-else class="no-cards">暂无公共牌</div>
      </div>
    </div>

    <div class="state-grid">
      <div class="state-item">
        <span class="label">底池:</span>
        <span class="value">{{ gameState.pot || 0 }}</span>
      </div>
      <div class="state-item">
        <span class="label">当前下注:</span>
        <span class="value">{{ gameState.current_bet || 0 }}</span>
      </div>
      <div class="state-item">
        <span class="label">最小加注:</span>
        <span class="value">{{ gameState.min_raise || 0 }}</span>
      </div>
      <div class="state-item">
        <span class="label">阶段:</span>
        <span class="value stage-badge">{{ formatStage(gameState.stage) }}</span>
      </div>
      <div class="state-item">
        <span class="label">手牌编号:</span>
        <span class="value">{{ gameState.hand_num || 1 }}</span>
      </div>
      <div class="state-item">
        <span class="label">位置:</span>
        <span class="value">{{ gameState.position || 0 }}</span>
      </div>
      <div class="state-item">
        <span class="label">庄家位置:</span>
        <span class="value">{{ gameState.dealer_position || 0 }}</span>
      </div>
    </div>

    <div class="state-section">
      <h4>玩家信息</h4>
      <div class="players-list">
        <div
          v-for="(player, index) in gameState.players_info"
          :key="index"
          class="player-state-item"
          :class="{
            'current-player': player.name === playerName,
            'folded': player.folded,
            'all-in': player.all_in
          }"
        >
          <div class="player-header">
            <el-icon v-if="player.name === playerName"><star /></el-icon>
            <span class="p-name">{{ player.name }}</span>
            <el-tag v-if="player.folded" size="small" type="danger">已弃牌</el-tag>
            <el-tag v-if="player.all_in" size="small" type="warning">全押</el-tag>
          </div>
          <div class="player-stats">
            <span>筹码: <strong>{{ player.chips }}</strong></span>
            <span>已下注: <strong>{{ player.bet_in_round }}</strong></span>
            <span v-if="player.position">位置: <strong>{{ player.position }}</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Star } from '@element-plus/icons-vue'

const props = defineProps({
  gameState: {
    type: Object,
    required: true
  },
  playerName: {
    type: String,
    default: ''
  }
})

const formatStage = (stage) => {
  const stageMap = {
    'preflop': '前翻牌',
    'flop': '翻牌',
    'turn': '转牌',
    'river': '河牌',
    'showdown': '摊牌'
  }
  return stageMap[stage] || stage
}

const isRedCard = (card) => {
  if (!card) return false
  return card.includes('♥') || card.includes('♦') || card.includes('红桃') || card.includes('方块')
}
</script>

<style scoped>
.game-state-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.state-section {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
}

.state-section h4 {
  margin: 0 0 0.75rem 0;
  color: #333;
  font-size: 0.95rem;
  font-weight: 600;
}

.cards-display {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.state-card {
  background: white;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  min-width: 2.5rem;
  height: 3rem;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: #333;
  border: 2px solid #333;
}

.state-card.red {
  color: #dc3545;
  border-color: #dc3545;
}

.no-cards {
  color: #999;
  font-style: italic;
  padding: 0.5rem;
}

.state-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
}

.state-item {
  background: white;
  border-radius: 0.5rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.state-item .label {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.state-item .value {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

.stage-badge {
  background: #e7f3ff;
  color: #1971c2;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-state-item {
  background: white;
  border-radius: 0.5rem;
  padding: 0.75rem;
  border-left: 3px solid #dee2e6;
  transition: all 0.2s ease;
}

.player-state-item.current-player {
  border-left-color: #ffd43b;
  background: linear-gradient(90deg, rgba(255, 212, 59, 0.1) 0%, white 100%);
}

.player-state-item.folded {
  opacity: 0.6;
  border-left-color: #fa5252;
}

.player-state-item.all-in {
  border-left-color: #fd7e14;
  box-shadow: 0 0 10px rgba(253, 126, 20, 0.2);
}

.player-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.p-name {
  font-weight: 600;
  color: #333;
}

.player-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #666;
}

.player-stats strong {
  color: #333;
}
</style>
