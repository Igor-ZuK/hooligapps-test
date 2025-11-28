import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Determine API target based on environment
// In Docker, use service name; locally, use localhost
const getApiTarget = () => {
  // Check if we're in Docker (backend service is accessible)
  if (process.env.VITE_API_URL) {
    return process.env.VITE_API_URL
  }

  return process.env.NODE_ENV === 'production' ? 'http://backend:8000' : 'http://localhost:8000'
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: getApiTarget(),
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
})

