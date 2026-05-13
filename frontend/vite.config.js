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
        'create-device': resolve(__dirname, 'src/widgets/device-create/main.js'),
        'edit-device': resolve(__dirname, 'src/widgets/device-edit/main.js'),
        'decision-tree': resolve(__dirname, 'src/main-decision-tree.js'),
        'delete-device': resolve(__dirname, 'src/main-delete-device.js'),
        'export-device': resolve(__dirname, 'src/main-export-device.js'),
        'import-device': resolve(__dirname, 'src/main-import-device.js'),
        'open-session': resolve(__dirname, 'src/main-open-session.js'),
        'dashboard-logic': resolve(__dirname, 'src/main-dashboard.js'),
        'create-asset': resolve(__dirname, 'src/main-create-asset.js'),
        'asset-delete-widget': resolve(__dirname, 'src/widgets/asset-delete/main.js')
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
