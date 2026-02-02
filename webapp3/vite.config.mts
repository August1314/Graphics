import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite 配置：以 webapp3 目录为根，React 入口为 src/main.tsx
export default defineConfig({
  plugins: [react()],
  root: '.',
  build: {
    outDir: 'dist',
  },
  server: {
    port: 5173,
  },
});


