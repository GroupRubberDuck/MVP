// shared/deviceFormFields.js
//
// Definizione dei campi del form Device.
// Condivisa tra DeviceCreateWidget e DeviceEditWidget.
//
// Responsabilità (SRP):
//   - Definire nomi dei campi, valori iniziali e regole di validazione
//
// NON è responsabile di:
//   - Logica del form (delegata a useFormModel)
//   - Orchestrazione create/edit (delegata ai widget)

export const deviceFormFields = {
  deviceName: {
    initialValue: '',
    rules: [
      v => v.trim() === '' ? 'Il nome è obbligatorio.' : null,
      v => v.length > 64 ? 'Massimo 64 caratteri.' : null,
    ],
  },
  deviceOs: {
    initialValue: '',
    rules: [
      v => v.trim() === '' ? 'Il sistema operativo è obbligatorio.' : null,
      v => v.length > 64 ? 'Massimo 64 caratteri.' : null,
    ],
  },
  deviceDescription: {
    initialValue: '',
    rules: [
      v => v.length > 512 ? 'Massimo 512 caratteri.' : null,
    ],
  },
}