// widgets/asset-delete/main.js
//
// Livello di integrazione: collante tra il mondo Flask/Jinja e Vue.
//
// Responsabilità (SRP):
//   - Leggere i dati dal DOM (attributi data-*)
//   - Montare il widget Vue passandogli le props
//
// NON è responsabile di:
//   - Logica di business (delegata al widget)
//   - Presentazione (delegata ai componenti)

import { createApp } from 'vue'
import AssetDeleteWidget from './AssetDeleteWidget.vue'

const mountPoint = document.getElementById('asset-delete-widget')

if (mountPoint) {
  const { deleteUrl, redirectUrl } = mountPoint.dataset

  createApp(AssetDeleteWidget, {
    deleteUrl,
    redirectUrl,
  }).mount(mountPoint)
}