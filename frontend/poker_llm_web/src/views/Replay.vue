<template>
  <div class="replay-container" v-if="hasData">
    <!-- 左侧控制面板 -->
    <div class="control-panel">
      <div class="panel-header">
        <h2>控制面板</h2>
        <el-button
          :icon="ArrowLeft"
          circle
          size="small"
          @click="backToHome"
          title="返回首页"
        />
      </div>

      <!-- 进度控制 -->
      <div class="progress-section">
        <div class="progress-info">
          <span>决策进度</span>
          <el-tag size="small">{{ currentDecisionIndex + 1 }} / {{ totalDecisions }}</el-tag>
        </div>
        <el-slider
          v-model="currentDecisionIndex"
          :min="0"
          :max="totalDecisions - 1"
          :show-tooltip="false"
          @change="handleSliderChange"
        />
      </div>

      <!-- 播放控制 -->
      <div class="play-controls">
        <el-button-group>
          <el-button
            :icon="DArrowLeft"
            :disabled="currentDecisionIndex === 0"
            @click="goToStart"
            title="回到开始"
          />
          <el-button
            :icon="ArrowLeft"
            :disabled="currentDecisionIndex === 0"
            @click="previous"
            title="上一步"
          />
          <el-button
            :type="isAutoPlaying ? 'danger' : 'primary'"
            :icon="isAutoPlaying ? VideoPause : VideoPlay"
            @click="togglePlay"
          >
            {{ isAutoPlaying ? '暂停' : '播放' }}
          </el-button>
          <el-button
            :icon="ArrowRight"
            :disabled="currentDecisionIndex >= totalDecisions - 1"
            @click="next"
            title="下一步"
          />
          <el-button
            :icon="DArrowRight"
            :disabled="currentDecisionIndex >= totalDecisions - 1"
            @click="goToEnd"
            title="跳到结尾"
          />
        </el-button-group>
      </div>

      <!-- 速度控制 -->
      <div class="speed-section">
        <span>播放速度:</span>
        <el-select v-model="speed" size="small" @change="handleSpeedChange">
          <el-option label="慢速" :value="3000" />
          <el-option label="中速" :value="1500" />
          <el-option label="快速" :value="800" />
          <el-option label="极速" :value="300" />
        </el-select>
      </div>

      <!-- 视图模式选择 -->
      <div class="view-mode-section">
        <div class="nav-title">视图模式</div>
        <el-radio-group v-model="viewMode" size="small" @change="handleViewModeChange">
          <el-radio-button label="spectator">
            <el-icon><view /></el-icon>
            观看者
          </el-radio-button>
          <el-radio-button label="player">
            <el-icon><user /></el-icon>
            角色视角
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 角色选择器（仅在角色视角模式下显示） -->
      <div class="player-selector" v-if="viewMode === 'player'">
        <div class="nav-title">选择角色</div>
        <el-select
          v-model="selectedPlayer"
          placeholder="选择玩家"
          size="small"
          @change="handlePlayerChange"
        >
          <el-option
            v-for="player in gameMetadata?.players || []"
            :key="player.name"
            :label="player.name"
            :value="player.name"
          >
            <span>{{ player.name }}</span>
            <span style="color: #8492a6; font-size: 12px; margin-left: 8px;">({{ player.model_name }})</span>
          </el-option>
        </el-select>
      </div>

      <!-- 手牌导航 -->
      <div class="hand-navigation" v-if="handNumbers.length > 0">
        <div class="nav-title">手牌导航</div>
        <div class="hand-list">
          <el-tag
            v-for="handNum in handNumbers"
            :key="handNum"
            :type="currentHandNumber === handNum ? 'primary' : 'info'"
            :effect="currentHandNumber === handNum ? 'dark' : 'plain'"
            @click="jumpToHand(handNum)"
            class="hand-tag"
            closable
          >
            #{{ handNum }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 中间游戏区域 -->
    <div class="game-area">
      <!-- 游戏信息栏 -->
      <div class="game-info-bar">
        <div class="info-group">
          <div class="info-item">
            <span class="label">手牌:</span>
            <el-tag size="small" type="primary">#{{ currentHandNumber }}</el-tag>
          </div>
          <div class="info-item">
            <span class="label">阶段:</span>
            <el-tag size="small" type="success">{{ formatStage(currentStage) }}</el-tag>
          </div>
        </div>
        <div class="info-group">
          <div class="info-item">
            <span class="label">底池:</span>
            <span class="pot-value">{{ currentPot }}</span>
          </div>
        </div>
      </div>

      <!-- 扑克桌面 -->
      <div class="poker-table">
        <!-- 公共牌 -->
        <div class="community-area">
          <div class="area-title">公共牌</div>
          <div class="cards-row">
            <transition-group name="card">
              <div
                v-for="(card, index) in currentCommunityCards"
                :key="card"
                class="table-card"
                :class="{ 'red': isRedCard(card) }"
                :style="{ animationDelay: `${index * 0.15}s` }"
              >
                {{ card }}
              </div>
            </transition-group>
            <div v-if="currentCommunityCards.length === 0" class="no-cards">暂无</div>
          </div>
        </div>

        <!-- 玩家区域 -->
        <div class="players-area">
          <div
            v-for="(player, index) in currentPlayers"
            :key="player.name"
            class="player-seat"
            :class="getSeatClasses(player)"
          >
            <!-- 当前行动指示器 -->
            <div v-if="isCurrentPlayer(player.name)" class="current-indicator">
              <el-icon><star /></el-icon>
            </div>

            <div class="player-header">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-chips">💰 {{ player.chips }}</div>
            </div>

            <!-- 玩家手牌 -->
            <div class="player-cards" v-if="shouldShowCards(player)">
              <div
                v-for="(card, cardIndex) in getPlayerCards(player)"
                :key="`${player.name}-${cardIndex}`"
                class="player-card"
                :class="{ 'red': isRedCard(card) }"
              >
                {{ card }}
              </div>
            </div>

            <!-- 玩家状态 -->
            <div class="player-status">
              <el-tag v-if="player.folded" size="small" type="danger">已弃牌</el-tag>
              <el-tag v-else-if="player.all_in" size="small" type="warning">全押</el-tag>
              <div v-else-if="player.bet_in_round > 0" class="bet-amount">
                已下注: {{ player.bet_in_round }}
              </div>
            </div>
          </div>
        </div>

        <!-- 当前行动信息 -->
        <div class="action-display" v-if="displayDecision">
          <div class="action-header">
            <div class="action-player">{{ displayDecision.player_name }}</div>
            <el-tag :type="getActionTagType(displayDecision.parsed_action)">
              {{ formatAction(displayDecision.parsed_action) }}
              <span v-if="displayDecision.action_amount > 0">: {{ displayDecision.action_amount }}</span>
            </el-tag>
          </div>
          <div class="action-reason" v-if="displayDecision.play_reason">
            <el-icon><chat-line-round /></el-icon>
            <span>{{ displayDecision.play_reason }}</span>
          </div>
          <div class="action-behavior" v-if="displayDecision.behavior">
            <el-icon><view /></el-icon>
            <span>"{{ displayDecision.behavior }}"</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 手牌结算弹窗 -->
    <HandResultModal
      v-model="showHandResult"
      :result-data="handResultData"
      :is-auto-playing="isAutoPlaying"
      @continue="handleContinueAfterResult"
    />

    <!-- 右侧详情面板 -->
    <div class="details-panel" v-if="showDetailsPanel">
      <div class="panel-tabs">
        <el-radio-group v-model="activeTab" size="small">
          <el-radio-button label="decisions">
            <el-icon><check /></el-icon>
            决策
          </el-radio-button>
          <el-radio-button label="reflections">
            <el-icon><refresh /></el-icon>
            反思
          </el-radio-button>
          <el-radio-button label="stats">
            <el-icon><data-analysis /></el-icon>
            统计
          </el-radio-button>
        </el-radio-group>
        <el-button
          :icon="showPanel ? Close : ArrowRight"
          circle
          size="small"
          @click="togglePanel"
        />
      </div>

      <div class="panel-content" v-show="showPanel">
        <div v-show="activeTab === 'decisions'" class="tab-content">
          <template v-if="viewMode === 'spectator'">
            <LLMDecisionDetail v-if="currentDecision" :decision="currentDecision" />
            <el-empty v-else description="暂无决策数据" />
          </template>
          <template v-else>
            <LLMDecisionDetail v-if="filteredDecision" :decision="filteredDecision" />
            <el-empty v-else description="角色视角模式下只显示选中玩家的决策" />
          </template>
        </div>

        <div v-show="activeTab === 'reflections'" class="tab-content">
          <LLMReflectionView :reflections="llmReflections" />
        </div>

        <div v-show="activeTab === 'stats'" class="tab-content">
          <GameStatsView
            :player-stats="playerStats"
            :decisions-by-hand="decisionsByHand"
            :game-metadata="gameMetadata"
            @jump-to-hand="jumpToHand"
          />
        </div>
      </div>
    </div>
  </div>

  <!-- 无数据提示 -->
  <div v-else class="no-data-container">
    <el-result
      icon="warning"
      title="没有游戏数据"
      sub-title="请先上传游戏日志文件"
    >
      <template #extra>
        <el-button type="primary" @click="backToHome">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import {
  ArrowLeft, DArrowLeft, ArrowRight, DArrowRight, VideoPlay, VideoPause,
  Star, Check, Refresh, DataAnalysis, Close, ChatLineRound, View, User
} from '@element-plus/icons-vue'
import LLMDecisionDetail from '@/components/LLMDecisionDetail.vue'
import LLMReflectionView from '@/components/LLMReflectionView.vue'
import GameStatsView from '@/components/GameStatsView.vue'
import HandResultModal from '@/components/HandResultModal.vue'

