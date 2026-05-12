import { createApp } from 'vue'
import OpenSessionAction from './OpenSessionAction.vue'

const el = document.getElementById('open-session-app')
if (el) {
  createApp(OpenSessionAction).mount(el)
}