import { describe, it, expect } from 'vitest';
import { assetFormFields } from '../../../src/shared/assetFormFields.js';

// --- assetFormFields Shared Schema -------------------------------------------

describe('Configurazione assetFormFields', () => {
  
  describe('Campo name', () => {
    const field = assetFormFields.name;

    it('Dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('Dovrebbe forzare la regola obbligatoria (non può essere vuoto o contenere solo spazi)', () => {
      const requiredRule = field.rules[0];
      
      expect(requiredRule('')).toBe("Il nome dell'asset è obbligatorio.");
      expect(requiredRule('   ')).toBe("Il nome dell'asset è obbligatorio."); // Test per il .trim()
      expect(requiredRule('Monitor Dell 27"')).toBeNull(); // Passa la validazione
    });
  });

  describe('Campo assetType', () => {
    const field = assetFormFields.assetType;

    it('Dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('Dovrebbe forzare la regola obbligatoria (è necessario selezionare una tipologia)', () => {
      const requiredRule = field.rules[0];
      
      expect(requiredRule('')).toBe('Seleziona una tipologia.');
      // Simuliamo la selezione di un'opzione valida dalla tendina
      expect(requiredRule('hardware')).toBeNull(); 
      expect(requiredRule('software')).toBeNull(); 
    });
  });

  describe('Campo description', () => {
    const field = assetFormFields.description;

    it('Dovrebbe avere un valore iniziale vuoto', () => {
      expect(field.initialValue).toBe('');
    });

    it('Dovrebbe avere un array di regole vuoto (nessuna validazione richiesta)', () => {
      // Verifichiamo esplicitamente che l'array delle regole sia vuoto
      expect(field.rules).toEqual([]);
      expect(field.rules.length).toBe(0);
    });
  });

});