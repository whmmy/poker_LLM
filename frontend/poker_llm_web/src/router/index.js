import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/replay',
    name: 'Replay',
    component: () => import('@/views/Replay.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router