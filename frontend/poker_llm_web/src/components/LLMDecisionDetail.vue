<template>
  <div class="llm-decision-detail" v-if="decision">
    <div class="decision-header">
      <div class="player-badge">
        <el-icon><user /></el-icon>
        <span class="player-name">{{ decision.player_name }}</span>
        <el-tag size="small" type="info">{{ decision.model_name }}</el-tag>
      </div>
      <div class="decision-meta">
        <el-tag size="small">手牌 #{{ decision.hand_number }}</el-tag>
        <el-tag size="small" type="success">{{ formatStage(decision.stage) }}</el-tag>
        <el-tag size="small" type="warning">
          <el-icon><clock /></el-icon>
          {{ (decision.response_time || 0).toFixed(2) }}s
        </el-tag>
      </div>
    </div>

    <el-collapse v-model="activeSections" class="decision-collapse">
      <!-- 选择的行动 -->
      <el-collapse-item name="action" class="action-section">
        <template #title>
          <div class="collapse-title">
            <el-icon><check /></el-icon>
            <span>决策结果</span>
            <el-tag :type="getActionType(decision.parsed_action)" size="small">
              {{ formatAction(decision.parsed_action) }}
              <span v-if="decision.action_amount > 0">: {{ decision.action_amount }}</span>
            </el-tag>
          </div>
        </template>
        <div class="action-content">
          <div class="decision-reason" v-if="decision.play_reason">
            <div class="reason-label">
              <el-icon><chat-line-round /></el-icon>
              决策理由
            </div>
            <div class="reason-text">{{ decision.play_reason }}</div>
          </div>
          <div class="behavior" v-if="decision.behavior">
            <div class="behavior-label">
              <el-icon><view /></el-icon>
              行为表现
            </div>
            <div class="behavior-text">"{{ decision.behavior }}"</div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 游戏状态 -->
      <el-collapse-item name="gamestate">
        <template #title>
          <div class="collapse-title">
            <el-icon><data-analysis /></el-icon>
            <span>游戏状态</span>
          </div>
        </template>
        <GameStateView :game-state="decision.game_state" :player-name="decision.player_name" />
      </el-collapse-item>

      <!-- Prompt -->
      <el-collapse-item name="prompt">
        <template #title>
          <div class="collapse-title">
            <el-icon><document /></el-icon>
            <span>输入 Prompt</span>
            <el-tag size="small" type="info">{{ getPromptLineCount(decision.prompt) }} 行</el-tag>
          </div>
        </template>
        <div class="prompt-content">
          <pre class="prompt-text">{{ decision.prompt }}</pre>
        </div>
      </el-collapse-item>

      <!-- 原始响应 -->
      <el-collapse-item name="response">
        <template #title>
          <div class="collapse-title">
            <el-icon><chat-dot-round /></el-icon>
            <span>模型响应</span>
          </div>
        </template>
        <div class="response-content">
          <pre class="response-text">{{ decision.raw_response }}</pre>
        </div>
      </el-collapse-item>

      <!-- 推理内容（如果有） -->
      <el-collapse-item name="reasoning" v-if="decision.reasoning_content">
        <template #title>
          <div class="collapse-title">
            <el-icon><magic-stick /></el-icon>
            <span>推理过程</span>
            <el-tag size="small" type="warning">DeepSeek-R1</el-tag>
          </div>
        </template>
        <div class="reasoning-content">
          <pre class="reasoning-text">{{ decision.reasoning_content }}</pre>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 错误提示 -->
    <el-alert
      v-if="decision.error"
      type="error"
      :title="'决策错误: ' + decision.error"
      :closable="false"
      show-icon
      class="error-alert"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  User, Clock, Check, ChatLineRound, View, DataAnalysis,
  Document, ChatDotRound, MagicStick
} from '@element-plus/icons-vue'
import GameStateView from './GameStateView.vue'

const props = defineProps({
  decision: {
    type: Object,
    default: null
  }
})

const activeSections = ref(['action'])

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
    'all-in': '全押',
    'small-blind': '小盲',
    'big-blind': '大盲'
  }
  return actionMap[action] || action
}

const getActionType = (action) => {
  const typeMap = {
    'fold': 'danger',
    'check': 'info',
    'call': 'success',
    'raise': 'warning',
    'all-in': 'danger'
  }
  return typeMap[action] || 'info'
}

const getPromptLineCount = (prompt) => {
  return prompt ? prompt.split('\n').length : 0
}
</script>

<style scoped>
.llm-decision-detail {
  height: 100%;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.decision-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.player-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.player-name {
  font-size: 1.1rem;
  font-weight: bold;
}

.decision-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.decision-collapse {
  border: none;
}

.decision-collapse :deep(.el-collapse-item__header) {
  background: #f5f7fa;
  border-radius: 0.5rem;
  padding: 0 1rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.decision-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  background: white;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.decision-collapse :deep(.el-collapse-item__content) {
  padding: 1rem;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.action-section :deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.action-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.decision-reason, .behavior {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border-left: 4px solid #667eea;
}

.reason-label, .behavior-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #667eea;
}

.reason-text, .behavior-text {
  color: #333;
  line-height: 1.6;
}

.behavior-text {
  font-style: italic;
}

.prompt-content, .response-content, .reasoning-content {
  background: #1e1e1e;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
}

.prompt-text, .response-text, .reasoning-text {
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.reasoning-text {
  color: #ffd700;
}

.error-alert {
  margin-top: 1rem;
}

/* 自定义滚动条 */
.llm-decision-detail::-webkit-scrollbar {
  width: 6px;
}

.llm-decision-detail::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.llm-decision-detail::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.llm-decision-detail::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
