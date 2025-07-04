<template>
  <div class="write-post" :class="themeStore.themeClass">
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
      <div class="write-form-container">
        <div class="page-header">
          <h1>✍️ 写新文章</h1>
          <p>分享你的想法和知识</p>
        </div>

        <form @submit.prevent="handleSubmit" class="write-form">
          <!-- 标题输入 -->
          <div class="form-group">
            <label for="title">📝 文章标题</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              placeholder="输入一个吸引人的标题..."
              required
              :disabled="submitting"
              maxlength="100"
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
              <option value="">请选择分类（可选）</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>

          <!-- 内容编辑器 -->
          <div class="form-group">
            <label for="content">📄 文章内容</label>
            <div class="editor-container">
              <!-- 编辑器工具栏 -->
              <div class="editor-toolbar">
                <div class="toolbar-left">
                  <div class="toolbar-group">
                    <button type="button" @click="insertText('**', '**')" class="toolbar-btn" title="粗体">
                      <strong>B</strong>
                    </button>
                    <button type="button" @click="insertText('*', '*')" class="toolbar-btn" title="斜体">
                      <em>I</em>
                    </button>
                    <button type="button" @click="insertText('`', '`')" class="toolbar-btn" title="代码">
                      Code
                    </button>
                    <button type="button" @click="insertText('~~', '~~')" class="toolbar-btn" title="删除线">
                      <s>S</s>
                    </button>
                  </div>
                  <div class="toolbar-group">
                    <button type="button" @click="insertText('# ', '')" class="toolbar-btn" title="一级标题">
                      H1
                    </button>
                    <button type="button" @click="insertText('## ', '')" class="toolbar-btn" title="二级标题">
                      H2
                    </button>
                    <button type="button" @click="insertText('### ', '')" class="toolbar-btn" title="三级标题">
                      H3
                    </button>
                  </div>
                  <div class="toolbar-group">
                    <button type="button" @click="insertText('- ', '')" class="toolbar-btn" title="无序列表">
                      • List
                    </button>
                    <button type="button" @click="insertText('1. ', '')" class="toolbar-btn" title="有序列表">
                      1. List
                    </button>
                    <button type="button" @click="insertText('> ', '')" class="toolbar-btn" title="引用">
                      Quote
                    </button>
                  </div>
                  <div class="toolbar-group">
                    <button type="button" @click="insertText('[链接文字](', ')')" class="toolbar-btn" title="链接">
                      🔗 Link
                    </button>
                    <button type="button" @click="insertText('![图片描述](', ')')" class="toolbar-btn" title="图片">
                      🖼️ Image
                    </button>
                    <button type="button" @click="insertText('```\n', '\n```')" class="toolbar-btn" title="代码块">
                      { } Code
                    </button>
                  </div>
                </div>
                <div class="toolbar-right">
                  <div class="toolbar-info">
                    <span class="word-count">{{ getWordCount(form.content) }} 字</span>
                    <span class="read-time">约 {{ getReadTime(form.content) }} 分钟阅读</span>
                  </div>
                </div>
              </div>

              <!-- 编辑器主体 -->
              <div class="editor-body">
                <div class="editor-pane">
                  <div class="pane-header">
                    <span class="pane-title">📝 编辑</span>
                    <button 
                      type="button" 
                      @click="togglePreview" 
                      class="preview-toggle"
                      :class="{ active: showPreview }"
                    >
                      {{ showPreview ? '隐藏预览' : '显示预览' }}
                    </button>
                  </div>
                  <textarea
                    id="content"
                    ref="contentTextarea"
                    v-model="form.content"
                    placeholder="开始写作你的文章...

你可以使用 Markdown 语法：

# 这是一级标题
## 这是二级标题
### 这是三级标题

**这是粗体文字**
*这是斜体文字*
`这是行内代码`
~~这是删除线~~

> 这是引用内容

- 这是无序列表项
- 另一个列表项

1. 这是有序列表项
2. 另一个编号项

