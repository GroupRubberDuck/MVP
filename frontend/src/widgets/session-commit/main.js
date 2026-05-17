// widgets/session-commit/main.js

import { createApp } from 'vue'
import SessionCommitWidget from './SessionCommitWidget.vue'

const mountPoint = document.getElementById('session-commit-widget')

if (mountPoint) {
  const { commitUrl } = mountPoint.dataset

  createApp(SessionCommitWidget, {
    commitUrl,
  }).mount(mountPoint)
}