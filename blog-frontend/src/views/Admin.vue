<template>
  <div class="admin" :class="themeStore.themeClass">
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
          <router-link to="/" class="brand-link">博客系统CI测试</router-link>
        </div>
        <div class="nav-menu">
          <span class="user-info">👤 {{ authStore.username }} (管理员)</span>
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/my-posts" class="nav-link">我的文章</router-link>
          <router-link to="/write" class="nav-link">写文章</router-link>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="container">
      <!-- 管理面板标题 -->
      <div class="admin-header">
        <h1>🛠️ 管理员面板</h1>
        <p class="admin-subtitle">用户管理、文章管理、评论管理</p>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-number">{{ users.length }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-number">{{ posts.length }}</div>
            <div class="stat-label">总文章数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">😎</div>
          <div class="stat-content">
            <div class="stat-number">{{ comments.length }}</div>
            <div class="stat-label">总评论数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <div class="stat-number">{{ formatDate(new Date()) }}</div>
            <div class="stat-label">今日日期</div>
          </div>
        </div>
      </div>

      <!-- 功能选项卡 -->
      <div class="tabs">
        <button 
          @click="activeTab = 'users'"
          :class="{ active: activeTab === 'users' }"
          class="tab-btn"
        >
          👥 用户管理
        </button>
        <button 
          @click="activeTab = 'posts'"
          :class="{ active: activeTab === 'posts' }"
          class="tab-btn"
        >
          📝 文章管理
        </button>
        <button 
          @click="activeTab = 'comments'"
          :class="{ active: activeTab === 'comments' }"
          class="tab-btn"
        >
          💬 评论管理
        </button>
      </div>

      <!-- 用户管理标签页 -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="section-header">
          <h2>👥 用户管理</h2>
          <div class="section-actions">
            <button @click="loadUsers" class="btn btn-secondary" :disabled="loading">
              {{ loading ? '刷新中...' : '🔄 刷新数据' }}
            </button>
          </div>
        </div>

        <!-- 用户列表 -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载用户数据中...</p>
        </div>

        <div v-else-if="users.length === 0" class="no-data">
          <div class="no-data-icon">👥</div>
          <h3>暂无用户数据</h3>
          <p>系统中还没有注册用户</p>
        </div>

        <div v-else class="users-table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>密码</th>
                <th>用户类型</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="user-row">
                <td>{{ user.id }}</td>
                <td>
                  <div class="user-info">
                    <span class="user-avatar">👤</span>
                    <span class="username">{{ user.username }}</span>
                  </div>
                </td>
                <td>
                  <div class="password-cell">
                    <span v-if="!showPasswords[user.id]" class="password-hidden">••••••••</span>
                    <span v-else class="password-visible">{{ user.password || '未获取' }}</span>
                    <button 
                      @click="togglePassword(user.id)" 
                      class="toggle-password-btn"
                      :title="showPasswords[user.id] ? '隐藏密码' : '显示密码'"
                    >
                      {{ showPasswords[user.id] ? '👁️' : '👁️‍🗨️' }}
                    </button>
                  </div>
                </td>
                <td>
                  <span :class="['user-type', { admin: user.is_admin }]">
                    {{ user.is_admin ? '👑 管理员' : '👤 普通用户' }}
                  </span>
                </td>
                <td>
                  <div class="user-actions">
                    <button 
                      v-if="!user.is_admin || user.id !== authStore.user?.id"
                      @click="confirmDeleteUser(user)"
                      class="action-btn delete-btn"
                      title="删除用户"
                    >
                      🗑️ 删除
                    </button>
                    <span v-else class="protected-user" title="不能删除自己">
                      🔒 受保护
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 文章管理标签页 -->
      <div v-if="activeTab === 'posts'" class="tab-content">
        <div class="section-header">
          <h2>📝 文章管理</h2>
          <div class="section-actions">
            <button @click="loadPosts" class="btn btn-secondary" :disabled="loading">
              {{ loading ? '刷新中...' : '🔄 刷新数据' }}
            </button>
          </div>
        </div>

        <!-- 文章列表 -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载文章数据中...</p>
        </div>

        <div v-else-if="posts.length === 0" class="no-data">
          <div class="no-data-icon">📝</div>
          <h3>暂无文章数据</h3>
          <p>系统中还没有发布的文章</p>
        </div>

        <div v-else class="posts-grid">
          <div v-for="post in posts" :key="post.id" class="post-card">
            <div class="post-header">
              <h3 class="post-title">{{ post.title }}</h3>
              <div class="post-meta">
                <span class="post-author">
                  <UserAvatar 
                    :username="post.author || post.username" 
                    :avatar="post.author_avatar" 
                    size="small" 
                  />
                  {{ post.author || post.username }}
                </span>
                <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
              </div>
            </div>
            <div class="post-content">
              {{ getPostPreview(post.content) }}
            </div>
            <div class="post-actions">
              <router-link :to="`/post/${post.id}`" class="btn btn-sm btn-secondary">
                👁️ 查看
              </router-link>
              <router-link :to="`/edit/${post.id}`" class="btn btn-sm btn-primary">
                ✏️ 编辑
              </router-link>
              <button @click="confirmDeletePost(post)" class="btn btn-sm btn-danger">
                🗑️ 删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 评论管理标签页 -->
      <div v-if="activeTab === 'comments'" class="tab-content">
        <div class="section-header">
          <h2>💬 评论管理</h2>
          <div class="section-actions">
            <button @click="loadComments" class="btn btn-secondary" :disabled="loading">
              {{ loading ? '刷新中...' : '🔄 刷新数据' }}
            </button>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载评论数据中...</p>
        </div>

        <div v-else-if="comments.length === 0" class="no-data">
          <div class="no-data-icon">💬</div>
          <h3>暂无评论数据</h3>
          <p>系统中还没有用户评论，或者后端API不支持评论管理功能</p>
          <div class="api-notice">
            <p><strong>注意：</strong>如果后端没有 <code>/admin/comments</code> API，评论数据将通过文章评论接口获取</p>
          </div>
        </div>

        <div v-else class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-card">
            <div class="comment-header">
              <div class="comment-info">
                <span class="comment-author">
                  <UserAvatar 
                    :username="comment.username" 
                    :avatar="comment.author_avatar" 
                    size="small" 
                  />
                  {{ comment.username }}
                </span>
                <span class="comment-post">📝 文章: {{ comment.post_title }}</span>
              </div>
              <div class="comment-date">{{ formatDateTime(comment.created_at) }}</div>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
            <div class="comment-actions">
              <router-link :to="`/post/${comment.post_id}`" class="btn btn-sm btn-secondary">
                👁️ 查看文章
              </router-link>
              <button @click="confirmDeleteComment(comment)" class="btn btn-sm btn-danger">
                🗑️ 删除评论
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除用户确认弹窗 -->
    <div v-if="showDeleteUserModal" class="modal-overlay" @click="cancelDeleteUser">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除用户</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除用户 <strong>{{ userToDelete?.username }}</strong> 吗？</p>
          <p class="warning-text">此操作将会：</p>
          <ul class="warning-list">
            <li>永久删除该用户账户</li>
            <li>删除该用户的所有文章</li>
            <li>删除该用户的所有评论</li>
            <li>此操作不可恢复！</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button @click="cancelDeleteUser" class="btn btn-secondary">取消</button>
          <button @click="deleteUser" class="btn btn-danger" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除文章确认弹窗 -->
    <div v-if="showDeletePostModal" class="modal-overlay" @click="cancelDeletePost">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除文章</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除文章 <strong>《{{ postToDelete?.title }}》</strong> 吗？</p>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button @click="cancelDeletePost" class="btn btn-secondary">取消</button>
          <button @click="deletePost" class="btn btn-danger" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除评论确认弹窗 -->
    <div v-if="showDeleteCommentModal" class="modal-overlay" @click="cancelDeleteComment">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 确认删除评论</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除这条评论吗？</p>
          <div class="comment-preview">
            <strong>评论内容：</strong>
            <p>{{ commentToDelete?.content?.substring(0, 100) }}{{ commentToDelete?.content?.length > 100 ? '...' : '' }}</p>
          </div>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button @click="cancelDeleteComment" class="btn btn-secondary">取消</button>
          <button @click="deleteComment" class="btn btn-danger" :disabled="deleting">
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
import UserAvatar from '../components/UserAvatar.vue'

