<!-- AssetForm.vue
  Componente dumb: template del form Asset.

  Responsabilità (SRP):
    - Renderizzare i campi del form Asset
    - Binding bidirezionale con i dati ricevuti dal padre

  NON è responsabile di:
    - Validazione (gestita dal composable nel widget)
    - Submit (gestito dal widget tramite slot per i bottoni)
    - Sapere se è in modalità create o edit
-->

<script setup>
import FormField from '@/components/FormField.vue'

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
    <FormField label="Nome Asset *" :error="errors.name">
      <input
        v-model="fields.name"
        type="text"
        placeholder="Esempio: Firewall Ufficio"
        class="form-input"
      />
    </FormField>

<FormField label="Tipologia *" :error="errors.assetType">
  <div class="radio-group">
    <label>
      <input type="radio" v-model="fields.assetType" value="security" />
      Security
    </label>
    <label>
      <input type="radio" v-model="fields.assetType" value="network" />
      Network
    </label>
  </div>
</FormField>

    <FormField label="Descrizione" :error="errors.description">
      <textarea
        v-model="fields.description"
        rows="4"
        placeholder="Dettagli opzionali sull'asset..."
        class="form-input"
      ></textarea>
    </FormField>

    <div class="form-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>
<style>
.radio-group {
  display: flex;
  gap: 16px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}</style>