const router = useRouter()
const gameStore = useGameStore()

// 响应式数据
const speed = ref(1500)
const showPanel = ref(true)
const showDetailsPanel = ref(true)
const showHandResult = ref(false)
const isJumping = ref(false) // 标记是否正在跳转，避免跳转时触发结算弹窗
let autoCloseTimer = null // 自动关闭结算弹窗的定时器

// 从 store 获取计算属性和状态
const hasData = computed(() => gameStore.fullGameLog !== null)
const currentDecisionIndex = computed({
  get: () => gameStore.currentDecisionIndex,
  set: (val) => gameStore.currentDecisionIndex = val
})
const currentDecision = computed(() => gameStore.currentDecision)
const currentPlayers = computed(() => gameStore.currentPlayers)
const currentCommunityCards = computed(() => gameStore.currentCommunityCards)
const currentPot = computed(() => gameStore.currentPot)
const currentStage = computed(() => gameStore.currentStage)
const currentHandNumber = computed(() => gameStore.currentHandNumber)
const isAutoPlaying = computed(() => gameStore.isAutoPlaying)
const activeTab = computed({
  get: () => gameStore.activeTab,
  set: (val) => gameStore.setActiveTab(val)
})

const totalDecisions = computed(() => gameStore.llmDecisions.length)
const llmReflections = computed(() => gameStore.llmReflections)
const playerStats = computed(() => gameStore.playerStats)
const decisionsByHand = computed(() => gameStore.decisionsByHand)
const gameMetadata = computed(() => gameStore.gameMetadata)
const viewMode = computed({
  get: () => gameStore.viewMode,
  set: (val) => gameStore.setViewMode(val)
})
const selectedPlayer = computed({
  get: () => gameStore.selectedPlayer,
  set: (val) => gameStore.setSelectedPlayer(val)
})
const filteredDecision = computed(() => gameStore.filteredDecision)
const handResultData = computed(() => gameStore.handResultData)

