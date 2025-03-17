<script setup>
import { RouterView } from 'vue-router'
import { ElConfigProvider } from 'element-plus'
</script>

<template>
  <el-config-provider>
    <div class="app-container">
      <RouterView />
    </div>
  </el-config-provider>
</template>

<style>
.app-container {
  min-height: 100vh;
  padding: 20px;
  background-color: #f0f2f5;
}
</style>
