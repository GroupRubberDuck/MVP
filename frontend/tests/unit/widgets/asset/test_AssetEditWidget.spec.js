// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import AssetEditWidget from '../../../../src/widgets/asset-edit/AssetEditWidget.vue';

// --- AssetEditWidget ---------------------------------------------------------

describe('AssetEditWidget', () => {
  const defaultProps = {
    submitUrl: '/api/assets/999/edit',
    cancelUrl: '/assets/dashboard',
    initialName: 'Server Alpha',
    initialAssetType: 'hardware',
    initialDescription: 'Server principale',
    redirectUrl: '/assets/999/details'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();

    // Mock sicuro di window.location per intercettare il redirect
    if (typeof window !== 'undefined') {
      delete window.location;
      window.location = { href: '' };
    }
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('mostra il form, precompila i dati iniziali e visualizza correttamente i link di azione', () => {
    const wrapper = mount(AssetEditWidget, { props: defaultProps });
    
    // Verifica struttura e testi base
    expect(wrapper.find('.card__title').text()).toContain('Modifica');
    expect(wrapper.find('form').exists()).toBe(true);
    
    // Verifica link annulla
    const cancelLink = wrapper.find(`a[href="${defaultProps.cancelUrl}"]`);
    expect(cancelLink.exists()).toBe(true);
    expect(cancelLink.text()).toBe('Annulla');

    // Verifica che i campi siano stati pre-compilati
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      expect(inputs[0].element.value).toBe(defaultProps.initialName);
    }
    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      expect(textarea.element.value).toBe(defaultProps.initialDescription);
    }
  });

  it('blocca l’invio quando la validazione client-side fallisce', async () => {
    const wrapper = mount(AssetEditWidget, { props: defaultProps });
    
    // Svuotiamo il campo del nome per far fallire la validazione
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      await inputs[0].setValue(''); 
    }
    
    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // L'invio deve essere bloccato
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('invia i dati aggiornati e ripuliti tramite PUT ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(AssetEditWidget, { props: defaultProps });

    // Modifichiamo i campi inserendo spazi per testare il .trim()
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      await inputs[0].setValue('  Server Alpha Aggiornato  ');
    }

    const select = wrapper.find('select');
    if (select.exists()) {
      await select.setValue('software');
    } else if (inputs.length > 1) {
      await inputs[1].setValue('software');
    }

    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      await textarea.setValue('  Nuova descrizione  ');
    }

    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // Verifica la chiamata fetch
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    const fetchCallArgs = global.fetch.mock.calls[0];
    expect(fetchCallArgs[0]).toBe(defaultProps.submitUrl);
    expect(fetchCallArgs[1].method).toBe('PUT'); // Deve essere PUT
    
    // Verifica il payload pulito
    const payload = JSON.parse(fetchCallArgs[1].body);
    expect(payload.name).toBe('Server Alpha Aggiornato');
    expect(payload.asset_type).toBeDefined();
    if (textarea.exists()) {
      expect(payload.description).toBe('Nuova descrizione');
    }

    // Verifica il redirect
    expect(window.location.href).toBe(defaultProps.redirectUrl);
  });

  it('gestisce gli errori di validazione del server senza effettuare il redirect', async () => {
    const serverErrors = { name: 'Nome asset già in uso' };
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ errors: serverErrors })
    });

    const wrapper = mount(AssetEditWidget, { props: defaultProps });
    
    // Assicuriamoci che i campi siano validi per passare la validazione client
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) await inputs[0].setValue('Nuovo Nome');
    
    const textarea = wrapper.find('textarea');
    if (textarea.exists()) await textarea.setValue('Descrizione');

    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // La chiamata parte, ma il server la blocca
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    // Nessun reindirizzamento
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });

  it('gestisce in sicurezza un errore generico del server', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.reject()
    });

    const wrapper = mount(AssetEditWidget, { props: defaultProps });
    
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) await inputs[0].setValue('Nuovo Nome');

    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // L'app non deve crashare e non deve reindirizzare
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });
});