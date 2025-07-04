<template>
  <div class="edit-post" :class="themeStore.themeClass">
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
      <div v-else-if="loadError" class="error-state">
        <div class="error-icon">❌</div>
        <h3>加载失败</h3>
        <p>{{ loadError }}</p>
        <div class="error-actions">
          <button @click="loadPost" class="btn btn-primary">重新加载</button>
          <router-link to="/my-posts" class="btn btn-secondary">返回我的文章</router-link>
        </div>
      </div>

      <!-- 编辑表单 -->
      <div v-else-if="post" class="edit-form-container">
        <div class="page-header">
          <h1>✏️ 编辑文章</h1>
          <p>修改你的文章内容</p>
        </div>

        <form @submit.prevent="handleSubmit" class="edit-form">
          <!-- 标题输入 -->
          <div class="form-group">
            <label for="title">📝 文章标题</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              placeholder="请输入文章标题"
              required
              :disabled="submitting"
            >
            <div class="input-hint">
              {{ form.title.length }}/100 字符
            </div>
          </div>

          <!-- 分类选择 -->
          <div class="form-group">
            <label for="category">🏷️ 文章分类</label>
            <select
              id="category"
              v-model="form.category_id"
              :disabled="submitting"
            >
              <option value="">请选择分类</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>

          <!-- 内容编辑 -->
          <div class="form-group">
            <label for="content">📄 文章内容</label>
            <div class="editor-container">
              <!-- 编辑器工具栏 -->
              <div class="editor-toolbar">
                <div class="toolbar-group">
                  <button type="button" @click="insertText('**', '**')" class="toolbar-btn">
                    <strong>B</strong>
                  </button>
                  <button type="button" @click="insertText('*', '*')" class="toolbar-btn">
                    <em>I</em>
                  </button>
                  <button type="button" @click="insertText('`', '`')" class="toolbar-btn">
                    Code
                  </button>
                </div>
                <div class="toolbar-group">
                  <button type="button" @click="insertText('# ', '')" class="toolbar-btn">
                    H1
                  </button>
                  <button type="button" @click="insertText('## ', '')" class="toolbar-btn">
                    H2
                  </button>
                  <button type="button" @click="insertText('### ', '')" class="toolbar-btn">
                    H3
                  </button>
                </div>
                <div class="toolbar-group">
                  <button type="button" @click="insertText('- ', '')" class="toolbar-btn">
                    List
                  </button>
                  <button type="button" @click="insertText('> ', '')" class="toolbar-btn">
                    Quote
                  </button>
                </div>
                <div class="toolbar-info">
                  <span class="word-count">{{ getWordCount(form.content) }} 字</span>
                </div>
              </div>

              <!-- 文本编辑器 -->
              <textarea
                id="content"
                ref="contentTextarea"  
                v-model="form.content"
                placeholder="开始写作你的文章内容...

支持 Markdown 语法：
# 一级标题
## 二级标题
**粗体文字**
*斜体文字*
`代码`
> 引用
- 列表项"
                required
                :disabled="submitting"
                @input="autoResize"
              ></textarea>
            </div>
            <div class="input-hint">
              支持 Markdown 语法，{{ getWordCount(form.content) }} 字符
            </div>
          </div>

          <!-- 预览区域 -->
          <div class="form-group" v-if="form.content.trim()">
            <label>👁️ 内容预览</label>
            <div class="preview-container">
              <div class="markdown-body" v-html="previewHtml"></div>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submitting || !form.title.trim() || !form.content.trim()"
            >
              {{ submitting ? '保存中...' : '💾 保存修改' }}
            </button>
            <router-link
              :to="`/post/${postId}`"
              class="btn btn-secondary"
              :class="{ disabled: submitting }"
            >
              取消编辑
            </router-link>

          </div>
        </form>
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

