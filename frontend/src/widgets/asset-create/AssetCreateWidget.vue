<!-- AssetCreateWidget.vue
  Widget smart di dominio: orchestra la creazione di un Asset.
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
  redirectUrl:{
        type: String,
        required:true,
  }
})

const { fields, errors, validate, setServerErrors } = useFormModel(assetFormFields)

async function createAsset() {
  if (!validate()) {
    throw new Error('Correggi gli errori nel form.')
  }

  const response = await fetch(props.submitUrl, {
    method: 'POST',
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
    throw new Error(data.error || 'Errore durante la creazione.')
  }

  return await response.json()
}

function onSuccess(data) {
  window.location.href = props.redirectUrl.replace("__ASSET_ID__",data.asset_id)
}
</script>

<template>
<div class="card" style="max-width: 600px; margin: 0 auto; margin-top: 20px;">
    <div class="card__header">
      <h2 class="card__title">Aggiungi Nuovo Asset</h2>
    </div>
    <div class="card__body">
  <form @submit.prevent>
    <AssetForm :fields="fields" :errors="errors">
      <template #actions>
        <AsyncButton
          :action="createAsset"
          label="Crea Asset"
          loading-label="Salvataggio..."
          button-class="btn btn--primary"
          @success="onSuccess"
        />
        <a :href="cancelUrl" class="btn btn--outline">Annulla</a>
      </template>
    </AssetForm>
  </form>
</div>

  </div>
</template>