<template>
  <div class="login-page" :class="themeStore.themeClass">
    <div class="background-gradient"></div>
    
    <!-- 主题切换按钮 -->
    <div class="theme-toggle">
      <button @click="themeStore.toggleTheme()" class="theme-btn" :title="themeStore.isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
        {{ themeStore.isDarkMode ? '🌞' : '🌙' }}
      </button>
    </div>
    
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>🚀 博客系统</h1>
          <p>欢迎回来！请登录您的账户</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label>👤 用户名</label>
            <input 
              v-model="form.username" 
              type="text" 
              placeholder="请输入用户名"
              required
            >
          </div>
          
          <div class="form-group">
            <label>🔒 密码</label>
            <input 
              v-model="form.password" 
              type="password" 
              placeholder="请输入密码"
              required
            >
          </div>
          
          <button 
            type="submit" 
            class="login-btn"
            :disabled="authStore.loading"
          >
            {{ authStore.loading ? '登录中...' : '登录' }}
          </button>
        </form>
        
        <div class="login-footer">
          <p>还没有账户？<router-link to="/register">立即注册</router-link></p>
        </div>
        
        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <!-- 成功信息显示 -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    
    // 初始化主题
    themeStore.initTheme()
    
    return {
      authStore,
      themeStore,
      router
    }
  },
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      errorMessage: '',
      successMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.successMessage = ''
      
      if (!this.form.username || !this.form.password) {
        this.errorMessage = '请填写完整的用户名和密码'
        return
      }
      
      const result = await this.authStore.login(this.form.username, this.form.password)
      
      if (result.success) {
        this.successMessage = result.message
        setTimeout(() => {
          this.router.push('/')
        }, 1000)
      } else {
        this.errorMessage = result.message
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

/* 主题切换按钮 */
.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.theme-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  font-size: 1.5em;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

/* 浅色模式 */
/* 浅色模式样式 */
.light-mode .background-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.light-mode .welcome-content,
.light-mode .feature-card,
.light-mode .post-card,
.light-mode .navbar,
.light-mode .carousel-container {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.light-mode .welcome-title .title-line,
.light-mode .nav-brand h2,
.light-mode .user-info,
.light-mode .post-title,
.light-mode .post-content,
.light-mode .loading,
.light-mode .no-posts,
.light-mode .feature-card h4,
.light-mode .slide-content h3 {
  color: #2c3e50;
}

.light-mode .welcome-subtitle,
.light-mode .feature-card p,
.light-mode .post-meta,
.light-mode .stat-label,
.light-mode .slide-content p {
  color: #5a6c7d;
}

.light-mode .gradient-text,
.light-mode .stat-number {
  color: #667eea;
}

.light-mode .filter-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
}

/* 深色模式 */
.dark-mode .background-gradient {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.dark-mode .login-card {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .login-header h1 {
  color: #ecf0f1;
}

.dark-mode .login-header p {
  color: rgba(236, 240, 241, 0.8);
}

.dark-mode .form-group label {
  color: #ecf0f1;
}

.dark-mode .form-group input {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ecf0f1;
}

.dark-mode .form-group input::placeholder {
  color: rgba(236, 240, 241, 0.6);
}

.dark-mode .form-group input:focus {
  border-color: rgba(52, 73, 94, 0.6);
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 3px rgba(52, 73, 94, 0.1);
}

.dark-mode .login-btn {
  background: rgba(52, 73, 94, 0.4);
  border: 1px solid rgba(52, 73, 94, 0.6);
  color: #ecf0f1;
}

.dark-mode .login-btn:hover:not(:disabled) {
  background: rgba(52, 73, 94, 0.5);
  border-color: rgba(52, 73, 94, 0.8);
  box-shadow: 0 4px 15px rgba(52, 73, 94, 0.3);
}

.dark-mode .login-footer p {
  color: rgba(236, 240, 241, 0.8);
}

.dark-mode .login-footer a {
  color: #ecf0f1;
}

.dark-mode .login-footer a:hover {
  color: rgba(52, 73, 94, 0.8);
}

.dark-mode .theme-btn {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.2);
}

.dark-mode .theme-btn:hover {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
}

.background-gradient {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  transition: background 0.3s ease;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  font-weight: bold;
  transition: color 0.3s ease;
}

.login-header p {
  font-size: 1.1em;
  transition: color 0.3s ease;
}

.login-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 1.1em;
  transition: color 0.3s ease;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border-radius: 8px;
  font-size: 1em;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
}

.login-btn {
  width: 100%;
  padding: 15px;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.login-footer a {
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s ease;
}

.error-message {
  background: rgba(255, 99, 99, 0.2);
  color: #ff6b6b;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid rgba(255, 99, 99, 0.3);
  text-align: center;
}

.success-message {
  background: rgba(99, 255, 99, 0.2);
  color: #51cf66;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid rgba(99, 255, 99, 0.3);
  text-align: center;
}
</style>