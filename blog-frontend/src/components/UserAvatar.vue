<template>
  <div class="user-avatar-display" :class="{ small: size === 'small', medium: size === 'medium', large: size === 'large' }">
    <img 
      v-if="avatar" 
      :src="avatar" 
      :alt="displayUsername + '的头像'"
      class="avatar-img"
    />
    <div v-else class="avatar-placeholder">
      👤
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserAvatar',
  props: {
    username: {
      type: String,
      default: '匿名用户'
    },
    avatar: {
      type: String,
      default: null
    },
    size: {
      type: String,
      default: 'medium',
      validator: value => ['small', 'medium', 'large'].includes(value)
    }
  },
  computed: {
    displayUsername() {
      return this.username || '匿名用户'
    }
  }
}
</script>

<style scoped>
.user-avatar-display {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-avatar-display.small {
  width: 20px;
  height: 20px;
}

.user-avatar-display.medium {
  width: 28px;
  height: 28px;
}

.user-avatar-display.large {
  width: 36px;
  height: 36px;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.user-avatar-display.small .avatar-placeholder {
  font-size: 0.6em;
}

.user-avatar-display.medium .avatar-placeholder {
  font-size: 0.7em;
}

.user-avatar-display.large .avatar-placeholder {
  font-size: 0.9em;
}

/* 深色模式样式 */
.dark-mode .user-avatar-display {
  border-color: rgba(93, 173, 226, 0.3);
  background: rgba(93, 173, 226, 0.1);
}

.dark-mode .avatar-placeholder {
  color: rgba(93, 173, 226, 0.8);
}

/* 浅色模式样式 */
.light-mode .user-avatar-display {
  border-color: rgba(102, 126, 234, 0.3);
  background: rgba(102, 126, 234, 0.1);
}

.light-mode .avatar-placeholder {
  color: rgba(102, 126, 234, 0.8);
}
</style>
