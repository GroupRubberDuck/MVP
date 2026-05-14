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
import DeviceCreateWidget from './DeviceCreateWidget.vue'
import { DEFAULT_STANDARD_ID } from '../../constants.js'


const mountPoint = document.getElementById('create-device-app')

if (mountPoint) {
  const { submitUrl, cancelUrl} = mountPoint.dataset

  createApp(DeviceCreateWidget, {
    submitUrl,
    cancelUrl,
    defaultStandardId: DEFAULT_STANDARD_ID,
  }).mount(mountPoint)

}