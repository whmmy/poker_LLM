import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  // 游戏数据
  const gameData = ref([])
  // 当前回放索引
  const currentIndex = ref(0)
  // 回放速度（毫秒）
  const replaySpeed = ref(1500)
  // 是否自动播放
  const isAutoPlaying = ref(false)
  // 播放定时器
  const playTimer = ref(null)
  
  // 设置游戏数据
  function setGameData(data) {
    gameData.value = data
    currentIndex.value = 0
  }
  
  // 获取当前动作
  const currentAction = computed(() => {
    if (gameData.value.length > 0 && currentIndex.value < gameData.value.length) {
      return gameData.value[currentIndex.value]
    }
    return null
  })
  
  // 获取所有玩家信息
  const players = computed(() => {
    // 查找最新的玩家信息记录
    let playerInfo = []
    
    // 首先找到基础玩家信息
    for (let i = currentIndex.value; i >= 0; i--) {
      const record = gameData.value[i]
      if (record.type === 1 && record.players) {
        playerInfo = JSON.parse(JSON.stringify(record.players))
        break
      }
    }
    
    // 然后检查当前索引之前的所有弃牌动作，更新玩家状态
    if (playerInfo.length > 0) {
      for (let i = 0; i <= currentIndex.value; i++) {
        const record = gameData.value[i]
        if (record.type === 3 && record.action === 'fold') {
          // 找到对应玩家并更新弃牌状态
          const player = playerInfo.find(p => p.name === record.player_name)
          if (player) {
            player.folded = true
          }
        }
      }
    }
    
    return playerInfo
  })
  
  // 获取当前公共牌
  const communityCards = computed(() => {
    // 查找最新的公共牌记录
    for (let i = currentIndex.value; i >= 0; i--) {
      const record = gameData.value[i]
      if (record.type === 2 && record.community_cards) {
        return record.community_cards
      }
    }
    return []
  })
  
  // 获取当前底池
  const currentPot = computed(() => {
    if (currentAction.value && currentAction.value.pot) {
      return currentAction.value.pot
    }
    return 0
  })
  
  // 获取当前阶段
  const currentStage = computed(() => {
    if (currentAction.value && currentAction.value.stage) {
      return currentAction.value.stage
    }
    return ''
  })
  
  // 前进到下一步
  function nextStep() {
    if (currentIndex.value < gameData.value.length - 1) {
      currentIndex.value++
      return true
    }
    return false
  }
  
  // 回到上一步
  function prevStep() {
    if (currentIndex.value > 0) {
      currentIndex.value--
      return true
    }
    return false
  }
  
  // 开始自动播放
  function startAutoPlay() {
    if (isAutoPlaying.value) return
    
    isAutoPlaying.value = true
    playTimer.value = setInterval(() => {
      const hasNext = nextStep()
      if (!hasNext) {
        stopAutoPlay()
      }
    }, replaySpeed.value)
  }
  
  // 停止自动播放
  function stopAutoPlay() {
    if (playTimer.value) {
      clearInterval(playTimer.value)
      playTimer.value = null
    }
    isAutoPlaying.value = false
  }
  
  // 设置播放速度
  function setReplaySpeed(speed) {
    replaySpeed.value = speed
    // 如果正在播放，重新启动计时器以应用新速度
    if (isAutoPlaying.value) {
      stopAutoPlay()
      startAutoPlay()
    }
  }
  
  // 重置到开始
  function resetToStart() {
    stopAutoPlay()
    currentIndex.value = 0
  }
  
  // 跳到结束
  function jumpToEnd() {
    stopAutoPlay()
    currentIndex.value = gameData.value.length - 1
  }
  
  return {
    gameData,
    currentIndex,
    replaySpeed,
    isAutoPlaying,
    currentAction,
    players,
    communityCards,
    currentPot,
    currentStage,
    setGameData,
    nextStep,
    prevStep,
    startAutoPlay,
    stopAutoPlay,
    setReplaySpeed,
    resetToStart,
    jumpToEnd
  }
})