import { defineStore } from 'pinia'
import ApiService from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoggedIn: false,
    loading: false
  }),

  getters: {
    isAdmin: (state) => state.user?.is_admin || false,
    username: (state) => state.user?.username || '',
    avatar: (state) => state.user?.avatar || null
  },

  actions: {
    async login(username, password) {
      this.loading = true
      try {
        const response = await ApiService.login(username, password)
        
        if (response.success) {
          this.user = {
            username: response.user.username,
            is_admin: response.user.is_admin,
            avatar: response.user.avatar_url || null  // 使用avatar_url字段
          }
          this.isLoggedIn = true
          return { success: true, message: response.message }
        }
        return { success: false, message: response.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await ApiService.logout()
        this.user = null
        this.isLoggedIn = false
        return { success: true }
      } catch (error) {
        return { success: false, message: error.message }
      }
    },

    async register(username, password) {
      this.loading = true
      try {
        const response = await ApiService.register(username, password)
        return { success: response.success, message: response.message }
      } catch (error) {
        return { success: false, message: error.message }
      } finally {
        this.loading = false
      }
    },

    async checkAuth() {
      try {
        const response = await ApiService.getCurrentUser()
        
        if (response.logged_in) {
          this.user = {
            username: response.username,
            is_admin: response.is_admin,
            avatar: response.avatar_url || null  // 使用avatar_url字段
          }
          this.isLoggedIn = true
        } else {
          this.user = null
          this.isLoggedIn = false
        }
      } catch (error) {
        console.error('checkAuth错误:', error)
        this.user = null
        this.isLoggedIn = false
      }
    },

    async uploadAvatar(file) {
      
      try {
        const response = await ApiService.uploadAvatar(file)
        
        if (response.success) {
          // 更新用户头像信息
          if (this.user && response.data) {
            this.user.avatar = response.data.avatar_url
          }
          return { 
            success: true, 
            message: response.message, 
            avatar_url: response.data ? response.data.avatar_url : null 
          }
        }
        return { success: false, message: response.message }
      } catch (error) {
        console.error('Auth store: 上传错误:', error)
        return { success: false, message: error.message }
      }
    }
  }
})