<!-- DeviceImportWidget.vue
  Widget smart di dominio: orchestra l'importazione di un Device da file.

  Responsabilità (SRP):
    - Gestire apertura/chiusura del modale
    - Eseguire l'upload del file verso il backend
    - Gestire il redirect/reload dopo il successo
    - Comporre i componenti dumb (BaseModal, FileDropZone, AsyncButton)

  NON è responsabile di:
    - Overlay e gestione Escape (delegato a BaseModal)
    - Stato loading/errore del bottone (delegato ad AsyncButton)
    - Drag & drop e selezione file (delegato a FileDropZone)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import AsyncButton from '@/components/AsyncButton.vue'
import FileDropZone from '@/components/FileDropZone.vue'

const props = defineProps({
  importUrl: {
    type: String,
    required: true,
  },
  redirectUrl: {
    type: String,
    required: true,
  },
})

const isModalOpen = ref(false)
const selectedFile = ref(null)
const dropZoneRef = ref(null)
const errorMessage = ref('')

function openModal() {
if(!isModalOpen.value){

        isModalOpen.value = true
        selectedFile.value = null
        errorMessage.value = ''
}
}

function closeModal() {
  isModalOpen.value = false
}

function onFileSelect(file) {
  selectedFile.value = file
  errorMessage.value = ''
}

function onFileError(message) {
  errorMessage.value = message
}

async function uploadFile() {
  if (!selectedFile.value) {
    throw new Error('Nessun file selezionato.')
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  const response = await fetch(props.importUrl, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || "Errore durante l'importazione.")
  }

  return await response.json()
}

function onSuccess() {
  window.location.href = props.redirectUrl
}
</script>

<template>
  <div>
    <button  @click="openModal" class="btn btn--outline">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      Importa Dispositivo
    </button>

    <BaseModal v-if="isModalOpen"
      
      @close="closeModal"
    >
      <h2>Importa Dispositivo</h2>
      <p class="description">Seleziona un file di configurazione per aggiungere un nuovo dispositivo al sistema.</p>

      <div v-if="errorMessage" class="alert-error">
        {{ errorMessage }}
      </div>

      <FileDropZone
        ref="dropZoneRef"
        accept=".json,.xml,.csv"
        placeholder="Clicca per caricare o trascina il file"
        hint="Formati supportati: JSON, XML, CSV"
        @select="onFileSelect"
        @error="onFileError"
      />

      <div class=" mt-4">
        <AsyncButton
          :action="uploadFile"
          label="Avvia Importazione"
          loading-label="Caricamento in corso..."
          @success="onSuccess"
          @error="(err) => errorMessage = err.message"
          button-class="btn btn--outline"
        />
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
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.import-card {
  max-width: 480px;
  width: 95%;
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border-top: 6px solid #10b981;
}

.title-primary {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.4rem;
  color: #064e3b;
  margin-bottom: 8px;
}

.description {
  color: #6b7280;
  font-size: 0.95rem;
  margin-bottom: 24px;
}

.upload-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  background: #f9fafb;
  transition: all 0.3s ease;
  position: relative;
}

.upload-zone--dragging {
  border-color: #10b981;
  background: #ecfdf5;
}

.upload-zone--active {
  border-style: solid;
  border-color: #10b981;
  background: #f0fdf4;
}

.upload-label {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  margin-bottom: 8px;
  color: #9ca3af;
}

.text-main {
  font-weight: 600;
  color: #374151;
}

.text-sub {
  font-size: 0.8rem;
  color: #9ca3af;
}

.file-info {
  color: #065f46;
  display: flex;
  flex-direction: column;
}

.file-size {
  font-size: 0.85rem;
  color: #6b7280;
}

.hidden-input {
  display: none;
}

.alert-error {
  background: #fef2f2;
  color: #b91c1c;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #fee2e2;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.mt-4 {
  margin-top: 32px;
}
</style>