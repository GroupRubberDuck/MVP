<script setup>
import { ref } from 'vue'

const props = defineProps({
  deviceId:   { type: String, required: true },
  deviceName: { type: String, required: true },
})

const emit = defineEmits(['close', 'deleted'])

const selectedFormat = ref('json')
const isExporting    = ref(false)
const exportDone     = ref(false)
const exportError    = ref('')
const isDeleting     = ref(false)

function closeModal() {
  if (!isDeleting.value) emit('close')
}

async function exportDevice() {
  isExporting.value = true
  exportDone.value  = false
  exportError.value = ''
  try {
    const res = await fetch(
      `/api/devices/${props.deviceId}/export?extension=${selectedFormat.value}`
    )
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || `Errore ${res.status}`)
    }
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `device_${props.deviceId}.${selectedFormat.value}`
    a.click()
    URL.revokeObjectURL(a.href)
    exportDone.value = true
  } catch (err) {
    exportError.value = err.message || 'Esportazione fallita.'
  } finally {
    isExporting.value = false
  }
}

async function confirmDelete() {
  isDeleting.value = true
  try {
    const res = await fetch(`/devices/${props.deviceId}`, { method: 'DELETE' })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || `Errore ${res.status}`)
    }
    emit('deleted')
  } catch (err) {
    alert(`Eliminazione fallita: ${err.message}`)
    isDeleting.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal" role="dialog" aria-modal="true">
      <h2 class="modal__title">Elimina dispositivo</h2>
      <p class="modal__body">
        Stai per eliminare il dispositivo <strong>«&nbsp;{{ deviceName }}&nbsp;»</strong>.
        <br>Questa operazione è <strong>irreversibile</strong>.<br><br>
        Vuoi esportare una copia prima di eliminarlo?
      </p>
      <div class="export-section">
        <p class="export-section__title">Esporta prima di eliminare</p>
        <div class="export-format-group">
          <button v-for="fmt in ['json','csv','xml']" :key="fmt"
                  class="export-format-btn"
                  :class="{ 'export-format-btn--active': selectedFormat === fmt }"
                  @click="selectedFormat = fmt">
            {{ fmt.toUpperCase() }}
          </button>
        </div>
        <div class="export-actions">
          <button class="btn btn--secondary btn--sm"
                  @click="exportDevice" :disabled="isExporting">
            <span v-if="isExporting" class="spinner"></span>
            {{ isExporting ? 'Esportazione…' : 'Esporta' }}
          </button>
          <span v-if="exportDone" class="alert-inline alert-inline--success">
            File scaricato
          </span>
          <span v-if="exportError" class="alert-inline alert-inline--error">
            {{ exportError }}
          </span>
        </div>
      </div>
      <div class="modal__footer">
        <button class="btn btn--outline" @click="closeModal" :disabled="isDeleting">
          Annulla
        </button>
        <button class="btn btn--danger" @click="confirmDelete" :disabled="isDeleting">
          <span v-if="isDeleting" class="spinner"></span>
          {{ isDeleting ? 'Eliminazione…' : 'Elimina definitivamente' }}
        </button>
      </div>
    </div>
  </div>
</template>