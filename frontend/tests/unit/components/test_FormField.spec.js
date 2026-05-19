// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import FormField from '../../../src/components/FormField.vue';

// --- FormField Component -----------------------------------------------------

describe('FormField', () => {
  it('dovrebbe renderizzare la label e il contenuto dello slot predefinito', () => {
    const wrapper = mount(FormField, {
      props: {
        label: 'Indirizzo IP'
      },
      slots: {
        // Inseriamo un finto input nello slot
        default: '<input type="text" id="mock-input" />'
      }
    });

    // Verifica che la label contenga il testo corretto
    const label = wrapper.find('label');
    expect(label.exists()).toBe(true);
    expect(label.text()).toContain('Indirizzo IP');

    // Verifica che l'input passato nello slot sia stato renderizzato dentro la label
    const slotContent = wrapper.find('#mock-input');
    expect(slotContent.exists()).toBe(true);
    
    // Non ci deve essere nessun messaggio di errore all'avvio
    expect(wrapper.find('.form-field-error').exists()).toBe(false);
  });

  it('dovrebbe renderizzare il messaggio di errore quando viene fornita la prop error', () => {
    const wrapper = mount(FormField, {
      props: {
        label: 'Nome Utente',
        error: 'Questo campo è obbligatorio.'
      }
    });

    // L'elemento dell'errore deve essere apparso nel DOM
    const errorSpan = wrapper.find('.form-field-error');
    expect(errorSpan.exists()).toBe(true);
    
    // Il testo deve corrispondere esattamente
    expect(errorSpan.text()).toBe('Questo campo è obbligatorio.');
  });

  it('dovrebbe nascondere il messaggio di errore in modo dinamico quando la prop error diventa null', async () => {
    const wrapper = mount(FormField, {
      props: {
        label: 'Password',
        error: 'Password troppo corta'
      }
    });

    // L'errore c'è all'inizio
    expect(wrapper.find('.form-field-error').exists()).toBe(true);

    // L'utente digita qualcosa di valido, quindi il padre rimuove l'errore
    await wrapper.setProps({ error: null });

    // Il messaggio di errore deve sparire immediatamente (grazie al v-if)
    expect(wrapper.find('.form-field-error').exists()).toBe(false);
  });
});