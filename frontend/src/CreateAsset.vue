<template>
  <div class="card" style="max-width: 600px; margin: 0 auto; margin-top: 20px;">
    <div class="card__header">
      <h2 class="card__title">{{ isEditing ? 'Modifica Asset' : 'Aggiungi Nuovo Asset' }}</h2>
    </div>
    
    <div class="card__body">
      <form @submit.prevent="submitForm">
        <div class="form-group" style="margin-bottom: 15px;">
          <label for="asset-name">Nome Asset *</label>
          <input type="text" id="asset-name" v-model="formData.name" class="form-control" style="width: 100%; padding: 8px;" required />
        </div>

        <div class="form-group" style="margin-bottom: 15px;">
          <label for="asset-type">Tipologia *</label>
          <select id="asset-type" v-model="formData.type" class="form-control" style="width: 100%; padding: 8px;" required>
            <option value="" disabled>Seleziona una tipologia</option>
            <option value="Security">Security</option>
            <option value="Network">Network</option>
          </select>
        </div>

        <div class="form-group" style="margin-bottom: 20px;">
          <label for="asset-desc">Descrizione</label>
          <textarea id="asset-desc" v-model="formData.description" class="form-control" rows="4" style="width: 100%; padding: 8px;"></textarea>
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

// Referenze reattive
const isEditing = ref(false);
const isLoading = ref(false);
const sessionId = ref('');
const assetId = ref('');

const formData = ref({
  name: '',
  type: '',
  description: ''
});

onMounted(() => {
  // Leggiamo i dati passati da Jinja2 tramite gli attributi HTML
  const el = document.getElementById('create-asset-app');
  if (el) {
    sessionId.value = el.dataset.sessionId;
    assetId.value = el.dataset.assetId;
    
    // Se c'è un assetId, stiamo modificando
    if (assetId.value) {
      isEditing.value = true;
      formData.value.name = el.dataset.assetName || '';
      formData.value.type = el.dataset.assetType || '';
      formData.value.description = el.dataset.assetDescription || '';
    }
  }
});

const goBack = () => {
  // Torna alla pagina precedente (la dashboard)
  window.history.back();
};

const submitForm = async () => {
  if (!sessionId.value) return alert("Errore: Session ID mancante.");

  isLoading.value = true;
  
  // Costruiamo URL e Metodo
  const url = isEditing.value 
    ? `/sessions/${sessionId.value}/assets/${assetId.value}` 
    : `/sessions/${sessionId.value}/assets`;
    
  const method = isEditing.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || "Errore di salvataggio sul server.");
    }

    // Se va tutto bene, torniamo alla dashboard simulando un redirect
    // (Usa l'URL corretto della tua dashboard nel backend se vuoi essere più preciso)
    window.history.back(); 

  } catch (error) {
    alert(error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>