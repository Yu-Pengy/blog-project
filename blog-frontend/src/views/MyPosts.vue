<template>
  <div class="my-posts" :class="themeStore.themeClass">
    <div class="background-gradient"></div>
    
    <!-- 主题切换按钮 -->
    <div class="theme-toggle">
      <button @click="themeStore.toggleTheme()" class="theme-btn" :title="themeStore.isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
        {{ themeStore.isDarkMode ? '🌞' : '🌙' }}
      </button>
    </div>
    
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">📝 博客系统</router-link>
        </div>
        <div class="nav-menu">
          <span class="user-info">👤 {{ authStore.username }}</span>
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/write" class="nav-link">写文章</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">管理面板</router-link>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="container">
      <div class="page-header">
        <h1>📚 我的文章</h1>
        <p>管理和查看你的所有文章</p>
        <div class="header-actions">
          <router-link to="/write" class="btn btn-primary">✍️ 写新文章</router-link>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-bar">
        <div class="stat-item">
          <div class="stat-number">{{ posts.length }}</div>
          <div class="stat-label">总文章数</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ totalWords }}</div>
          <div class="stat-label">总字数</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ publishedThisMonth }}</div>
          <div class="stat-label">本月发布</div>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="posts-section">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="posts.length === 0" class="no-posts">
          <div class="no-posts-icon">📝</div>
          <h3>还没有文章</h3>
          <p>快去写你的第一篇文章吧！</p>
          <router-link to="/write" class="btn btn-primary">立即开始写作</router-link>
        </div>
        
        <div v-else class="posts-list">
          <div 
            v-for="post in posts" 
            :key="post.id" 
            class="post-item"
          >
            <div class="post-content">
              <div class="post-header">
                <h3 class="post-title" @click="viewPost(post.id)">{{ post.title }}</h3>
                <div class="post-meta">
                  <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
                  <span v-if="post.category_name" class="post-category">
                    🏷️ {{ post.category_name }}
                  </span>
                  <span class="post-words">📄 {{ getWordCount(post.content) }} 字</span>
                </div>
              </div>
              
              <div class="post-preview" v-html="post.preview_html"></div>
            </div>
            
            <div class="post-actions">
              <button @click="viewPost(post.id)" class="action-btn view-btn">
                👁️ 查看
              </button>
              <button @click="editPost(post.id)" class="action-btn edit-btn">
                ✏️ 编辑
              </button>
              <button @click="confirmDelete(post)" class="action-btn delete-btn">
                🗑️ 删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除文章《{{ deleteTarget?.title }}》吗？</p>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button @click="cancelDelete" class="btn btn-secondary">取消</button>
          <button @click="deletePost" class="btn btn-danger" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.show" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import ApiService from '../services/api'

