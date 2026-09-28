import { createRouter, createWebHistory } from 'vue-router'
// 定义路由配置对象---数组
const routes = [
  {
    path: '',
    component: () => import('../components/login.vue')
  },
  {
    path: '/register',
    component: () => import('../components/register.vue')
  },
  {
    path: '/chat',
    component: () => import('../components/chat.vue')
  }

]

// 设置路由模式为history模式---默认为hash模式，访问路径有一个#号
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