// 显示的决策（根据视图模式）
const displayDecision = computed(() => {
  if (viewMode.value === 'spectator') {
    return currentDecision.value
  }
  return filteredDecision.value
})

const handNumbers = computed(() => {
  return Object.keys(decisionsByHand.value).map(Number).sort((a, b) => a - b)
})

// 方法
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

const getActionTagType = (action) => {
  const typeMap = {
    'fold': 'danger',
    'check': 'info',
    'call': 'success',
    'raise': 'warning',
    'all-in': 'danger'
  }
  return typeMap[action] || 'info'
}

const isRedCard = (card) => {
  if (!card) return false
  return card.includes('♥') || card.includes('♦') || card.includes('红桃') || card.includes('方块')
}

const isCurrentPlayer = (playerName) => {
  return currentDecision.value && currentDecision.value.player_name === playerName
}

const shouldShowCards = (player) => {
  // 观看者模式：显示所有未弃牌玩家的手牌
  if (viewMode.value === 'spectator' && !player.folded) {
    // 在有决策数据时显示手牌
    return currentDecision.value !== null
  }
  // 角色视角模式：只显示选中玩家的手牌
  if (viewMode.value === 'player' && player.name === selectedPlayer.value && !player.folded) {
    return currentDecision.value !== null
  }
  // 如果是摊牌阶段，显示所有未弃牌玩家的手牌
  if (currentStage.value === 'showdown' && !player.folded) {
    return true
  }
  return false
}

