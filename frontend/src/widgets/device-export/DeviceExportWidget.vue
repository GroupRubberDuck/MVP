<!-- DeviceExportWidget.vue
  Widget smart di dominio: orchestra l'esportazione di un Device.

  Responsabilità (SRP):
    - Gestire apertura/chiusura del modale
    - Gestire la selezione del formato di esportazione
    - Avviare il download del file
    - Comporre i componenti dumb (BaseModal)

  NON è responsabile di:
    - Overlay e gestione Escape (delegato a BaseModal)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/BaseModal.vue'

const props = defineProps({
  deviceName: {
    type: String,
    required: true,
  },
  exportBaseUrl: {
    type: String,
    required: true,
  },
})

const isModalOpen = ref(false)
const exportFormat = ref('json')

function openModal() {
  if (!isModalOpen.value) {
    isModalOpen.value = true
    exportFormat.value = 'json'
  }
}

function closeModal() {
  isModalOpen.value = false
}

function downloadFile() {
  const url = `${props.exportBaseUrl}?extension=${exportFormat.value}`
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  closeModal()
}
</script>

<template>
  <div>
    <button @click="openModal" class="btn btn--secondary btn--sm">
      Esporta dispositivo
    </button>

    <BaseModal
      v-if="isModalOpen"
      @close="closeModal"
    >
      <h2>Esporta Dispositivo</h2>
      <p>Seleziona il formato per esportare i dati di <strong>{{ deviceName }}</strong>:</p>

      <select v-model="exportFormat" class="form-input format-select">
        <option value="json">JSON (.json)</option>
        <option value="xml">XML (.xml)</option>
        <option value="csv">CSV (.csv)</option>
      </select>

      <div>
        <button @click="downloadFile" class="btn btn--outline">
          Scarica File
        </button>
        <button @click="closeModal" class="btn btn--outline">
          Annulla
        </button>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.export-card {
  max-width: 400px;
  width: 100%;
  background: white;
  padding: 24px;
  border-radius: 8px;
  border-top: 4px solid #3b82f6;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.title-primary {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1e3a8a;
  margin: 0 0 16px 0;
  font-size: 20px;
}

.icon {
  color: #3b82f6;
}

.export-body p {
  margin-bottom: 12px;
  color: #4b5563;
  line-height: 1.5;
}

.format-select {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  margin-bottom: 16px;
  font-size: 16px;
  background-color: #f9fafb;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

</style>