[这是链接](https://example.com)
![这是图片](图片地址)

```
这是代码块
支持多行代码
```

---

快捷键：
- Ctrl+B：粗体
- Ctrl+I：斜体
- Ctrl+K：链接
- Tab：增加缩进
- Shift+Tab：减少缩进"
                    required
                    :disabled="submitting"
                    @input="autoResize"
                    @keydown="handleKeyDown"
                  ></textarea>
                </div>
                
                <!-- 预览面板 -->
                <div v-if="showPreview" class="preview-pane">
                  <div class="pane-header">
                    <span class="pane-title">👁️ 预览</span>
                  </div>
                  <div class="preview-content">
                    <div v-if="form.content.trim()" class="markdown-body" v-html="previewHtml"></div>
                    <div v-else class="preview-empty">
                      开始写作以查看预览效果...
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="input-hint">
              支持完整的 Markdown 语法，{{ getWordCount(form.content) }} 字符
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submitting || !form.title.trim() || !form.content.trim()"
            >
              {{ submitting ? '发布中...' : '🚀 发布文章' }}
            </button>
            <button
              type="button"
              @click="saveDraft"
              class="btn btn-outline"
              :disabled="submitting"
            >
              💾 保存草稿
            </button>
            <router-link
              to="/"
              class="btn btn-secondary"
              :class="{ disabled: submitting }"
            >
              取消
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
import { useRouter } from 'vue-router'
import ApiService from '../services/api'

export default {
  name: 'WritePost',
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    
    return { authStore, themeStore, router }
  },
  data() {
    return {
      categories: [],
      form: {
        title: '',
        content: '',
        category_id: ''
      },
      showPreview: false,
      submitting: false,
      message: {
        show: false,
        text: '',
        type: 'success'
      }
    }
  },
  computed: {
    previewHtml() {
      if (!this.form.content.trim()) return ''
      
      // 简化的Markdown渲染
      let html = this.form.content
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/## (.*)/g, '<h2>$1</h2>')
        .replace(/# (.*)/g, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/~~(.*?)~~/g, '<del>$1</del>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/^> (.*)/gm, '<blockquote>$1</blockquote>')
        .replace(/^- (.*)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*)/gm, '<li>$1</li>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
        .replace(/```\n([\s\S]*?)\n```/g, '<pre><code>$1</code></pre>')
        .replace(/\n/g, '<br>')
        .replace(/---/g, '<hr>')
      
      // 包装列表项
      html = html.replace(/(<li>.*?<\/li>)/g, match => {
        if (!match.includes('<ul>') && !match.includes('<ol>')) {
          return `<ul>${match}</ul>`
        }
        return match
      })
      
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
    
    await this.loadCategories()
  },
  mounted() {
    this.autoResize()
  },
  methods: {
    async loadCategories() {
      try {
        this.categories = await ApiService.getCategories()
      } catch (error) {
        console.error('加载分类失败:', error)
      }
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
        const result = await ApiService.createPost({
          title: this.form.title.trim(),
          content: this.form.content.trim(),
          category_id: this.form.category_id || null
        })

        if (result.success) {
          this.showMessage('文章发布成功！', 'success')
          this.clearDraft()
          setTimeout(() => {
            this.router.push('/my-posts')
          }, 1500)
        }
      } catch (error) {
        this.showMessage('发布失败：' + error.message, 'error')
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

    handleKeyDown(event) {
      // 快捷键支持
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'b':
            event.preventDefault()
            this.insertText('**', '**')
            break
          case 'i':
            event.preventDefault()
            this.insertText('*', '*')
            break
          case 'k':
            event.preventDefault()
            this.insertText('[', ']()')
            break
        }
      }
      
      // Tab键处理
      if (event.key === 'Tab') {
        event.preventDefault()
        const textarea = event.target
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        
        if (event.shiftKey) {
          // Shift+Tab: 减少缩进
          const lines = this.form.content.substring(0, start).split('\n')
          const currentLine = lines[lines.length - 1]
          if (currentLine.startsWith('  ')) {
            const beforeText = this.form.content.substring(0, start - currentLine.length)
            const afterText = this.form.content.substring(start)
            this.form.content = beforeText + currentLine.substring(2) + afterText
            this.$nextTick(() => {
              textarea.selectionStart = start - 2
              textarea.selectionEnd = end - 2
            })
          }
        } else {
          // Tab: 增加缩进
          const beforeText = this.form.content.substring(0, start)
          const afterText = this.form.content.substring(end)
          this.form.content = beforeText + '  ' + afterText
          this.$nextTick(() => {
            textarea.selectionStart = start + 2
            textarea.selectionEnd = end + 2
          })
        }
      }
    },

    togglePreview() {
      this.showPreview = !this.showPreview
    },

    autoResize() {
      const textarea = this.$refs.contentTextarea
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.max(400, textarea.scrollHeight) + 'px'
      }
    },

    getWordCount(content) {
      if (!content) return 0
      return content.replace(/\s/g, '').length
    },

    getReadTime(content) {
      if (!content) return 0
      const wordCount = this.getWordCount(content)
      return Math.max(1, Math.ceil(wordCount / 400))
    },

    saveDraft() {
      const draftData = {
        title: this.form.title,
        content: this.form.content,
        category_id: this.form.category_id,
        timestamp: Date.now()
      }
      localStorage.setItem('write_draft', JSON.stringify(draftData))
      this.showMessage('草稿已保存', 'success')
    },



    clearDraft() {
      localStorage.removeItem('write_draft')
    },

    showMessage(text, type = 'success') {
      this.message = { show: true, text, type }
      setTimeout(() => {
        this.message.show = false
      }, 3000)
    }
  },
  beforeUnmount() {
    // 页面离开时自动保存草稿
    if (this.form.title.trim() || this.form.content.trim()) {
      this.saveDraft()
    }
  }
}
</script>

