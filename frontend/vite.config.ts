import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',  // 监听所有网络接口，允许通过IP访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 使用IPv4地址而不是localhost
        changeOrigin: true
      }
    }
  }
})
