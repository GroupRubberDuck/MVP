<!-- OpenSessionWidget.vue
  Widget smart di dominio: avvia una nuova sessione di valutazione.

  Responsabilità (SRP):
    - Eseguire la chiamata POST per creare una sessione
    - Gestire il redirect alla dashboard dopo il successo
    - Mostrare errori specifici del dominio
    - Comporre AsyncButton

  NON è responsabile di:
    - Stato loading/errore del bottone (delegato ad AsyncButton)
    - Struttura degli URL (iniettati dal Livello 3)
-->

<script setup>
import { ref } from 'vue'
import AsyncButton from '@/components/AsyncButton.vue'

const props = defineProps({
  createSessionUrl: {
    type: String,
    required: true,
  },
  deviceId: {
    type: String,
    required: true,
  },
  redirectUrlTemplate: {
    type: String,
    required: true,
  },
})

const errorMessage = ref('')

async function openSession() {
  errorMessage.value = ''

  const response = await fetch(props.createSessionUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device_id: props.deviceId }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || 'Impossibile avviare la sessione.')
  }

  return await response.json()
}

function onSuccess(data) {
  window.location.href = props.redirectUrlTemplate.replace('__SESSION_ID__', data.session_id)
}
function onError(err) {
  errorMessage.value = err.message
}
</script>

<template>
  <div>
    <AsyncButton
      :action="openSession"
      label="Avvia Valutazione"
      loading-label="Avvio in corso..."
      button-class="btn btn--outline"
      @success="onSuccess"
      @error="onError"
    />
    <!-- <span class="error-text" v-if="errorMessage"  >
      {{ errorMessage }} 
    </span> -->
  </div>
</template>
<style >

.error-text{
        color: red;
        background-color: white;
padding: 8px 20px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;

  display: inline-block;
}


</style>