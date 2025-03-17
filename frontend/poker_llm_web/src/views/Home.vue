<template>
  <div class="home-container">
    <div class="header">
      <h1>扑克LLM游戏回放</h1>
      <p>上传游戏日志文件，观看AI玩家的德州扑克对战</p>
    </div>
    
    <div class="upload-area">
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请上传game_logs目录中的JSON格式游戏日志文件
          </div>
        </template>
      </el-upload>
      
      <div class="action-buttons" v-if="gameData.length > 0">
        <el-button type="primary" @click="startReplay">开始回放</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGameStore } from '@/stores/game'

const router = useRouter()
const gameStore = useGameStore()
const gameData = ref([])

const handleFileChange = (file) => {
  if (file.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        gameData.value = data
        ElMessage.success('游戏日志加载成功')
      } catch (error) {
        ElMessage.error('文件格式错误，请上传有效的JSON文件')
        console.error('解析错误:', error)
      }
    }
    reader.readAsText(file.raw)
  }
}

const startReplay = () => {
  if (gameData.value.length > 0) {
    gameStore.setGameData(gameData.value)
    router.push('/replay')
  } else {
    ElMessage.warning('请先上传游戏日志文件')
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.header {
  margin-bottom: 3rem;
}

.header h1 {
  font-size: 2.5rem;
  color: #409EFF;
  margin-bottom: 1rem;
}

.header p {
  font-size: 1.2rem;
  color: #606266;
}

.upload-area {
  max-width: 500px;
  margin: 0 auto;
}

.action-buttons {
  margin-top: 2rem;
}

.el-upload__tip {
  color: #909399;
}
</style>