export default {
  name: 'EditPost',
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
      categories: [],
      form: {
        title: '',
        content: '',
        category_id: ''
      },
      loading: false,
      loadError: null,
      submitting: false,
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
    previewHtml() {
      if (!this.form.content.trim()) return ''
      
      // 简化的Markdown渲染（实际项目中建议使用专门的Markdown库）
      let html = this.form.content
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/## (.*)/g, '<h2>$1</h2>')
        .replace(/# (.*)/g, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/^> (.*)/gm, '<blockquote>$1</blockquote>')
        .replace(/^- (.*)/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>')
      
      // 包装列表项
      html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')
      
      return html
    }
  },
  async created() {
    if (!this.authStore.isLoggedIn) {
      this.router.push('/login')
      return
    }
    // 初始化主题
    this.themeStore.initTheme()
    await this.loadData()
  },
  mounted() {
    this.autoResize()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.loadError = null
      
      try {
        const [postData, categoriesData] = await Promise.all([
          ApiService.getPost(this.postId),
          ApiService.getCategories()
        ])
        
        this.post = postData
        this.categories = categoriesData
        
        // 检查编辑权限
        if (!this.authStore.isAdmin && postData.author !== this.authStore.username) {
          this.loadError = '您没有权限编辑此文章'
          return
        }
        
        // 填充表单
        this.form = {
          title: postData.title || '',
          content: postData.content || '',
          category_id: postData.category_id || ''
        }
        
        this.$nextTick(() => {
          this.autoResize()
        })
        
      } catch (error) {
        this.loadError = error.message
      } finally {
        this.loading = false
      }
    },

    async loadPost() {
      await this.loadData()
    },

    async handleLogout() {
      const result = await this.authStore.logout()
      if (result.success) {
        this.router.push('/')
      }
    },

    async handleSubmit() {
      if (!this.form.title.trim() || !this.form.content.trim()) {
        this.showMessage('请填写完整的标题和内容', 'error')
        return
      }

      this.submitting = true
      try {
        const result = await ApiService.updatePost(this.postId, {
          title: this.form.title.trim(),
          content: this.form.content.trim(),
          category_id: this.form.category_id || null
        })

        if (result.success) {
          this.showMessage('文章更新成功！', 'success')
          setTimeout(() => {
            this.router.push(`/post/${this.postId}`)
          }, 1500)
        }
      } catch (error) {
        this.showMessage('更新失败：' + error.message, 'error')
      } finally {
        this.submitting = false
      }
    },

    insertText(before, after) {
      const textarea = this.$refs.contentTextarea
      if (!textarea) return

      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selectedText = this.form.content.substring(start, end)
      
      const newText = before + selectedText + after
      const beforeText = this.form.content.substring(0, start)
      const afterText = this.form.content.substring(end)
      
      this.form.content = beforeText + newText + afterText
      
      this.$nextTick(() => {
        textarea.focus()
        textarea.selectionStart = start + before.length
        textarea.selectionEnd = start + before.length + selectedText.length
        this.autoResize()
      })
    },

    autoResize() {
      const textarea = this.$refs.contentTextarea
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.max(300, textarea.scrollHeight) + 'px'
      }
    },

    getWordCount(content) {
      if (!content) return 0
      return content.replace(/\s/g, '').length
    },



    showMessage(text, type = 'success') {
      this.message = { show: true, text, type }
      setTimeout(() => {
        this.message.show = false
      }, 3000)
    }
  },

}
</script>

<style scoped>
.edit-post {
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

.light-mode .theme-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(0, 0, 0, 0.2);
}

