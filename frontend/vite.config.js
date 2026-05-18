import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
    resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
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
        'delete-device': resolve(__dirname, 'src/main-delete-device.js'),
        'export-device': resolve(__dirname, 'src/main-export-device.js'),
        'import-device': resolve(__dirname, 'src/main-import-device.js'),
        'open-session': resolve(__dirname, 'src/main-open-session.js'),
        'dashboard-logic': resolve(__dirname, 'src/main-dashboard.js'),
        'create-asset': resolve(__dirname, 'src/main-create-asset.js'),
        'asset-delete-widget': resolve(__dirname, 'src/widgets/asset-delete/main.js'),
        'requirement-evaluation-widget':resolve(__dirname, 'src/widgets/requirement-evaluation/main.js'),
        'device-import-widget':resolve(__dirname, 'src/widgets/device-import/main.js'),
        'open-session-widget':resolve(__dirname, 'src/widgets/open-session/main.js'),
        'export-device-widget':resolve(__dirname, 'src/widgets/device-export/main.js'),
        'edit-asset-widget':resolve(__dirname, 'src/widgets/asset-edit/main.js'),
        'create-asset-widget':resolve(__dirname, 'src/widgets/asset-create/main.js'),
        'session-commit-widget':resolve(__dirname, 'src/widgets/session-commit/main.js'),
        'session-close-widget':resolve(__dirname, 'src/widgets/session-close/main.js'),
        'session-commit-and-close-widget':resolve(__dirname, 'src/widgets/session-commit-and-close/main.js'),
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
