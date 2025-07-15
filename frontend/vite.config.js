import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Remove trailing slash to prevent redirects
            if (proxyReq.path.endsWith('/') && proxyReq.path !== '/') {
              proxyReq.path = proxyReq.path.slice(0, -1);
            }
          });
        }
      },
    },
  },
})
