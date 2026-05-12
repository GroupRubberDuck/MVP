<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="closeModal">
    <div class="card delete-card">

      <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

      <p class="section-label">Elimina dispositivo</p>
      <p class="info-text">
        Stai per eliminare <strong>{{ deviceName }}</strong>. Questa operazione è irreversibile.
      </p>

      <div class="export-row">
        <span class="info-text">Esporta una copia prima di eliminare:</span>
        <div class="export-controls">
          <select v-model="exportFormat" class="form-input select-format">
            <option value="json">JSON</option>
            <option value="xml">XML</option>
            <option value="csv">CSV</option>
          </select>
          <button @click="exportDevice" class="btn btn--outline" :disabled="isDeleting">Esporta</button>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn--danger" :disabled="isDeleting" @click="deleteDevice">
          {{ isDeleting ? 'Eliminazione...' : 'Elimina' }}
        </button>
        <button class="btn btn--outline" @click="closeModal" :disabled="isDeleting">Annulla</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isVisible = ref(false)
const deviceId = ref('')
const deviceName = ref('')
const exportFormat = ref('json') 
const isDeleting = ref(false)
const errorMessage = ref('')

onMounted(() => {
  window.openDeleteModal = (id, name) => {
    deviceId.value = id
    deviceName.value = name
    errorMessage.value = ''
    exportFormat.value = 'json' 
    isDeleting.value = false
    isVisible.value = true
  }
})

function closeModal() {
  if (!isDeleting.value) {
    isVisible.value = false
  }
}

function exportDevice() {
  // Nota l'aggiunta di /api se il tuo controller lo richiede
  const exportUrl = `/api/devices/${deviceId.value}/export?extension=${exportFormat.value}`;
  
  // Crea link invisibile, clicca e rimuovi
  const link = document.createElement('a');
  link.href = exportUrl;
  link.setAttribute('download', ''); 
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function deleteDevice() {
  isDeleting.value = true
  errorMessage.value = ''
  try {
    
    const response = await fetch(`/devices/${deviceId.value}`, { method: 'DELETE' })
    if (response.ok) {
      // Reindirizza alla lista dopo l'eliminazione con successo
      window.location.href = '/devices';
    } else {
      const data = await response.json().catch(() => ({}))
      errorMessage.value = data.error || "Errore durante l'eliminazione."
    }
  } catch {
    errorMessage.value = 'Errore di rete.'
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.delete-card {
  max-width: 500px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 2rem;
}

.delete-title {
  font-size: 22px;
  font-weight: 500;
  color: #c0392b;
  margin: 0;
}

.export-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.export-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.select-format {
  width: 130px;
  font-size: 15px;
  padding: 8px 12px;
}

.form-actions {
  display: flex;
  gap: 16px;  /* era 8px */
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  border: 0.5px solid #fca5a5;
}
</style>