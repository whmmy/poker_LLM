<template>
  <el-dialog
    v-model="visible"
    title="🏆 手牌结算"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
    class="hand-result-dialog"
  >
    <!-- 自动播放倒计时提示 -->
    <div class="auto-play-hint" v-if="isAutoPlaying && autoCloseCountdown > 0">
      <el-icon><video-play /></el-icon>
      <span>{{ autoCloseCountdown }} 秒后自动继续播放...</span>
    </div>

    <div class="result-content" v-if="resultData">
      <!-- 手牌信息 -->
      <div class="hand-info">
        <el-tag size="large" type="primary">手牌 #{{ resultData.handNumber }}</el-tag>
        <el-tag size="large" type="warning" style="margin-left: 10px">
          {{ resultData.stage === 'showdown' ? '摊牌' : resultData.stage }}
        </el-tag>
      </div>

      <!-- 公共牌和底池 -->
      <div class="pot-cards-section" v-if="resultData.communityCards && resultData.communityCards.length > 0">
        <div class="section-title">
          <el-icon><coin /></el-icon>
          <span>底池: {{ resultData.pot }}</span>
        </div>
        <div class="community-cards-display">
          <span
            v-for="(card, index) in resultData.communityCards"
            :key="index"
            class="result-card"
            :class="{ 'red': isRedCard(card) }"
          >
            {{ card }}
          </span>
        </div>
      </div>

      <!-- 底池信息（无公共牌时） -->
      <div class="pot-section" v-else>
        <div class="section-title">
          <el-icon><coin /></el-icon>
          <span>底池: {{ resultData.pot }}</span>
        </div>
      </div>

      <!-- 赢家信息 -->
      <div class="winners-section">
        <div class="section-title">
          <el-icon><trophy /></el-icon>
          <span>获胜玩家</span>
        </div>
        <div class="winners-list">
          <div
            v-for="winner in resultData.winners"
            :key="winner.name"
            class="winner-item"
          >
            <div class="winner-header">
              <el-avatar :size="40" class="winner-avatar">
                {{ winner.name.charAt(0) }}
              </el-avatar>
              <div class="winner-info">
                <div class="winner-name">{{ winner.name }}</div>
                <el-tag type="success" size="small">
                  赢得 {{ winner.amount || 0 }} 筹码
                </el-tag>
              </div>
            </div>
            <!-- 获胜牌型 -->
            <div class="winning-hand" v-if="winner.hand_description || winner.hand">
              <div class="hand-label">牌型:</div>
              <div class="hand-cards">
                <span
                  v-for="(card, index) in (winner.hand || [])"
                  :key="index"
                  class="result-card"
                  :class="{ 'red': isRedCard(card) }"
                >
                  {{ card }}
                </span>
              </div>
              <div class="hand-description">{{ winner.hand_description }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 所有未弃牌玩家详情 -->
      <div class="all-players-section" v-if="activePlayers.length > 0">
        <div class="section-title">
          <el-icon><user /></el-icon>
          <span>玩家详情</span>
        </div>
        <div class="players-grid">
          <div
            v-for="player in activePlayers"
            :key="player.name"
            class="player-result-card"
            :class="{ 'winner': resultData.winners?.some(w => w.name === player.name) }"
          >
            <div class="player-result-header">
              <div class="player-result-name">{{ player.name }}</div>
              <el-tag
                :type="player.net_result >= 0 ? 'success' : 'danger'"
                size="small"
              >
                {{ player.net_result >= 0 ? '+' : '' }}{{ player.net_result }}
              </el-tag>
            </div>
            <div class="player-hand-cards">
              <span
                v-for="(card, index) in player.hand"
                :key="index"
                class="result-card small"
                :class="{ 'red': isRedCard(card) }"
              >
                {{ card }}
              </span>
            </div>
            <div class="player-stats">
              <div class="stat-item">
                <span class="stat-label">下注:</span>
                <span class="stat-value">{{ player.total_bet }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">局前:</span>
                <span class="stat-value">{{ player.chips_before }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">局后:</span>
                <span class="stat-value">{{ player.chips_after }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底池分配 -->
      <div class="pot-section" v-if="resultData.potDistribution && resultData.potDistribution.length > 0">
        <div class="section-title">
          <el-icon><coin /></el-icon>
          <span>底池分配</span>
        </div>
        <div class="pot-list">
          <div
            v-for="(dist, index) in resultData.potDistribution"
            :key="index"
            class="pot-item"
          >
            <span class="pot-player">{{ dist.player }}</span>
            <span class="pot-amount">+{{ dist.amount }}</span>
          </div>
        </div>
      </div>

      <!-- 摊牌手牌 -->
      <div class="showdown-section" v-if="resultData.showCards && Object.keys(resultData.showCards).length > 0">
        <div class="section-title">
          <el-icon><view /></el-icon>
          <span>摊牌手牌</span>
        </div>
        <div class="showdown-cards">
          <div
            v-for="(cards, playerName) in resultData.showCards"
            :key="playerName"
            class="showdown-player"
          >
            <div class="showdown-player-name">{{ playerName }}</div>
            <div class="showdown-player-cards">
              <span
                v-for="(card, index) in cards"
                :key="index"
                class="result-card"
                :class="{ 'red': isRedCard(card) }"
              >
                {{ card }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleContinue">继续下一手</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, watch, ref, onUnmounted } from 'vue'
import { Trophy, Coin, View, User, VideoPlay } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  resultData: {
    type: Object,
    default: null
  },
  isAutoPlaying: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'continue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 过滤出参与的玩家（排除已出局的玩家）
const activePlayers = computed(() => {
  if (!props.resultData || !props.resultData.players) {
    return []
  }

  return props.resultData.players.filter(player => {
    // 排除已经出局的玩家：
    // 1. 没有手牌的（hand 为空数组）
    // 2. 本局下注为 0 的（未参与这局）
    return player.hand && player.hand.length > 0 && player.total_bet > 0
  })
})

// 倒计时逻辑
const autoCloseCountdown = ref(0)
let countdownTimer = null

// 监听弹窗显示状态，启动倒计时
watch(visible, (newVal) => {
  if (newVal && props.isAutoPlaying) {
    autoCloseCountdown.value = 5
    countdownTimer = setInterval(() => {
      autoCloseCountdown.value--
      if (autoCloseCountdown.value <= 0) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }, 1000)
  } else {
    // 清理定时器
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
    autoCloseCountdown.value = 0
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})

const isRedCard = (card) => {
  if (!card) return false
  return card.includes('♥') || card.includes('♦') || card.includes('红桃') || card.includes('方块')
}

const handleClose = () => {
  visible.value = false
}

const handleContinue = () => {
  emit('continue')
  handleClose()
}
</script>

<style scoped>
.hand-result-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px 8px 0 0;
}

.hand-result-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 1.3rem;
  font-weight: bold;
}

.auto-play-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  color: #667eea;
  font-weight: 600;
}

.auto-play-hint .el-icon {
  font-size: 1.2rem;
}

.result-content {
  padding: 1rem 0;
}

.hand-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.winners-section {
  margin-bottom: 1.5rem;
}

.winners-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.winner-item {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.winner-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.winner-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
}

.winner-info {
  flex: 1;
}

.winner-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.25rem;
}

.winning-hand {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.hand-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.hand-cards {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.result-card {
  width: 45px;
  height: 63px;
  background: white;
  border-radius: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-card.red {
  color: #dc3545;
}

.result-card:not(.red) {
  color: #333;
}

.hand-description {
  font-size: 0.95rem;
  color: #667eea;
  font-weight: 600;
}

.pot-cards-section {
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.75rem;
  padding: 1rem;
}

.pot-cards-section .section-title {
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.community-cards-display {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.community-cards-display .result-card {
  background: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.pot-section {
  margin-bottom: 1.5rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 1rem;
}

.all-players-section {
  margin-bottom: 1.5rem;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.player-result-card {
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 0.75rem;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.player-result-card.winner {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border-color: #ffd43b;
  box-shadow: 0 2px 8px rgba(255, 212, 59, 0.3);
}

.player-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.player-result-name {
  font-weight: 600;
  color: #333;
}

.player-hand-cards {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.result-card.small {
  width: 35px;
  height: 49px;
  font-size: 0.85rem;
}

.player-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 600;
  color: #333;
}

.pot-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: white;
  border-radius: 0.5rem;
}

.pot-player {
  font-weight: 500;
  color: #333;
}

.pot-amount {
  font-weight: bold;
  color: #10b981;
}

.showdown-section {
  margin-bottom: 1rem;
}

.showdown-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.showdown-player {
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.showdown-player-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  text-align: center;
}

.showdown-player-cards {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
