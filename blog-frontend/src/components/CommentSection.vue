<template>
  <div class="comment-section" :class="{ 'light-mode': !themeStore.isDarkMode }">
    <div class="comment-header">
      <h3>💬 评论 ({{ comments.length }})</h3>
      <p class="comment-subtitle">分享你的想法和观点</p>
    </div>

    <!-- 写评论区域 -->
    <div v-if="authStore.isLoggedIn" class="comment-form-container">
      <form @submit.prevent="submitComment" class="comment-form">
        <div class="form-group">
          <label for="comment-content">写下你的评论</label>
          <textarea
            id="comment-content"
            v-model="newComment.content"
            placeholder="分享你的想法、观点或问题..."
            required
            :disabled="submitting"
            @input="autoResize"
            ref="commentTextarea"
          ></textarea>
          <div class="comment-hint">
            {{ getWordCount(newComment.content) }} 字 | 支持简单的 Markdown 语法
          </div>
        </div>
        
        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="submitting || !newComment.content.trim()"
          >
            {{ submitting ? '发布中...' : '💬 发布评论' }}
          </button>
          <button
            type="button"
            @click="clearComment"
            class="btn btn-secondary"
            :disabled="submitting"
          >
            清空
          </button>
        </div>
      </form>
    </div>

    <!-- 未登录提示 -->
    <div v-else class="login-prompt">
      <div class="prompt-content">
        <span class="prompt-icon">🔒</span>
        <span class="prompt-text">请登录后参与评论讨论</span>
        <router-link to="/login" class="btn btn-primary">立即登录</router-link>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载评论中...</p>
      </div>

      <div v-else-if="comments.length === 0" class="no-comments">
        <div class="no-comments-icon">💭</div>
        <h4>暂无评论</h4>
        <p>成为第一个评论的人吧！</p>
      </div>

      <div v-else class="comments-container">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="comment-item"
        >
          <div class="comment-main">
            <div class="comment-avatar">
              <UserAvatar 
                :username="comment.username" 
                :avatar="comment.author_avatar" 
                size="medium" 
              />
            </div>
            
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-author">{{ comment.username }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                <div v-if="canEditComment(comment)" class="comment-actions">
                  <button @click="editComment(comment)" class="action-btn edit-btn">
                    ✏️
                  </button>
                  <button @click="confirmDelete(comment)" class="action-btn delete-btn">
                    🗑️
                  </button>
                </div>
              </div>
              
              <div class="comment-body">
                <div v-if="editingComment && editingComment.id === comment.id" class="edit-form">
                  <textarea
                    v-model="editForm.content"
                    class="edit-textarea"
                    required
                    @input="autoResizeEdit"
                    ref="editTextarea"
                  ></textarea>
                  <div class="edit-actions">
                    <button @click="saveEdit" class="btn btn-sm btn-primary" :disabled="editSubmitting">
                      {{ editSubmitting ? '保存中...' : '保存' }}
                    </button>
                    <button @click="cancelEdit" class="btn btn-sm btn-secondary">
                      取消
                    </button>
                  </div>
                </div>
                <div v-else class="comment-text" v-html="renderCommentContent(comment.content)"></div>
              </div>
              
              <!-- 回复按钮 -->
              <div class="comment-footer">
                <button
                  v-if="authStore.isLoggedIn"
                  @click="toggleReply(comment)"
                  class="reply-btn"
                  :class="{ active: replyingTo && replyingTo.id === comment.id }"
                >
                  💬 回复
                </button>
              </div>
            </div>
          </div>

          <!-- 回复表单 -->
          <div v-if="replyingTo && replyingTo.id === comment.id" class="reply-form">
            <form @submit.prevent="submitReply" class="comment-form">
              <div class="form-group">
                <textarea
                  v-model="replyForm.content"
                  placeholder="回复 @{{ comment.username }}..."
                  required
                  :disabled="replySubmitting"
                  @input="autoResizeReply"
                  ref="replyTextarea"
                ></textarea>
              </div>
              <div class="form-actions">
                <button
                  type="submit"
                  class="btn btn-sm btn-primary"
                  :disabled="replySubmitting || !replyForm.content.trim()"
                >
                  {{ replySubmitting ? '回复中...' : '发布回复' }}
                </button>
                <button
                  type="button"
                  @click="cancelReply"
                  class="btn btn-sm btn-secondary"
                  :disabled="replySubmitting"
                >
                  取消
                </button>
              </div>
            </form>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
            <div
              v-for="reply in comment.replies"
              :key="reply.id"
              class="reply-item"
            >
              <div class="comment-avatar">
                <UserAvatar 
                  :username="reply.username" 
                  :avatar="reply.author_avatar" 
                  size="small" 
                />
              </div>
              
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-author">{{ reply.username }}</span>
                  <span class="reply-indicator">回复 @{{ comment.username }}</span>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                  <div v-if="canEditComment(reply)" class="comment-actions">
                    <button @click="editComment(reply)" class="action-btn edit-btn">
                      ✏️
                    </button>
                    <button @click="confirmDelete(reply)" class="action-btn delete-btn">
                      🗑️
                    </button>
                  </div>
                </div>
                
                <div class="comment-body">
                  <div v-if="editingComment && editingComment.id === reply.id" class="edit-form">
                    <textarea
                      v-model="editForm.content"
                      class="edit-textarea"
                      required
                      @input="autoResizeEdit"
                    ></textarea>
                    <div class="edit-actions">
                      <button @click="saveEdit" class="btn btn-sm btn-primary" :disabled="editSubmitting">
                        {{ editSubmitting ? '保存中...' : '保存' }}
                      </button>
                      <button @click="cancelEdit" class="btn btn-sm btn-secondary">
                        取消
                      </button>
                    </div>
                  </div>
                  <div v-else class="comment-text" v-html="renderCommentContent(reply.content)"></div>
                </div>
              </div>
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
          <p>确定要删除这条评论吗？</p>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button @click="cancelDelete" class="btn btn-secondary">取消</button>
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
import ApiService from '../services/api'
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'CommentSection',
  components: {
    UserAvatar
  },
  props: {
    postId: {
      type: Number,
      required: true
    }
  },
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    return { authStore, themeStore }
  },
  data() {
    return {
      comments: [],
      loading: false,
      submitting: false,
      replySubmitting: false,
      editSubmitting: false,
      deleting: false,
      newComment: {
        content: ''
      },
      replyForm: {
        content: ''
      },
      editForm: {
        content: ''
      },
      replyingTo: null,
      editingComment: null,
      deleteTarget: null,
      showDeleteModal: false,
      message: {
        show: false,
        text: '',
        type: 'success'
      }
    }
  },
  async created() {
    await this.loadComments()
  },
  methods: {
    async loadComments() {
      this.loading = true
      try {
        this.comments = await ApiService.getComments(this.postId)
        
        // 修复可能缺失的字段
        this.comments.forEach((comment, index) => {
          
          // 设置用户名字段
          if (!comment.username) {
            comment.username = comment.author_name || comment.author || comment.user || comment.user_name || comment.created_by || '匿名用户'
          }
          
          // 设置头像字段
          if (!comment.author_avatar && comment.avatar) {
            comment.author_avatar = comment.avatar
          } else if (!comment.author_avatar && comment.avatar_url) {
            comment.author_avatar = comment.avatar_url
          }
          
          // 临时解决方案：如果评论作者是当前登录用户，使用当前用户的头像
          if (!comment.author_avatar && comment.username === this.authStore.username && this.authStore.avatar) {
            comment.author_avatar = this.authStore.avatar
          }
          
          // 尝试多种可能的头像字段
          if (!comment.author_avatar) {
            if (comment.avatar) {
              comment.author_avatar = comment.avatar
            } else if (comment.user_avatar) {
              comment.author_avatar = comment.user_avatar
            } else if (comment.avatar_url) {
              comment.author_avatar = comment.avatar_url
            } else if (comment.profile_picture) {
              comment.author_avatar = comment.profile_picture
            } else if (comment.user && comment.user.avatar) {
              comment.author_avatar = comment.user.avatar
            }
          }
          
          // 修复回复数据
          if (comment.replies && Array.isArray(comment.replies)) {
            comment.replies.forEach((reply, replyIndex) => {
              
              // 设置用户名字段
              if (!reply.username) {
                reply.username = reply.author_name || reply.author || reply.user || reply.user_name || reply.created_by || '匿名用户'
              }
              
              // 设置头像字段
              if (!reply.author_avatar && reply.avatar) {
                reply.author_avatar = reply.avatar
              } else if (!reply.author_avatar && reply.avatar_url) {
                reply.author_avatar = reply.avatar_url
              }
              
              // 临时解决方案：如果回复作者是当前登录用户，使用当前用户的头像
              if (!reply.author_avatar && reply.username === this.authStore.username && this.authStore.avatar) {
                reply.author_avatar = this.authStore.avatar
              }
              
              // 修复回复头像字段
              if (!reply.author_avatar) {
                if (reply.avatar) {
                  reply.author_avatar = reply.avatar
                } else if (reply.user_avatar) {
                  reply.author_avatar = reply.user_avatar
                } else if (reply.avatar_url) {
                  reply.author_avatar = reply.avatar_url
                } else if (reply.profile_picture) {
                  reply.author_avatar = reply.profile_picture
                } else if (reply.user && reply.user.avatar) {
                  reply.author_avatar = reply.user.avatar
                }
              }
              
            })
          }
        })
      } catch (error) {
        this.showMessage('加载评论失败：' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },

    async submitComment() {
      if (!this.newComment.content.trim()) return

      this.submitting = true
      try {
        const result = await ApiService.createComment(this.postId, {
          content: this.newComment.content.trim()
        })

        if (result.success) {
          this.showMessage('评论发布成功！', 'success')
          this.newComment.content = ''
          await this.loadComments()
        }
      } catch (error) {
        this.showMessage('发布失败：' + error.message, 'error')
      } finally {
        this.submitting = false
      }
    },

    async submitReply() {
      if (!this.replyForm.content.trim() || !this.replyingTo) return

      this.replySubmitting = true
      try {
        const result = await ApiService.createComment(this.postId, {
          content: this.replyForm.content.trim(),
          parent_id: this.replyingTo.id
        })

        if (result.success) {
          this.showMessage('回复发布成功！', 'success')
          this.cancelReply()
          await this.loadComments()
        }
      } catch (error) {
        this.showMessage('回复失败：' + error.message, 'error')
      } finally {
        this.replySubmitting = false
      }
    },

    editComment(comment) {
      this.editingComment = comment
      this.editForm.content = comment.content
      this.$nextTick(() => {
        this.autoResizeEdit()
      })
    },

    async saveEdit() {
      if (!this.editForm.content.trim() || !this.editingComment) return

      this.editSubmitting = true
      try {
        const result = await ApiService.updateComment(this.editingComment.id, {
          content: this.editForm.content.trim()
        })

        if (result.success) {
          this.showMessage('评论更新成功！', 'success')
          this.cancelEdit()
          await this.loadComments()
        }
      } catch (error) {
        this.showMessage('更新失败：' + error.message, 'error')
      } finally {
        this.editSubmitting = false
      }
    },

    cancelEdit() {
      this.editingComment = null
      this.editForm.content = ''
    },

    toggleReply(comment) {
      if (this.replyingTo && this.replyingTo.id === comment.id) {
        this.cancelReply()
      } else {
        this.replyingTo = comment
        this.replyForm.content = ''
        this.$nextTick(() => {
          this.$refs.replyTextarea?.focus()
        })
      }
    },

    cancelReply() {
      this.replyingTo = null
      this.replyForm.content = ''
    },

    confirmDelete(comment) {
      this.deleteTarget = comment
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.deleteTarget = null
    },

    async deleteComment() {
      if (!this.deleteTarget) return

      this.deleting = true
      try {
        const result = await ApiService.deleteComment(this.deleteTarget.id)
        if (result.success) {
          this.showMessage('评论删除成功', 'success')
          await this.loadComments()
        }
      } catch (error) {
        this.showMessage('删除失败：' + error.message, 'error')
      } finally {
        this.deleting = false
        this.showDeleteModal = false
        this.deleteTarget = null
      }
    },

    clearComment() {
      this.newComment.content = ''
    },

    canEditComment(comment) {
      if (!this.authStore.isLoggedIn) return false
      return this.authStore.isAdmin || comment.username === this.authStore.username
    },

    getWordCount(content) {
      if (!content) return 0
      return content.replace(/\s/g, '').length
    },

    renderCommentContent(content) {
      if (!content) return ''
      
      // 简单的Markdown渲染
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
    },

    formatDate(dateString) {
      try {
        // 创建时间对象
        let date = new Date(dateString)
        
        // 修复8小时时区问题：将时间向前推8小时
        // 这是因为后端可能返回的是UTC时间，但前端需要按本地时间计算
        date = new Date(date.getTime() + 8 * 60 * 60 * 1000)
        
        const now = new Date()
        const diff = now - date

        // 1分钟内
        if (diff < 60000) {
          return '刚刚'
        }
        // 1小时内
        if (diff < 3600000) {
          return Math.floor(diff / 60000) + '分钟前'
        }
        // 24小时内
        if (diff < 86400000) {
          return Math.floor(diff / 3600000) + '小时前'
        }
        // 7天内
        if (diff < 604800000) {
          return Math.floor(diff / 86400000) + '天前'
        }
        // 超过7天显示具体日期
        return date.toLocaleDateString('zh-CN', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        console.error('时间格式化错误:', error)
        return '未知时间'
      }
    },

    autoResize() {
      this.$nextTick(() => {
        const textarea = this.$refs.commentTextarea
        if (textarea) {
          textarea.style.height = 'auto'
          textarea.style.height = Math.max(80, textarea.scrollHeight) + 'px'
        }
      })
    },

    autoResizeReply() {
      this.$nextTick(() => {
        const textarea = this.$refs.replyTextarea
        if (textarea) {
          textarea.style.height = 'auto'
          textarea.style.height = Math.max(60, textarea.scrollHeight) + 'px'
        }
      })
    },

    autoResizeEdit() {
      this.$nextTick(() => {
        const textarea = this.$refs.editTextarea
        if (textarea) {
          textarea.style.height = 'auto'
          textarea.style.height = Math.max(60, textarea.scrollHeight) + 'px'
        }
      })
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
.comment-section {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.comment-header {
  margin-bottom: 30px;
}

.comment-header h3 {
  color: white;
  font-size: 1.5em;
  margin-bottom: 5px;
}

.comment-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95em;
}

/* 评论表单样式 */
.comment-form-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: white;
  font-weight: bold;
  font-size: 1em;
}

.form-group textarea {
  min-height: 80px;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1em;
  line-height: 1.5;
  resize: none;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.comment-hint {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85em;
}

.form-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 登录提示样式 */
.login-prompt {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.prompt-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.prompt-icon {
  font-size: 2em;
}

.prompt-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1em;
}

/* 评论列表样式 */
.comments-list {
  margin-top: 20px;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: white;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-comments {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.no-comments-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.no-comments h4 {
  color: white;
  margin-bottom: 10px;
}

/* 评论项样式 */
.comment-item {
  margin-bottom: 25px;
}

.comment-main {
  display: flex;
  gap: 15px;
}

.comment-avatar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.comment-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.comment-author {
  color: white;
  font-weight: bold;
  font-size: 0.95em;
}

.reply-indicator {
  color: rgba(102, 126, 234, 0.8);
  font-size: 0.85em;
}

.comment-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85em;
}

.comment-actions {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

.action-btn {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.delete-btn:hover {
  background: rgba(255, 99, 99, 0.3);
  border-color: rgba(255, 99, 99, 0.5);
}

.comment-body {
  margin-bottom: 10px;
}

.comment-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  word-break: break-word;
}

.comment-text code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #e6db74;
}

.comment-footer {
  display: flex;
  align-items: center;
  gap: 15px;
}

.reply-btn {
  background: none;
  border: none;
  color: rgba(102, 126, 234, 0.8);
  cursor: pointer;
  font-size: 0.9em;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.reply-btn:hover,
.reply-btn.active {
  background: rgba(102, 126, 234, 0.2);
  color: white;
}

/* 编辑表单样式 */
.edit-form {
  margin: 10px 0;
}

.edit-textarea {
  width: 100%;
  min-height: 60px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.95em;
  line-height: 1.5;
  resize: none;
  margin-bottom: 10px;
  font-family: inherit;
}

.edit-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.15);
}

.edit-actions {
  display: flex;
  gap: 8px;
}

/* 回复表单样式 */
.reply-form {
  margin-top: 15px;
  margin-left: 55px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 回复列表样式 */
.replies-list {
  margin-top: 15px;
  margin-left: 55px;
  border-left: 2px solid rgba(255, 255, 255, 0.1);
  padding-left: 20px;
}

.reply-item {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
}

.reply-item .comment-avatar {
  width: 32px;
  height: 32px;
}

.reply-item .avatar-icon {
  font-size: 1em;
}

.reply-item .comment-content {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
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

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background: rgba(255, 99, 99, 0.3);
  color: white;
  border: 1px solid rgba(255, 99, 99, 0.5);
}

.btn-danger:hover:not(:disabled) {
  background: rgba(255, 99, 99, 0.4);
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
  max-width: 400px;
  width: 90%;
}

.modal-header {
  padding: 20px 20px 0;
  color: white;
  text-align: center;
}

.modal-body {
  padding: 20px;
  color: white;
  text-align: center;
}

.warning-text {
  color: rgba(255, 99, 99, 0.8);
  font-size: 0.9em;
  margin-top: 10px;
}

.modal-footer {
  padding: 0 20px 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
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

/* ================== 亮色主题样式 ================== */
.comment-section.light-mode {
  color: #2c3e50;
}

/* 标题和文本 */
.comment-section.light-mode .comment-header h3,
.comment-section.light-mode .comment-subtitle,
.comment-section.light-mode .comment-hint,
.comment-section.light-mode .comment-author,
.comment-section.light-mode .comment-date,
.comment-section.light-mode .comment-content,
.comment-section.light-mode .comment-text,
.comment-section.light-mode .no-comments p,
.comment-section.light-mode .no-comments h4,
.comment-section.light-mode .loading p,
.comment-section.light-mode .prompt-text,
.comment-section.light-mode label {
  color: #2c3e50 !important;
}

/* 次要文本 */
.comment-section.light-mode .comment-meta,
.comment-section.light-mode .comment-time,
.comment-section.light-mode .comment-actions span,
.comment-section.light-mode .reply-indicator {
  color: #7f8c8d !important;
}

/* 表单容器和卡片 */
.comment-section.light-mode .comment-form-container,
.comment-section.light-mode .login-prompt,
.comment-section.light-mode .comment-item,
.comment-section.light-mode .reply-item,
.comment-section.light-mode .reply-form {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  color: #2c3e50;
}

/* 输入框和文本域 */
.comment-section.light-mode textarea,
.comment-section.light-mode input,
.comment-section.light-mode .edit-textarea {
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  color: #2c3e50 !important;
}

.comment-section.light-mode textarea::placeholder,
.comment-section.light-mode input::placeholder {
  color: #95a5a6 !important;
}

.comment-section.light-mode textarea:focus,
.comment-section.light-mode input:focus,
.comment-section.light-mode .edit-textarea:focus {
  border-color: #667eea !important;
  background: rgba(255, 255, 255, 1) !important;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* 按钮样式 */
.comment-section.light-mode .btn-primary {
  background: #667eea !important;
  color: white !important;
  border: 1px solid #667eea !important;
}

.comment-section.light-mode .btn-primary:hover {
  background: #5a67d8 !important;
}

.comment-section.light-mode .btn-secondary {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #2c3e50 !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
}

.comment-section.light-mode .btn-secondary:hover {
  background: rgba(0, 0, 0, 0.05) !important;
}

.comment-section.light-mode .btn-danger {
  background: #e74c3c !important;
  color: white !important;
}

.comment-section.light-mode .reply-btn {
  color: #667eea !important;
  background: transparent !important;
}

.comment-section.light-mode .reply-btn:hover,
.comment-section.light-mode .reply-btn.active {
  background: rgba(102, 126, 234, 0.1) !important;
}

.comment-section.light-mode .action-btn {
  color: #7f8c8d !important;
  background: transparent !important;
}

.comment-section.light-mode .action-btn:hover {
  background: rgba(0, 0, 0, 0.1) !important;
}

/* 模态框 */
.comment-section.light-mode .modal {
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  color: #2c3e50;
}

.comment-section.light-mode .modal-header,
.comment-section.light-mode .modal-body {
  color: #2c3e50 !important;
}

.comment-section.light-mode .warning-text {
  color: #e74c3c !important;
}

/* 消息提示 */
.comment-section.light-mode .message {
  color: #2c3e50 !important;
}

.comment-section.light-mode .message.success {
  background: rgba(46, 204, 113, 0.1) !important;
  border-color: #2ecc71 !important;
}

.comment-section.light-mode .message.error {
  background: rgba(231, 76, 60, 0.1) !important;
  border-color: #e74c3c !important;
}

/* 头像和图标 */
.comment-section.light-mode .avatar-icon {
  color: #7f8c8d !important;
}

.comment-section.light-mode .no-comments-icon {
  color: #bdc3c7 !important;
}

/* 加载动画 */
.comment-section.light-mode .spinner {
  border-color: rgba(0, 0, 0, 0.1) !important;
  border-top-color: #667eea !important;
}
</style>
