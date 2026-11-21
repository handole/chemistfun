import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    hmr: {
      // Tailscale Funnel expose port 443 (HTTPS), bukan :5173
      // Browser harus konek WebSocket HMR ke port 443, bukan 5173
      clientPort: 443,
    },
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://backend:8000',
        changeOrigin: true
      }
    }
  }
})