const getPlayerCards = (player) => {
  if (currentDecision.value && currentDecision.value.game_state) {
    const gameState = currentDecision.value.game_state
    // 查找所有玩家的手牌（从 game_state.players_info 中获取）
    const playersInfo = gameState.players_info || []
    const playerInfo = playersInfo.find(p => p.name === player.name)
    if (playerInfo && playerInfo.hand) {
      return playerInfo.hand
    }
    // 兼容旧格式
    if (gameState.hand && isCurrentPlayer(player.name)) {
      return gameState.hand
    }
  }
  return []
}

const getSeatClasses = (player) => {
  return {
    'current': isCurrentPlayer(player.name),
    'folded': player.folded,
    'all-in': player.all_in
  }
}

const handleSliderChange = () => {
  isJumping.value = true // 标记为跳转操作
  if (isAutoPlaying.value) {
    gameStore.stopAutoPlay()
  }
  setTimeout(() => {
    isJumping.value = false
  }, 100)
}

const handleSpeedChange = () => {
  gameStore.setReplaySpeed(speed.value)
}

const previous = () => {
  gameStore.prevDecision()
}

const next = () => {
  gameStore.nextDecision()
}

const goToStart = () => {
  isJumping.value = true
  gameStore.resetToStart()
  setTimeout(() => {
    isJumping.value = false
  }, 100)
}

const goToEnd = () => {
  isJumping.value = true
  gameStore.jumpToEnd()
  setTimeout(() => {
    isJumping.value = false
  }, 100)
}

const togglePlay = () => {
  if (isAutoPlaying.value) {
    gameStore.stopAutoPlay()
  } else {
    gameStore.startAutoPlay()
  }
}

const jumpToHand = (handNumber) => {
  isJumping.value = true // 标记为跳转操作
  gameStore.jumpToHand(handNumber)
  // 延迟重置标志位，确保 watch 不会触发
  setTimeout(() => {
    isJumping.value = false
  }, 100)
}

const togglePanel = () => {
  showPanel.value = !showPanel.value
}

const backToHome = () => {
  gameStore.stopAutoPlay()
  router.push('/')
}

// 处理视图模式变化
const handleViewModeChange = (mode) => {
  gameStore.setViewMode(mode)
}

// 处理玩家选择变化
const handlePlayerChange = (playerName) => {
  gameStore.setSelectedPlayer(playerName)
}

// 处理手牌结算后的继续
const handleContinueAfterResult = () => {
  showHandResult.value = false
  gameStore.handResultData = null
  // 清理自动关闭定时器
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
    autoCloseTimer = null
  }
}

// 自动关闭结算弹窗并继续播放
const autoCloseAndContinue = () => {
  // 5秒后自动关闭并继续
  autoCloseTimer = setTimeout(() => {
    showHandResult.value = false
    gameStore.handResultData = null
    gameStore.startAutoPlay()
    autoCloseTimer = null
  }, 5000)
}

// 监听决策变化，检查是否显示手牌结算
watch(currentDecision, (newDecision, oldDecision) => {
  if (!newDecision) return

  // 如果正在跳转，不显示结算弹窗
  if (isJumping.value) return

  const currentHandNum = newDecision.hand_number
  const oldHandNum = oldDecision?.hand_number

  // 检查是否是手牌的最后一个决策（下一手的 hand_number 变了）
  const isHandEnd = oldHandNum && currentHandNum !== oldHandNum

  if (isHandEnd) {
    // 检查上一手牌是否有结算数据
    const handResult = gameStore.getHandResult(oldHandNum)
    if (handResult) {
      // 清理之前的定时器
      if (autoCloseTimer) {
        clearTimeout(autoCloseTimer)
        autoCloseTimer = null
      }

      // 传入正确的手牌号（上一手）
      gameStore.checkHandEnd(oldHandNum)

      if (gameStore.handResultData) {
        showHandResult.value = true

        // 如果正在自动播放，5秒后自动关闭并继续
        if (isAutoPlaying.value) {
          autoCloseAndContinue()
        }
      }
    }
  }
})

// 键盘快捷键
const handleKeyPress = (e) => {
  switch(e.key) {
    case 'ArrowLeft':
      previous()
      break
    case 'ArrowRight':
      next()
      break
    case ' ':
      e.preventDefault()
      togglePlay()
      break
    case 'Home':
      goToStart()
      break
    case 'End':
      goToEnd()
      break
  }
}

