// widgets/device-delete/main.js

import { createApp } from 'vue'
import DeviceDeleteWidget from './DeviceDeleteWidget.vue'

const mountPoint = document.getElementById('device-delete-widget')

if (mountPoint) {
  const { deviceName, deleteUrl, exportBaseUrl, redirectUrl } = mountPoint.dataset

  createApp(DeviceDeleteWidget, {
    deviceName,
    deleteUrl,
    exportBaseUrl,
    redirectUrl,
  }).mount(mountPoint)
}