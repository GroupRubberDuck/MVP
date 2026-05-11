<script setup>

import { ref, computed } from 'vue'
const emit = defineEmits(['close', 'imported'])
const importFile    = ref(null)
const isDragging    = ref(false)
const isImporting   = ref(false)
const importSuccess = ref('')
const importError   = ref('')
const ALLOWED_EXT = ['json', 'csv', 'xml']
const fileIcon = computed(() => {
  if (!importFile.value) return ''
  const ext = importFile.value.name.split('.').pop().toLowerCase()
  return ext === 'json' ? '📄' : ext === 'xml' ? '📋' : '📊'
})

const fileSizeLabel = computed(() => {
  if (!importFile.value) return ''
  const b = importFile.value.size
  return b < 1024 ? `${b} B`
    : b < 1024 * 1024 ? `${(b / 1024).toFixed(1)} KB`
    : `${(b / (1024 * 1024)).toFixed(2)} MB`
})

function validateFile(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!ALLOWED_EXT.includes(ext))
    return `Formato ".${ext}" non supportato. Usa JSON, CSV o XML.`
  return null
}

function setFile(file) {
  importError.value   = ''
  importSuccess.value = ''
  const err = validateFile(file)
  if (err) { importError.value = err; return }
  importFile.value = file
}

function onFileSelected(e) {
  if (e.target.files[0]) setFile(e.target.files[0])
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0])
}

function removeFile() {
  importFile.value    = null
  importError.value   = ''
  importSuccess.value = ''
}

function closeModal() {
  if (isImporting.value) return
  emit('close')
}
async function submitImport() {
  if (!importFile.value || isImporting.value) return
  isImporting.value   = true
  importError.value   = ''
  importSuccess.value = ''

  const formData = new FormData()
  formData.append('file', importFile.value)

  try {
    const res  = await fetch('/api/devices/import', {
      method: 'POST',
      body:   formData,
    })
    const data = await res.json()

    if (res.ok) {
      importSuccess.value = data.message || 'Dispositivo importato con successo.'
      importFile.value    = null
      setTimeout(() => emit('imported'), 1200)
    } else {
      importError.value = data.error || `Errore ${res.status}: importazione fallita.`
    }
  } catch {
    importError.value = 'Errore di rete. Verifica la connessione e riprova.'
  } finally {
    isImporting.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="import-modal-title">

      <h2 class="modal__title" id="import-modal-title">Importa Dispositivo</h2>
      <p class="modal__body">
        Carica un file di configurazione per aggiungere un dispositivo al sistema.<br>
        Formati supportati: <strong>JSON, CSV, XML</strong> — max 10 MB.
      </p>

      <div 
        v-if="!importFile"
        class="upload-area"
        :class="{ 'upload-area--dragover': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()">

        <div class="upload-area__icon">📂</div>
        <p class="upload-area__title">Trascina qui il file o clicca per selezionarlo</p>
        <p class="upload-area__hint">.json &nbsp;·&nbsp; .csv &nbsp;·&nbsp; .xml</p>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept=".json,.csv,.xml"
        style="display:none"
        @change="onFileSelected"/>

      <div v-if="importFile" class="file-preview">
        <span class="file-preview__icon">{{ fileIcon }}</span>
        <div class="file-preview__info">
          <p class="file-preview__name">{{ importFile.name }}</p>
          <p class="file-preview__size">{{ fileSizeLabel }}</p>
        </div>
        <button class="file-preview__remove" @click="removeFile" title="Rimuovi">✕</button>
      </div>

      <div v-if="importSuccess" class="alert-inline alert-inline--success">
          {{ importSuccess }}
      </div>
      <div v-if="importError" class="alert-inline alert-inline--error">
          {{ importError }}
      </div>

      <div class="modal__footer">
        <button class="btn btn--outline" @click="closeModal" :disabled="isImporting">
          Annulla
        </button>
        <button
          class="btn btn--primary"
          @click="submitImport"
          :disabled="!importFile || isImporting">
          <span v-if="isImporting" class="spinner"></span>
          {{ isImporting ? 'Importazione…' : 'Importa' }}
        </button>
      </div>
    </div>
  </div>
</template>