import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  },
  // Use repository name as base when deploying to GitHub Pages.
  // Override via VITE_BASE env var if needed.
  base: process.env.VITE_BASE || '/'
})

