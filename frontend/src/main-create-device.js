import { createApp } from 'vue'
import CreateDeviceForm from './CreateDeviceForm.vue'
const el = document.getElementById('create-device-app')
if (el) {
  createApp(CreateDeviceForm).mount(el)
}
