// widgets/device-edit/main.js

import { createApp } from 'vue'
import DeviceEditWidget from './DeviceEditWidget.vue'
import { DEFAULT_STANDARD_ID } from '../../constants.js'

const mountPoint = document.getElementById('device-edit-widget')

if (mountPoint) {
  const { submitUrl, cancelUrl, initialName, initialOs, initialDescription } = mountPoint.dataset

  createApp(DeviceEditWidget, {
    submitUrl,
    cancelUrl,
    initialName,
    initialOs,
    initialDescription,
    defaultStandardId: DEFAULT_STANDARD_ID,
  }).mount(mountPoint)
}