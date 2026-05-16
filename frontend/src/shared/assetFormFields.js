export const assetFormFields = {
  name: {
    initialValue: '',
    rules: [
      v => v.trim() === '' ? "Il nome dell'asset è obbligatorio." : null,
    ],
  },
  assetType: {
    initialValue: '',
    rules: [
      v => v === '' ? 'Seleziona una tipologia.' : null,
    ],
  },
  description: {
    initialValue: '',
    rules: [],
  },
}