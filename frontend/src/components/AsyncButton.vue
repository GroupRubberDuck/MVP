<!-- AsyncButton.vue
  Componente dumb generico: esegue una funzione asincrona al click,
  gestendo lo stato di loading e la cattura degli errori.

  Responsabilità (SRP):
    - Ricevere una funzione asincrona dall'esterno
    - Gestire lo stato UI (loading, errore)
    - Esporre feedback visivo minimale (disabled durante loading)

  NON è responsabile di:
    - Sapere cosa fa la funzione asincrona (dominio)
    - Decidere cosa succede dopo il successo (redirect, rimozione DOM, ecc.)
    - Stile visivo (delegato al widget che lo usa)
-->

<script setup>
import { ref } from 'vue'

const props = defineProps({
  /** Funzione asincrona da eseguire al click. Deve restituire una Promise. */
  action: {
    type: Function,
    required: true,
  },
  /** Testo del bottone nello stato di default */
  label: {
    type: String,
    default: 'Conferma',
  },
  /** Testo del bottone durante il caricamento */
  loadingLabel: {
    type: String,
    default: 'Caricamento...',
  },
  buttonClass: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['success', 'error'])

const isLoading = ref(false)
const error = ref(null)

async function handleClick() {
  if (isLoading.value) return

  isLoading.value = true
  error.value = null

  try {
    const result = await props.action()
    emit('success', result)
  } catch (err) {
    error.value = err.message ?? 'Errore sconosciuto'
    emit('error', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <button
      :disabled="isLoading"
      @click="handleClick"
      :class="buttonClass"
    >
      {{ isLoading ? loadingLabel : label }}
    </button>
    <span v-if="error" class="error-text">{{ error }}</span>
  </div>
</template>