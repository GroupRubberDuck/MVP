// widgets/device-import/main.js

import { createApp } from 'vue'
import DeviceImportWidget from './DeviceImportWidget.vue'

const mountPoint = document.getElementById('device-import-widget')

if (mountPoint) {
  const { importUrl, redirectUrl } = mountPoint.dataset

  createApp(DeviceImportWidget, {
    importUrl,
    redirectUrl,
  }).mount(mountPoint)
}