<template>
  <div class="home" :class="themeStore.themeClass">
    <div class="background-gradient"></div>
    
    <!-- 主题切换按钮 -->
    <div class="theme-toggle">
      <button @click="themeStore.toggleTheme()" class="theme-btn" :title="themeStore.isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
        {{ themeStore.isDarkMode ? '🌞' : '🌙' }}
      </button>
    </div>
    
    <!-- 未登录状态 -->
    <div v-if="!authStore.isLoggedIn" class="welcome-container">
      <!-- 轮播图区域 -->
      <div class="carousel-section">
        <div class="carousel-container">
          <div class="carousel-wrapper" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
            <div v-for="(slide, index) in slides" :key="index" class="carousel-slide">
              <div class="slide-content">
                <div class="slide-icon">{{ slide.icon }}</div>
                <h3>{{ slide.title }}</h3>
                <p>{{ slide.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- 轮播指示器 -->
          <div class="carousel-indicators">
            <button 
              v-for="(slide, index) in slides" 
              :key="index"
              @click="goToSlide(index)"
              :class="{ active: currentSlide === index }"
              class="indicator"
            ></button>
          </div>
          
          <!-- 轮播控制按钮 -->
          <button @click="prevSlide" class="carousel-btn prev-btn">‹</button>
          <button @click="nextSlide" class="carousel-btn next-btn">›</button>
        </div>
      </div>

      <!-- 主要欢迎内容 -->
      <div class="welcome-content">
        <div class="welcome-header">
          <h1 class="welcome-title">
            <span class="title-line">🚀 欢迎来到</span>
            <span class="title-line gradient-text">博客系统</span>
          </h1>
          <p class="welcome-subtitle">分享你的想法，记录你的生活，连接全世界</p>
        </div>
        
        <!-- 特色功能介绍 -->
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.id">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h4>{{ feature.title }}</h4>
            <p>{{ feature.description }}</p>
          </div>
        </div>
        
        <!-- 行动按钮 -->
        <div class="welcome-actions">
          <router-link to="/login" class="btn btn-primary">
            <span class="btn-icon">🔐</span>
            立即登录
          </router-link>
          <router-link to="/register" class="btn btn-secondary">
            <span class="btn-icon">✨</span>
            免费注册
          </router-link>
        </div>
        
        <!-- 统计数据 -->
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-number" data-target="1000">0</div>
            <div class="stat-label">用户数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="5000">0</div>
            <div class="stat-label">文章数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="10000">0</div>
            <div class="stat-label">访问次数</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 已登录状态 -->
    <div v-else class="main-content">
      <!-- 导航栏 -->
      <nav class="navbar">
        <div class="nav-container">
          <div class="nav-brand">
            <h2>📝 博客系统</h2>
          </div>
          <div class="nav-menu">
            <div class="user-info" @click="showAvatarUpload = true">
              <div class="user-avatar" :title="'点击上传头像'">
                <img 
                  v-if="authStore.avatar" 
                  :src="authStore.avatar" 
                  :alt="authStore.username + '的头像'"
                  class="avatar-img"
                />
                <div v-else class="avatar-placeholder">
                  👤
                </div>
              </div>
              <span class="username">{{ authStore.username }}</span>
            </div>
            <router-link to="/my-posts" class="nav-link">我的文章</router-link>
            <router-link to="/write" class="nav-link">写文章</router-link>
            <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">管理面板</router-link>
            <button @click="handleLogout" class="logout-btn">退出</button>
          </div>
        </div>
      </nav>
      
      <!-- 主要内容区域 -->
      <div class="container">
        <!-- 搜索框 -->
        <div class="search-section">
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchKeyword" 
              @keyup.enter="performSearch"
              placeholder="搜索文章标题、内容..."
              class="search-input"
            >
            <button @click="performSearch" class="search-btn" :disabled="searchLoading">
              {{ searchLoading ? '搜索中...' : '🔍 搜索' }}
            </button>
            <button v-if="isSearchMode" @click="clearSearch" class="clear-btn" title="清除搜索">
              ✕
            </button>
          </div>
          <div v-if="isSearchMode" class="search-status">
            <span class="search-info">
              🔍 搜索 "{{ currentSearchKeyword }}" 的结果
              <span v-if="searchResults.length > 0">({{ searchResults.length }} 篇文章)</span>
              <span v-if="searchMethod === 'local'" class="search-method-tag">本地搜索</span>
            </span>
          </div>
        </div>
        
        <!-- 分类筛选 -->
        <div class="filters" v-if="!isSearchMode">
          <button 
            @click="selectedCategory = null"
            :class="{ active: selectedCategory === null }"
            class="filter-btn"
          >
            全部文章 ({{ posts.length }})
          </button>
          <button 
            v-for="category in categories" 
            :key="category.id"
            @click="selectedCategory = category.id"
            :class="{ active: selectedCategory === category.id }"
            class="filter-btn"
          >
            {{ category.name }}
          </button>
        </div>
        
        <!-- 文章列表 -->
        <div class="posts-list">
          <div v-if="loading || searchLoading" class="loading">
            <div class="spinner"></div>
            <p>{{ searchLoading ? '搜索中...' : '加载中...' }}</p>
          </div>
          
          <div v-else-if="filteredPosts.length === 0" class="no-posts">
            <div class="no-posts-icon">{{ isSearchMode ? '🤖' : '🙌' }}</div>
            <h3>{{ isSearchMode ? '未找到相关文章' : '暂无文章' }}</h3>
            <p>{{ isSearchMode ? '尝试使用不同的关键词进行搜索' : '还没有文章，快去写第一篇吧！' }}</p>
            <router-link v-if="!isSearchMode" to="/write" class="btn btn-primary">写文章</router-link>
            <button v-else @click="clearSearch" class="btn btn-secondary">清除搜索</button>
          </div>
          
          <div v-else class="posts-grid">
            <article 
              v-for="post in filteredPosts" 
              :key="post.id" 
              class="post-card"
              @click="viewPost(post.id)"
              @contextmenu="showPreview(post, $event)"
            >
              <div class="post-header">
                <h3 class="post-title">{{ post.title }}</h3>
                <div class="post-meta">
                  <span class="post-author">
                    <UserAvatar 
                      :username="post.author" 
                      :avatar="post.author_avatar" 
                      size="small" 
                    />
                    {{ post.author }}
                  </span>
                  <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
                  <span v-if="post.category_name" class="post-category">
                    🏷️ {{ post.category_name }}
                  </span>
                </div>
              </div>
              
              <div class="post-content" v-html="post.preview_html"></div>
              
              <div class="post-footer">
                <button class="read-more-btn">阅读全文 →</button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 悬浮预览窗口 -->
    <div 
      v-if="previewPost" 
      class="preview-modal"
      :class="{ active: previewPost }"
      @click.self="hidePreview"
    >
      <div class="preview-content">
        <div class="preview-header">
          <h3 class="preview-title">{{ previewPost.title }}</h3>
          <button @click="hidePreview" class="close-btn" title="关闭">×</button>
          <div class="preview-meta">
            <span class="preview-author">
              <UserAvatar 
                :username="previewPost.author" 
                :avatar="previewPost.author_avatar" 
                size="small" 
              />
              {{ previewPost.author }}
            </span>
            <span class="preview-date">📅 {{ formatDate(previewPost.created_at) }}</span>
            <span v-if="previewPost.category_name" class="preview-category">
              🏷️ {{ previewPost.category_name }}
            </span>
          </div>
        </div>
        
        <div class="preview-body">
          <div class="preview-excerpt" v-html="previewPost.preview_html || previewPost.content"></div>
          
          <div class="preview-stats">
            <div class="stat-item">
              <span class="stat-icon">📖</span>
              <span class="stat-text">约 {{ getReadTime(previewPost.content || '') }} 分钟阅读</span>
            </div>
          </div>
        </div>
        
        <div class="preview-footer">
          <button @click="viewPost(previewPost.id)" class="preview-read-btn">
            阅读全文 →
          </button>
        </div>
      </div>
    </div>
    
    <!-- 头像上传模态框 -->
    <div 
      v-if="showAvatarUpload" 
      class="avatar-upload-modal"
      :class="{ active: showAvatarUpload }"
      @click.self="closeAvatarUpload" 
    >
      <div class="avatar-upload-content">
        <div class="avatar-upload-header">
          <h3>上传头像</h3>
          <button @click="closeAvatarUpload" class="close-btn" title="关闭">×</button>
        </div>
        
        <div class="avatar-upload-body">
          <!-- 当前头像预览 -->
          <div class="current-avatar-section">
            <h4>当前头像</h4>
            <div class="current-avatar">
              <img 
                v-if="authStore.avatar" 
                :src="authStore.avatar" 
                :alt="authStore.username + '的头像'"
                class="current-avatar-img"
              />
              <div v-else class="current-avatar-placeholder">
                👤
              </div>
            </div>
          </div>
          
          <!-- 文件选择区域 -->
          <div class="file-select-section">
            <h4>选择新头像</h4>
            <div class="file-drop-zone" @click="$refs.avatarInput.click()">
              <input 
                ref="avatarInput"
                type="file" 
                accept="image/*" 
                @change="handleFileSelect"
                style="display: none"
              />
              <div v-if="!avatarPreview" class="drop-zone-content">
                <div class="drop-zone-icon">📷</div>
                <p>点击选择图片文件</p>
                <p class="file-hint">支持 JPG、PNG、GIF 格式，建议大小不超过 5MB</p>
              </div>
              <div v-else class="preview-container">
                <img :src="avatarPreview" alt="头像预览" class="avatar-preview" />
                <button @click.stop="clearSelection" class="clear-preview-btn" title="清除选择">×</button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="avatar-upload-footer">
          <button @click="closeAvatarUpload" class="btn btn-secondary">取消</button>
          <button 
            @click="uploadAvatar" 
            :disabled="!avatarFile || avatarUploading"
            class="btn btn-primary"
          >
            {{ avatarUploading ? '上传中...' : '上传头像' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import ApiService from '../services/api'
import UserAvatar from '../components/UserAvatar.vue'

export default {
  name: 'Home',
  components: {
    UserAvatar
  },
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
      posts: [],
      categories: [],
      selectedCategory: null,
      loading: false,
      // 搜索相关
      searchKeyword: '',
      currentSearchKeyword: '',
      searchResults: [],
      isSearchMode: false,
      searchLoading: false,
      searchMethod: '', // 'api' 或 'local'
      // 右键预览相关
      previewPost: null,
      // 头像上传相关
      showAvatarUpload: false,
      avatarFile: null,
      avatarPreview: null,
      avatarUploading: false,
      // 轮播图数据
      currentSlide: 0,
      slideInterval: null,
      slides: [
        {
          icon: '✍️',
          title: '自由写作',
          description: '随心所欲地表达你的想法，支持富文本编辑器'
        },
        {
          icon: '🌐',
          title: '全球分享',
          description: '与世界各地的读者分享你的故事和见解'
        },
        {
          icon: '💬',
          title: '互动交流',
          description: '通过评论功能与读者建立深度连接'
        },
        {
          icon: '📊',
          title: '数据统计',
          description: '详细的阅读统计，了解你的影响力'
        }
      ],
      // 特色功能
      features: [
        {
          id: 1,
          icon: '🎨',
          title: '美观设计',
          description: '现代化的界面设计，提供最佳阅读体验'
        },
        {
          id: 2,
          icon: '📱',
          title: '响应式',
          description: '完美适配各种设备，随时随地写作'
        },
        {
          id: 3,
          icon: '🔒',
          title: '安全可靠',
          description: '数据加密保护，让你的内容更安全'
        },
        {
          id: 4,
          icon: '⚡',
          title: '快速加载',
          description: '优化的性能，让阅读体验更流畅'
        },
        {
          id: 5,
          icon: '🌙',
          title: '主题切换',
          description: '支持明暗主题自由切换，保护你的视力'
        },
        {
          id: 6,
          icon: '☁️',
          title: '云端同步',
          description: '数据云端存储，多设备无缝同步访问'
        }
      ]
    }
  },
  computed: {
    filteredPosts() {
      // 如果是搜索模式，返回搜索结果
      if (this.isSearchMode) {
        return this.searchResults
      }
      
      // 否则按分类筛选
      if (this.selectedCategory === null) {
        return this.posts
      }
      return this.posts.filter(post => post.category_id === this.selectedCategory)
    }
  },
  async created() {
    // 首先检查用户的认证状态
    await this.authStore.checkAuth()
    
    if (this.authStore.isLoggedIn) {
      await this.loadData()
    } else {
      // 启动轮播图自动播放
      this.startCarousel()
      // 启动数字动画
      this.$nextTick(() => {
        this.animateNumbers()
      })
    }
  },
  
  mounted() {
    // 添加ESC键监听
    this.handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        if (this.previewPost) {
          this.hidePreview()
        } else if (this.showAvatarUpload) {
          this.closeAvatarUpload()
        }
      }
    }
    document.addEventListener('keydown', this.handleKeyDown)
  },
  
  beforeUnmount() {
    // 清理轮播图定时器
    if (this.slideInterval) {
      clearInterval(this.slideInterval)
    }
    // 清理键盘事件监听器
    if (this.handleKeyDown) {
      document.removeEventListener('keydown', this.handleKeyDown)
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const [postsData, categoriesData] = await Promise.all([
          ApiService.getPosts(),
          ApiService.getCategories()
        ])
        this.posts = postsData
        this.categories = categoriesData
        
        // 调试：检查文章数据结构
        if (postsData.length > 0) {
          console.log('文章数据样例:', postsData[0])
          console.log('是否包含author_avatar:', 'author_avatar' in postsData[0])
        }
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async handleLogout() {
      const result = await this.authStore.logout()
      if (result.success) {
        this.router.go(0) // 刷新页面
      }
    },
    
    viewPost(postId) {
      this.router.push(`/post/${postId}`)
    },
    
    // 搜索相关方法
    async performSearch() {
      if (!this.searchKeyword.trim()) {
        return
      }
      
      this.searchLoading = true
      this.currentSearchKeyword = this.searchKeyword.trim()
      
      try {
        console.log('开始搜索，关键词:', this.currentSearchKeyword)
        
        // 调用搜索API
        const response = await ApiService.get('/search', {
          params: {
            keyword: this.currentSearchKeyword
          }
        })
        
        console.log('搜索API响应:', response)
        
        // 处理不同的响应格式
        let posts = []
        if (response.data && response.data.posts) {
          posts = response.data.posts
        } else if (response.posts) {
          posts = response.posts
        } else if (response.data && Array.isArray(response.data)) {
          posts = response.data
        } else if (Array.isArray(response)) {
          posts = response
        }
        
        console.log('解析到的文章列表:', posts)
        
        this.searchResults = posts
        this.isSearchMode = true
        this.searchMethod = 'api'
        
        if (posts.length === 0) {
          console.log('未找到搜索结果')
        }
        
      } catch (error) {
        console.error('搜索失败:', error)
        
        // 更详细的错误处理
        if (error.message.includes('404') || error.message.includes('Not Found')) {
          console.log('后端搜索API不可用，使用前端搜索降级方案')
          this.searchResults = this.performLocalSearch(this.currentSearchKeyword)
          this.isSearchMode = true
          this.searchMethod = 'local'
        } else if (error.message.includes('网络')) {
          alert('网络连接失败，请检查网络连接')
          this.searchResults = []
          this.isSearchMode = false
          this.searchMethod = ''
        } else {
          console.log('搜索API出错，尝试前端搜索降级方案')
          this.searchResults = this.performLocalSearch(this.currentSearchKeyword)
          this.isSearchMode = true
          this.searchMethod = 'local'
        }
      } finally {
        this.searchLoading = false
      }
    },
    
    // 前端搜索降级方案
    performLocalSearch(keyword) {
      if (!keyword || this.posts.length === 0) {
        return []
      }
      
      const searchTerm = keyword.toLowerCase()
      return this.posts.filter(post => {
        const title = (post.title || '').toLowerCase()
        const content = (post.content || post.preview_html || '').toLowerCase()
        const author = (post.author || '').toLowerCase()
        
        return title.includes(searchTerm) || 
               content.includes(searchTerm) || 
               author.includes(searchTerm)
      })
    },
    
    clearSearch() {
      this.searchKeyword = ''
      this.currentSearchKeyword = ''
      this.searchResults = []
      this.isSearchMode = false
      this.searchMethod = ''
      this.selectedCategory = null // 重置分类筛选
    },
    
    formatDate(dateString) {
      try {
        return new Date(dateString).toLocaleDateString('zh-CN')
      } catch {
        return '未知日期'
      }
    },
    
    // 轮播图控制方法
    startCarousel() {
      this.slideInterval = setInterval(() => {
        this.nextSlide()
      }, 4000) // 每4秒切换
    },
    
    nextSlide() {
      this.currentSlide = (this.currentSlide + 1) % this.slides.length
    },
    
    prevSlide() {
      this.currentSlide = this.currentSlide === 0 ? this.slides.length - 1 : this.currentSlide - 1
    },
    
    goToSlide(index) {
      this.currentSlide = index
    },
    
    // 数字动画
    animateNumbers() {
      const statNumbers = document.querySelectorAll('.stat-number')
      statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target'))
        let count = 0
        const increment = target / 100
        
        const updateCount = () => {
          if (count < target) {
            count += increment
            stat.textContent = Math.floor(count).toLocaleString()
            setTimeout(updateCount, 30)
          } else {
            stat.textContent = target.toLocaleString()
          }
        }
        
        // 延迟启动动画
        setTimeout(updateCount, 500)
      })
    },
    
    // 右键预览相关方法
    showPreview(post, event) {
      // 阻止默认的右键菜单
      event.preventDefault()
      
      // 清除可能存在的隐藏定时器
      if (this.hideTimer) {
        clearTimeout(this.hideTimer)
        this.hideTimer = null
      }
      
      // 立即显示预览窗口
      this.previewPost = post
    },
    
    hidePreview() {
      this.previewPost = null
    },
    
    getReadTime(content) {
      if (!content) return 1
      const wordCount = content.replace(/\s/g, '').length
      return Math.max(1, Math.ceil(wordCount / 400))
    },

    // 获取作者头像的方法
    getAuthorAvatar(authorName) {
      // 如果是当前用户，返回当前用户的头像
      if (authorName === this.authStore.username) {
        return this.authStore.avatar
      }
      // 否则返回null，显示默认头像
      return null
    },
    // 头像上传相关方法
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        alert('请选择图片文件')
        return
      }
      
      // 验证文件大小 (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('文件大小不能超过 5MB')
        return
      }
      
      this.avatarFile = file
      
      // 创建预览
      const reader = new FileReader()
      reader.onload = (e) => {
        this.avatarPreview = e.target.result
      }
      reader.readAsDataURL(file)
    },

    clearSelection() {
      this.avatarFile = null
      this.avatarPreview = null
      if (this.$refs.avatarInput) {
        this.$refs.avatarInput.value = ''
      }
    },

    closeAvatarUpload() {
      this.showAvatarUpload = false
      this.clearSelection()
    },

    async uploadAvatar() {
      if (!this.avatarFile) {
        alert('请先选择头像文件')
        return
      }
      
      console.log('开始上传头像...')
      console.log('当前登录状态:', this.authStore.isLoggedIn)
      console.log('当前用户:', this.authStore.user)
      
      // 上传前先检查一下当前的登录状态
      try {
        await this.authStore.checkAuth()
        if (!this.authStore.isLoggedIn) {
          alert('登录已过期，请重新登录')
          this.$router.push('/login')
          return
        }
      } catch (error) {
        console.error('检查登录状态失败:', error)
        alert('无法验证登录状态，请重新登录')
        this.$router.push('/login')
        return
      }
      
      this.avatarUploading = true
      
      try {
        const result = await this.authStore.uploadAvatar(this.avatarFile)
        console.log('头像上传结果:', result)
        
        if (result.success) {
          alert('头像上传成功！')
          this.closeAvatarUpload()
        } else {
          alert(result.message || '头像上传失败')
        }
      } catch (error) {
        console.error('头像上传失败:', error)
        alert('头像上传失败: ' + (error.message || '未知错误'))
      } finally {
        this.avatarUploading = false
      }
    },
  },
  watch: {
    'authStore.isLoggedIn'(newVal) {
      if (newVal) {
        this.loadData()
      }
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  width: 100%;
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

.light-mode .nav-link {
  color: #667eea;
}

.light-mode .nav-link:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #5a6fd8;
}

.light-mode .nav-link.router-link-active {
  background: rgba(102, 126, 234, 0.15);
  color: #5a6fd8;
}

.light-mode .username {
  color: #2c3e50 !important;
}

/* 深色模式样式 */
.dark-mode .background-gradient {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.dark-mode .welcome-content,
.dark-mode .feature-card,
.dark-mode .post-card,
.dark-mode .navbar,
.dark-mode .carousel-container {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .welcome-title .title-line,
.dark-mode .nav-brand h2,
.dark-mode .user-info,
.dark-mode .post-title,
.dark-mode .post-content,
.dark-mode .loading,
.dark-mode .no-posts,
.dark-mode .feature-card h4,
.dark-mode .slide-content h3 {
  color: #ecf0f1;
}

.dark-mode .welcome-subtitle,
.dark-mode .feature-card p,
.dark-mode .post-meta,
.dark-mode .stat-label,
.dark-mode .slide-content p {
  color: rgba(236, 240, 241, 0.8);
}

.dark-mode .gradient-text,
.dark-mode .stat-number {
  color: #5dade2;
}

.dark-mode .filter-btn {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(93, 173, 226, 0.3);
  color: #5dade2;
}

.dark-mode .filter-btn:hover, .dark-mode .filter-btn.active {
  background: #5dade2;
  color: #2c3e50;
  border-color: #5dade2;
}

.dark-mode .btn-primary {
  background: #5dade2;
  color: #2c3e50;
}

.dark-mode .btn-primary:hover {
  background: #3498db;
}

.dark-mode .btn-secondary {
  background: transparent;
  color: #5dade2;
  border: 2px solid #5dade2;
}

.dark-mode .btn-secondary:hover {
  background: #5dade2;
  color: #2c3e50;
}

.dark-mode .nav-link {
  color: #5dade2;
}

.dark-mode .nav-link:hover {
  background: rgba(93, 173, 226, 0.1);
  color: #3498db;
}

.dark-mode .nav-link.router-link-active {
  background: rgba(93, 173, 226, 0.15);
  color: #3498db;
}

.dark-mode .read-more-btn {
  color: #5dade2;
}

.dark-mode .read-more-btn:hover {
  color: #3498db;
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

/* 欢迎页面样式 */
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  text-align: center;
  width: 100%;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 轮播图样式 */
.carousel-section {
  width: 100%;
  max-width: 800px;
  margin-bottom: 40px;
}

.carousel-container {
  position: relative;
  height: 180px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.carousel-wrapper {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease-in-out;
}

.carousel-slide {
  min-width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.slide-content {
  text-align: center;
}

.slide-icon {
  font-size: 2.5em;
  margin-bottom: 15px;
}

.slide-content h3 {
  font-size: 1.4em;
  margin-bottom: 10px;
  font-weight: 600;
  transition: color 0.3s ease;
}

.slide-content p {
  font-size: 0.95em;
  line-height: 1.5;
  transition: color 0.3s ease;
}

.carousel-indicators {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: #667eea;
  transform: scale(1.2);
}

.dark-mode .indicator.active {
  background: #5dade2;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #667eea;
  font-size: 20px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.carousel-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-50%) scale(1.05);
}

.dark-mode .carousel-btn {
  background: rgba(0, 0, 0, 0.7);
  color: #5dade2;
  border-color: rgba(255, 255, 255, 0.1);
}

.dark-mode .carousel-btn:hover {
  background: #5dade2;
  color: #2c3e50;
}

.prev-btn {
  left: 15px;
}

.next-btn {
  right: 15px;
}

.welcome-content {
  border-radius: 20px;
  padding: 50px 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  max-width: 1000px;
  width: 100%;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.welcome-header {
  margin-bottom: 40px;
}

.welcome-title {
  margin-bottom: 20px;
  font-weight: bold;
}

.title-line {
  display: block;
  font-size: clamp(2em, 5vw, 3em);
  line-height: 1.2;
  transition: color 0.3s ease;
}

.welcome-subtitle {
  font-size: clamp(1em, 3vw, 1.2em);
  margin-bottom: 30px;
  line-height: 1.6;
  transition: color 0.3s ease;
}

/* 特色功能网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 40px 0;
}

.feature-card {
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 2.2em;
  margin-bottom: 15px;
}

.feature-card h4 {
  font-size: 1.1em;
  margin-bottom: 10px;
  font-weight: 600;
  transition: color 0.3s ease;
}

.feature-card p {
  font-size: 0.9em;
  line-height: 1.5;
  transition: color 0.3s ease;
}

.welcome-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 40px 0;
}

/* 统计数据样式 */
.stats-section {
  display: flex;
  justify-content: space-around;
  margin-top: 40px;
  flex-wrap: wrap;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: clamp(1.8em, 4vw, 2.5em);
  font-weight: 700;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.stat-label {
  font-size: clamp(0.9em, 2vw, 1em);
  transition: color 0.3s ease;
}

/* 主要内容样式 */
.main-content {
  width: 100%;
  min-height: 100vh;
}

.navbar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.nav-container {
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 100%;
}

.nav-brand h2 {
  margin: 0;
  font-size: clamp(1.2em, 3vw, 1.5em);
  transition: color 0.3s ease;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: clamp(0.9em, 2vw, 1em);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar:hover {
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 1.2em;
  color: rgba(255, 255, 255, 0.8);
}

.username {
  transition: color 0.3s ease;
  font-weight: 600;
}

.dark-mode .user-info:hover {
  background: rgba(93, 173, 226, 0.1);
}

.dark-mode .user-avatar {
  border-color: rgba(93, 173, 226, 0.3);
}

.dark-mode .user-avatar:hover {
  border-color: rgba(93, 173, 226, 0.6);
}

.dark-mode .username {
  color: #5dade2;
}

.nav-link {
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: clamp(0.9em, 2vw, 1em);
  white-space: nowrap;
  color: #667eea;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #5a6fd8;
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  background: rgba(102, 126, 234, 0.15);
  color: #5a6fd8;
  font-weight: 600;
}

.logout-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: clamp(0.9em, 2vw, 1em);
  white-space: nowrap;
}

.logout-btn:hover {
  background: #c0392b;
}

/* 容器样式 */
.container {
  margin: 0 auto;
  padding: 40px;
  width: 100%;
  max-width: 100%;
}

/* 搜索框样式 */
.search-section {
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.search-box:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px 15px;
  font-size: 1em;
  color: #2c3e50;
  background: transparent;
  border-radius: 8px;
}

.search-input::placeholder {
  color: #aab8c2;
}

.search-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.95em;
  white-space: nowrap;
}

.search-btn:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.clear-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #c0392b;
  transform: scale(1.05);
}

.search-status {
  margin-top: 15px;
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
}

.search-info {
  color: #667eea;
  font-weight: 600;
  font-size: 0.95em;
}

.search-method-tag {
  display: inline-block;
  background: rgba(255, 193, 7, 0.2);
  color: #f39c12;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
  margin-left: 8px;
  border: 1px solid rgba(243, 156, 18, 0.3);
}

/* 深色模式搜索样式 */
.dark-mode .search-box {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark-mode .search-input {
  color: #ecf0f1;
}

.dark-mode .search-input::placeholder {
  color: rgba(236, 240, 241, 0.6);
}

.dark-mode .search-btn {
  background: #5dade2;
  color: #2c3e50;
}

.dark-mode .search-btn:hover:not(:disabled) {
  background: #3498db;
}

.dark-mode .search-status {
  background: rgba(93, 173, 226, 0.1);
  border-color: rgba(93, 173, 226, 0.2);
}

.dark-mode .search-info {
  color: #5dade2;
}

.dark-mode .search-method-tag {
  background: rgba(243, 156, 18, 0.2);
  color: #f1c40f;
  border-color: rgba(241, 196, 15, 0.3);
}

/* 过滤器样式 */
.filters {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  flex-wrap: wrap;
  width: 100%;
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  gap: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 文章列表样式 */
.posts-list {
  width: 100%;
}

.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
  width: 100%;
}

.post-card {
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  min-height: 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.post-card::before {
  content: "右键查看详情";
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7em;
  opacity: 0;
  transform: translateY(-5px);
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 10;
}

.post-card:hover::before {
  opacity: 1;
  transform: translateY(0);
}

.dark-mode .post-card::before {
  background: rgba(93, 173, 226, 0.9);
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.post-title {
  font-size: clamp(1.1em, 2.5vw, 1.3em);
  margin-bottom: 10px;
  font-weight: 600;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: clamp(0.8em, 2vw, 0.9em);
  transition: color 0.3s ease;
}

.post-content {
  line-height: 1.6;
  margin-bottom: 15px;
  font-size: clamp(0.9em, 2vw, 1em);
  transition: color 0.3s ease;
}

.post-footer {
  display: flex;
  justify-content: flex-end;
}

.read-more-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: color 0.3s ease;
  font-size: clamp(0.9em, 2vw, 1em);
}

/* 加载和空状态样式 */
.loading, .no-posts {
  text-align: center;
  padding: 60px 20px;
  width: 100%;
  transition: color 0.3s ease;
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

.no-posts-icon {
  font-size: clamp(3em, 8vw, 4em);
  margin-bottom: 20px;
}

.no-posts h3 {
  font-size: clamp(1.2em, 4vw, 1.5em);
  margin-bottom: 10px;
}

.no-posts p {
  font-size: clamp(1em, 3vw, 1.1em);
  margin-bottom: 20px;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-size: clamp(0.9em, 2.5vw, 1em);
  white-space: nowrap;
}

.btn-icon {
  font-size: 1.1em;
}

.btn-primary {
  background: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

/* 悬浮预览窗口样式 */
.preview-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  background: var(--bg-primary, rgba(255, 255, 255, 0.98));
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  z-index: 1000;
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  pointer-events: none;
  overflow: hidden;
}

.preview-modal.active {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
  pointer-events: all;
}

.preview-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 80vh;
}

.preview-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  position: relative;
}

.preview-title {
  font-size: 1.4em;
  font-weight: 700;
  color: var(--text-primary, #2c3e50);
  margin-bottom: 12px;
  line-height: 1.3;
  transition: color 0.3s ease;
  padding-right: 40px; /* 为关闭按钮留出空间 */
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary, #7f8c8d);
  cursor: pointer;
  transition: all 0.3s ease;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  transform: scale(1.1);
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 0.9em;
  color: var(--text-secondary, #7f8c8d);
  transition: color 0.3s ease;
}

.preview-author,
.preview-date,
.preview-category {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.preview-excerpt {
  color: var(--text-primary, #2c3e50);
  line-height: 1.7;
  margin-bottom: 24px;
  max-height: 200px;
  overflow-y: auto;
  transition: color 0.3s ease;
}

.preview-excerpt h1,
.preview-excerpt h2,
.preview-excerpt h3 {
  color: var(--text-primary, #2c3e50);
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.preview-excerpt p {
  margin: 12px 0;
}

.preview-excerpt strong {
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
}

.preview-excerpt code {
  background: var(--bg-secondary, rgba(0, 0, 0, 0.05));
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #e74c3c;
}

.preview-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.05));
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9em;
  color: var(--text-secondary, #7f8c8d);
  transition: color 0.3s ease;
}

.stat-icon {
  font-size: 1.1em;
}

.stat-text {
  font-weight: 500;
}

.preview-footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.05));
  display: flex;
  justify-content: flex-end;
}

.preview-read-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95em;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.preview-read-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 深色模式样式 */
.dark-mode .preview-modal {
  background: rgba(44, 62, 80, 0.98);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.dark-mode .preview-title {
  color: #ecf0f1;
}

.dark-mode .close-btn {
  color: rgba(236, 240, 241, 0.7);
}

.dark-mode .close-btn:hover {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.dark-mode .preview-meta {
  color: rgba(236, 240, 241, 0.8);
}

.dark-mode .preview-excerpt {
  color: #ecf0f1;
}

.dark-mode .preview-excerpt h1,
.dark-mode .preview-excerpt h2,
.dark-mode .preview-excerpt h3,
.dark-mode .preview-excerpt strong {
  color: #ecf0f1;
}

.dark-mode .preview-excerpt code {
  background: rgba(255, 255, 255, 0.1);
  color: #f39c12;
}

.dark-mode .stat-item {
  color: rgba(236, 240, 241, 0.7);
}

.dark-mode .preview-read-btn {
  background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
  box-shadow: 0 4px 15px rgba(93, 173, 226, 0.3);
}

.dark-mode .preview-read-btn:hover {
  box-shadow: 0 6px 20px rgba(93, 173, 226, 0.4);
}

/* 头像上传模态框样式 */
.avatar-upload-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.avatar-upload-modal.active {
  opacity: 1;
  visibility: visible;
}

.avatar-upload-content {
  background: var(--bg-primary, rgba(255, 255, 255, 0.98));
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.avatar-upload-modal.active .avatar-upload-content {
  transform: scale(1);
}

.avatar-upload-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.avatar-upload-header h3 {
  margin: 0;
  font-size: 1.3em;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
}

.avatar-upload-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.current-avatar-section {
  margin-bottom: 24px;
  text-align: center;
}

.current-avatar-section h4 {
  margin-bottom: 12px;
  color: var(--text-primary, #2c3e50);
  font-size: 1.1em;
}

.current-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto;
  overflow: hidden;
  border: 3px solid var(--border-color, rgba(0, 0, 0, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, rgba(0, 0, 0, 0.05));
}

.current-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.current-avatar-placeholder {
  font-size: 2em;
  color: var(--text-secondary, #7f8c8d);
}

.file-select-section h4 {
  margin-bottom: 12px;
  color: var(--text-primary, #2c3e50);
  font-size: 1.1em;
}

.file-drop-zone {
  border: 2px dashed var(--border-color, rgba(102, 126, 234, 0.3));
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-secondary, rgba(102, 126, 234, 0.05));
  position: relative;
}

.file-drop-zone:hover {
  border-color: var(--primary-color, #667eea);
  background: var(--bg-secondary, rgba(102, 126, 234, 0.1));
}

.drop-zone-content {
  pointer-events: none;
}

.drop-zone-icon {
  font-size: 3em;
  margin-bottom: 16px;
}

.drop-zone-content p {
  margin: 8px 0;
  color: var(--text-primary, #2c3e50);
  font-weight: 500;
}

.file-hint {
  font-size: 0.9em;
  color: var(--text-secondary, #7f8c8d) !important;
  font-weight: 400 !important;
}

.preview-container {
  position: relative;
  display: inline-block;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--primary-color, #667eea);
}

.clear-preview-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-preview-btn:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.avatar-upload-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 深色模式样式 */
.dark-mode .preview-modal {
  background: rgba(44, 62, 80, 0.98);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.dark-mode .preview-title {
  color: #ecf0f1;
}

.dark-mode .close-btn {
  color: rgba(236, 240, 241, 0.7);
}

.dark-mode .close-btn:hover {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.dark-mode .preview-meta {
  color: rgba(236, 240, 241, 0.8);
}

.dark-mode .preview-excerpt {
  color: #ecf0f1;
}

.dark-mode .preview-excerpt h1,
.dark-mode .preview-excerpt h2,
.dark-mode .preview-excerpt h3,
.dark-mode .preview-excerpt strong {
  color: #ecf0f1;
}

.dark-mode .preview-excerpt code {
  background: rgba(255, 255, 255, 0.1);
  color: #f39c12;
}

.dark-mode .stat-item {
  color: rgba(236, 240, 241, 0.7);
}

.dark-mode .preview-read-btn {
  background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
  box-shadow: 0 4px 15px rgba(93, 173, 226, 0.3);
}

.dark-mode .preview-read-btn:hover {
  box-shadow: 0 6px 20px rgba(93, 173, 226, 0.4);
}

/* 头像上传模态框样式 */
.dark-mode .avatar-upload-content {
  background: rgba(44, 62, 80, 0.98);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark-mode .avatar-upload-header h3,
.dark-mode .current-avatar-section h4,
.dark-mode .file-select-section h4 {
  color: #ecf0f1;
}

.dark-mode .current-avatar {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.dark-mode .current-avatar-placeholder {
  color: rgba(236, 240, 241, 0.7);
}

.dark-mode .file-drop-zone {
  border-color: rgba(93, 173, 226, 0.3);
  background: rgba(93, 173, 226, 0.05);
}

.dark-mode .file-drop-zone:hover {
  border-color: #5dade2;
  background: rgba(93, 173, 226, 0.1);
}

.dark-mode .drop-zone-content p {
  color: #ecf0f1;
}

.dark-mode .file-hint {
  color: rgba(236, 240, 241, 0.7) !important;
}

.dark-mode .avatar-preview {
  border-color: #5dade2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-modal {
    width: 95%;
    max-height: 85vh;
    margin: 20px;
  }
  
  .preview-header,
  .preview-body,
  .preview-footer {
    padding: 16px;
  }
  
  .preview-title {
    font-size: 1.2em;
  }
  
  .preview-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .preview-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .avatar-upload-modal {
    width: 95%;
    max-width: 500px;
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .search-section {
    margin-bottom: 20px;
  }
  
  .search-box {
    padding: 10px;
  }
  
  .search-input {
    padding: 8px 12px;
    font-size: 0.95em;
  }
  
  .search-btn,
  .clear-btn {
    padding: 8px 16px;
    font-size: 0.9em;
  }
  
  .preview-modal {
    width: 100%;
    height: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .preview-excerpt {
    max-height: 150px;
  }
  
  .avatar-upload-modal {
    width: 95%;
    max-width: 500px;
    padding: 20px;
  }
}
</style>