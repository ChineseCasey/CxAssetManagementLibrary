import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/antd/',
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/libraries': 'http://127.0.0.1:8000',
      '/assets': 'http://127.0.0.1:8000',
      '/search': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',
      '/manage': 'http://127.0.0.1:8000',
      '/favorites': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/version': 'http://127.0.0.1:8000',
      '/metrics': 'http://127.0.0.1:8000',
    },
  },
})
