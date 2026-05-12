<template>
  <div class="create-device-container">
    
    <div class="page-header">
      <div class="page-header__text">
        <h1>{{ isEditMode ? 'Modifica Dispositivo' : 'Nuovo Dispositivo' }}</h1>
        <p>
          {{ isEditMode 
            ? 'Aggiorna le informazioni del dispositivo nel sistema.' 
            : 'Compila i campi per registrare un nuovo dispositivo nel sistema.' 
          }}
        </p>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2>{{ isEditMode ? 'Modifica Dispositivo' : 'Informazioni Dispositivo' }}</h2>
      </div>
 
      <form @submit.prevent="submit" novalidate>
        
        <div v-if="errorMessage" class="alert-error">
          {{ errorMessage }}
        </div>

        <p class="section-label">Informazioni Generali</p>

        <div class="form-group">
          <label class="form-label" for="device-name">Nome Dispositivo *</label>
          <input
            id="device-name"
            v-model="form.device_name"
            class="form-input"
            :class="{ 'form-input-error': errors.device_name }"
            type="text"
            maxlength="64"
            placeholder="es. Router principale"
          />
          <span class="form-hint">
            Max 64 caratteri ({{ form.device_name.length }}/64)
          </span>
          <span v-if="errors.device_name" class="form-error">
            {{ errors.device_name }}
          </span>
        </div>

        <div class="form-group">
          <label class="form-label" for="device-os">Sistema Operativo *</label>
          <input
            id="device-os"
            v-model="form.device_os"
            class="form-input"
            :class="{ 'form-input-error': errors.device_os }"
            type="text"
            maxlength="64"
            placeholder="es. Linux, Windows"
          />
          <span v-if="errors.device_os" class="form-error">
            {{ errors.device_os }}
          </span>
        </div>

        <p class="section-label">Descrizione e Funzionalità</p>

        <div class="form-group">
          <label class="form-label" for="device-description">Descrizione</label>
          <textarea
            id="device-description"
            v-model="form.device_description"
            class="form-input form-textarea"
            maxlength="512"
            placeholder="Aggiungi dettagli sul dispositivo..."
            rows="4"
          ></textarea>
          <span class="form-hint">
            Facoltativo – max 512 caratteri ({{ form.device_description.length }}/512)
          </span>
        </div>

        <div class="form-actions">
          <button 
            type="submit"
            class="btn btn--primary"
            :disabled="isSubmitting" 
          >
            {{ isSubmitting ? 'Salvataggio...' : (isEditMode ? 'Salva Modifiche' : 'Crea Dispositivo') }}
          </button>
          
          <a :href="isEditMode ? `/devices/${deviceId}` : '/devices'" class="btn btn--outline">
            Annulla
          </a>
        </div>
        
      </form>
    </div>
  </div>
</template>


<script setup>
import { DEFAULT_STANDARD_ID } from './constants.js'
import { reactive, ref, computed, onMounted } from 'vue'

const form = reactive({
  device_name: '',
  device_os: '',
  device_description: '',
  standard_id: DEFAULT_STANDARD_ID
})

const errors = reactive({
  device_name: '',
  device_os: ''
})

const isSubmitting = ref(false)
const errorMessage = ref('')

// --- GESTIONE MODALITÀ MODIFICA ---
const deviceId = ref(null)
const isEditMode = computed(() => deviceId.value !== null)

onMounted(() => {
  // Cerca un ID tra /devices/ e /edit
  const match = window.location.pathname.match(/\/devices\/([^\/]+)\/edit/);
  
  if (match && match[1]) {
    deviceId.value = match[1];
    loadDeviceData(); 
  }
})

async function loadDeviceData() {
  try {
    // Chiediamo al server i dati del dispositivo (ritornati come JSON)
    const response = await fetch(`/api/devices/${deviceId.value}`); 
    
    if (response.ok) {
      const data = await response.json();
      form.device_name = data.name || '';
      form.device_os = data.os || '';
      form.device_description = data.description || '';
      
      if (data.standard_id) {
        form.standard_id = data.standard_id;
      }
    } else {
      errorMessage.value = "Impossibile recuperare i dati del dispositivo.";
    }
  } catch (error) {
    errorMessage.value = "Errore di rete durante il caricamento.";
  }
}

function validate() {
  errors.device_name = ''
  errors.device_os = ''
  let valid = true

  if (!form.device_name.trim()) {
    errors.device_name = 'Il nome è obbligatorio.'
    valid = false
  }

  if (!form.device_os.trim()) {
    errors.device_os = 'Il sistema operativo è obbligatorio.'
    valid = false
  }

  return valid
}

async function submit() {
  errorMessage.value = ''
  if (!validate()) return

  isSubmitting.value = true
  try {
    // Sceglie metodo e URL in base alla modalità (Crea = POST, Modifica = PUT)
    const url = isEditMode.value ? `/devices/${deviceId.value}` : '/devices'
    const method = isEditMode.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_name: form.device_name.trim(),
        device_os: form.device_os.trim(),
        device_description: form.device_description.trim(),
        standard_id: form.standard_id
      })
    })

    if (response.status === 201 || response.status === 204 || response.status === 200) {
      // Se è una creazione, prendiamo l'ID nuovo. Se è modifica, usiamo l'ID corrente.
      let targetId = deviceId.value
      if (!isEditMode.value) {
        const data = await response.json()
        targetId = data.device_id
      }
      window.location.href = `/devices/${targetId}`
    } else {
      const data = await response.json().catch(() => ({}))
      errorMessage.value = data.error || 'Errore durante il salvataggio del dispositivo.'
    }
  } catch (error) {
    errorMessage.value = 'Errore di rete. Impossibile contattare il server.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.card {
  max-width: 640px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

.section-label {
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  color: #6b7280;
  margin-top: 0;
  margin-bottom: 16px;
  letter-spacing: 0.05em;
}

.alert-error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #f87171;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input-error {
  border-color: #ef4444;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
  min-height: 100px;
}

.form-hint {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 6px;
}

.form-error {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #ef4444;
  margin-top: 6px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
</style>