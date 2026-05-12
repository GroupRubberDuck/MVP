import { createApp } from 'vue'
import DeleteDeviceForm from './DeleteDeviceForm.vue' 
const el = document.getElementById('delete-device-app')
if (el) {
  createApp(DeleteDeviceForm).mount(el)
}