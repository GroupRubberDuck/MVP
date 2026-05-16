// widgets/asset-create/main.js

import { createApp } from 'vue'
import AssetCreateWidget from './AssetCreateWidget.vue'

const mountPoint = document.getElementById('asset-create-widget')

if (mountPoint) {
  const { submitUrl, cancelUrl, redirectUrl} = mountPoint.dataset

  createApp(AssetCreateWidget, {
    submitUrl, 
    cancelUrl,
    redirectUrl
  }).mount(mountPoint)
}