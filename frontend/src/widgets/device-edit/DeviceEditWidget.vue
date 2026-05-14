<!-- DeviceEditWidget.vue -->

<script setup>
import { useFormModel } from '../../shared/useFormModel.js'
import { deviceFormFields } from '../../shared/deviceFormFields.js'
import DeviceForm from '../../components/DeviceForm.vue'
import AsyncButton from '../../components/AsyncButton.vue'

const props = defineProps({
  submitUrl: {
    type: String,
    required: true,
  },
  cancelUrl: {
    type: String,
    required: true,
  },

  defaultStandardId: {
    type: String,
    required: true,
  },
  initialName: {
    type: String,
    required: true,
  },
  initialOs: {
    type: String,
    required: true,
  },
  initialDescription: {
    type: String,
    default: '',
  },
})

const { fields, errors, validate, setServerErrors } = useFormModel(deviceFormFields)

// Popola i campi con i dati iniettati dal server
fields.deviceName = props.initialName
fields.deviceOs = props.initialOs
fields.deviceDescription = props.initialDescription

async function updateDevice() {
  if (!validate()) {
    throw new Error('Correggi gli errori nel form.')
  }

  const response = await fetch(props.submitUrl, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      device_name: fields.deviceName.trim(),
      device_os: fields.deviceOs.trim(),
      device_description: fields.deviceDescription.trim(),
      standard_id: props.defaultStandardId,
    }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    if (data.errors) {
      setServerErrors(data.errors)
    }
    throw new Error(data.error || 'Errore durante il salvataggio.')
  }

  return await response.json()
}

function onSuccess(data) {
  window.location.href = data.redirect_url
}
</script>

<template>
  <form @submit.prevent>
    <DeviceForm :fields="fields" :errors="errors">
      <template #actions>
        <AsyncButton
          :action="updateDevice"
          label="Salva Modifiche"
          loading-label="Salvataggio..."
          @success="onSuccess"
        />
        <a :href="cancelUrl" class="btn btn--outline">Annulla</a>
      </template>
    </DeviceForm>
  </form>
</template>