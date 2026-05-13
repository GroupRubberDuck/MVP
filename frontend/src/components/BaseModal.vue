<!-- BaseModal.vue
  Componente dumb generico: guscio modale riutilizzabile.

  Responsabilità (SRP):
    - Renderizzare un overlay con contenuto centrato
    - Chiudere il modale alla pressione di Escape
    - Chiudere il modale al click sull'overlay (fuori dal contenuto)

  NON è responsabile di:
    - Contenuto del modale (delegato allo slot)
    - Decidere quando aprirsi/chiudersi (controllato dal padre con v-if)
    - Bottoni o azioni (li mette il widget smart nello slot)
    - Stile visivo (delegato al widget che lo usa)
-->

<script setup>
import { onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['close'])

function onKeydown(event) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

function onOverlayClick(event) {
  // Emette close solo se il click è sull'overlay stesso,
  // non su un elemento figlio (il contenuto del modale)
  if (event.target === event.currentTarget) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div
    class="base-modal-overlay"
    @click="onOverlayClick"
  >
    <div class="base-modal-content">
      <slot></slot>
    </div>
  </div>
</template>