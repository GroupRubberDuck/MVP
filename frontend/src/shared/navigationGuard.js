// shared/navigationGuard.js
//
// Gestione del blocco navigazione per pagine con dati non salvati.
//
// Responsabilità (SRP):
//   - Attivare/disattivare il prompt di conferma uscita pagina
//
// NON è responsabile di:
//   - Decidere quando attivare il blocco (lo decide chi lo importa)

function handleBeforeUnload(event) {
  event.preventDefault()
  event.returnValue = ''
}

export function enableNavigationGuard() {
  window.addEventListener('beforeunload', handleBeforeUnload)
}

export function disableNavigationGuard() {
  window.removeEventListener('beforeunload', handleBeforeUnload)
}

export function temporarilyDisableNavigationGuard(ms = 1000) {
  disableNavigationGuard()
  setTimeout(() => {
    enableNavigationGuard()
  }, ms)
}