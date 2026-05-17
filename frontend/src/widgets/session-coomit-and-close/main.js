// widgets/session-commit-and-close/main.js

import { createApp } from 'vue'
import SessionCommitAndCloseWidget from './SessionCommitAndCloseWidget.vue'

const mountPoint = document.getElementById('session-commit-and-close-widget')

if (mountPoint) {
  const { commitAndCloseUrl, redirectUrl } = mountPoint.dataset

  createApp(SessionCommitAndCloseWidget, {
    commitAndCloseUrl,
    redirectUrl,
  }).mount(mountPoint)
}