// widgets/asset-edit/main.js

import { createApp } from 'vue'
import AssetEditWidget from './AssetEditWidget.vue'

const mountPoint = document.getElementById('asset-edit-widget')

if (mountPoint) {
  const { submitUrl, cancelUrl,redirectUrl, initialName, initialAssetType, initialDescription} = mountPoint.dataset

  createApp(AssetEditWidget, {
    submitUrl, 
    cancelUrl,
    redirectUrl,
    initialName, 
    initialAssetType, 
    initialDescription
  }).mount(mountPoint)
}