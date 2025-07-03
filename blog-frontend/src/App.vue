<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    
    // 应用启动时检查用户登录状态
    authStore.checkAuth()
    
    return {
      authStore
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
}

#app {
  min-height: 100vh;
}

/* 全局样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  font-size: 1em;
  transition: all 0.3s ease;
}

.btn-primary {
  background: rgba(102, 126, 234, 0.3);
  color: white;
  border: 1px solid rgba(102, 126, 234, 0.5);
}

.btn-primary:hover {
  background: rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

.btn-danger {
  background: rgba(255, 99, 99, 0.3);
  color: white;
  border: 1px solid rgba(255, 99, 99, 0.5);
}

.btn-danger:hover {
  background: rgba(255, 99, 99, 0.4);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
}
</style>