export default {
  name: 'MyPosts',
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    
    return { authStore, themeStore, router }
  },
  data() {
    return {
      posts: [],
      loading: false,
      showDeleteModal: false,
      deleteTarget: null,
      deleting: false,
      message: {
        show: false,
        text: '',
        type: 'success'
      }
    }
  },
  computed: {
    totalWords() {
      return this.posts.reduce((total, post) => total + this.getWordCount(post.content), 0)
    },
    publishedThisMonth() {
      const now = new Date()
      const thisMonth = now.getMonth()
      const thisYear = now.getFullYear()
      
      return this.posts.filter(post => {
        const postDate = new Date(post.created_at)
        return postDate.getMonth() === thisMonth && postDate.getFullYear() === thisYear
      }).length
    }
  },
  async created() {
    if (!this.authStore.isLoggedIn) {
      this.router.push('/login')
      return
    }
    
    // 初始化主题
    this.themeStore.initTheme()
    
    await this.loadMyPosts()
  },
  methods: {
    async loadMyPosts() {
      this.loading = true
      try {
        this.posts = await ApiService.getMyPosts()
      } catch (error) {
        this.showMessage('加载文章失败：' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },

    async handleLogout() {
      const result = await this.authStore.logout()
      if (result.success) {
        this.router.push('/')
      }
    },

    viewPost(postId) {
      this.router.push(`/post/${postId}`)
    },

    editPost(postId) {
      this.router.push(`/edit/${postId}`)
    },

    confirmDelete(post) {
      this.deleteTarget = post
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.deleteTarget = null
    },

    async deletePost() {
      if (!this.deleteTarget) return
      
      this.deleting = true
      try {
        const result = await ApiService.deletePost(this.deleteTarget.id)
        if (result.success) {
          this.showMessage('文章删除成功', 'success')
          this.posts = this.posts.filter(p => p.id !== this.deleteTarget.id)
        }
      } catch (error) {
        this.showMessage('删除失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeleteModal = false
        this.deleteTarget = null
      }
    },

    formatDate(dateString) {
      try {
        return new Date(dateString).toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch {
        return '未知日期'
      }
    },

    getWordCount(content) {
      if (!content) return 0
      // 简单的中文字数统计
      return content.replace(/\s/g, '').length
    },

    showMessage(text, type = 'success') {
      this.message = { show: true, text, type }
      setTimeout(() => {
        this.message.show = false
      }, 3000)
    }
  }
}
</script>

<style scoped>
.my-posts {
  min-height: 100vh;
  width: 100%;
  transition: all 0.3s ease;
}

/* 主题相关 CSS 变量 */
.my-posts.light-mode {
  --bg-primary: rgba(255, 255, 255, 0.95);
  --bg-secondary: rgba(255, 255, 255, 0.8);
  --bg-tertiary: rgba(255, 255, 255, 0.6);
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --text-muted: #bdc3c7;
  --border-color: rgba(44, 62, 80, 0.1);
  --shadow-color: rgba(0, 0, 0, 0.1);
  --accent-color: #3498db;
  --success-color: #27ae60;
  --error-color: #e74c3c;
  --warning-color: #f39c12;
  --navbar-bg: rgba(255, 255, 255, 0.9);
  --card-bg: rgba(255, 255, 255, 0.95);
  --stats-bg: rgba(255, 255, 255, 0.9);
  --modal-bg: rgba(255, 255, 255, 0.98);
  --hover-bg: rgba(52, 152, 219, 0.1);
}

.my-posts.dark-mode {
  --bg-primary: rgba(26, 32, 44, 0.95);
  --bg-secondary: rgba(45, 55, 72, 0.8);
  --bg-tertiary: rgba(74, 85, 104, 0.6);
  --text-primary: #e2e8f0;
  --text-secondary: #a0aec0;
  --text-muted: #718096;
  --border-color: rgba(226, 232, 240, 0.1);
  --shadow-color: rgba(0, 0, 0, 0.3);
  --accent-color: #4299e1;
  --success-color: #48bb78;
  --error-color: #f56565;
  --warning-color: #ed8936;
  --navbar-bg: rgba(26, 32, 44, 0.9);
  --card-bg: rgba(26, 32, 44, 0.95);
  --stats-bg: rgba(45, 55, 72, 0.9);
  --modal-bg: rgba(26, 32, 44, 0.98);
  --hover-bg: rgba(66, 153, 225, 0.1);
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
  border: 2px solid var(--border-color, rgba(255, 255, 255, 0.3));
  background: var(--bg-primary, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  color: var(--text-primary, white);
  font-size: 1.5em;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px var(--shadow-color, rgba(0, 0, 0, 0.1));
}

.theme-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px var(--shadow-color, rgba(0, 0, 0, 0.15));
  background: var(--bg-secondary, rgba(255, 255, 255, 0.2));
}

.background-gradient {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  transition: all 0.3s ease;
}

.my-posts.light-mode .background-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.my-posts.dark-mode .background-gradient {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

/* 导航栏样式 */
.navbar {
  background: var(--navbar-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  padding: 1rem 0;
  transition: all 0.3s ease;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-link {
  color: var(--text-primary, white);
  text-decoration: none;
  font-size: clamp(1.2em, 3vw, 1.5em);
  font-weight: bold;
  transition: color 0.3s ease;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.user-info {
  color: var(--text-primary, white);
  font-weight: bold;
  transition: color 0.3s ease;
}

.nav-link {
  color: var(--text-primary, white);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: var(--hover-bg, rgba(255, 255, 255, 0.1));
}

.logout-btn {
  background: var(--error-color, rgba(255, 99, 99, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--error-color, rgba(255, 99, 99, 0.5));
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: var(--error-color, rgba(255, 99, 99, 0.4));
  transform: translateY(-1px);
}

/* 主要内容样式 */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: var(--text-primary, white);
  font-size: clamp(2em, 5vw, 2.5em);
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.page-header p {
  color: var(--text-secondary, rgba(255, 255, 255, 0.8));
  font-size: clamp(1em, 3vw, 1.1em);
  margin-bottom: 20px;
  transition: color 0.3s ease;
}

.header-actions {
  margin-top: 20px;
}

/* 统计栏样式 */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  background: var(--stats-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px var(--shadow-color, rgba(0, 0, 0, 0.1));
}

.stat-number {
  color: var(--text-primary, white);
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.stat-label {
  color: var(--text-secondary, rgba(255, 255, 255, 0.7));
  font-size: 0.9em;
  transition: color 0.3s ease;
}

/* 文章列表样式 */
.posts-section {
  width: 100%;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-item {
  background: var(--card-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px var(--shadow-color, rgba(0, 0, 0, 0.1));
}

.post-item:hover {
  background: var(--hover-bg, rgba(255, 255, 255, 0.15));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px var(--shadow-color, rgba(0, 0, 0, 0.15));
}

.post-content {
  flex: 1;
}

.post-title {
  color: var(--text-primary, white);
  font-size: 1.3em;
  margin-bottom: 10px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.post-title:hover {
  color: var(--accent-color, rgba(102, 126, 234, 0.8));
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 0.9em;
  color: var(--text-secondary, rgba(255, 255, 255, 0.7));
  transition: color 0.3s ease;
}

.post-preview {
  color: var(--text-primary, rgba(255, 255, 255, 0.9));
  line-height: 1.6;
  transition: color 0.3s ease;
}

.post-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: bold;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.view-btn {
  background: var(--accent-color, rgba(102, 126, 234, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--accent-color, rgba(102, 126, 234, 0.5));
}

.view-btn:hover {
  background: var(--accent-color, rgba(102, 126, 234, 0.4));
  transform: translateY(-1px);
}

.edit-btn {
  background: var(--warning-color, rgba(255, 193, 7, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--warning-color, rgba(255, 193, 7, 0.5));
}

.edit-btn:hover {
  background: var(--warning-color, rgba(255, 193, 7, 0.4));
  transform: translateY(-1px);
}

.delete-btn {
  background: var(--error-color, rgba(255, 99, 99, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--error-color, rgba(255, 99, 99, 0.5));
}

.delete-btn:hover {
  background: var(--error-color, rgba(255, 99, 99, 0.4));
  transform: translateY(-1px);
}

/* 加载和空状态样式 */
.loading, .no-posts {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-primary, white);
  transition: color 0.3s ease;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color, rgba(255, 255, 255, 0.3));
  border-top: 4px solid var(--text-primary, white);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-posts-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal {
  background: var(--modal-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 0;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  box-shadow: 0 8px 32px var(--shadow-color, rgba(0, 0, 0, 0.3));
  max-width: 400px;
  width: 90%;
  transition: all 0.3s ease;
}

.modal-header {
  padding: 20px 20px 0;
  color: var(--text-primary, white);
  text-align: center;
  transition: color 0.3s ease;
}

.modal-body {
  padding: 20px;
  color: var(--text-primary, white);
  text-align: center;
  transition: color 0.3s ease;
}

.warning-text {
  color: var(--error-color, rgba(255, 99, 99, 0.8));
  font-size: 0.9em;
  margin-top: 10px;
  transition: color 0.3s ease;
}

.modal-footer {
  padding: 0 20px 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-size: 1em;
}

.btn-primary {
  background: var(--accent-color, rgba(102, 126, 234, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--accent-color, rgba(102, 126, 234, 0.5));
}

.btn-primary:hover {
  background: var(--accent-color, rgba(102, 126, 234, 0.4));
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, white);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.3));
}

.btn-secondary:hover {
  background: var(--bg-tertiary, rgba(255, 255, 255, 0.2));
  transform: translateY(-2px);
}

.btn-danger {
  background: var(--error-color, rgba(255, 99, 99, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--error-color, rgba(255, 99, 99, 0.5));
}

.btn-danger:hover:not(:disabled) {
  background: var(--error-color, rgba(255, 99, 99, 0.4));
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: var(--text-primary, white);
  font-weight: bold;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.message.success {
  background: var(--success-color, rgba(76, 175, 80, 0.9));
  border: 1px solid var(--success-color, rgba(76, 175, 80, 0.5));
}

.message.error {
  background: var(--error-color, rgba(244, 67, 54, 0.9));
  border: 1px solid var(--error-color, rgba(244, 67, 54, 0.5));
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .post-item {
    flex-direction: column;
    gap: 15px;
  }
  
  .post-actions {
    flex-direction: row;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .stats-bar {
    grid-template-columns: 1fr;
  }
}
</style>