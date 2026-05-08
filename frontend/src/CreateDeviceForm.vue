<template>
  <div class="card" style="max-width: 640px; margin: 0 auto;">
    <div class="card__header">
      <h2 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #111827;">Informazioni Dispositivo</h2>
    </div>

    <div v-if="errorMessage" class="alert--error">
      {{ errorMessage }}
    </div>

    <p class="section-label">Informazioni Generali</p>

    <div class="form-group">
      <label class="form-label" for="device-name">Nome Dispositivo *</label>
      <input
        id="device-name"
        v-model="form.device_name"
        class="form-input"
        :class="{ 'form-input--error': errors.device_name }"
        type="text"
        maxlength="64"
        placeholder="es. Router principale"
      />
      <span class="form-hint">Compreso tra 1 e 64 caratteri ({{ form.device_name.length }}/64)</span>
      <span v-if="errors.device_name" class="form-error">{{ errors.device_name }}</span>
    </div>

    <div class="form-group">
      <label class="form-label" for="device-os">Sistema Operativo *</label>
      <input
        id="device-os"
        v-model="form.device_os"
        class="form-input"
        :class="{ 'form-input--error': errors.device_os }"
        type="text"
        maxlength="64"
        placeholder="es. Linux, Windows"
      />
      <span class="form-hint">Compreso tra 1 e 64 caratteri ({{ form.device_os.length }}/64)</span>
      <span v-if="errors.device_os" class="form-error">{{ errors.device_os }}</span>
    </div>

    <p class="section-label">Descrizione e Funzionalità</p>

    <div class="form-group">
      <label class="form-label" for="device-description">Descrizione</label>
      <textarea
        id="device-description"
        v-model="form.device_description"
        class="form-input"
        maxlength="512"
        placeholder="Aggiungi dettagli sul dispositivo..."
        rows="4"
        style="resize: vertical; font-family: inherit;"
      ></textarea>
      <span class="form-hint">Facoltativo – max 512 caratteri ({{ form.device_description.length }}/512)</span>
    </div>

    <div class="form-actions">
      <button 
        :disabled="isSubmitting" 
        @click="submit"
        style="padding: 10px 16px; font-size: 0.875rem; font-weight: 500; border-radius: 6px; cursor: pointer; border: none; background-color: #4f46e5; color: white;"
      >
        {{ isSubmitting ? 'Salvataggio...' : 'Crea Dispositivo' }}
      </button>
      
      <a 
        href="/devices"
        style="padding: 10px 16px; font-size: 0.875rem; font-weight: 500; border-radius: 6px; cursor: pointer; border: 1px solid #d1d5db; background-color: transparent; color: #374151; text-decoration: none;"
      >
        Annulla
      </a>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const form = reactive({
  device_name: '',
  device_os: '',
  device_description: ''
})

const errors = reactive({
  device_name: '',
  device_os: ''
})

const isSubmitting = ref(false)
const errorMessage = ref('')

function validate() {
  errors.device_name = ''
  errors.device_os = ''
  let valid = true

  if (form.device_name.trim().length < 1 || form.device_name.trim().length > 64) {
    errors.device_name = 'Il nome deve essere compreso tra 1 e 64 caratteri.'
    valid = false
  }

  if (form.device_os.trim().length < 1 || form.device_os.trim().length > 64) {
    errors.device_os = 'Il sistema operativo deve essere tra 1 e 64 caratteri.'
    valid = false
  }

  return valid
}

async function submit() {
  errorMessage.value = ''
  if (!validate()) return

  isSubmitting.value = true
  try {
    const response = await fetch('/devices', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_name: form.device_name.trim(),
        device_os: form.device_os.trim(),
        // 1. CORREZIONE: Invia sempre stringa, non null
        device_description: form.device_description.trim(),
        // 2. CORREZIONE: ID standard fittizio ma formalmente corretto per MongoDB
        standard_id: "60b9c8d7e6f5a4b3c2d1e0f9" 
      })
    })

    if (response.status === 201) {
      const data = await response.json()
      window.location.href = `/devices/${data.device_id}`
    } else {
      const data = await response.json().catch(() => ({}))
      errorMessage.value = data.error || 'Errore durante la creazione del dispositivo.'
    }
  } catch {
    errorMessage.value = 'Errore di rete. Controlla la connessione.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  font-family: 'Segoe UI', system-ui, sans-serif;
}
.card__header {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 16px;
  margin-bottom: 24px;
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
.alert--error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #f87171;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
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

.form-input--error {
  border-color: #ef4444;
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
  gap: 10px;
  margin-top: 24px;
}
</style>