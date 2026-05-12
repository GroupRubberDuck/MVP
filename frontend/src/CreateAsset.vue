<template>
  <div class="card" style="max-width: 600px; margin: 0 auto; margin-top: 20px;">
    <div class="card__header">
      <h2 class="card__title">{{ isEditing ? 'Modifica Asset' : 'Aggiungi Nuovo Asset' }}</h2>
    </div>
    
    <div class="card__body">
      <form @submit.prevent="submitForm" novalidate>
        <!-- Nome Asset -->
        <div class="form-group" style="margin-bottom: 15px;">
          <label for="asset-name">Nome Asset *</label>
          <input 
            type="text" 
            id="asset-name" 
            v-model="formData.name" 
            class="form-control" 
            :class="{'is-invalid': errors.name}"
            style="width: 100%; padding: 8px;" 
            placeholder="Esempio: Firewall Ufficio"
          />
          <span v-if="errors.name" style="color: #dc3545; font-size: 0.85em; display: block; margin-top: 5px;">
            {{ errors.name }}
          </span>
        </div>

        <!-- Tipologia -->
        <div class="form-group" style="margin-bottom: 15px;">
          <label for="asset-type">Tipologia *</label>
          <select 
            id="asset-type" 
            v-model="formData.asset_type" 
            class="form-control" 
            :class="{'is-invalid': errors.asset_type}"
            style="width: 100%; padding: 8px;"
          >
            <option value="" disabled>Seleziona una tipologia</option>
            <option value="Security">Security</option>
            <option value="Network">Network</option>
          </select>
          <span v-if="errors.asset_type" style="color: #dc3545; font-size: 0.85em; display: block; margin-top: 5px;">
            {{ errors.asset_type }}
          </span>
        </div>

        <!-- Descrizione -->
        <div class="form-group" style="margin-bottom: 20px;">
          <label for="asset-desc">Descrizione</label>
          <textarea 
            id="asset-desc" 
            v-model="formData.description" 
            class="form-control" 
            rows="4" 
            style="width: 100%; padding: 8px;"
            placeholder="Dettagli opzionali sull'asset..."
          ></textarea>
        </div>

        <div class="form-actions" style="display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" class="btn btn--outline" @click="goBack">Annulla</button>
          <button type="submit" class="btn btn--primary" :disabled="isLoading">
            {{ isLoading ? 'Salvataggio...' : 'Salva Asset' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const isEditing = ref(false);
const isLoading = ref(false);
const sessionId = ref('');
const deviceId = ref('');
const assetId = ref('');

const formData = ref({
  name: '',
  asset_type: '', 
  description: ''
});

const errors = ref({
  name: null,
  asset_type: null
});

onMounted(() => {
  const el = document.getElementById('create-asset-app');
  if (el) {
    // Recupero ID fondamentali
    sessionId.value = el.dataset.sessionId;
    deviceId.value = el.dataset.deviceId;
    assetId.value = el.dataset.assetId;
    
    // Se c'è un assetId, stiamo modificando un asset esistente
    if (assetId.value) {
      isEditing.value = true;
      formData.value.name = el.dataset.assetName || '';
      formData.value.asset_type = el.dataset.assetType || '';
      formData.value.description = el.dataset.assetDescription || '';
    }
  }
});

const validateForm = () => {
  let isValid = true;
  errors.value.name = null;
  errors.value.asset_type = null;

  if (!formData.value.name || !formData.value.name.trim()) {
    errors.value.name = "Il nome dell'asset è obbligatorio.";
    isValid = false;
  }

  if (!formData.value.asset_type) {
    errors.value.asset_type = "Seleziona una tipologia obbligatoria.";
    isValid = false;
  }

  return isValid;
};

const goBack = () => {
  window.history.back();
};

const submitForm = async () => {
  if (!validateForm()) return;
  
  // Controllo critico: se mancano gli ID, il backend darà 404 o 500
  if (!sessionId.value || !deviceId.value) {
    return alert("Errore tecnico: ID sessione o dispositivo non trovati nel template.");
  }

  isLoading.value = true;
  
  // Costruzione URL dinamico per API Flask
  const baseUrl = `/api/sessions/${sessionId.value}/devices/${deviceId.value}/assets`;
  const url = isEditing.value ? `${baseUrl}/${assetId.value}` : baseUrl;
  const method = isEditing.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: formData.value.name,
        asset_type: formData.value.asset_type,
        description: formData.value.description
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || "Errore durante la comunicazione con il server.");
    }

    alert(isEditing.value ? "Asset aggiornato correttamente!" : "Nuovo asset creato!");
    
    // Gestione blocco navigazione dashboard
    if (window.dashboardAction && window.dashboardAction.allowExit) {
        window.dashboardAction.allowExit();
    }
    
    // Reindirizzamento alla dashboard del dispositivo
    window.location.href = `/sessions/${sessionId.value}/devices/${deviceId.value}`;

  } catch (error) {
    alert("Attenzione: " + error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>