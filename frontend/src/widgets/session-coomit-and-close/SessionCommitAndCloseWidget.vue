<!-- SessionCommitAndCloseWidget.vue
  Widget smart di dominio: salva e chiude la sessione in un'unica operazione.

  Responsabilità (SRP):
    - Eseguire la chiamata POST per commit-and-close
    - Disabilitare il navigation guard e fare redirect

  NON è responsabile di:
    - Stato loading/errore del bottone (delegato ad AsyncButton)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import AsyncButton from '@/components/AsyncButton.vue'
import { disableNavigationGuard } from '@/shared/navigationGuard.js'

const props = defineProps({
  commitAndCloseUrl: {
    type: String,
    required: true,
  },
  redirectUrl: {
    type: String,
    required: true,
  },
})

async function commitAndClose() {
  const response = await fetch(props.commitAndCloseUrl, { method: 'POST' })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || 'Errore durante salva e chiudi.')
  }
}

function onSuccess() {
  disableNavigationGuard()
  window.location.href = props.redirectUrl
}
</script>

<template>
  <AsyncButton
    :action="commitAndClose"
    label="Salva e Chiudi"
    loading-label="Salvataggio..."
    button-class="btn btn--primary"
    @success="onSuccess"
  />
</template>