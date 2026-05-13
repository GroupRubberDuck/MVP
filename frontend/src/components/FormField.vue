<!-- FormField.vue
  Componente dumb generico: wrapper per un campo di form.

  Responsabilità (SRP):
    - Mostrare una label associata all'input
    - Mostrare un eventuale messaggio d'errore

  NON è responsabile di:
    - Tipo di input (delegato allo slot)
    - Validazione (delegata al composable)
    - Stile (delegato al widget/CSS esterno)
-->

<script setup>
defineProps({
  /** Testo della label */
  label: {
    type: String,
    required: true,
  },
  /** Messaggio d'errore, null se il campo è valido */
  error: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <div class="form-field">
    <label>
      {{ label }}
      <slot></slot>
    </label>
    <span v-if="error" class="form-field-error">
      {{ error }}
    </span>
  </div>
</template>