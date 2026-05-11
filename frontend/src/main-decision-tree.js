import { createApp } from 'vue'
import { createPinia } from 'pinia'
import DecisionTreeWidget from './decision-tree/components/DecisionTreeWidget.vue'

const mountEl = document.getElementById('decision-tree-app')

if (mountEl) {
  const app = createApp(DecisionTreeWidget)
  app.use(createPinia())
    
  app.mount(mountEl)
}