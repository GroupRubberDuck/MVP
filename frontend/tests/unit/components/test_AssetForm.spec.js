// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import AssetForm from '../../../src/components/AssetForm.vue';
import FormField from '@/components/FormField.vue';

// --- AssetForm Component -----------------------------------------------------

describe('AssetForm', () => {
  // Funzione helper per generare props fresche per ogni test
  const createProps = () => ({
    fields: {
      name: 'Firewall Principale',
      assetType: 'security',
      description: 'Gestisce il traffico in entrata'
    },
    errors: {
      name: null,
      assetType: null,
      description: null
    }
  });

  it('dovrebbe renderizzare tutti gli input e popolarli con i dati iniziali dei campi', () => {
    const props = createProps();
    const wrapper = mount(AssetForm, { props });

    // 1. Verifica input testo (nome)
    const nameInput = wrapper.find('input[type="text"]');
    expect(nameInput.exists()).toBe(true);
    expect(nameInput.element.value).toBe('Firewall Principale');

    // 2. Verifica radio button (tipologia)
    const securityRadio = wrapper.find('input[type="radio"][value="security"]');
    const networkRadio = wrapper.find('input[type="radio"][value="network"]');
    expect(securityRadio.element.checked).toBe(true);
    expect(networkRadio.element.checked).toBe(false);

    // 3. Verifica textarea (descrizione)
    const textarea = wrapper.find('textarea');
    expect(textarea.exists()).toBe(true);
    expect(textarea.element.value).toBe('Gestisce il traffico in entrata');
  });

  it("dovrebbe aggiornare l'oggetto fields in modo reattivo quando l'utente digita o seleziona le opzioni", async () => {
    const props = createProps();
    const wrapper = mount(AssetForm, { props });

    // 1. Modifichiamo il testo del nome
    const nameInput = wrapper.find('input[type="text"]');
    await nameInput.setValue('Nuovo Router');
    expect(props.fields.name).toBe('Nuovo Router'); // L'oggetto originale deve essersi aggiornato

    // 2. Cambiamo la selezione del radio button in "network"
    const networkRadio = wrapper.find('input[type="radio"][value="network"]');
    await networkRadio.setValue(); // Simula il click/selezione
    expect(props.fields.assetType).toBe('network');

    // 3. Modifichiamo la textarea
    const textarea = wrapper.find('textarea');
    await textarea.setValue('Nuova descrizione del router');
    expect(props.fields.description).toBe('Nuova descrizione del router');
  });

  it('dovrebbe renderizzare il contenuto passato nello slot "actions"', () => {
    const props = createProps();
    const wrapper = mount(AssetForm, {
      props,
      slots: {
        actions: '<button class="test-submit-btn">Invia Form</button>'
      }
    });

    // Verifica che il bottone inserito nello slot venga renderizzato correttamente nel DOM
    const slotButton = wrapper.find('button.test-submit-btn');
    expect(slotButton.exists()).toBe(true);
    expect(slotButton.text()).toBe('Invia Form');
  });
});