import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { readdirSync } from 'fs'

// Genera automaticamente un entry point per ogni .vue in src/components/
// Ogni componente viene compilato come file JS separato in backend/static/vue/
function getComponentEntries() {
  const componentsDir = resolve(__dirname, 'src/components')
  const entries = {}
  readdirSync(componentsDir)
    .filter(f => f.endsWith('.vue'))
    .forEach(f => {
      const name = f.replace('.vue', '').toLowerCase()
      entries[name] = resolve(componentsDir, f)
    })
  return entries
}

export default defineConfig({
  plugins: [vue()],
  build: {
    // Output direttamente nella cartella static di Flask
    outDir: '../backend/static/vue',
    emptyOutDir: false,        // non svuotare — altri file statici vivono lì
    lib: {
      entry: getComponentEntries(),
      formats: ['es'],         // ES module — compatibile con <script type="module">
    },
    rollupOptions: {
      // Vue è esternalizzato: viene caricato dalla CDN nel template Flask
      // e non bundlato dentro ogni componente
      external: ['vue'],
      output: {
        globals: { vue: 'Vue' },
        // Nome file = nome entry (es. importdevicemodal.js)
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
      }
    }
  }
})