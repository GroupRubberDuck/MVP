import { createApp } from 'vue'
import ExportDeviceModal from './ExportDeviceModal.vue'

const el = document.getElementById('export-device-app')
if (el) {
  createApp(ExportDeviceModal).mount(el)
}