<template>
  <div class="replay-container">
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
                class="card player-card"
                :style="{animationDelay: `${cardIndex * 0.2}s`, left: `${cardIndex * 60}px`, zIndex: cardIndex + 1}"
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
    
    <!-- 控制面板 -->
    <div class="control-panel">
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  font-family: 'Arial', sans-serif;
}

.game-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.game-header h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 2rem;
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
  font-weight: bold;
  margin-right: 0.5rem;
  color: #606266;
}

.info-item .value {
  color: #409EFF;
  font-weight: bold;
}

.poker-table {
  background-color: #1a6c35;
  border-radius: 50%;
  padding: 3rem;
  margin: 0 auto 2rem;
  position: relative;
  width: 800px;
  height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  border: 15px solid #8B4513;
}

.community-cards {
  text-align: center;
  margin-bottom: 2rem;
}

.community-cards h3 {
  color: #f8f9fa;
  margin-bottom: 1rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.cards-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
  position: relative;
  height: 100px;
  margin: 10px 0;
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
  border: 1px solid #dcdfe6;
  position: absolute;
  z-index: 1;
  margin: 0 5px;
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
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  width: 100%;
  margin-top: 20px;
}

.player-seat {
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 1rem;
  padding: 1rem;
  margin: 0.5rem;
  min-width: 180px;
  min-height: 200px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
}

.active-player {
  box-shadow: 0 0 15px #f8e71c;
  transform: scale(1.05);
  background-color: rgba(0, 0, 0, 0.7);
  border: 1px solid #f8e71c;
}

.folded-player {
  opacity: 0.6;
}

.player-info {
  color: #f8f9fa;
  margin-bottom: 1rem;
}

.player-name {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #f8f9fa;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.player-chips {
  color: #67c23a;
  font-weight: bold;
}

.player-bet {
  color: #e6a23c;
}

.player-cards {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  position: relative;
  height: 80px;
  margin-top: 10px;
  width: 100%;
}

.player-card {
  position: absolute;
  transition: all 0.3s ease;
}

.status-tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  margin-top: 0.5rem;
  font-weight: bold;
}

.folded {
  background-color: #f56c6c;
  color: white;
}

.all-in {
  background-color: #e6a23c;
  color: white;
}

.current-action {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-top: 2rem;
  width: 400px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border: 1px solid #dcdfe6;
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
  color: #303133;
}

.action-amount {
  color: #67c23a;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.action-behavior {
  margin-top: 1rem;
  text-align: left;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
}

.behavior-title {
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #303133;
}

.behavior-content {
  font-style: italic;
  color: #606266;
  line-height: 1.5;
}

.control-panel {
  background-color: #f5f7fa;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.progress {
  margin-bottom: 1.5rem;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.speed-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
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