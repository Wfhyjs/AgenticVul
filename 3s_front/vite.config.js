import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
module.exports = defineConfig({
  plugins: [
    vue(),
  ],
  rules: {

  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '127.0.0.1', // 设置为'0.0.0.0'以监听所有网络接口
    port: 5173, // 设置端口号，例如3000
    proxy: {
      '/uploadProject': 'http://127.0.0.1:5000',
    },
  }
})
