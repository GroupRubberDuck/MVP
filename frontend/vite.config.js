import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  experimental: {
    // Forza Vite ad utilizzare path assolute.
    // Rimuovendolo tutte le immagini e i link rompono.
    renderBuiltUrl(filename) {
      return '/static/vue/' + filename
    }
  },
  build: {
    // Forza Vite a sputare i file nella cartella di Flask
    outDir: '../backend/static/vue',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        'helloworld': resolve(__dirname, 'src/main.js'),
      },
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`
      }
    }
  },
  base: '/static/vue/',
})
