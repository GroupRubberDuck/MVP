// widgets/dashboard/main.js
//
// Entry point della dashboard di valutazione.
//
// Responsabilità:
//   - Attivare il blocco navigazione
//   - Collegare data-allow-exit ai link che devono uscire

import { 
  enableNavigationGuard, 
  disableNavigationGuard,
  temporarilyDisableNavigationGuard 
} from '@/shared/navigationGuard.js'

window.addEventListener('load', () => {
  enableNavigationGuard()

  document.querySelectorAll('[data-allow-exit]').forEach(link => {
    link.addEventListener('click', () => {
      disableNavigationGuard()
    })
  })

  document.querySelectorAll('[data-allow-download]').forEach(link => {
    link.addEventListener('click', () => {
      temporarilyDisableNavigationGuard(2000)
    })
  })
})

