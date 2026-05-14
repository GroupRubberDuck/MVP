<!-- AssetDeleteWidget.vue
  Widget smart di dominio: orchestra l'eliminazione di un Asset.

  Responsabilità (SRP):
    - Definire la logica di business per l'eliminazione (chiamata HTTP DELETE)
    - Decidere cosa succede dopo il successo (redirect)
    - Comporre i componenti dumb necessari (AsyncButton)

  NON è responsabile di:
    - Gestire lo stato di loading/errore del bottone (delegato ad AsyncButton)
    - Conoscere come i dati arrivano dal server (delegato al Livello 3)
    - Stile visivo del bottone
-->

<script setup>
import AsyncButton from '../../components/AsyncButton.vue'
import BaseModal from '../../components/BaseModal.vue'
import { ref } from 'vue'

const props = defineProps({
  /** URL dell'endpoint DELETE, iniettato dal Livello 3 */
  deleteUrl: {
    type: String,
    required: true,
  },
  /** URL a cui redirigere dopo eliminazione riuscita */
  redirectUrl: {
    type: String,
    required: true,
  },
})


const isModalOpen = ref(false)

function openModal() {
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}
/**
 * Esegue la chiamata DELETE.
 * Questa funzione viene passata come prop `action` ad AsyncButton.
 * Non gestisce loading/errori UI — è responsabilità di AsyncButton.
 *
 * @returns {Promise<void>}
 * @throws {Error} se la risposta HTTP non è ok
 */
async function deleteAsset() {
  const response = await fetch(props.deleteUrl, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(`Eliminazione fallita (${response.status})`)
  }
}

function onSuccess() {
  window.location.href = props.redirectUrl
}
</script>

<template>

  <div>
    <button v-if="!isModalOpen" @click="openModal">
      Elimina
    </button>

    <BaseModal
      v-else
      @close="closeModal"
    >
      <p>Sei sicuro di voler eliminare questo asset?</p>
      <AsyncButton
        :action="deleteAsset"
        label="Conferma eliminazione"
        loading-label="Eliminazione..."
        @success="onSuccess"
      />
      <button @click="closeModal">
        Annulla
      </button>
    </BaseModal>

  </div>
</template>