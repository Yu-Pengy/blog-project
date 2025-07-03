<template>
  <div class="post-detail" :class="themeStore.themeClass">
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
          <router-link to="/my-posts" class="nav-link">我的文章</router-link>
          <router-link to="/write" class="nav-link">写文章</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">管理面板</router-link>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">❌</div>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <div class="error-actions">
          <button @click="loadPost" class="btn btn-primary">重新加载</button>
          <router-link to="/" class="btn btn-secondary">返回首页</router-link>
        </div>
      </div>

      <!-- 文章内容 -->
      <article v-else-if="post" class="post-article">
        <!-- 文章头部 -->
        <header class="post-header">
          <div class="post-category" v-if="post.category_name">
            🏷️ {{ post.category_name }}
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="post-meta">
            <div class="meta-item">
              <UserAvatar 
                :username="post.author" 
                :avatar="post.author_avatar" 
                size="small" 
              />
              <span class="meta-text">{{ post.author }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-icon">📅</span>
              <span class="meta-text">{{ formatDate(post.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-icon">📄</span>
              <span class="meta-text">{{ getWordCount(post.content) }} 字</span>
            </div>
            <div class="meta-item">
              <span class="meta-icon">⏱️</span>
              <span class="meta-text">约 {{ getReadTime(post.content) }} 分钟阅读</span>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div v-if="canEditPost" class="post-actions">
            <button @click="editPost" class="action-btn edit-btn">
              ✏️ 编辑文章
            </button>
            <button @click="confirmDelete" class="action-btn delete-btn">
              🗑️ 删除文章
            </button>
          </div>
        </header>

        <!-- 文章内容 -->
        <div class="post-content">
          <div class="markdown-body" v-html="post.content_html"></div>
        </div>

        <!-- 文章底部 -->
        <footer class="post-footer">
          <div class="post-stats">
            <div class="stat">
              <span class="stat-label">发布时间</span>
              <span class="stat-value">{{ formatFullDate(post.created_at) }}</span>
            </div>
            <div v-if="post.updated_at && post.updated_at !== post.created_at" class="stat">
              <span class="stat-label">最后更新</span>
              <span class="stat-value">{{ formatFullDate(post.updated_at) }}</span>
            </div>
          </div>
          
          <div class="navigation-actions">
            <router-link to="/" class="btn btn-secondary">
              ← 返回首页
            </router-link>
            <router-link to="/my-posts" class="btn btn-secondary">
              📚 我的文章
            </router-link>
          </div>
        </footer>

        <!-- 评论区域 -->
        <CommentSection :post-id="parseInt(route.params.id)" />
      </article>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除文章《{{ post?.title }}》吗？</p>
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
import { useRouter, useRoute } from 'vue-router'
import ApiService from '../services/api'
import CommentSection from '../components/CommentSection.vue'
import UserAvatar from '../components/UserAvatar.vue'

export default {
  name: 'PostDetail',
  components: {
    CommentSection,
    UserAvatar
  },
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    const route = useRoute()
    
    return { authStore, themeStore, router, route }
  },
  data() {
    return {
      post: null,
      loading: false,
      error: null,
      showDeleteModal: false,
      deleting: false,
      message: {
        show: false,
        text: '',
        type: 'success'
      }
    }
  },
  computed: {
    postId() {
      return parseInt(this.route.params.id)
    },
    canEditPost() {
      if (!this.post || !this.authStore.isLoggedIn) return false
      return this.authStore.isAdmin || this.post.author === this.authStore.username
    }
  },
  async created() {
    // 检查用户认证状态
    await this.authStore.checkAuth()
    
    if (!this.authStore.isLoggedIn) {
      this.router.push('/login')
      return
    }
    // 初始化主题
    this.themeStore.initTheme()
    await this.loadPost()
  },
  methods: {
    async loadPost() {
      this.loading = true
      this.error = null
      try {
        this.post = await ApiService.getPost(this.postId)
      } catch (error) {
        this.error = error.message
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

    editPost() {
      this.router.push(`/edit/${this.postId}`)
    },

    confirmDelete() {
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
    },

    async deletePost() {
      if (!this.post) return
      
      this.deleting = true
      try {
        const result = await ApiService.deletePost(this.post.id)
        if (result.success) {
          this.showMessage('文章删除成功', 'success')
          setTimeout(() => {
            this.router.push('/my-posts')
          }, 1500)
        }
      } catch (error) {
        this.showMessage('删除失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeleteModal = false
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

    formatFullDate(dateString) {
      try {
        return new Date(dateString).toLocaleString('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return '未知时间'
      }
    },

    getWordCount(content) {
      if (!content) return 0
      return content.replace(/\s/g, '').length
    },

    getReadTime(content) {
      if (!content) return 0
      const wordCount = this.getWordCount(content)
      // 按照中文阅读速度约400字/分钟计算
      return Math.max(1, Math.ceil(wordCount / 400))
    },

    showMessage(text, type = 'success') {
      this.message = { show: true, text, type }
      setTimeout(() => {
        this.message.show = false
      }, 3000)
    }
  },
  watch: {
    '$route'(to, from) {
      if (to.params.id !== from.params.id) {
        this.loadPost()
      }
    }
  }
}
</script>

<style scoped>
.post-detail {
  min-height: 100vh;
  width: 100%;
  transition: all 0.3s ease;
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

/* 浅色模式背景 */
.light-mode .background-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 暗色模式背景 */
.dark-mode .background-gradient {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

/* 导航栏样式 */
.navbar {
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  transition: all 0.3s ease;
}

.light-mode .navbar {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .navbar {
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
  text-decoration: none;
  font-size: clamp(1.2em, 3vw, 1.5em);
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .brand-link {
  color: #2c3e50;
}

.dark-mode .brand-link {
  color: white;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.user-info {
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .user-info {
  color: #2c3e50;
}

.dark-mode .user-info {
  color: white;
}

.nav-link {
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.light-mode .nav-link {
  color: #5dade2;
}

.light-mode .nav-link:hover {
  background: rgba(93, 173, 226, 0.1);
}

.dark-mode .nav-link {
  color: white;
}

.dark-mode .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
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

.light-mode .theme-btn {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
  color: #2c3e50;
}

.dark-mode .theme-btn {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.2);
  color: white;
}

.logout-btn {
  border: 1px solid rgba(255, 99, 99, 0.5);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.light-mode .logout-btn {
  background: #e74c3c;
  color: white;
}

.light-mode .logout-btn:hover {
  background: #c0392b;
}

.dark-mode .logout-btn {
  background: rgba(255, 99, 99, 0.3);
  color: white;
}

.dark-mode .logout-btn:hover {
  background: rgba(255, 99, 99, 0.4);
}

/* 主要内容样式 */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

/* 加载和错误状态样式 */
.loading, .error-state {
  text-align: center;
  padding: 60px 20px;
  transition: color 0.3s ease;
}

.light-mode .loading,
.light-mode .error-state {
  color: #2c3e50;
}

.dark-mode .loading, 
.dark-mode .error-state {
  color: rgba(255, 255, 255, 0.9);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 20px;
}

/* 文章样式 */
.post-article {
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.light-mode .post-article {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .post-article {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.post-header {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  transition: border-color 0.3s ease;
}

.light-mode .post-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .post-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.post-category {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.9em;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.light-mode .post-category {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.dark-mode .post-category {
  background: rgba(102, 126, 234, 0.3);
  color: white;
  border: 1px solid rgba(102, 126, 234, 0.5);
}

.post-title {
  font-size: clamp(1.8em, 4vw, 2.5em);
  margin-bottom: 20px;
  line-height: 1.3;
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .post-title {
  color: #2c3e50;
}

.dark-mode .post-title {
  color: white;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 25px;
  transition: color 0.3s ease;
}

.light-mode .post-meta {
  color: #7f8c8d;
}

.dark-mode .post-meta {
  color: rgba(255, 255, 255, 0.7);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95em;
}

.meta-icon {
  font-size: 1.1em;
}

.post-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  transition: all 0.3s ease;
}

.edit-btn {
  background: rgba(255, 193, 7, 0.3);
  border: 1px solid rgba(255, 193, 7, 0.5);
  transition: all 0.3s ease;
}

.edit-btn:hover {
  background: rgba(255, 193, 7, 0.4);
  transform: translateY(-2px);
}

.light-mode .edit-btn {
  color: #f39c12;
}

.dark-mode .edit-btn {
  color: white;
  background: rgba(255, 193, 7, 0.4);
  border: 1px solid rgba(255, 193, 7, 0.6);
}

.delete-btn {
  background: rgba(255, 99, 99, 0.3);
  border: 1px solid rgba(255, 99, 99, 0.5);
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background: rgba(255, 99, 99, 0.4);
  transform: translateY(-2px);
}

.light-mode .delete-btn {
  color: #e74c3c;
}

.dark-mode .delete-btn {
  color: white;
  background: rgba(255, 99, 99, 0.4);
  border: 1px solid rgba(255, 99, 99, 0.6);
}

/* 文章内容样式 */
.post-content {
  margin-bottom: 40px;
}

.markdown-body {
  line-height: 1.8;
  font-size: 1.1em;
  transition: all 0.3s ease;
}

.light-mode .markdown-body {
  color: #2c3e50;
}

.dark-mode .markdown-body {
  color: rgba(255, 255, 255, 0.9);
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin: 30px 0 20px 0;
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .markdown-body h1,
.light-mode .markdown-body h2,
.light-mode .markdown-body h3,
.light-mode .markdown-body h4,
.light-mode .markdown-body h5,
.light-mode .markdown-body h6 {
  color: #2c3e50;
}

.dark-mode .markdown-body h1,
.dark-mode .markdown-body h2,
.dark-mode .markdown-body h3,
.dark-mode .markdown-body h4,
.dark-mode .markdown-body h5,
.dark-mode .markdown-body h6 {
  color: white;
}

.markdown-body h1 { font-size: 1.8em; }
.markdown-body h2 { font-size: 1.6em; }
.markdown-body h3 { font-size: 1.4em; }
.markdown-body h4 { font-size: 1.2em; }

.markdown-body p {
  margin: 15px 0;
}

.markdown-body code {
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  transition: all 0.3s ease;
}

.light-mode .markdown-body code {
  background: rgba(0, 0, 0, 0.1);
  color: #e91e63;
}

.dark-mode .markdown-body code {
  background: rgba(0, 0, 0, 0.3);
  color: #e6db74;
}

.markdown-body pre {
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 20px 0;
  transition: all 0.3s ease;
}

.light-mode .markdown-body pre {
  background: rgba(0, 0, 0, 0.05);
}

.dark-mode .markdown-body pre {
  background: rgba(0, 0, 0, 0.6);
}

.markdown-body pre code {
  background: none;
  padding: 0;
  transition: color 0.3s ease;
}

.light-mode .markdown-body pre code {
  color: #2c3e50;
}

.dark-mode .markdown-body pre code {
  color: #f8f8f2;
}

.markdown-body blockquote {
  margin: 20px 0;
  padding: 15px 20px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.light-mode .markdown-body blockquote {
  border-left: 4px solid rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

.dark-mode .markdown-body blockquote {
  border-left: 4px solid rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.markdown-body ul, .markdown-body ol {
  margin: 15px 0;
  padding-left: 30px;
}

.markdown-body li {
  margin: 8px 0;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.markdown-body th,
.markdown-body td {
  padding: 12px;
  text-align: left;
  transition: all 0.3s ease;
}

.light-mode .markdown-body th,
.light-mode .markdown-body td {
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .markdown-body th,
.dark-mode .markdown-body td {
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.markdown-body th {
  font-weight: bold;
  transition: background 0.3s ease;
}

.light-mode .markdown-body th {
  background: rgba(0, 0, 0, 0.05);
}

.dark-mode .markdown-body th {
  background: rgba(0, 0, 0, 0.5);
}

/* 文章底部样式 */
.post-footer {
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  transition: border-color 0.3s ease;
}

.light-mode .post-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .post-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.post-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.light-mode .stat-label {
  color: #7f8c8d;
}

.dark-mode .stat-label {
  color: rgba(255, 255, 255, 0.6);
}

.stat-value {
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .stat-value {
  color: #2c3e50;
}

.dark-mode .stat-value {
  color: white;
}

.navigation-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
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

.dark-mode .modal-overlay {
  background: rgba(0, 0, 0, 0.8);
}

.modal {
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  transition: all 0.3s ease;
}

.light-mode .modal {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .modal {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 20px 20px 0;
  text-align: center;
  transition: color 0.3s ease;
}

.light-mode .modal-header {
  color: #2c3e50;
}

.dark-mode .modal-header {
  color: white;
}

.modal-body {
  padding: 20px;
  text-align: center;
  transition: color 0.3s ease;
}

.light-mode .modal-body {
  color: #2c3e50;
}

.dark-mode .modal-body {
  color: white;
}

.warning-text {
  font-size: 0.9em;
  margin-top: 10px;
  transition: color 0.3s ease;
}

.light-mode .warning-text {
  color: #e74c3c;
}

.dark-mode .warning-text {
  color: rgba(255, 99, 99, 0.9);
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
  border: 1px solid rgba(102, 126, 234, 0.5);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

.light-mode .btn-primary {
  background: #667eea;
  color: white;
}

.light-mode .btn-primary:hover {
  background: #5a6fd8;
}

.dark-mode .btn-primary {
  background: rgba(102, 126, 234, 0.4);
  color: white;
  border: 1px solid rgba(102, 126, 234, 0.6);
}

.btn-secondary {
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  transform: translateY(-2px);
}

.light-mode .btn-secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #2c3e50;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.light-mode .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.9);
}

.dark-mode .btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark-mode .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-danger {
  border: 1px solid rgba(255, 99, 99, 0.5);
  transition: all 0.3s ease;
}

.btn-danger:hover:not(:disabled) {
  background: rgba(255, 99, 99, 0.4);
}

.light-mode .btn-danger {
  background: #e74c3c;
  color: white;
}

.dark-mode .btn-danger {
  background: rgba(255, 99, 99, 0.4);
  color: white;
  border: 1px solid rgba(255, 99, 99, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: bold;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.message.success {
  background: rgba(76, 175, 80, 0.9);
  border: 1px solid rgba(76, 175, 80, 0.5);
}

.message.error {
  background: rgba(244, 67, 54, 0.9);
  border: 1px solid rgba(244, 67, 54, 0.5);
}

.dark-mode .message.success {
  background: rgba(76, 175, 80, 0.95);
  border: 1px solid rgba(76, 175, 80, 0.7);
}

.dark-mode .message.error {
  background: rgba(244, 67, 54, 0.95);
  border: 1px solid rgba(244, 67, 54, 0.7);
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
  
  .post-article {
    padding: 25px;
  }
  
  .post-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .post-actions {
    flex-direction: column;
  }
  
  .navigation-actions {
    flex-direction: column;
  }
  
  .post-stats {
    flex-direction: column;
    gap: 15px;
  }
}

/* 评论区域主题适配 - 使用更强的选择器优先级和深度选择器 */
.post-detail.light-mode >>> .comment-section,
.post-detail.light-mode ::v-deep .comment-section,
.post-detail.light-mode :deep(.comment-section) {
  color: #2c3e50 !important;
}

.post-detail.light-mode >>> .comment-section h3,
.post-detail.light-mode >>> .comment-section h4,
.post-detail.light-mode >>> .comment-section .comment-subtitle,
.post-detail.light-mode >>> .comment-section .comment-hint,
.post-detail.light-mode >>> .comment-section .comment-author,
.post-detail.light-mode >>> .comment-section .comment-date,
.post-detail.light-mode >>> .comment-section .comment-content,
.post-detail.light-mode >>> .comment-section .comment-text,
.post-detail.light-mode >>> .comment-section .no-comments p,
.post-detail.light-mode >>> .comment-section .loading p,
.post-detail.light-mode >>> .comment-section .prompt-text,
.post-detail.light-mode >>> .comment-section label,
.post-detail.light-mode >>> .comment-section .comment-header h3,
.post-detail.light-mode ::v-deep .comment-section h3,
.post-detail.light-mode ::v-deep .comment-section h4,
.post-detail.light-mode ::v-deep .comment-section .comment-subtitle,
.post-detail.light-mode ::v-deep .comment-section .comment-hint,
.post-detail.light-mode ::v-deep .comment-section .comment-author,
.post-detail.light-mode ::v-deep .comment-section .comment-date,
.post-detail.light-mode ::v-deep .comment-section .comment-content,
.post-detail.light-mode ::v-deep .comment-section .comment-text,
.post-detail.light-mode ::v-deep .comment-section .no-comments p,
.post-detail.light-mode ::v-deep .comment-section .loading p,
.post-detail.light-mode ::v-deep .comment-section .prompt-text,
.post-detail.light-mode ::v-deep .comment-section label,
.post-detail.light-mode ::v-deep .comment-section .comment-header h3 {
  color: #2c3e50 !important;
}

.post-detail.light-mode >>> .comment-section .comment-meta,
.post-detail.light-mode >>> .comment-section .comment-time,
.post-detail.light-mode >>> .comment-section .comment-actions span,
.post-detail.light-mode >>> .comment-section .reply-indicator,
.post-detail.light-mode ::v-deep .comment-section .comment-meta,
.post-detail.light-mode ::v-deep .comment-section .comment-time,
.post-detail.light-mode ::v-deep .comment-section .comment-actions span,
.post-detail.light-mode ::v-deep .comment-section .reply-indicator {
  color: #7f8c8d !important;
}

.post-detail.light-mode >>> .comment-section .comment-item,
.post-detail.light-mode >>> .comment-section .reply-item,
.post-detail.light-mode ::v-deep .comment-section .comment-item,
.post-detail.light-mode ::v-deep .comment-section .reply-item {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.post-detail.light-mode >>> .comment-section .comment-form-container,
.post-detail.light-mode >>> .comment-section .login-prompt,
.post-detail.light-mode >>> .comment-section .reply-form,
.post-detail.light-mode ::v-deep .comment-section .comment-form-container,
.post-detail.light-mode ::v-deep .comment-section .login-prompt,
.post-detail.light-mode ::v-deep .comment-section .reply-form {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.post-detail.light-mode >>> .comment-section textarea,
.post-detail.light-mode >>> .comment-section input,
.post-detail.light-mode >>> .comment-section .edit-textarea,
.post-detail.light-mode ::v-deep .comment-section textarea,
.post-detail.light-mode ::v-deep .comment-section input,
.post-detail.light-mode ::v-deep .comment-section .edit-textarea {
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  color: #2c3e50 !important;
}

.post-detail.light-mode >>> .comment-section textarea::placeholder,
.post-detail.light-mode >>> .comment-section input::placeholder,
.post-detail.light-mode ::v-deep .comment-section textarea::placeholder,
.post-detail.light-mode ::v-deep .comment-section input::placeholder {
  color: #95a5a6 !important;
}

.post-detail.light-mode >>> .comment-section textarea:focus,
.post-detail.light-mode >>> .comment-section input:focus,
.post-detail.light-mode >>> .comment-section .edit-textarea:focus,
.post-detail.light-mode ::v-deep .comment-section textarea:focus,
.post-detail.light-mode ::v-deep .comment-section input:focus,
.post-detail.light-mode ::v-deep .comment-section .edit-textarea:focus {
  border-color: #667eea !important;
  background: rgba(255, 255, 255, 1) !important;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* 按钮样式覆盖 */
.post-detail.light-mode >>> .comment-section .btn-primary,
.post-detail.light-mode ::v-deep .comment-section .btn-primary {
  background: #667eea !important;
  color: white !important;
  border: 1px solid #667eea !important;
}

.post-detail.light-mode >>> .comment-section .btn-secondary,
.post-detail.light-mode ::v-deep .comment-section .btn-secondary {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #2c3e50 !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
}

.post-detail.light-mode >>> .comment-section .reply-btn,
.post-detail.light-mode ::v-deep .comment-section .reply-btn {
  color: #667eea !important;
  background: transparent !important;
}

.post-detail.light-mode >>> .comment-section .action-btn,
.post-detail.light-mode ::v-deep .comment-section .action-btn {
  color: #7f8c8d !important;
  background: transparent !important;
}

.post-detail.light-mode >>> .comment-section .action-btn:hover,
.post-detail.light-mode ::v-deep .comment-section .action-btn:hover {
  background: rgba(0, 0, 0, 0.1) !important;
}

/* 模态框样式覆盖 */
.post-detail.light-mode >>> .comment-section .modal,
.post-detail.light-mode ::v-deep .comment-section .modal {
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.post-detail.light-mode >>> .comment-section .modal-header,
.post-detail.light-mode >>> .comment-section .modal-body,
.post-detail.light-mode ::v-deep .comment-section .modal-header,
.post-detail.light-mode ::v-deep .comment-section .modal-body {
  color: #2c3e50 !important;
}

.post-detail.light-mode >>> .comment-section .warning-text,
.post-detail.light-mode ::v-deep .comment-section .warning-text {
  color: #e74c3c !important;
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  
  .post-article {
    padding: 20px;
  }
  
  .markdown-body {
    font-size: 1em;
  }
}
</style>