export default {
  name: 'Admin',
  components: {
    UserAvatar
  },
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    
    return { authStore, themeStore, router }
  },
  data() {
    return {
      activeTab: 'users',
      users: [],
      posts: [],
      comments: [],
      loading: false,
      deleting: false,
      showPasswords: {}, // 控制密码显示状态
      userToDelete: null,
      postToDelete: null,
      commentToDelete: null,
      showDeleteUserModal: false,
      showDeletePostModal: false,
      showDeleteCommentModal: false,
      message: {
        show: false,
        text: '',
        type: 'success'
      }
    }
  },
  async created() {
    // 检查管理员权限
    if (!this.authStore.isAdmin) {
      this.showMessage('无权限访问管理面板', 'error')
      this.router.push('/')
      return
    }
    
    await this.loadData()
  },
  methods: {
    async loadData() {
      // 先加载用户和文章数据
      await Promise.all([
        this.loadUsers(),
        this.loadPosts()
      ])
      
      // 然后加载评论数据（需要依赖文章数据）
      await this.loadComments()
    },

    async loadUsers() {
      this.loading = true
      try {
        this.users = await ApiService.getAdminUsers()
        // 初始化密码显示状态
        this.showPasswords = {}
        this.users.forEach(user => {
          this.showPasswords[user.id] = false
        })
      } catch (error) {
        this.showMessage('加载用户数据失败：' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },

    async loadPosts() {
      this.loading = true
      try {
        this.posts = await ApiService.getAdminPosts()
      } catch (error) {
        this.showMessage('加载文章数据失败：' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },

    async loadComments() {
      this.loading = true
      try {
        // 尝试获取所有评论
        try {
          this.comments = await ApiService.getAdminComments()
          console.log('成功从管理员API获取评论:', this.comments.length, '条')
        } catch (apiError) {
          if (apiError.message === 'ADMIN_COMMENTS_API_NOT_FOUND') {
            console.warn('后端没有 /admin/comments API，使用替代方案')
            this.showMessage('后端暂不支持评论管理API，使用替代方案获取评论', 'warning')
          } else {
            console.warn('getAdminComments API调用失败:', apiError.message)
          }
          
          // 使用替代方案：通过文章获取评论
          this.comments = await this.getAllCommentsFromPosts()
          if (this.comments.length > 0) {
            console.log('通过文章API获取到评论:', this.comments.length, '条')
          }
        }
      } catch (error) {
        this.showMessage('加载评论数据失败：' + error.message, 'error')
        console.error('评论加载错误:', error)
        this.comments = []
      } finally {
        this.loading = false
      }
    },

    // 通过获取所有文章的评论来获取所有评论
    async getAllCommentsFromPosts() {
      try {
        const allComments = []
        
        // 遍历所有文章，获取每篇文章的评论
        for (const post of this.posts) {
          try {
            const postComments = await ApiService.getComments(post.id)
            // 为每个评论添加文章信息
            const commentsWithPostInfo = postComments.map(comment => ({
              ...comment,
              post_id: post.id,
              post_title: post.title,
              post_author: post.author || post.username
            }))
            allComments.push(...commentsWithPostInfo)
          } catch (commentError) {
            console.warn(`获取文章 ${post.id} 的评论失败:`, commentError)
            // 继续处理其他文章的评论
          }
        }
        
        // 按时间倒序排列
        allComments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        
        return allComments
      } catch (error) {
        console.error('通过文章获取评论失败:', error)
        return []
      }
    },

    togglePassword(userId) {
      this.showPasswords[userId] = !this.showPasswords[userId]
    },

    confirmDeleteUser(user) {
      this.userToDelete = user
      this.showDeleteUserModal = true
    },

    cancelDeleteUser() {
      this.showDeleteUserModal = false
      this.userToDelete = null
    },

    async deleteUser() {
      if (!this.userToDelete) return

      this.deleting = true
      try {
        const result = await ApiService.deleteUser(this.userToDelete.id)
        if (result.success) {
          this.showMessage(`用户 ${this.userToDelete.username} 删除成功`, 'success')
          await this.loadUsers()
        }
      } catch (error) {
        this.showMessage('删除用户失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeleteUserModal = false
        this.userToDelete = null
      }
    },

    confirmDeletePost(post) {
      this.postToDelete = post
      this.showDeletePostModal = true
    },

    cancelDeletePost() {
      this.showDeletePostModal = false
      this.postToDelete = null
    },

    async deletePost() {
      if (!this.postToDelete) return

      this.deleting = true
      try {
        const result = await ApiService.deletePost(this.postToDelete.id)
        if (result.success) {
          this.showMessage(`文章《${this.postToDelete.title}》删除成功`, 'success')
          await this.loadPosts()
        }
      } catch (error) {
        this.showMessage('删除文章失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeletePostModal = false
        this.postToDelete = null
      }
    },

    confirmDeleteComment(comment) {
      this.commentToDelete = comment
      this.showDeleteCommentModal = true
    },

    cancelDeleteComment() {
      this.showDeleteCommentModal = false
      this.commentToDelete = null
    },

    async deleteComment() {
      if (!this.commentToDelete) return

      this.deleting = true
      try {
        const result = await ApiService.deleteComment(this.commentToDelete.id)
        if (result.success) {
          this.showMessage('评论删除成功', 'success')
          await this.loadComments()
        }
      } catch (error) {
        this.showMessage('删除评论失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeleteCommentModal = false
        this.commentToDelete = null
      }
    },

    async handleLogout() {
      const result = await this.authStore.logout()
      if (result.success) {
        this.router.push('/')
      }
    },

    getPostPreview(content) {
      if (!content) return ''
      return content.length > 100 ? content.substring(0, 100) + '...' : content
    },

    formatDate(dateString) {
      try {
        // 如果传入的是Date对象（如new Date()），直接使用
        if (dateString instanceof Date) {
          return dateString.toLocaleDateString('zh-CN')
        }
        // 如果是字符串日期，修复8小时时区问题
        const date = new Date(new Date(dateString).getTime() + 8 * 60 * 60 * 1000)
        return date.toLocaleDateString('zh-CN')
      } catch {
        return '未知日期'
      }
    },

    formatDateTime(dateString) {
      try {
        // 修复8小时时区问题
        const date = new Date(new Date(dateString).getTime() + 8 * 60 * 60 * 1000)
        return date.toLocaleString('zh-CN')
      } catch {
        return '未知时间'
      }
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
.admin {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: -1;
  transition: all 0.3s ease;
}

/* 明暗主题适配 */
.admin.light-mode .background-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.admin.dark-mode .background-gradient {
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
  color: white;
  font-size: 1.5em;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.theme-btn:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.theme-btn:active {
  transform: scale(0.95);
}

/* 浅色模式下的主题按钮 */
.admin.light-mode .theme-btn {
  border-color: rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.8);
  color: #2d3436;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.admin.light-mode .theme-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 0, 0, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 导航栏样式 */
.navbar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  width: 100%;
  transition: all 0.3s ease;
}

.admin.light-mode .navbar {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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

.nav-brand .brand-link {
  color: white;
  text-decoration: none;
  font-size: 1.5em;
  font-weight: bold;
  transition: color 0.3s ease;
}

.admin.light-mode .nav-brand .brand-link {
  color: #2c3e50;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.user-info {
  color: white;
  font-weight: bold;
  font-size: 1em;
  transition: color 0.3s ease;
}

.admin.light-mode .user-info {
  color: #2c3e50;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 1em;
  white-space: nowrap;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.admin.light-mode .nav-link {
  color: #2c3e50;
}

.admin.light-mode .nav-link:hover {
  background: rgba(0, 0, 0, 0.1);
}

.logout-btn {
  background: rgba(255, 99, 99, 0.3);
  color: white;
  border: 1px solid rgba(255, 99, 99, 0.5);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1em;
  white-space: nowrap;
}

.logout-btn:hover {
  background: rgba(255, 99, 99, 0.4);
}

.admin.light-mode .logout-btn {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
}

.admin.light-mode .logout-btn:hover {
  background: rgba(231, 76, 60, 0.2);
}

/* 主要内容样式 */
.container {
  margin: 0 auto;
  padding: 40px;
  width: 100%;
  max-width: 100%;
}

.admin-header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
  transition: color 0.3s ease;
}

.admin.light-mode .admin-header {
  color: #2c3e50;
}

.admin-header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.admin-subtitle {
  font-size: 1.2em;
  opacity: 0.8;
}

/* 统计卡片样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

.admin.light-mode .stat-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.admin.light-mode .stat-card:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5em;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: white;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.admin.light-mode .stat-number {
  color: #667eea;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1em;
  transition: color 0.3s ease;
}

.admin.light-mode .stat-label {
  color: #5a6c7d;
}

/* 选项卡样式 */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  transition: border-color 0.3s ease;
}

.admin.light-mode .tabs {
  border-bottom-color: rgba(0, 0, 0, 0.1);
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-btn.active {
  color: white;
  border-bottom-color: rgba(102, 126, 234, 0.8);
  background: rgba(255, 255, 255, 0.1);
}

.admin.light-mode .tab-btn {
  color: rgba(45, 52, 54, 0.7);
}

.admin.light-mode .tab-btn:hover {
  color: #2d3436;
  background: rgba(0, 0, 0, 0.05);
}

.admin.light-mode .tab-btn.active {
  color: #2d3436;
  background: rgba(0, 0, 0, 0.05);
  border-bottom-color: #74b9ff;
}

/* 标签页内容样式 */
.tab-content {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.section-header h2 {
  color: white;
  font-size: 1.8em;
  margin: 0;
  transition: color 0.3s ease;
}

.admin.light-mode .section-header h2 {
  color: #2c3e50;
}

.section-actions {
  display: flex;
  gap: 10px;
}

/* 加载和空状态样式 */
.loading, .no-data {
  text-align: center;
  padding: 60px 20px;
  color: white;
  transition: color 0.3s ease;
}

.admin.light-mode .loading,
.admin.light-mode .no-data {
  color: #2c3e50;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
  transition: border-color 0.3s ease;
}

.admin.light-mode .spinner {
  border-color: rgba(44, 62, 80, 0.3);
  border-top-color: #2c3e50;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data-icon {
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.6;
}

.no-data h3 {
  font-size: 1.5em;
  margin-bottom: 10px;
}

.api-notice {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  transition: all 0.3s ease;
}

.admin.light-mode .api-notice {
  background: rgba(241, 196, 15, 0.1);
  border-color: rgba(241, 196, 15, 0.3);
}

.api-notice p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9em;
  line-height: 1.5;
  transition: color 0.3s ease;
}

.admin.light-mode .api-notice p {
  color: rgba(45, 52, 54, 0.8);
}

.api-notice code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #ffd700;
  transition: all 0.3s ease;
}

.admin.light-mode .api-notice code {
  background: rgba(0, 0, 0, 0.1);
  color: #f39c12;
}

/* 密码显示样式 */
.password-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.password-hidden {
  font-family: monospace;
  letter-spacing: 2px;
}

.password-visible {
  font-family: monospace;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.admin.light-mode .password-visible {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

.toggle-password-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.toggle-password-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.admin.light-mode .toggle-password-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

.admin.light-mode .toggle-password-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

/* 评论列表样式 */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

.admin.light-mode .comment-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.admin.light-mode .comment-card:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.comment-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.comment-author {
  color: white;
  font-weight: bold;
  font-size: 1em;
  transition: color 0.3s ease;
}

.admin.light-mode .comment-author {
  color: #2d3436;
}

.comment-post {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9em;
  transition: color 0.3s ease;
}

.admin.light-mode .comment-post {
  color: rgba(45, 52, 54, 0.6);
}

.comment-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85em;
  white-space: nowrap;
  transition: color 0.3s ease;
}

.admin.light-mode .comment-date {
  color: rgba(45, 52, 54, 0.5);
}

.comment-content {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 15px;
  word-break: break-word;
  background: rgba(0, 0, 0, 0.1);
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid rgba(102, 126, 234, 0.5);
  transition: all 0.3s ease;
}

.admin.light-mode .comment-content {
  color: rgba(45, 52, 54, 0.8);
  background: rgba(0, 0, 0, 0.05);
  border-left-color: #74b9ff;
}

.comment-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.comment-preview {
  background: rgba(0, 0, 0, 0.2);
  padding: 10px;
  border-radius: 6px;
  margin: 10px 0;
  border-left: 3px solid rgba(255, 255, 255, 0.3);
}

.comment-preview p {
  margin: 5px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}
.users-table-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow-x: auto;
  transition: all 0.3s ease;
}

.admin.light-mode .users-table-container {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  color: white;
  transition: color 0.3s ease;
}

.admin.light-mode .users-table {
  color: #2c3e50;
}

.users-table th {
  padding: 15px 10px;
  text-align: left;
  font-weight: bold;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.admin.light-mode .users-table th {
  border-bottom-color: rgba(0, 0, 0, 0.1);
  color: #2c3e50;
}

.users-table td {
  padding: 15px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: border-color 0.3s ease;
}

.admin.light-mode .users-table td {
  border-bottom-color: rgba(0, 0, 0, 0.05);
}

.user-row:hover {
  background: rgba(255, 255, 255, 0.05);
  transition: background 0.3s ease;
}

.admin.light-mode .user-row:hover {
  background: rgba(0, 0, 0, 0.03);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  font-size: 1.2em;
}

.username {
  font-weight: bold;
}

.user-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  background: rgba(255, 255, 255, 0.1);
}

.user-type.admin {
  background: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.user-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.view-btn:hover {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
}

.delete-btn:hover {
  background: rgba(255, 99, 99, 0.3);
  border-color: rgba(255, 99, 99, 0.5);
}

.protected-user {
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2em;
}

/* 文章网格样式 */
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.post-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

.admin.light-mode .post-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.admin.light-mode .post-card:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.post-header {
  margin-bottom: 15px;
}

.post-title {
  color: white;
  font-size: 1.3em;
  margin-bottom: 8px;
  font-weight: bold;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.admin.light-mode .post-title {
  color: #2c3e50;
}

.post-meta {
  display: flex;
  gap: 15px;
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.7);
  flex-wrap: wrap;
  transition: color 0.3s ease;
}

.admin.light-mode .post-meta {
  color: #5a6c7d;
}

.post-content {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 15px;
  transition: color 0.3s ease;
}

.admin.light-mode .post-content {
  color: #2c3e50;
}

.post-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-size: 0.9em;
  white-space: nowrap;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85em;
}

.btn-primary {
  background: rgba(102, 126, 234, 0.3);
  color: white;
  border: 1px solid rgba(102, 126, 234, 0.5);
}

.btn-primary:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

.admin.light-mode .btn-primary {
  background: rgba(116, 185, 255, 0.2);
  color: #0984e3;
  border-color: rgba(116, 185, 255, 0.4);
}

.admin.light-mode .btn-primary:hover:not(:disabled) {
  background: rgba(116, 185, 255, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.admin.light-mode .btn-secondary {
  background: rgba(99, 110, 114, 0.1);
  color: #636e72;
  border-color: rgba(99, 110, 114, 0.3);
}

.admin.light-mode .btn-secondary:hover:not(:disabled) {
  background: rgba(99, 110, 114, 0.2);
}

.btn-danger {
  background: rgba(255, 99, 99, 0.3);
  color: white;
  border: 1px solid rgba(255, 99, 99, 0.5);
}

.btn-danger:hover:not(:disabled) {
  background: rgba(255, 99, 99, 0.4);
}

.admin.light-mode .btn-danger {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
}

.admin.light-mode .btn-danger:hover:not(:disabled) {
  background: rgba(231, 76, 60, 0.2);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
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
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.admin.light-mode .modal {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.user-modal {
  max-width: 600px;
}

.modal-header {
  padding: 20px 20px 0;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: color 0.3s ease;
}

.admin.light-mode .modal-header {
  color: #2d3436;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 2em;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.admin.light-mode .close-btn {
  color: #2d3436;
}

.admin.light-mode .close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 20px;
  color: white;
  transition: color 0.3s ease;
}

.admin.light-mode .modal-body {
  color: #2d3436;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-label {
  font-weight: bold;
  color: rgba(255, 255, 255, 0.8);
}

.detail-value {
  color: white;
}

.status-active {
  color: #4caf50;
}

.warning-text {
  color: rgba(255, 99, 99, 0.8);
  font-size: 0.95em;
  margin-top: 10px;
}

.warning-list {
  color: rgba(255, 99, 99, 0.7);
  margin: 10px 0;
  padding-left: 20px;
}

.warning-list li {
  margin: 5px 0;
}

.modal-footer {
  padding: 0 20px 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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
  max-width: 400px;
}

.message.success {
  background: rgba(76, 175, 80, 0.9);
  border: 1px solid rgba(76, 175, 80, 0.5);
}

.message.error {
  background: rgba(244, 67, 54, 0.9);
  border: 1px solid rgba(244, 67, 54, 0.5);
}

.message.warning {
  background: rgba(255, 193, 7, 0.9);
  border: 1px solid rgba(255, 193, 7, 0.5);
  color: #000;
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
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .posts-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .container {
    padding: 20px;
  }
  
  .admin-header h1 {
    font-size: 2em;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .tabs {
    flex-wrap: wrap;
  }
  
  .users-table-container {
    padding: 10px;
  }
  
  .users-table th,
  .users-table td {
    padding: 10px 5px;
    font-size: 0.9em;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
  
  .modal {
    width: 95%;
    margin: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 1.5em;
  }
  
  .user-actions {
    flex-direction: column;
    gap: 5px;
  }
  
  .post-actions {
    flex-direction: column;
  }
}

/* Admin页面的用户名和头像样式 */
.post-author, .comment-author {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>