import { describe, it, expect } from 'vitest';
import { useFormModel } from '../../../src/shared/useFormModel.js';

// --- useFormModel Composable -------------------------------------------------

describe('useFormModel composable', () => {
  // Prepariamo un finto schema di regole per testare la logica
  const dummyDefinitions = {
    username: {
      initialValue: '',
      rules: [
        (v) => (v.trim() === '' ? 'Il nome è obbligatorio' : null),
        (v) => (v.length < 3 ? 'Minimo 3 caratteri' : null)
      ]
    },
    age: {
      initialValue: 18,
      rules: [
        (v) => (v < 18 ? 'Devi essere maggiorenne' : null)
      ]
    },
    optionalField: {
      initialValue: 'ciao',
      rules: [] // Nessuna regola, sempre valido
    }
  };

  it('inizializza correttamente campi ed errori in base alle definizioni', () => {
    const { fields, errors, isValid } = useFormModel(dummyDefinitions);

    // I campi devono avere i valori iniziali
    expect(fields.username).toBe('');
    expect(fields.age).toBe(18);
    expect(fields.optionalField).toBe('ciao');

    // Gli errori devono nascere tutti nulli
    expect(errors.username).toBeNull();
    expect(errors.age).toBeNull();
    expect(errors.optionalField).toBeNull();
    expect(isValid.value).toBe(true); 
  });

  it('valida un singolo campo rispettando rigorosamente l’ordine delle regole', () => {
    const { fields, errors, validateField } = useFormModel(dummyDefinitions);

    // 1. Il nome è vuoto, deve fallire la prima regola
    let result = validateField('username');
    expect(result).toBe(false);
    expect(errors.username).toBe('Il nome è obbligatorio');

    // 2. Il nome ha 2 lettere, passa la prima regola ma fallisce la seconda
    fields.username = 'ab';
    result = validateField('username');
    expect(result).toBe(false);
    expect(errors.username).toBe('Minimo 3 caratteri');

    // 3. Il nome è corretto, cancella gli errori precedenti
    fields.username = 'Mario';
    result = validateField('username');
    expect(result).toBe(true);
    expect(errors.username).toBeNull();
  });

  it('valida tutti i campi contemporaneamente con validate()', () => {
    const { fields, errors, validate, isValid } = useFormModel(dummyDefinitions);

    // Allo stato iniziale, 'username' è vuoto, quindi fallisce
    let allValid = validate();
    expect(allValid).toBe(false);
    expect(errors.username).toBe('Il nome è obbligatorio');
    expect(isValid.value).toBe(false);

    // Sistemiamo tutti i campi
    fields.username = 'Admin';
    fields.age = 25;
    
    // Ora deve passare tutto
    allValid = validate();
    expect(allValid).toBe(true);
    expect(isValid.value).toBe(true);
  });

  it('imposta correttamente gli errori del server e ignora i campi sconosciuti', () => {
    const { errors, setServerErrors, isValid } = useFormModel(dummyDefinitions);

    // Simuliamo degli errori tornati dal backend
    setServerErrors({
      username: 'Nome utente già in uso nel database',
      nonExistentField: 'Questo errore deve essere ignorato'
    });

    // Ha agganciato l'errore del server al campo giusto
    expect(errors.username).toBe('Nome utente già in uso nel database');
    
    // L'altro campo rimane pulito
    expect(errors.age).toBeNull();
    
    // Il campo inventato dal server non fa crashare l'app e viene scartato
    expect(errors.nonExistentField).toBeUndefined(); 
    
    // Lo stato complessivo passa a non valido
    expect(isValid.value).toBe(false);
  });

  it('reimposta completamente campi ed errori allo stato iniziale', () => {
    const { fields, errors, reset, validate, setServerErrors } = useFormModel(dummyDefinitions);

    // 1. "Sporchiamo" lo stato modificando valori e creando errori
    fields.username = 'hacker_boy';
    fields.age = 10;
    setServerErrors({ optionalField: 'Errore strano' });
    validate(); 

    // 2. Chiamiamo il reset
    reset();

    // 3. Tutto deve essere tornato esattamente come all'inizio
    expect(fields.username).toBe('');
    expect(fields.age).toBe(18);
    expect(fields.optionalField).toBe('ciao');
    
    expect(errors.username).toBeNull();
    expect(errors.age).toBeNull();
    expect(errors.optionalField).toBeNull();
  });
});