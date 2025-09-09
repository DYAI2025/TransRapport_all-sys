import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// https://vitejs.dev/config/
export default defineConfig(async () => ({
  plugins: [svelte()],
  clearScreen: false,
  base: './', // Ensure assets load from file:// URLs in bundled app
  // NO SERVER CONFIG - offline only, no dev server
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2021',
    minify: true,
    sourcemap: false,
    rollupOptions: {
      external: ['@tauri-apps/api/shell']
    }
  }
}));