<style scoped>
.write-post {
  min-height: 100vh;
  width: 100%;
  transition: all 0.3s ease;
}

/* 主题相关 CSS 变量 */
.write-post.light-mode {
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
  --navbar-bg: rgba(255, 255, 255, 0.9);
  --form-bg: rgba(255, 255, 255, 0.95);
  --input-bg: rgba(255, 255, 255, 0.8);
  --toolbar-bg: rgba(248, 249, 250, 0.9);
  --code-bg: rgba(248, 249, 250, 0.9);
  --preview-bg: rgba(248, 249, 250, 0.8);
}

.write-post.dark-mode {
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
  --navbar-bg: rgba(26, 32, 44, 0.9);
  --form-bg: rgba(26, 32, 44, 0.95);
  --input-bg: rgba(45, 55, 72, 0.8);
  --toolbar-bg: rgba(26, 32, 44, 0.9);
  --code-bg: rgba(26, 32, 44, 0.9);
  --preview-bg: rgba(45, 55, 72, 0.8);
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

.write-post.light-mode .background-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.write-post.dark-mode .background-gradient {
  background: linear-gradient(135deg, #2d3436 0%, #636e72 50%, #2c2c54 100%);
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
}

.nav-link {
  color: var(--text-primary, white);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
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
  transition: color 0.3s ease;
}

/* 表单容器 */
.write-form-container {
  background: var(--form-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  box-shadow: 0 8px 32px var(--shadow-color, rgba(0, 0, 0, 0.1));
  transition: all 0.3s ease;
}

.write-form {
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
  color: var(--text-primary, white);
  font-weight: bold;
  font-size: 1.1em;
  transition: color 0.3s ease;
}

.form-group input,
.form-group select {
  padding: 12px 16px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.3));
  border-radius: 8px;
  background: var(--input-bg, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, white);
  font-size: 1em;
  transition: all 0.3s ease;
}

.form-group input::placeholder {
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--accent-color, rgba(102, 126, 234, 0.6));
  background: var(--bg-primary, rgba(255, 255, 255, 0.9));
  color: var(--text-primary, #2c3e50);
  box-shadow: 0 0 0 3px rgba(var(--accent-color), 0.1);
}

.write-post.light-mode .form-group input:focus,
.write-post.light-mode .form-group select:focus {
  color: #2c3e50;
}

.write-post.dark-mode .form-group input:focus,
.write-post.dark-mode .form-group select:focus {
  color: #e2e8f0;
}

.form-group select option {
  background: var(--bg-primary, white);
  color: var(--text-primary, #2c3e50);
}

.form-group input:disabled,
.form-group select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-hint {
  color: var(--text-muted, rgba(255, 255, 255, 0.7));
  font-size: 0.9em;
  transition: color 0.3s ease;
}

/* 编辑器样式 */
.editor-container {
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.3));
  border-radius: 12px;
  background: var(--input-bg, rgba(255, 255, 255, 0.1));
  overflow: hidden;
  transition: all 0.3s ease;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: var(--toolbar-bg, rgba(0, 0, 0, 0.2));
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  flex-wrap: wrap;
  gap: 15px;
  transition: all 0.3s ease;
}

