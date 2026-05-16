<!-- AssetEditWidget.vue
  Widget smart di dominio: orchestra la modifica di un Asset.
-->

<script setup>
import { useFormModel } from '@/shared/useFormModel.js'
import { assetFormFields } from '@/shared/assetFormFields.js'
import AssetForm from '@/components/AssetForm.vue'
import AsyncButton from '@/components/AsyncButton.vue'

const props = defineProps({
  submitUrl: {
    type: String,
    required: true,
  },
  cancelUrl: {
    type: String,
    required: true,
  },
  initialName: {
    type: String,
    required: true,
  },
  initialAssetType: {
    type: String,
    required: true,
  },
  initialDescription: {
    type: String,
    default: '',
  },
  redirectUrl:{
    type: String,
    required: true,
  },
})

const { fields, errors, validate, setServerErrors } = useFormModel(assetFormFields)

fields.name = props.initialName
fields.assetType = props.initialAssetType
fields.description = props.initialDescription

async function updateAsset() {
  if (!validate()) {
    throw new Error('Correggi gli errori nel form.')
  }

  const response = await fetch(props.submitUrl, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: fields.name.trim(),
      asset_type: fields.assetType,
      description: fields.description.trim(),
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
    <AssetForm :fields="fields" :errors="errors">
      <template #actions>
        <AsyncButton
          :action="updateAsset"
          label="Salva Modifiche"
          loading-label="Salvataggio..."
          button-class="btn btn--primary"
          @success="onSuccess"
        />
        <a :href="cancelUrl" class="btn btn--outline">Annulla</a>
      </template>
    </AssetForm>
  </form>
</template>