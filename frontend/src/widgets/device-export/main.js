// widgets/device-export/main.js

import { createApp } from 'vue'
import DeviceExportWidget from './DeviceExportWidget.vue'

const mountPoint = document.getElementById('device-export-widget')

if (mountPoint) {
  const { deviceName, exportBaseUrl } = mountPoint.dataset

  createApp(DeviceExportWidget, {
    deviceName,
    exportBaseUrl,
  }).mount(mountPoint)
}