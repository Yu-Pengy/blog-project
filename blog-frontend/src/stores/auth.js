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
        console.log('登录API响应:', response)
        
        if (response.success) {
          this.user = {
            username: response.user.username,
            is_admin: response.user.is_admin,
            avatar: response.user.avatar_url || null  // 使用avatar_url字段
          }
          this.isLoggedIn = true
          console.log('登录后用户信息:', this.user)
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
        console.log('checkAuth API响应:', response)
        
        if (response.logged_in) {
          this.user = {
            username: response.username,
            is_admin: response.is_admin,
            avatar: response.avatar_url || null  // 使用avatar_url字段
          }
          this.isLoggedIn = true
          console.log('用户信息更新后:', this.user)
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
      console.log('Auth store: 开始上传头像')
      console.log('Auth store: 当前用户状态:', this.user)
      console.log('Auth store: 登录状态:', this.isLoggedIn)
      
      try {
        const response = await ApiService.uploadAvatar(file)
        console.log('Auth store: API响应:', response)
        
        if (response.success) {
          // 更新用户头像信息
          if (this.user && response.data) {
            console.log('Auth store: 更新用户头像:', response.data.avatar_url)
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