// 生命周期
onMounted(() => {
  if (!hasData.value) {
    return
  }
  speed.value = gameStore.replaySpeed
  document.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  gameStore.stopAutoPlay()
  // 清理自动关闭定时器
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
    autoCloseTimer = null
  }
  document.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.replay-container {
  display: grid;
  grid-template-columns: 280px 1fr 400px;
  gap: 1rem;
  padding: 1rem;
  height: 100vh;
  background: #f0f2f5;
}

/* 控制面板 */
.control-panel {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.play-controls {
  display: flex;
  justify-content: center;
}

.speed-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.hand-navigation {
  border-top: 1px solid #f0f0f0;
  padding-top: 1rem;
}

.nav-title {
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #333;
}

.hand-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hand-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.hand-tag:hover {
  transform: scale(1.05);
}

.view-mode-section, .player-selector {
  border-top: 1px solid #f0f0f0;
  padding-top: 1rem;
}

.view-mode-section :deep(.el-radio-group) {
  width: 100%;
  display: flex;
}

.view-mode-section :deep(.el-radio-button) {
  flex: 1;
}

.view-mode-section :deep(.el-radio-button__inner) {
  width: 100%;
}

.player-selector .el-select {
  width: 100%;
}

/* 游戏区域 */
.game-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: hidden;
}

.game-info-bar {
  background: white;
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-group {
  display: flex;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-item .label {
  color: #666;
  font-size: 0.9rem;
}

.pot-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #f59e0b;
}

.poker-table {
  flex: 1;
  background: linear-gradient(135deg, #1a6c35 0%, #2d8a4e 100%);
  border-radius: 2rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.poker-table::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 70%;
  border: 8px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  pointer-events: none;
}

.community-area {
  text-align: center;
  z-index: 1;
}

.area-title {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.cards-row {
  display: flex;
  justify-content: center;
  gap: 1rem;
  min-height: 100px;
  align-items: center;
}

.table-card, .player-card {
  width: 60px;
  height: 84px;
  background: white;
  border-radius: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: cardDeal 0.4s ease-out backwards;
}

.table-card.red, .player-card.red {
  color: #dc3545;
}

.table-card:not(.red), .player-card:not(.red) {
  color: #333;
}

.no-cards {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.players-area {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  z-index: 1;
}

.player-seat {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1rem;
  min-width: 150px;
  position: relative;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.player-seat.current {
  border-color: #ffd43b;
  box-shadow: 0 0 20px rgba(255, 212, 59, 0.5);
  transform: scale(1.05);
}

.player-seat.folded {
  opacity: 0.5;
}

.player-seat.all-in {
  border-color: #fd7e14;
  box-shadow: 0 0 15px rgba(253, 126, 20, 0.4);
}

.current-indicator {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffd43b;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #333;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translateX(-50%) scale(1);
  }
  50% {
    transform: translateX(-50%) scale(1.1);
  }
}

.player-header {
  text-align: center;
  margin-bottom: 0.75rem;
}

.player-name {
  color: white;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.player-chips {
  color: #ffd43b;
  font-size: 0.9rem;
}

.player-cards {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.player-card {
  width: 45px;
  height: 63px;
  font-size: 1.1rem;
}

.player-status {
  text-align: center;
  min-height: 24px;
}

.bet-amount {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}

.action-display {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.action-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.action-player {
  font-weight: bold;
  font-size: 1.2rem;
  color: #333;
}

.action-reason, .action-behavior {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  text-align: left;
  margin-top: 0.75rem;
  font-size: 0.95rem;
  color: #666;
  line-height: 1.5;
}

.action-behavior {
  font-style: italic;
  color: #888;
}

/* 详情面板 */
.details-panel {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-tabs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.panel-content {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: 100%;
  overflow-y: auto;
  padding: 0;
}

/* 无数据容器 */
.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
}

/* 动画 */
@keyframes cardDeal {
  from {
    opacity: 0;
    transform: translateY(-50px) rotateY(180deg);
  }
  to {
    opacity: 1;
    transform: translateY(0) rotateY(0);
  }
}

.card-enter-active {
  transition: all 0.4s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

/* 响应式 */
@media (max-width: 1400px) {
  .replay-container {
    grid-template-columns: 250px 1fr 350px;
  }
}

@media (max-width: 1024px) {
  .replay-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .control-panel, .details-panel {
    height: auto;
    max-height: 300px;
  }
}
</style>
