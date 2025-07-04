import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDarkMode: false
  }),

  getters: {
    themeClass: (state) => state.isDarkMode ? 'dark-mode' : 'light-mode'
  },

  actions: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode
      // 保存到本地存储
      localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light')
    },

    initTheme() {
      // 从本地存储读取主题设置
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        this.isDarkMode = savedTheme === 'dark'
      } else {
        // 如果没有保存的设置，检查系统偏好
        this.isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      }
    }
  }
})