.dark-mode .theme-btn:hover {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* 加载和错误状态 */
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
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.dark-mode .spinner {
  border-color: rgba(93, 173, 226, 0.2);
  border-top-color: #5dade2;
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

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: clamp(2em, 5vw, 2.5em);
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.light-mode .page-header h1 {
  color: #2c3e50;
}

.dark-mode .page-header h1 {
  color: white;
}

.page-header p {
  font-size: clamp(1em, 3vw, 1.1em);
  transition: color 0.3s ease;
}

.light-mode .page-header p {
  color: #5a6c7d;
}

.dark-mode .page-header p {
  color: rgba(255, 255, 255, 0.8);
}

/* 表单容器 */
.edit-form-container {
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.light-mode .edit-form-container {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .edit-form-container {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* 表单组样式 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: bold;
  font-size: 1.1em;
  transition: color 0.3s ease;
}

.light-mode .form-group label {
  color: #2c3e50;
}

.dark-mode .form-group label {
  color: white;
}

.form-group input,
.form-group select {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 1em;
  transition: all 0.3s ease;
}

.light-mode .form-group input,
.light-mode .form-group select {
  border: 1px solid rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.9);
  color: #2c3e50;
}

.dark-mode .form-group input,
.dark-mode .form-group select {
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.form-group input::placeholder {
  transition: color 0.3s ease;
}

.light-mode .form-group input::placeholder {
  color: #95a5a6;
}

.dark-mode .form-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.light-mode .form-group input:focus,
.light-mode .form-group select:focus {
  border-color: #667eea;
  background: rgba(255, 255, 255, 1);
}

.dark-mode .form-group input:focus,
.dark-mode .form-group select:focus {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.15);
}

.form-group input:disabled,
.form-group select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-hint {
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.light-mode .input-hint {
  color: #7f8c8d;
}

.dark-mode .input-hint {
  color: rgba(255, 255, 255, 0.7);
}

/* 编辑器样式 */
.editor-container {
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.light-mode .editor-container {
  border: 1px solid rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.9);
}

.dark-mode .editor-container {
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  flex-wrap: wrap;
  gap: 10px;
  transition: all 0.3s ease;
}

.light-mode .editor-toolbar {
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .editor-toolbar {
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.toolbar-group {
  display: flex;
  gap: 5px;
}

.toolbar-btn {
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.light-mode .toolbar-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #2c3e50;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.light-mode .toolbar-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #667eea;
}

.dark-mode .toolbar-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.dark-mode .toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.toolbar-info {
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.light-mode .toolbar-info {
  color: #7f8c8d;
}

.dark-mode .toolbar-info {
  color: rgba(255, 255, 255, 0.7);
}

.word-count {
  font-weight: bold;
}

.editor-container textarea {
  width: 100%;
  min-height: 300px;
  padding: 20px;
  border: none;
  background: transparent;
  font-size: 1em;
  line-height: 1.6;
  resize: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  transition: color 0.3s ease;
}

.light-mode .editor-container textarea {
  color: #2c3e50;
}

.dark-mode .editor-container textarea {
  color: white;
}

.editor-container textarea::placeholder {
  transition: color 0.3s ease;
}

.light-mode .editor-container textarea::placeholder {
  color: #95a5a6;
}

.dark-mode .editor-container textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.editor-container textarea:focus {
  outline: none;
}

/* 预览容器 */
.preview-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.light-mode .preview-container {
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark-mode .preview-container {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.markdown-body {
  line-height: 1.8;
  transition: color 0.3s ease;
}

.light-mode .markdown-body {
  color: #2c3e50;
}

.dark-mode .markdown-body {
  color: rgba(255, 255, 255, 0.95);
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
  margin: 20px 0 10px 0;
  font-weight: bold;
  transition: color 0.3s ease;
}

.light-mode .markdown-body h1,
.light-mode .markdown-body h2,
.light-mode .markdown-body h3 {
  color: #2c3e50;
}

.dark-mode .markdown-body h1,
.dark-mode .markdown-body h2,
.dark-mode .markdown-body h3 {
  color: white;
}

.markdown-body h1 { font-size: 1.8em; }
.markdown-body h2 { font-size: 1.5em; }
.markdown-body h3 { font-size: 1.3em; }

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

.markdown-body blockquote {
  margin: 15px 0;
  padding: 10px 15px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.light-mode .markdown-body blockquote {
  border-left: 4px solid rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

.dark-mode .markdown-body blockquote {
  border-left: 4px solid rgba(102, 126, 234, 0.6);
  background: rgba(0, 0, 0, 0.2);
}

.markdown-body ul {
  margin: 15px 0;
  padding-left: 25px;
}

.markdown-body li {
  margin: 5px 0;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 30px;
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

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.light-mode .btn-primary {
  background: #667eea;
  color: white;
}

.light-mode .btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
}

.dark-mode .btn-primary {
  background: rgba(102, 126, 234, 0.4);
  color: white;
  border: 1px solid rgba(102, 126, 234, 0.6);
}

.dark-mode .btn-primary:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-secondary:hover:not(.disabled) {
  transform: translateY(-2px);
}

.light-mode .btn-secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #2c3e50;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.light-mode .btn-secondary:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.9);
}

.dark-mode .btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.dark-mode .btn-secondary:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.btn-outline {
  background: transparent;
  transition: all 0.3s ease;
}

.btn-outline:hover:not(:disabled) {
  transform: translateY(-2px);
}

.light-mode .btn-outline {
  color: #667eea;
  border: 1px solid #667eea;
}

.light-mode .btn-outline:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.1);
}

.dark-mode .btn-outline {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.dark-mode .btn-outline:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.btn:disabled,
.btn.disabled {
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
  
  .edit-form-container {
    padding: 25px;
  }
  
  .editor-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .toolbar-group {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  
  .edit-form-container {
    padding: 20px;
  }
  
  .editor-container textarea {
    padding: 15px;
    font-size: 14px;
  }
}
</style>