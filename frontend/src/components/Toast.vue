<!-- Toast.vue
  Componente dumb generico: mostra un messaggio temporaneo
  che scompare automaticamente dopo un timeout.

  Responsabilità (SRP):
    - Mostrare un messaggio
    - Scomparire dopo un tempo definito
    - Emettere un evento alla chiusura (per cleanup nel padre)

  NON è responsabile di:
    - Decidere quando apparire (controllato dal padre con v-if)
    - Contenuto o tipo del messaggio (ricevuto via props)
    - Posizionamento visivo (delegato al CSS esterno)
-->

<script setup>
import { onMounted } from 'vue'

const props = defineProps({
  /** Testo del messaggio */
  message: {
    type: String,
    required: true,
  },
  /** Durata in millisecondi prima della chiusura automatica */
  duration: {
    type: Number,
    default: 3000,
  },
})

const emit = defineEmits(['close'])

onMounted(() => {
  setTimeout(() => {
    emit('close')
  }, props.duration)
})
</script>

<template>
  <div class="toast">
    {{ message }}
  </div>
</template>