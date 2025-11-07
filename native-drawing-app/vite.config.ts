import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  root: 'ui',
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'ui/src'),
    },
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'ui/index.html'),
      },
    },
  },
  server: {
    port: 3000,
    strictPort: true,
  },
});
