<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="closeModal">
    <div class="card import-card">
      <div class="card__header">
        <h2 class="title-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          Importa Dispositivo
        </h2>
      </div>

      <div class="import-body">
        <div v-if="errorMessage" class="alert-error">
          {{ errorMessage }}
        </div>

        <p class="description">
          Seleziona un file di configurazione per aggiungere un nuovo dispositivo al sistema.
        </p>

        <div 
          class="upload-zone" 
          :class="{ 'upload-zone--active': selectedFile, 'upload-zone--dragging': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileChange" 
            accept=".json,.xml,.csv" 
            id="file-upload" 
            class="hidden-input" 
          />
          
          <label for="file-upload" class="upload-label">
            <div class="upload-icon">
              <svg v-if="!selectedFile" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <span v-if="!selectedFile" class="text-main">Clicca per caricare o trascina il file</span>
            <span v-else class="file-info">
              <strong>{{ selectedFile.name }}</strong>
              <span class="file-size">({{ formatSize(selectedFile.size) }})</span>
            </span>
            <span class="text-sub">Formati supportati: JSON, XML, CSV</span>
          </label>
        </div>
      </div>

      <div class="form-actions mt-4">
        <button 
          class="btn btn--primary" 
          :disabled="!selectedFile || isUploading" 
          @click="uploadFile"
        >
          <span v-if="isUploading">Caricamento in corso...</span>
          <span v-else>Avvia Importazione</span>
        </button>
        <button class="btn btn--outline" @click="closeModal" :disabled="isUploading">
          Annulla
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isVisible = ref(false)
const selectedFile = ref(null)
const isUploading = ref(false)
const isDragging = ref(false)
const errorMessage = ref('')
const fileInput = ref(null)

onMounted(() => {
  window.openImportModal = () => {
    selectedFile.value = null
    errorMessage.value = ''
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
    isVisible.value = true
  }
})

const closeModal = () => {
  if (!isUploading.value) isVisible.value = false
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) selectedFile.value = file
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && ['application/json', 'text/xml', 'text/csv'].includes(file.type) || file.name.match(/\.(json|xml|csv)$/i)) {
    selectedFile.value = file
  } else {
    errorMessage.value = "Formato file non valido. Carica solo .json, .xml o .csv"
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function uploadFile() {
  if (!selectedFile.value) return

  isUploading.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await fetch('/api/devices/import', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      window.location.reload()
    } else {
      const data = await response.json().catch(() => ({}))
      errorMessage.value = data.error || "Errore critico durante l'importazione."
    }
  } catch (e) {
    errorMessage.value = "Impossibile contattare il server. Controlla la connessione."
  } finally {
    isUploading.value = false
  }
}
</script>

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