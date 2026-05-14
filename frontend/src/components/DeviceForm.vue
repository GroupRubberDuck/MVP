<!-- DeviceForm.vue
  Componente dumb: template del form Device.
  
  Responsabilità (SRP):
    - Renderizzare i campi del form Device
    - Binding bidirezionale con i dati ricevuti dal padre
  
  NON è responsabile di:
    - Validazione (gestita dal composable nel widget)
    - Submit (gestito dal widget tramite slot per i bottoni)
    - Sapere se è in modalità create o edit
-->

<script setup>
import FormField from './FormField.vue'

defineProps({
  fields: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <div>
    <p class="section-label">Informazioni Generali</p>

    <FormField label="Nome Dispositivo *" :error="errors.deviceName">
      <input
        v-model="fields.deviceName"
        type="text"
        maxlength="64"
        placeholder="es. Router principale"
        class="form-input"
        :class="{ 'form-input-error': errors.deviceName }"
      />
      <span class="form-hint">
        Max 64 caratteri ({{ fields.deviceName.length }}/64)
      </span>
    </FormField>

    <FormField label="Sistema Operativo *" :error="errors.deviceOs">
      <input
        v-model="fields.deviceOs"
        type="text"
        maxlength="64"
        placeholder="es. Linux, Windows"
        class="form-input"
        :class="{ 'form-input-error': errors.deviceOs }"
      />
      <span class="form-hint">
        Max 64 caratteri ({{ fields.deviceOs.length }}/64)
      </span>
    </FormField>

    <p class="section-label">Descrizione e Funzionalità</p>

    <FormField label="Descrizione" :error="errors.deviceDescription">
      <textarea
        v-model="fields.deviceDescription"
        maxlength="512"
        placeholder="Aggiungi dettagli sul dispositivo..."
        rows="4"
        class="form-input form-textarea"
      ></textarea>
      <span class="form-hint">
        Facoltativo – max 512 caratteri ({{ fields.deviceDescription.length }}/512)
      </span>
    </FormField>

    <div class="form-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>