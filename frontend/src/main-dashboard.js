import { createApp } from 'vue'
import DashboardLogic from './DashboardLogic.vue' // Il file con tutto il codice che abbiamo scritto prima

const el = document.getElementById('dashboard-logic-app')

if (el) {
  createApp(DashboardLogic).mount(el)
}