<script setup>
import { ref } from 'vue'
import AsyncButton from '@/components/AsyncButton.vue'
import Toast from '@/components/Toast.vue'

const props = defineProps({
  commitUrl: {
    type: String,
    required: true,
  },
})

const toastMessage = ref('')

async function commitSession() {
  toastMessage.value = ''

  const response = await fetch(props.commitUrl, { method: 'POST' })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || 'Errore durante il salvataggio.')
  }
}

function onSuccess() {
  toastMessage.value = 'Sessione salvata con successo.'
}

function clearToast() {
  toastMessage.value = ''
}
</script>

<template>
  <div>
    <AsyncButton
      :action="commitSession"
      label="Salva Sessione"
      loading-label="Salvataggio..."
      button-class="btn btn--outline"
      @success="onSuccess"
    />
    <Toast
      v-if="toastMessage"
      :message="toastMessage"
      :duration="3000"
      @close="clearToast"
    />
  </div>
</template>