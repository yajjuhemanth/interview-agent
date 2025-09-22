import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API calls to Flask backend running on 5000
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/get': 'http://localhost:5000',
      '/agent': 'http://localhost:5000',
    }
  }
})