.toolbar-left {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.toolbar-group {
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  padding: 8px 12px;
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, white);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.3));
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.toolbar-btn:hover {
  background: var(--bg-tertiary, rgba(255, 255, 255, 0.2));
  transform: translateY(-1px);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.toolbar-info {
  display: flex;
  gap: 15px;
  color: var(--text-secondary, rgba(255, 255, 255, 0.7));
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.word-count,
.read-time {
  font-weight: bold;
}

/* 编辑器主体 */
.editor-body {
  display: flex;
  min-height: 400px;
}

.editor-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: var(--bg-secondary, rgba(0, 0, 0, 0.1));
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  transition: all 0.3s ease;
}

.pane-title {
  color: var(--text-primary, white);
  font-weight: bold;
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.preview-toggle {
  padding: 4px 8px;
  background: var(--accent-color, rgba(102, 126, 234, 0.3));
  color: var(--text-primary, white);
  border: 1px solid var(--accent-color, rgba(102, 126, 234, 0.5));
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  transition: all 0.3s ease;
}

.preview-toggle:hover,
.preview-toggle.active {
  background: var(--accent-color, rgba(102, 126, 234, 0.5));
  transform: translateY(-1px);
}

.editor-pane textarea {
  flex: 1;
  padding: 20px;
  border: none;
  background: transparent;
  color: var(--text-primary, white);
  font-size: 1em;
  line-height: 1.8;
  resize: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  transition: color 0.3s ease;
}

.editor-pane textarea::placeholder {
  color: var(--text-muted, rgba(255, 255, 255, 0.5));
}

.editor-pane textarea:focus {
  outline: none;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--preview-bg, rgba(0, 0, 0, 0.1));
  transition: all 0.3s ease;
}

.preview-empty {
  color: var(--text-muted, rgba(255, 255, 255, 0.5));
  text-align: center;
  margin-top: 50px;
  font-style: italic;
  transition: color 0.3s ease;
}

/* Markdown预览样式 */
.markdown-body {
  color: var(--text-primary, rgba(255, 255, 255, 0.95));
  line-height: 1.8;
  transition: color 0.3s ease;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
  color: var(--text-primary, white);
  margin: 25px 0 15px 0;
  font-weight: bold;
  transition: color 0.3s ease;
}

.markdown-body h1 { font-size: 1.8em; }
.markdown-body h2 { font-size: 1.5em; }
.markdown-body h3 { font-size: 1.3em; }

.markdown-body p {
  margin: 15px 0;
}

.markdown-body strong {
  color: var(--text-primary, white);
  font-weight: bold;
  transition: color 0.3s ease;
}

.markdown-body em {
  font-style: italic;
}

.markdown-body del {
  text-decoration: line-through;
  opacity: 0.7;
}

.markdown-body code {
  background: var(--code-bg, rgba(0, 0, 0, 0.4));
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #e6db74;
  font-size: 0.9em;
  transition: background 0.3s ease;
}

.markdown-body pre {
  background: var(--code-bg, rgba(0, 0, 0, 0.4));
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 20px 0;
  transition: background 0.3s ease;
}

.markdown-body pre code {
  background: none;
  padding: 0;
  color: #f8f8f2;
}

.markdown-body blockquote {
  border-left: 4px solid var(--accent-color, rgba(102, 126, 234, 0.6));
  margin: 20px 0;
  padding: 15px 20px;
  background: var(--bg-secondary, rgba(0, 0, 0, 0.2));
  border-radius: 4px;
  transition: all 0.3s ease;
}

.markdown-body ul,
.markdown-body ol {
  margin: 15px 0;
  padding-left: 30px;
}

.markdown-body li {
  margin: 8px 0;
}

.markdown-body a {
  color: var(--accent-color, rgba(102, 126, 234, 0.8));
  text-decoration: none;
  transition: color 0.3s ease;
}

.markdown-body a:hover {
  color: var(--text-primary, white);
  text-decoration: underline;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
}

.markdown-body hr {
  border: none;
  height: 2px;
  background: var(--border-color, rgba(255, 255, 255, 0.3));
  margin: 30px 0;
  border-radius: 1px;
  transition: background 0.3s ease;
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
  padding: 14px 28px;
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

.btn-primary:hover:not(:disabled) {
  background: var(--accent-color, rgba(102, 126, 234, 0.4));
  transform: translateY(-2px);
  box-shadow: 0 4px 15px var(--shadow-color, rgba(102, 126, 234, 0.3));
}

.btn-secondary {
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, white);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.3));
}

.btn-secondary:hover:not(.disabled) {
  background: var(--bg-tertiary, rgba(255, 255, 255, 0.2));
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary, white);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.5));
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  transform: translateY(-2px);
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
  
  .write-form-container {
    padding: 25px;
  }
  
  .editor-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .toolbar-left {
    justify-content: center;
  }
  
  .toolbar-right {
    justify-content: center;
  }
  
  .editor-body {
    flex-direction: column;
  }
  
  .preview-pane {
    border-left: none;
    border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  }
  
  .form-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  
  .write-form-container {
    padding: 20px;
  }
  
  .editor-pane textarea {
    padding: 15px;
    font-size: 14px;
  }
  
  .toolbar-group {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>