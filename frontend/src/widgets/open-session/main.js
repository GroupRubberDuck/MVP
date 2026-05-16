
import { createApp } from 'vue'
import OpenSessionWidget from './OpenSessionWidget.vue'

const mountPoint = document.getElementById('open-session-widget')

if (mountPoint) {
const { createSessionUrl, deviceId, redirectUrlTemplate } = mountPoint.dataset

createApp(OpenSessionWidget, {
  createSessionUrl,
  deviceId,
  redirectUrlTemplate,
}).mount(mountPoint)
}