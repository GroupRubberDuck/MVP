<!-- SessionCloseWidget.vue
  Widget smart di dominio: chiude la sessione con conferma.

  Responsabilità (SRP):
    - Mostrare un modale di conferma prima della chiusura
    - Eseguire la chiamata DELETE per chiudere la sessione
    - Disabilitare il navigation guard e fare redirect

  NON è responsabile di:
    - Overlay e gestione Escape (delegato a BaseModal)
    - Stato loading/errore del bottone (delegato ad AsyncButton)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import AsyncButton from '@/components/AsyncButton.vue'
import { disableNavigationGuard } from '@/shared/navigationGuard.js'

const props = defineProps({
  closeUrl: {
    type: String,
    required: true,
  },
  redirectUrl: {
    type: String,
    required: true,
  },
})

const isModalOpen = ref(false)

function openModal() {
  if (!isModalOpen.value) {
    isModalOpen.value = true
  }
}

function closeModal() {
  isModalOpen.value = false
}

async function closeSession() {
  const response = await fetch(props.closeUrl, { method: 'DELETE' })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || 'Errore nella chiusura della sessione.')
  }
}

function onSuccess() {
  disableNavigationGuard()
  window.location.href = props.redirectUrl
}
</script>

<template>
  <div>
    <button @click="openModal" class="btn btn--danger">
      Chiudi Sessione
    </button>

    <BaseModal v-if="isModalOpen" @close="closeModal">
      <p>Sei sicuro di voler chiudere la sessione?</p>
      <p>I dati non salvati andranno persi.</p>
      <div>
        <AsyncButton
          :action="closeSession"
          label="Conferma chiusura"
          loading-label="Chiusura..."
          button-class="btn btn--danger"
          @success="onSuccess"
        />
        <button @click="closeModal" class="btn btn--outline">Annulla</button>
      </div>
    </BaseModal>
  </div>
</template>