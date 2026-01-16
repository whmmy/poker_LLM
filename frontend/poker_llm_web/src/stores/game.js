import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  // 完整的游戏日志数据（新格式）
  const fullGameLog = ref(null)
  // 当前回放的索引（基于 llm_decisions 数组）
  const currentDecisionIndex = ref(0)
  // 当前事件索引（基于 events 数组）
  const currentEventIndex = ref(0)
  // 回放速度（毫秒）
  const replaySpeed = ref(1500)
  // 是否自动播放
  const isAutoPlaying = ref(false)
  // 播放定时器
  const playTimer = ref(null)
  // 是否显示 LLM 详情面板
  const showLLMDetails = ref(true)
  // 当前选中的标签页 (decisions/reflections/stats)
  const activeTab = ref('decisions')
  // 是否显示 LLM 决策详情
  const showDecisionDetails = ref(true)
  // 视图模式: 'spectator' (观看者模式) 或 'player' (角色视角模式)
  const viewMode = ref('spectator')
  // 选中的玩家名称（角色视角模式下使用）
  const selectedPlayer = ref(null)
  // 手牌结束结算数据
  const handResultData = ref(null)

  // 设置游戏数据
  function setGameData(data) {
    fullGameLog.value = data
    currentDecisionIndex.value = 0
    currentEventIndex.value = 0
  }

  // 游戏元信息
  const gameMetadata = computed(() => {
    if (!fullGameLog.value) return null
    return {
      game_id: fullGameLog.value.game_id,
      start_time: fullGameLog.value.start_time,
      end_time: fullGameLog.value.end_time,
      initial_chips: fullGameLog.value.initial_chips,
      small_blind: fullGameLog.value.small_blind,
      big_blind: fullGameLog.value.big_blind,
      players: fullGameLog.value.players || []
    }
  })

  // LLM 决策列表
  const llmDecisions = computed(() => {
    if (!fullGameLog.value) return []
    return fullGameLog.value.llm_decisions || []
  })

  // LLM 反思列表
  const llmReflections = computed(() => {
    if (!fullGameLog.value) return []
    return fullGameLog.value.llm_reflections || []
  })

  // 游戏事件列表
  const gameEvents = computed(() => {
    if (!fullGameLog.value) return []
    return fullGameLog.value.events || []
  })

  // 按手牌分组的事件
  const eventsByHand = computed(() => {
    const groups = {}
    gameEvents.value.forEach(event => {
      const handNum = event.hand_number
      if (!groups[handNum]) {
        groups[handNum] = []
      }
      groups[handNum].push(event)
    })
    return groups
  })

  // 获取某手牌的结算结果
  const getHandResult = (handNumber) => {
    const events = eventsByHand.value[handNumber] || []
    return events.find(e => e.type === 6) // type 6 是 HandResultLog
  }

  // 当前决策
  const currentDecision = computed(() => {
    if (llmDecisions.value.length > 0 && currentDecisionIndex.value < llmDecisions.value.length) {
      return llmDecisions.value[currentDecisionIndex.value]
    }
    return null
  })

  // 当前事件
  const currentEvent = computed(() => {
    if (gameEvents.value.length > 0 && currentEventIndex.value < gameEvents.value.length) {
      return gameEvents.value[currentEventIndex.value]
    }
    return null
  })

  // 获取当前游戏状态的玩家信息
  const currentPlayers = computed(() => {
    if (!currentDecision.value || !currentDecision.value.game_state) {
      return gameMetadata.value?.players || []
    }
    return currentDecision.value.game_state.players_info || []
  })

  // 当前公共牌
  const currentCommunityCards = computed(() => {
    if (!currentDecision.value || !currentDecision.value.game_state) {
      return []
    }
    return currentDecision.value.game_state.community_cards || []
  })

  // 当前底池
  const currentPot = computed(() => {
    if (!currentDecision.value || !currentDecision.value.game_state) {
      return 0
    }
    return currentDecision.value.game_state.pot || 0
  })

  // 当前阶段
  const currentStage = computed(() => {
    if (!currentDecision.value) return ''
    return currentDecision.value.stage || ''
  })

  // 当前手牌编号
  const currentHandNumber = computed(() => {
    if (!currentDecision.value) return 1
    return currentDecision.value.hand_number || 1
  })

  // 玩家统计信息
  const playerStats = computed(() => {
    if (!fullGameLog.value || !fullGameLog.value.players) return []

    const stats = {}
    const players = fullGameLog.value.players

    // 初始化统计
    players.forEach(p => {
      stats[p.name] = {
        name: p.name,
        model_name: p.model_name,
        initial_chips: p.initial_chips,
        decisions: [],
        reflections: [],
        final_chips: 0,
        rank: 0
      }
    })

    // 统计决策
    llmDecisions.value.forEach(d => {
      if (stats[d.player_name]) {
        stats[d.player_name].decisions.push(d)
      }
    })

    // 统计反思
    llmReflections.value.forEach(r => {
      if (stats[r.player_name]) {
        stats[r.player_name].reflections.push(r)
      }
    })

    // 设置最终筹码和排名
    if (fullGameLog.value.final_rankings) {
      fullGameLog.value.final_rankings.forEach(r => {
        if (stats[r.name]) {
          stats[r.name].final_chips = r.final_chips
          stats[r.name].rank = r.rank
        }
      })
    }

    return Object.values(stats)
  })

  // 按手牌分组的决策
  const decisionsByHand = computed(() => {
    const groups = {}
    llmDecisions.value.forEach(d => {
      const handNum = d.hand_number
      if (!groups[handNum]) {
        groups[handNum] = []
      }
      groups[handNum].push(d)
    })
    return groups
  })

  // 按手牌分组的反思
  const reflectionsByHand = computed(() => {
    const groups = {}
    llmReflections.value.forEach(r => {
      const handNum = r.hand_number
      if (!groups[handNum]) {
        groups[handNum] = []
      }
      groups[handNum].push(r)
    })
    return groups
  })

  // 前进到下一个决策
  function nextDecision() {
    if (currentDecisionIndex.value < llmDecisions.value.length - 1) {
      currentDecisionIndex.value++
      syncEventIndex()
      return true
    }
    return false
  }

  // 回到上一个决策
  function prevDecision() {
    if (currentDecisionIndex.value > 0) {
      currentDecisionIndex.value--
      syncEventIndex()
      return true
    }
    return false
  }

  // 同步事件索引到决策对应的时间点
  function syncEventIndex() {
    if (!currentDecision.value) return

    const decisionTimestamp = currentDecision.value.timestamp
    let closestIndex = 0
    let minDiff = Infinity

    gameEvents.value.forEach((event, index) => {
      if (event.timestamp) {
        const diff = Math.abs(new Date(event.timestamp) - new Date(decisionTimestamp))
        if (diff < minDiff) {
          minDiff = diff
          closestIndex = index
        }
      }
    })

    currentEventIndex.value = closestIndex
  }

  // 跳转到指定决策
  function jumpToDecision(index) {
    if (index >= 0 && index < llmDecisions.value.length) {
      currentDecisionIndex.value = index
      syncEventIndex()
    }
  }

  // 跳转到指定手牌
  function jumpToHand(handNumber) {
    const decisionIndex = llmDecisions.value.findIndex(d => d.hand_number === handNumber)
    if (decisionIndex !== -1) {
      jumpToDecision(decisionIndex)
    }
  }

  // 开始自动播放
  function startAutoPlay() {
    if (isAutoPlaying.value) return

    isAutoPlaying.value = true
    playTimer.value = setInterval(() => {
      const hasNext = nextDecision()
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
    if (isAutoPlaying.value) {
      stopAutoPlay()
      startAutoPlay()
    }
  }

  // 重置到开始
  function resetToStart() {
    stopAutoPlay()
    currentDecisionIndex.value = 0
    currentEventIndex.value = 0
  }

  // 跳到结束
  function jumpToEnd() {
    stopAutoPlay()
    currentDecisionIndex.value = llmDecisions.value.length - 1
    syncEventIndex()
  }

  // 切换 LLM 详情面板
  function toggleLLMDetails() {
    showLLMDetails.value = !showLLMDetails.value
  }

  // 设置当前标签页
  function setActiveTab(tab) {
    activeTab.value = tab
  }

  // 切换决策详情显示
  function toggleDecisionDetails() {
    showDecisionDetails.value = !showDecisionDetails.value
  }

  // 设置视图模式
  function setViewMode(mode) {
    viewMode.value = mode
    if (mode === 'player' && !selectedPlayer.value) {
      // 如果切换到玩家模式且没有选中玩家，选择第一个玩家
      const players = gameMetadata.value?.players || []
      if (players.length > 0) {
        selectedPlayer.value = players[0].name
      }
    }
  }

  // 设置选中的玩家
  function setSelectedPlayer(playerName) {
    selectedPlayer.value = playerName
  }

  // 过滤当前决策（根据视图模式）
  const filteredDecision = computed(() => {
    if (!currentDecision.value) return null
    if (viewMode.value === 'spectator') {
      return currentDecision.value
    }
    // 角色视角模式：只返回选中玩家的决策
    if (currentDecision.value.player_name === selectedPlayer.value) {
      return currentDecision.value
    }
    return null
  })

  // 检测手牌结束并显示结算
  function checkHandEnd() {
    if (!currentDecision.value || !currentDecision.value.game_state) return

    const gameState = currentDecision.value.game_state
    // 检查是否是摊牌阶段且有手牌结果
    if (currentDecision.value.stage === 'showdown' && gameState.hand_result) {
      handResultData.value = {
        handNumber: currentDecision.value.hand_number,
        winners: gameState.hand_result.winners || [],
        potDistribution: gameState.hand_result.pot_distribution || [],
        showCards: gameState.showdown_cards || {}
      }
    }
  }

  return {
    fullGameLog,
    currentDecisionIndex,
    currentEventIndex,
    replaySpeed,
    isAutoPlaying,
    showLLMDetails,
    activeTab,
    showDecisionDetails,
    gameMetadata,
    llmDecisions,
    llmReflections,
    gameEvents,
    currentDecision,
    currentEvent,
    currentPlayers,
    currentCommunityCards,
    currentPot,
    currentStage,
    currentHandNumber,
    playerStats,
    decisionsByHand,
    reflectionsByHand,
    eventsByHand,
    getHandResult,
    setGameData,
    nextDecision,
    prevDecision,
    jumpToDecision,
    jumpToHand,
    startAutoPlay,
    stopAutoPlay,
    setReplaySpeed,
    resetToStart,
    jumpToEnd,
    toggleLLMDetails,
    setActiveTab,
    toggleDecisionDetails,
    viewMode,
    selectedPlayer,
    handResultData,
    filteredDecision,
    setViewMode,
    setSelectedPlayer,
    checkHandEnd
  }
})
