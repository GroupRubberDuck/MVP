// widgets/session-close/main.js

import { createApp } from 'vue'
import SessionCloseWidget from './SessionCloseWidget.vue'

const mountPoint = document.getElementById('session-close-widget')

if (mountPoint) {
  const { closeUrl, redirectUrl } = mountPoint.dataset

  createApp(SessionCloseWidget, {
    closeUrl,
    redirectUrl,
  }).mount(mountPoint)
}