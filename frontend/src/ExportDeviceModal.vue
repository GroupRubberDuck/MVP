<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="closeModal">
    <div class="card export-card">
      <div class="card__header">
        <h2 class="title-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Esporta Dispositivo
        </h2>
      </div>

      <div class="export-body">
        <p>Seleziona il formato per esportare i dati di <strong>{{ deviceName }}</strong>:</p>
        
        <select v-model="exportFormat" class="form-input format-select">
          <option value="json">JSON (.json)</option>
          <option value="xml">XML (.xml)</option>
          <option value="csv">CSV (.csv)</option>
        </select>
      </div>

      <div class="form-actions mt-4">
        <button class="btn btn--primary" @click="downloadFile">
          Scarica File
        </button>
        <button class="btn btn--outline" @click="closeModal">Annulla</button>
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

onMounted(() => {
  // Funzione globale per aprire il pop-up
  window.openExportModal = (id, name) => {
    deviceId.value = id;
    deviceName.value = name;
    exportFormat.value = 'json'; 
    isVisible.value = true;
  }
})

function closeModal() {
  isVisible.value = false;
}

function downloadFile() {
  // Costruiamo l'URL puntando alle API del backend
  const exportUrl = `/api/devices/${deviceId.value}/export?extension=${exportFormat.value}`;
  
  const link = document.createElement('a');
  link.href = exportUrl;
  
  // Suggerisce al browser di scaricare il file invece di aprirlo
  link.setAttribute('download', ''); 
  
  document.body.appendChild(link);
  link.click();
  
  // Pulizia
  document.body.removeChild(link);
  closeModal(); 
}
</script>

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