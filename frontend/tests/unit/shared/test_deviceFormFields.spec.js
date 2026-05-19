import { describe, it, expect } from 'vitest';
import { deviceFormFields } from '../../../src/shared/deviceFormFields.js';

// --- deviceFormFields Shared Schema ------------------------------------------

describe('Configurazione deviceFormFields', () => {
  
  describe('Campo deviceName', () => {
    const field = deviceFormFields.deviceName;

    it('Dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('Dovrebbe forzare la regola obbligatoria (non può essere vuoto o contenere solo spazi)', () => {
      const requiredRule = field.rules[0];
      
      expect(requiredRule('')).toBe('Il nome è obbligatorio.');
      expect(requiredRule('   ')).toBe('Il nome è obbligatorio.'); // Test per il .trim()
      expect(requiredRule('Server Alpha')).toBeNull(); // Passa la validazione
    });

    it('Dovrebbe forzare la regola della lunghezza massima (64 caratteri)', () => {
      const maxLengthRule = field.rules[1];
      
      const exactValidString = 'a'.repeat(64);
      expect(maxLengthRule(exactValidString)).toBeNull();
      
      const invalidLongString = 'a'.repeat(65);
      expect(maxLengthRule(invalidLongString)).toBe('Massimo 64 caratteri.');
    });
  });

  describe('Campo deviceOs', () => {
    const field = deviceFormFields.deviceOs;

    it('Dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('Dovrebbe forzare la regola obbligatoria (non può essere vuoto o contenere solo spazi)', () => {
      const requiredRule = field.rules[0];
      
      expect(requiredRule('')).toBe('Il sistema operativo è obbligatorio.');
      expect(requiredRule('   ')).toBe('Il sistema operativo è obbligatorio.');
      expect(requiredRule('Ubuntu 22.04')).toBeNull();
    });

    it('Dovrebbe forzare la regola della lunghezza massima (64 caratteri)', () => {
      const maxLengthRule = field.rules[1];
      
      const exactValidString = 'a'.repeat(64);
      expect(maxLengthRule(exactValidString)).toBeNull();
      
      const invalidLongString = 'b'.repeat(65);
      expect(maxLengthRule(invalidLongString)).toBe('Massimo 64 caratteri.');
    });
  });

  describe('Campo deviceDescription', () => {
    const field = deviceFormFields.deviceDescription;

    it('dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('dovrebbe consentire stringhe vuote poiché non è strettamente obbligatorio', () => {
      const maxLengthRule = field.rules[0];
      
      // Essendo opzionale, la stringa vuota deve passare il test della lunghezza
      expect(maxLengthRule('')).toBeNull();
    });

    it('dovrebbe forzare la regola della lunghezza massima (512 caratteri)', () => {
      const maxLengthRule = field.rules[0];
      
      const exactValidString = 'c'.repeat(512);
      expect(maxLengthRule(exactValidString)).toBeNull();
      
      const invalidLongString = 'd'.repeat(513);
      expect(maxLengthRule(invalidLongString)).toBe('Massimo 512 caratteri.');
    });
  });

});