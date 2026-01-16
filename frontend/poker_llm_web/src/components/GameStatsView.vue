<template>
  <div class="game-stats-view">
    <div class="stats-header">
      <el-icon><data-analysis /></el-icon>
      <h3>游戏统计</h3>
    </div>

    <!-- 最终排名 -->
    <div class="stats-section">
      <h4>最终排名</h4>
      <div class="rankings-list">
        <div
          v-for="(player, index) in sortedPlayers"
          :key="player.name"
          class="ranking-item"
          :class="{ 'winner': index === 0 }"
        >
          <div class="rank-badge" :class="'rank-' + (index + 1)">
            {{ index + 1 }}
          </div>
          <div class="player-info">
            <div class="player-name">{{ player.name }}</div>
            <div class="model-name">{{ player.model_name }}</div>
          </div>
          <div class="chips-info">
            <div class="final-chips">{{ player.final_chips || 0 }}</div>
            <div class="chips-change" :class="getChangeClass(player)">
              {{ getChipsChange(player) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 玩家决策统计 -->
    <div class="stats-section">
      <h4>决策统计</h4>
      <div class="stats-grid">
        <div
          v-for="player in playerStats"
          :key="player.name"
          class="player-stat-card"
        >
          <div class="stat-card-header">
            <span class="stat-player-name">{{ player.name }}</span>
            <el-tag size="small">{{ player.decisions.length }} 次决策</el-tag>
          </div>

          <div class="action-breakdown">
            <div class="action-stat" v-for="(count, action) in getActionBreakdown(player)" :key="action">
              <span class="action-label">{{ formatAction(action) }}:</span>
              <span class="action-count">{{ count }}</span>
            </div>
          </div>

          <div class="reflection-stat" v-if="player.reflections.length > 0">
            <el-icon><refresh /></el-icon>
            <span>{{ player.reflections.length }} 次反思</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 手牌统计 -->
    <div class="stats-section" v-if="handNumbers.length > 0">
      <h4>手牌记录 (共 {{ handNumbers.length }} 手)</h4>
      <div class="hands-grid">
        <div
          v-for="handNum in handNumbers"
          :key="handNum"
          class="hand-card"
          @click="$emit('jump-to-hand', handNum)"
        >
          <div class="hand-number">#{{ handNum }}</div>
          <div class="hand-decisions">
            <el-tag size="small">{{ getHandDecisionCount(handNum) }} 个决策</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 游戏信息 -->
    <div class="stats-section" v-if="gameMetadata">
      <h4>游戏信息</h4>
      <div class="game-info-grid">
        <div class="info-item">
          <span class="info-label">游戏ID:</span>
          <span class="info-value">{{ gameMetadata.game_id }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">初始筹码:</span>
          <span class="info-value">{{ gameMetadata.initial_chips }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">小盲/大盲:</span>
          <span class="info-value">{{ gameMetadata.small_blind }} / {{ gameMetadata.big_blind }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">开始时间:</span>
          <span class="info-value">{{ formatDateTime(gameMetadata.start_time) }}</span>
        </div>
        <div class="info-item" v-if="gameMetadata.end_time">
          <span class="info-label">结束时间:</span>
          <span class="info-value">{{ formatDateTime(gameMetadata.end_time) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { DataAnalysis, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  playerStats: {
    type: Array,
    default: () => []
  },
  decisionsByHand: {
    type: Object,
    default: () => ({})
  },
  gameMetadata: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['jump-to-hand'])

const sortedPlayers = computed(() => {
  return [...props.playerStats].sort((a, b) => {
    if (b.final_chips !== a.final_chips) {
      return b.final_chips - a.final_chips
    }
    return (a.rank || 999) - (b.rank || 999)
  })
})

const handNumbers = computed(() => {
  return Object.keys(props.decisionsByHand).map(Number).sort((a, b) => a - b)
})

const getChipsChange = (player) => {
  const change = (player.final_chips || 0) - (player.initial_chips || 0)
  return change > 0 ? `+${change}` : `${change}`
}

const getChangeClass = (player) => {
  const change = (player.final_chips || 0) - (player.initial_chips || 0)
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const getActionBreakdown = (player) => {
  const breakdown = {}
  player.decisions.forEach(d => {
    const action = d.parsed_action || 'unknown'
    breakdown[action] = (breakdown[action] || 0) + 1
  })
  return breakdown
}

const getHandDecisionCount = (handNum) => {
  return props.decisionsByHand[handNum]?.length || 0
}

const formatAction = (action) => {
  const actionMap = {
    'fold': '弃牌',
    'check': '过牌',
    'call': '跟注',
    'raise': '加注',
    'all-in': '全押'
  }
  return actionMap[action] || action
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.game-stats-view {
  height: 100%;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stats-header h3 {
  margin: 0;
  flex: 1;
}

.stats-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.rankings-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.ranking-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.ranking-item.winner {
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.2) 0%, #f8f9fa 100%);
  border: 2px solid #ffd43b;
}

.rank-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd43b 0%, #fab005 100%);
  box-shadow: 0 2px 8px rgba(255, 212, 59, 0.5);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #adb5bd 0%, #868e96 100%);
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #ffa94d 0%, #fd7e14 100%);
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: 600;
  color: #333;
}

.model-name {
  font-size: 0.85rem;
  color: #666;
}

.chips-info {
  text-align: right;
}

.final-chips {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.chips-change {
  font-size: 0.9rem;
  font-weight: 600;
}

.chips-change.positive {
  color: #40c057;
}

.chips-change.negative {
  color: #fa5252;
}

.chips-change.neutral {
  color: #868e96;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.player-stat-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border-left: 3px solid #667eea;
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.stat-player-name {
  font-weight: 600;
  color: #333;
}

.action-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.action-stat {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.action-label {
  color: #666;
}

.action-count {
  font-weight: 600;
  color: #333;
}

.reflection-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #dee2e6;
  font-size: 0.85rem;
  color: #11998e;
}

.hands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.hand-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 0.75rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.hand-card:hover {
  background: #e9ecef;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.hand-number {
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.game-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.info-item {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
  display: block;
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

/* 自定义滚动条 */
.game-stats-view::-webkit-scrollbar {
  width: 6px;
}

.game-stats-view::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.game-stats-view::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.game-stats-view::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
