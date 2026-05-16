<!-- FileDropZone.vue
  Componente dumb generico: area di upload file con drag & drop.

  Responsabilità (SRP):
    - Mostrare l'area di drop con feedback visivo
    - Gestire drag & drop e selezione file via click
    - Validare il tipo di file accettato
    - Emettere il file selezionato al padre

  NON è responsabile di:
    - Sapere cosa fare col file (upload, parsing, ecc.)
    - Mostrare errori di business (delegato al widget)
    - Stile visivo (delegato al widget)
-->

<script setup>
import { ref } from 'vue'

const props = defineProps({
  /** Estensioni accettate, es. '.json,.xml,.csv' */
  accept: {
    type: String,
    default: '',
  },
  /** Testo mostrato quando nessun file è selezionato */
  placeholder: {
    type: String,
    default: 'Clicca per caricare o trascina il file',
  },
  /** Testo dei formati supportati */
  hint: {
    type: String,
    default: '',
  },
  /** Disabilita l'interazione */
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['select', 'error'])

const isDragging = ref(false)
const fileInput = ref(null)
const selectedFile = ref(null)

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    emit('select', file)
  }
}

function handleDrop(e) {
  isDragging.value = false
  if (props.disabled) return

  const file = e.dataTransfer.files[0]
  if (!file) return

  if (isFileAccepted(file)) {
    selectedFile.value = file
    emit('select', file)
  } else {
    emit('error', 'Formato file non valido.')
  }
}

function isFileAccepted(file) {
  if (!props.accept) return true
  const extensions = props.accept.split(',').map(ext => ext.trim().toLowerCase())
  const fileName = file.name.toLowerCase()
  return extensions.some(ext => fileName.endsWith(ext))
}

function reset() {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

function formatSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

defineExpose({ reset })
</script>

<template>
  <div
    class="file-drop-zone"
    :class="{
      'file-drop-zone--active': selectedFile,
      'file-drop-zone--dragging': isDragging,
      'file-drop-zone--disabled': disabled,
    }"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    @click="fileInput?.click()"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :disabled="disabled"
      class="file-drop-zone__input"
      @change="handleFileChange"
    />

    <div v-if="!selectedFile" class="file-drop-zone__placeholder">
      <div class="upload-icon">
              <svg v-if="!selectedFile" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
        <span>{{ placeholder }}</span>
      <span v-if="hint" class="file-drop-zone__hint">{{ hint }}</span>
    </div>

    <div v-else class="file-drop-zone__file-info">
      <strong>{{ selectedFile.name }}</strong>
      <span>({{ formatSize(selectedFile.size) }})</span>
    </div>
  </div>
</template>

<style scoped>
.file-drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  background: #f9fafb;
  transition: all 0.3s ease;
  cursor: pointer;
}

.file-drop-zone--dragging {
  border-color: #10b981;
  background: #ecfdf5;
}

.file-drop-zone--active {
  border-style: solid;
  border-color: #10b981;
  background: #f0fdf4;
}

.file-drop-zone--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-drop-zone__input {
  display: none;
}

.file-drop-zone__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-weight: 600;
}

.file-drop-zone__hint {
  font-size: 0.8rem;
  color: #9ca3af;
  font-weight: 400;
}

.file-drop-zone__file-info {
  color: #065f46;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.file-drop-zone__file-info span {
  font-size: 0.85rem;
  color: #6b7280;
}
</style>