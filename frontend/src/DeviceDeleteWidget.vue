<!-- DeviceDeleteWidget.vue
  Widget smart di dominio: orchestra l'eliminazione di un Device
  con opzione di esportazione preventiva.

  Responsabilità (SRP):
    - Gestire apertura/chiusura del modale
    - Definire la logica di eliminazione (HTTP DELETE)
    - Definire la logica di esportazione (download file)
    - Comporre i componenti dumb (BaseModal, AsyncButton)

  NON è responsabile di:
    - Overlay e gestione Escape (delegato a BaseModal)
    - Stato loading/errore del bottone (delegato ad AsyncButton)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import { ref } from 'vue'
import AsyncButton from './components/AsyncButton.vue'
import BaseModal from './components/BaseModal.vue'

const props = defineProps({
  deviceName: {
    type: String,
    required: true,
  },
  deleteUrl: {
    type: String,
    required: true,
  },
  exportBaseUrl: {
    type: String,
    required: true,
  },
  redirectUrl: {
    type: String,
    required: true,
  },
})

const isModalOpen = ref(false)
const exportFormat = ref('json')

function openModal() {
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function deleteDevice() {
  const response = await fetch(props.deleteUrl, {
    method: 'DELETE',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || 'Eliminazione fallita')
  }
}

function exportDevice() {
  const url = `${props.exportBaseUrl}?extension=${exportFormat.value}`
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function onDeleteSuccess() {
  window.location.href = props.redirectUrl
}
</script>

<template>
  <div>
    <button class="btn-red" v-if="!isModalOpen" @click="openModal">
      Elimina
    </button>

    <BaseModal
      v-else
      @close="closeModal"
    >
      <p>Elimina dispositivo</p>
      <p>
        Stai per eliminare <strong>{{ deviceName }}</strong>.
        Questa operazione è irreversibile.
      </p>

      <div>
        <span>Esporta una copia prima di eliminare:</span>
        <select v-model="exportFormat">
          <option value="json">JSON</option>
          <option value="xml">XML</option>
          <option value="csv">CSV</option>
        </select>
        <button @click="exportDevice">
          Esporta
        </button>
      </div>

      <div>
        <AsyncButton
          :action="deleteDevice"
          label="Elimina"
          loading-label="Eliminazione..."
          @success="onDeleteSuccess"
        />
        <button @click="closeModal">
          Annulla
        </button>
      </div>
    </BaseModal>
  </div>
</template>