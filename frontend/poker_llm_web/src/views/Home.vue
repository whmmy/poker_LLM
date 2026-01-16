<template>
  <div class="home-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <div class="title-area">
        <h1 class="main-title">
          <span class="poker-icon">♠</span>
          扑克 LLM 游戏回放系统
          <span class="poker-icon">♥</span>
        </h1>
        <p class="subtitle">AI 玩家德州扑克对局深度分析平台</p>
      </div>

      <!-- 功能介绍 -->
      <div class="features">
        <div class="feature-item">
          <el-icon class="feature-icon"><view /></el-icon>
          <span>游戏回放</span>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon"><chat-dot-round /></el-icon>
          <span>LLM 决策分析</span>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon"><refresh /></el-icon>
          <span>反思过程</span>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon"><data-analysis /></el-icon>
          <span>数据统计</span>
        </div>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <div class="upload-card">
        <div class="upload-header">
          <el-icon class="upload-icon"><upload-filled /></el-icon>
          <h2>上传游戏日志</h2>
        </div>

        <el-upload
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          :show-file-list="false"
          accept=".json"
        >
          <div class="upload-content">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="upload-text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <div class="upload-hint">
              支持 enhanced_poker_game_*.json 格式的增强日志文件
            </div>
          </div>
        </el-upload>

        <!-- 快速加载测试数据 -->
        <div class="quick-load" v-if="!hasData">
          <el-divider>或</el-divider>
          <el-button
            type="info"
            plain
            @click="loadSampleData"
            :loading="loading"
          >
            <el-icon><document /></el-icon>
            加载示例数据
          </el-button>
        </div>

        <!-- 已加载的数据信息 -->
        <div class="loaded-info" v-if="hasData">
          <el-alert
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              <div class="success-title">
                <span>已加载游戏日志</span>
                <el-tag size="small">{{ gameMetadata?.game_id || 'Unknown' }}</el-tag>
              </div>
            </template>
            <div class="game-summary">
              <div class="summary-item">
                <el-icon><user /></el-icon>
                <span>{{ playerCount }} 位玩家</span>
              </div>
              <div class="summary-item">
                <el-icon><chat-dot-round /></el-icon>
                <span>{{ decisionCount }} 条决策记录</span>
              </div>
              <div class="summary-item">
                <el-icon><refresh /></el-icon>
                <span>{{ reflectionCount }} 条反思记录</span>
              </div>
            </div>
          </el-alert>

          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              @click="startReplay"
              class="start-button"
            >
              <el-icon><video-play /></el-icon>
              开始回放
            </el-button>
            <el-button
              size="large"
              @click="resetData"
            >
              <el-icon><delete /></el-icon>
              重新加载
            </el-button>
          </div>
        </div>
      </div>

      <!-- 使用说明 -->
      <div class="instructions-card">
        <h3>
          <el-icon><question-filled /></el-icon>
          使用说明
        </h3>
        <div class="instruction-list">
          <div class="instruction-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>上传日志文件</h4>
              <p>从 <code>game_logs</code> 目录中选择增强格式的游戏日志文件（enhanced_poker_game_*.json）</p>
            </div>
          </div>
          <div class="instruction-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>回放游戏</h4>
              <p>使用控制面板逐步播放或自动播放游戏过程，观察每个决策点</p>
            </div>
          </div>
          <div class="instruction-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>分析 LLM 思考</h4>
              <p>查看每个 AI 玩家的完整决策过程，包括输入 prompt、游戏状态、决策理由和模型响应</p>
            </div>
          </div>
          <div class="instruction-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <h4>查看统计</h4>
              <p>浏览玩家统计、决策分布、反思记录等数据洞察</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <p>扑克 LLM 游戏回放系统 | 基于增强日志系统 v2.0</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  UploadFilled, Document, View, ChatDotRound, Refresh, DataAnalysis,
  VideoPlay, Delete, QuestionFilled, User
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGameStore } from '@/stores/game'

const router = useRouter()
const gameStore = useGameStore()

const loading = ref(false)

