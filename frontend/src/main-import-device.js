import { createApp } from 'vue'
import ImportDeviceModal from './ImportDeviceModal.vue'

const el = document.getElementById('import-device-app')
if (el) {
    createApp(ImportDeviceModal).mount(el)
}