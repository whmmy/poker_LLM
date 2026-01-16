<template>
  <div class="llm-reflection-view">
    <div class="reflection-header">
      <el-icon><refresh /></el-icon>
      <h3>LLM 反思记录</h3>
      <el-badge :value="reflections.length" class="badge" />
    </div>

    <div v-if="reflections.length === 0" class="empty-state">
      <el-empty description="暂无反思记录" />
    </div>

    <div v-else class="reflections-list">
      <div
        v-for="(reflection, index) in reflections"
        :key="index"
        class="reflection-item"
      >
        <div class="reflection-header-bar">
          <div class="player-info">
            <el-icon><user /></el-icon>
            <span class="player-name">{{ reflection.player_name }}</span>
            <el-tag size="small" type="info">{{ reflection.model_name }}</el-tag>
          </div>
          <div class="hand-info">
            <el-tag size="small">手牌 #{{ reflection.hand_number }}</el-tag>
            <el-tag size="small" type="success">
              <el-icon><clock /></el-icon>
              {{ formatTime(reflection.timestamp) }}
            </el-tag>
          </div>
        </div>

        <el-collapse class="reflection-collapse">
          <!-- 游戏结果 -->
          <el-collapse-item name="result">
            <template #title>
              <div class="collapse-title">
                <el-icon><trophy /></el-icon>
                <span>游戏结果</span>
              </div>
            </template>
            <div class="game-result">{{ reflection.game_result }}</div>
          </el-collapse-item>

          <!-- 更新的评估 -->
          <el-collapse-item name="opinions" v-if="hasUpdatedOpinions(reflection)">
            <template #title>
              <div class="collapse-title">
                <el-icon><chat-line-round /></el-icon>
                <span>更新的玩家评估</span>
                <el-badge :value="Object.keys(reflection.updated_opinions || {}).length" size="small" />
              </div>
            </template>
            <div class="opinions-list">
              <div
                v-for="(opinion, targetPlayer) in reflection.updated_opinions"
                :key="targetPlayer"
                class="opinion-item"
              >
                <div class="opinion-target">
                  <el-icon><user /></el-icon>
                  {{ targetPlayer }}
                </div>
                <div class="opinion-content">{{ opinion }}</div>
              </div>
            </div>
          </el-collapse-item>

          <!-- Prompt -->
          <el-collapse-item name="prompt">
            <template #title>
              <div class="collapse-title">
                <el-icon><document /></el-icon>
                <span>反思 Prompt</span>
              </div>
            </template>
            <div class="prompt-content">
              <pre class="prompt-text">{{ reflection.prompt }}</pre>
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
              <pre class="response-text">{{ reflection.raw_response }}</pre>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Refresh, User, Clock, Trophy, ChatLineRound, Document, ChatDotRound } from '@element-plus/icons-vue'

const props = defineProps({
  reflections: {
    type: Array,
    default: () => []
  }
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const hasUpdatedOpinions = (reflection) => {
  return reflection.updated_opinions && Object.keys(reflection.updated_opinions).length > 0
}
</script>

<style scoped>
.llm-reflection-view {
  height: 100%;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.reflection-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.reflection-header h3 {
  margin: 0;
  flex: 1;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.reflections-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reflection-item {
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reflection-header-bar {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.player-name {
  font-weight: 600;
  color: #333;
}

.hand-info {
  display: flex;
  gap: 0.5rem;
}

.reflection-collapse {
  border: none;
}

.reflection-collapse :deep(.el-collapse-item__header) {
  background: #f5f7fa;
  border-radius: 0.5rem;
  padding: 0 1rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.reflection-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  background: white;
}

.reflection-collapse :deep(.el-collapse-item__content) {
  padding: 1rem;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.game-result {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  line-height: 1.6;
  color: #333;
}

.opinions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.opinion-item {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 0.75rem;
  border-left: 3px solid #11998e;
}

.opinion-target {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #11998e;
  margin-bottom: 0.5rem;
}

.opinion-content {
  color: #333;
  line-height: 1.5;
}

.prompt-content, .response-content {
  background: #1e1e1e;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
}

.prompt-text, .response-text {
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 自定义滚动条 */
.llm-reflection-view::-webkit-scrollbar {
  width: 6px;
}

.llm-reflection-view::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.llm-reflection-view::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.llm-reflection-view::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
