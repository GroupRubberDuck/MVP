// shared/useFormModel.js
//
// Composable generico per la gestione di form.
//
// Responsabilità (SRP):
//   - Mantenere lo stato reattivo dei campi
//   - Eseguire validazione client-side campo per campo
//   - Integrare errori server-side
//   - Esporre lo stato di validità complessivo
//
// NON è responsabile di:
//   - Rendering (è logica pura, nessun template)
//   - Chiamate HTTP (le fa il widget)
//   - Regole di validazione specifiche del dominio (le riceve in input)

import { reactive, computed } from 'vue'

/**
 * @param {Object} fieldDefinitions - Definizione dei campi del form
 *   Ogni chiave è il nome del campo, il valore è un oggetto con:
 *   - initialValue: valore iniziale
 *   - rules: array di funzioni di validazione
 *     Ogni regola: (value) => string | null
 *     Restituisce un messaggio d'errore o null se valido
 *
 * @example
 *   const { fields, errors, isValid, validate, setServerErrors, reset } = useFormModel({
 *     name: {
 *       initialValue: '',
 *       rules: [
 *         v => v.trim() === '' ? 'Il nome è obbligatorio' : null,
 *       ],
 *     },
 *     os: {
 *       initialValue: '',
 *       rules: [],
 *     },
 *   })
 */
export function useFormModel(fieldDefinitions) {
  const fieldNames = Object.keys(fieldDefinitions)

  // Stato reattivo: valori dei campi
  const fields = reactive(
    Object.fromEntries(
      fieldNames.map(name => [name, fieldDefinitions[name].initialValue])
    )
  )

  // Stato reattivo: errori per campo (stringa o null)
  const errors = reactive(
    Object.fromEntries(
      fieldNames.map(name => [name, null])
    )
  )

  /**
   * Valida un singolo campo.
   * Esegue le regole in ordine, si ferma al primo errore.
   */
  function validateField(name) {
    const rules = fieldDefinitions[name].rules || []
    for (const rule of rules) {
      const error = rule(fields[name])
      if (error) {
        errors[name] = error
        return false
      }
    }
    errors[name] = null
    return true
  }

  /**
   * Valida tutti i campi.
   * @returns {boolean} true se tutti i campi sono validi
   */
  function validate() {
    let allValid = true
    for (const name of fieldNames) {
      if (!validateField(name)) {
        allValid = false
      }
    }
    return allValid
  }

  /**
   * Imposta errori ricevuti dal server.
   * @param {Object} serverErrors - { nomeCampo: 'messaggio errore', ... }
   */
  function setServerErrors(serverErrors) {
    for (const [name, message] of Object.entries(serverErrors)) {
      if (name in errors) {
        errors[name] = message
      }
    }
  }

  /** Resetta campi e errori ai valori iniziali */
  function reset() {
    for (const name of fieldNames) {
      fields[name] = fieldDefinitions[name].initialValue
      errors[name] = null
    }
  }

  const isValid = computed(() =>
    fieldNames.every(name => errors[name] === null)
  )

  return {
    fields,
    errors,
    isValid,
    validate,
    validateField,
    setServerErrors,
    reset,
  }
}