// 从 store 获取数据
const gameMetadata = computed(() => gameStore.gameMetadata)
const llmDecisions = computed(() => gameStore.llmDecisions)
const llmReflections = computed(() => gameStore.llmReflections)

const hasData = computed(() => gameStore.fullGameLog !== null)
const playerCount = computed(() => gameMetadata.value?.players?.length || 0)
const decisionCount = computed(() => llmDecisions.value.length)
const reflectionCount = computed(() => llmReflections.value.length)

const handleFileChange = (file) => {
  if (file.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        validateAndLoadData(data)
      } catch (error) {
        ElMessage.error('文件格式错误，请上传有效的 JSON 文件')
        console.error('解析错误:', error)
      }
    }
    reader.readAsText(file.raw)
  }
}

const validateAndLoadData = (data) => {
  // 验证是否为增强格式日志
  if (!data.game_id || !data.llm_decisions) {
    ElMessage.warning('请上传增强格式的游戏日志（enhanced_poker_game_*.json）')
    return
  }

  gameStore.setGameData(data)
  ElMessage.success({
    message: `成功加载游戏日志 ${data.game_id}`,
    duration: 2000
  })
}

const loadSampleData = async () => {
  loading.value = true
  try {
    // 尝试加载示例日志文件
    const response = await fetch('/game_logs/enhanced_poker_game_a4cd6211.json')
    if (response.ok) {
      const data = await response.json()
      validateAndLoadData(data)
    } else {
      ElMessage.warning('示例数据文件不存在，请手动上传日志文件')
    }
  } catch (error) {
    ElMessage.warning('无法加载示例数据，请手动上传日志文件')
    console.error('加载示例数据错误:', error)
  } finally {
    loading.value = false
  }
}

const startReplay = () => {
  if (hasData.value) {
    router.push('/replay')
  } else {
    ElMessage.warning('请先上传游戏日志文件')
  }
}

const resetData = () => {
  gameStore.fullGameLog = null
  ElMessage.info('已清除数据，请重新上传日志文件')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.header-section {
  text-align: center;
  color: white;
  margin-bottom: 3rem;
  animation: fadeInDown 0.8s ease;
}

.title-area {
  margin-bottom: 2rem;
}

.main-title {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.poker-icon {
  font-size: 2.5rem;
  animation: float 3s ease-in-out infinite;
}

.poker-icon:last-child {
  color: #ff6b6b;
  animation-delay: 0.5s;
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

.features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  backdrop-filter: blur(10px);
}

.feature-icon {
  font-size: 1.2rem;
}

.upload-section {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

.upload-card, .instructions-card {
  background: white;
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.upload-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.upload-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.upload-header h2 {
  margin: 0.5rem 0 0 0;
  color: #333;
}

.upload-area {
  margin-bottom: 1.5rem;
}

.upload-content {
  padding: 2rem;
}

.el-icon--upload {
  font-size: 4rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.upload-text em {
  color: #667eea;
  font-style: normal;
  font-weight: 600;
}

.upload-hint {
  font-size: 0.9rem;
  color: #999;
}

.quick-load {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.start-button {
  flex: 2;
  font-size: 1.1rem;
  height: 50px;
}

.success-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.game-summary {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.instructions-card h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1.5rem 0;
  color: #333;
}

.instruction-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.instruction-item {
  display: flex;
  gap: 1rem;
  align-items: start;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.step-content p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.step-content code {
  background: #f0f0f0;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: 'Consolas', monospace;
  font-size: 0.85rem;
}

.footer {
  text-align: center;
  color: white;
  margin-top: 3rem;
  opacity: 0.8;
  font-size: 0.9rem;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .upload-section {
    grid-template-columns: 1fr;
  }

  .main-title {
    font-size: 2rem;
    flex-wrap: wrap;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-upload-dragger) {
  border-radius: 1rem;
  border: 2px dashed #667eea;
  background: #f8f9fa;
}

:deep(.el-upload-dragger:hover) {
  border-color: #764ba2;
  background: #f0f0f0;
}
</style>
