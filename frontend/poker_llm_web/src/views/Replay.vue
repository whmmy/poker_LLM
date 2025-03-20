<template>
  <div class="replay-container">
    <!-- 控制面板 - 移到左侧 -->
    <div class="control-panel">
      <h2>控制面板</h2>
      <div class="progress">
        <span>进度: {{ currentIndex + 1 }} / {{ gameData.length }}</span>
        <el-slider 
          v-model="currentIndex" 
          :min="0" 
          :max="gameData.length - 1"
          :disabled="gameData.length === 0"
          @change="handleSliderChange"
        />
      </div>
      
      <div class="controls">
        <el-button @click="resetToStart" :disabled="currentIndex === 0">
          <el-icon><d-arrow-left /></el-icon>
        </el-button>
        <el-button @click="prevStep" :disabled="currentIndex === 0">
          <el-icon><arrow-left /></el-icon>
        </el-button>
        
        <el-button 
          type="primary" 
          @click="toggleAutoPlay"
        >
          <el-icon v-if="isAutoPlaying"><video-pause /></el-icon>
          <el-icon v-else><video-play /></el-icon>
          {{ isAutoPlaying ? '暂停' : '自动播放' }}
        </el-button>
        
        <el-button @click="nextStep" :disabled="currentIndex >= gameData.length - 1">
          <el-icon><arrow-right /></el-icon>
        </el-button>
        <el-button @click="jumpToEnd" :disabled="currentIndex >= gameData.length - 1">
          <el-icon><d-arrow-right /></el-icon>
        </el-button>
      </div>
      
      <div class="speed-control">
        <span>播放速度:</span>
        <el-select v-model="speed" @change="handleSpeedChange">
          <el-option label="慢速" :value="3000" />
          <el-option label="中速" :value="1500" />
          <el-option label="快速" :value="800" />
          <el-option label="极速" :value="300" />
        </el-select>
      </div>
      
      <el-button type="default" @click="backToHome">返回首页</el-button>
    </div>
    
    <div class="game-content">
      <div class="game-header">
        <h1>德州扑克游戏回放</h1>
        <div class="game-info">
          <div class="info-item">
            <span class="label">当前阶段:</span>
            <span class="value">{{ formatStage(currentStage) }}</span>
          </div>
          <div class="info-item">
            <span class="label">底池:</span>
            <span class="value">{{ currentPot }}</span>
          </div>
          <div class="info-item">
            <span class="label">手牌编号:</span>
            <span class="value">{{ currentAction?.hand_number || 1 }}</span>
          </div>
        </div>
      </div>
      
      <div class="poker-table">
        <!-- 公共牌区域 -->
        <div class="community-cards">
          <h3>公共牌</h3>
          <div class="cards-container">
            <transition-group name="card">
              <div 
                v-for="(card, index) in communityCards" 
                :key="card" 
                class="card"
                :style="{animationDelay: `${index * 0.2}s`}"
              >
                {{ card }}
              </div>
            </transition-group>
          </div>
        </div>
        
        <!-- 玩家区域 -->
        <div class="players-container">
          <div 
            v-for="(player, index) in players" 
            :key="player.name"
            class="player-seat"
            :class="{
              'active-player': currentAction && currentAction.player_name === player.name,
              'folded-player': player.folded
            }"
          >
            <div class="player-info">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-chips">筹码: {{ player.chips }}</div>
              <div class="player-bet">已下注: {{ player.bet_in_round }}</div>
              <div class="player-status">
                <span v-if="player.folded" class="status-tag folded">已弃牌</span>
                <span v-else-if="player.all_in" class="status-tag all-in">全押</span>
              </div>
            </div>
            
            <div class="player-cards">
              <transition-group name="card">
                <div 
                  v-for="(card, cardIndex) in player.hand" 
                  :key="`${player.name}-${card}`"
                  class="card"
                  :style="{animationDelay: `${cardIndex * 0.2}s`}"
                >
                  {{ card }}
                </div>
              </transition-group>
            </div>
          </div>
        </div>
        
        <!-- 当前行动信息 -->
        <div class="current-action" v-if="currentAction">
          <div class="action-player">{{ currentAction.player_name }}</div>
          <div class="action-type">{{ formatAction(currentAction.action) }}</div>
          <div class="action-amount" v-if="currentAction.amount > 0">金额: {{ currentAction.amount }}</div>
          <div class="action-behavior" v-if="currentAction.behavior">
            <div class="behavior-title">行为描述:</div>
            <div class="behavior-content">{{ currentAction.behavior }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { ElMessage } from 'element-plus'
import { DArrowLeft, DArrowRight, ArrowLeft, ArrowRight, VideoPlay, VideoPause } from '@element-plus/icons-vue'

const router = useRouter()
const gameStore = useGameStore()

// 从store获取数据
const gameData = computed(() => gameStore.gameData)
const currentIndex = computed({
  get: () => gameStore.currentIndex,
  set: (val) => gameStore.currentIndex = val
})
const currentAction = computed(() => gameStore.currentAction)
const players = computed(() => gameStore.players)
const communityCards = computed(() => gameStore.communityCards)
const currentPot = computed(() => gameStore.currentPot)
const currentStage = computed(() => gameStore.currentStage)
const isAutoPlaying = computed(() => gameStore.isAutoPlaying)

// 播放速度
const speed = ref(1500)

// 格式化阶段名称
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

// 格式化行动类型
const formatAction = (action) => {
  const actionMap = {
    'fold': '弃牌',
    'check': '过牌',
    'call': '跟注',
    'raise': '加注',
    'all-in': '全押',
    'small-blind': '小盲注',
    'big-blind': '大盲注'
  }
  return actionMap[action] || action
}

// 控制函数
const nextStep = () => {
  gameStore.nextStep()
}

const prevStep = () => {
  gameStore.prevStep()
}

const resetToStart = () => {
  gameStore.resetToStart()
}

const jumpToEnd = () => {
  gameStore.jumpToEnd()
}

const toggleAutoPlay = () => {
  if (isAutoPlaying.value) {
    gameStore.stopAutoPlay()
  } else {
    gameStore.startAutoPlay()
  }
}

const handleSpeedChange = (newSpeed) => {
  gameStore.setReplaySpeed(newSpeed)
}

const handleSliderChange = (value) => {
  // 如果正在自动播放，先停止
  if (isAutoPlaying.value) {
    gameStore.stopAutoPlay()
  }
}

const backToHome = () => {
  gameStore.stopAutoPlay()
  router.push('/')
}

// 检查是否有游戏数据
onMounted(() => {
  if (gameData.value.length === 0) {
    ElMessage.warning('没有游戏数据，请先上传游戏日志')
    router.push('/')
  }
  
  // 设置初始速度
  speed.value = gameStore.replaySpeed
})

// 组件销毁时停止自动播放
onUnmounted(() => {
  gameStore.stopAutoPlay()
})
</script>

<style scoped>
.replay-container {
  display: flex;
  padding: 1rem;
  gap: 1.5rem;
  height: 100vh;
}

/* 控制面板样式 - 左侧固定 */
.control-panel {
  background-color: #f5f7fa;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 2rem);
  overflow-y: auto;
}

.control-panel h2 {
  color: #409EFF;
  margin-bottom: 1.5rem;
  text-align: center;
}

.progress {
  margin-bottom: 1.5rem;
  color: #000;
}

.controls {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.speed-control {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

/* 游戏内容区域 */
.game-content {
  flex: 1;
  overflow-y: auto;
  max-width: calc(100% - 280px);
}

.game-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.game-header h1 {
  color: #409EFF;
  margin-bottom: 1rem;
}

.game-info {
  display: flex;
  gap: 2rem;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #000;
  font-weight: bold;
  margin-right: 0.5rem;
}

.info-item .value {
  color: #409EFF;
  font-weight: bold;
}

.poker-table {
  background-color: #1a6c35;
  border-radius: 50%;
  padding: 3rem;
  margin-bottom: 2rem;
  position: relative;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.community-cards {
  text-align: center;
  margin-bottom: 2rem;
}

.community-cards h3 {
  color: white;
  margin-bottom: 1rem;
}

.cards-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1rem;
  min-width: 3rem;
  min-height: 4rem;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  animation: cardAppear 0.5s ease-out;
  color: #000;
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.players-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  width: 100%;
}

.player-seat {
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 1rem;
  padding: 1rem;
  margin: 0.5rem;
  min-width: 200px;
  transition: all 0.3s ease;
}

.active-player {
  box-shadow: 0 0 15px #f8e71c;
  transform: scale(1.05);
  background-color: rgba(0, 0, 0, 0.7);
}

.folded-player {
  opacity: 0.5;
  border: 2px dashed #f56c6c;
  position: relative;
  background-color: rgba(0, 0, 0, 0.3);
}

.folded-player .player-cards {
  filter: grayscale(100%);
  opacity: 0.4;
}

.folded-player::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    rgba(245, 108, 108, 0.1),
    rgba(245, 108, 108, 0.1) 10px,
    rgba(0, 0, 0, 0.2) 10px,
    rgba(0, 0, 0, 0.2) 20px
  );
  border-radius: 1rem;
  pointer-events: none;
}

.player-status {
  margin-top: 0.5rem;
  text-align: center;
}

.status-tag {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  font-weight: bold;
  margin-top: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.folded {
  background-color: #f56c6c;
  color: white;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.7;
  }
}

.all-in {
  background-color: #e6a23c;
  color: white;
}

.current-action {
  width: 80%;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 1rem;
  margin-top: 2rem;
  max-width: 80%;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  color: #000;
}

.action-player {
  font-weight: bold;
  font-size: 1.2rem;
  color: #409EFF;
  margin-bottom: 0.5rem;
}

.action-type {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.action-behavior {
  margin-top: 1rem;
  text-align: left;
}

.behavior-title {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.behavior-content {
  font-style: italic
}
/* 卡片动画 */
.card-enter-active,
.card-leave-active {
  transition: all 0.5s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(-50px);
}

.card-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>

.control-panel {
  backgroun