// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import DeviceForm from '../../../src/components/DeviceForm.vue';

// --- DeviceForm Component ----------------------------------------------------

describe('DeviceForm', () => {
  // Funzione helper per generare le props base fresche per ogni test
  const createProps = () => ({
    fields: {
      deviceName: 'Router Alpha',
      deviceOs: 'Cisco IOS',
      deviceDescription: 'Router di confine'
    },
    errors: {
      deviceName: null,
      deviceOs: null,
      deviceDescription: null
    }
  });

  it('Dovrebbe renderizzare gli input e le textarea con i dati iniziali e i contatori di caratteri', () => {
    const props = createProps();
    const wrapper = mount(DeviceForm, { props });

    const inputs = wrapper.findAll('input[type="text"]');
    const textarea = wrapper.find('textarea');

    // Verifica i valori
    expect(inputs[0].element.value).toBe('Router Alpha');
    expect(inputs[1].element.value).toBe('Cisco IOS');
    expect(textarea.element.value).toBe('Router di confine');

    // Verifica i contatori di caratteri (il testo deve contenere la lunghezza esatta della stringa)
    const hints = wrapper.findAll('.form-hint');
    expect(hints[0].text()).toContain('12/64'); 
    expect(hints[1].text()).toContain('9/64');  
    expect(hints[2].text()).toContain('17/512'); 
  });

  it('Dovrebbe aggiornare i campi in modo reattivo e aggiornare i contatori quando l\'utente digita', async () => {
    const props = createProps();
    const wrapper = mount(DeviceForm, { props });

    const inputs = wrapper.findAll('input[type="text"]');
    
    // L'utente digita un nome più lungo
    await inputs[0].setValue('Router Beta Ext');
    
    // L'oggetto props.fields deve essersi aggiornato
    expect(props.fields.deviceName).toBe('Router Beta Ext');

    // Il contatore nel DOM deve essersi aggiornato in tempo reale
    const hints = wrapper.findAll('.form-hint');
    expect(hints[0].text()).toContain('15/64');
  });

  it('Dovrebbe applicare la classe form-input-error solo quando è presente un errore', async () => {
    const props = createProps();
    // Simuliamo che il validatore abbia trovato un errore nel nome, ma non nel sistema operativo
    props.errors.deviceName = 'Il nome è obbligatorio.';
    
    const wrapper = mount(DeviceForm, { props });

    const inputs = wrapper.findAll('input[type="text"]');
    const nameInput = inputs[0];
    const osInput = inputs[1];

    // L'input del nome DEVE avere la classe d'errore 
    expect(nameInput.classes()).toContain('form-input-error');
    
    // L'input del sistema operativo NON deve averla perché il suo errore è null
    expect(osInput.classes()).not.toContain('form-input-error');
  });

  it('Dovrebbe renderizzare lo slot delle azioni correttamente', () => {
    const props = createProps();
    const wrapper = mount(DeviceForm, {
      props,
      slots: {
        actions: '<button id="submit-test">Salva Dispositivo</button>'
      }
    });

    const actionButton = wrapper.find('#submit-test');
    expect(actionButton.exists()).toBe(true);
    expect(actionButton.text()).toBe('Salva Dispositivo');
  });
});