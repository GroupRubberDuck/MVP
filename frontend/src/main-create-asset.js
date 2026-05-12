import { createApp } from 'vue'
import CreateAsset from './CreateAsset.vue'

const el = document.getElementById('create-asset-app')

if (el) {
  createApp(CreateAsset).mount(el)
}