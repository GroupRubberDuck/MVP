// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import AssetCreateWidget from '../../../../src/widgets/asset-create/AssetCreateWidget.vue';

// --- AssetCreateWidget -------------------------------------------------------

describe('AssetCreateWidget', () => {
  const defaultProps = {
    submitUrl: '/api/assets/create',
    cancelUrl: '/assets/dashboard',
    redirectUrl: '/assets/__ASSET_ID__/details'
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

  it('dovrebbe renderizzare correttamente la struttura del form, il titolo e i link di azione', () => {
    const wrapper = mount(AssetCreateWidget, { props: defaultProps });
    
    // Verifica struttura e testi base
    expect(wrapper.find('.card__title').text()).toBe('Aggiungi Nuovo Asset');
    expect(wrapper.find('form').exists()).toBe(true);
    
    // Verifica link annulla
    const cancelLink = wrapper.find(`a[href="${defaultProps.cancelUrl}"]`);
    expect(cancelLink.exists()).toBe(true);
    expect(cancelLink.text()).toBe('Annulla');
  });

  it('dovrebbe impedire l\'invio quando la validazione lato client fallisce (form vuoto)', async () => {
    const wrapper = mount(AssetCreateWidget, { props: defaultProps });
    
    // Proviamo a inviare il form vuoto
    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // L'invio deve essere bloccato prima del fetch
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('dovrebbe inviare i dati senza spazi tramite POST e sostituire __ASSET_ID__ in caso di reindirizzamento riuscito', async () => {
    const mockAssetId = 'ASSET-777';
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ asset_id: mockAssetId }) // Il server restituisce il nuovo ID
    });

    const wrapper = mount(AssetCreateWidget, { props: defaultProps });

    // Compiliamo i campi (supponendo che AssetForm renderizzi standard input/textarea/select)
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      await inputs[0].setValue('  Nuovo Server Asset  '); 
    }
    
    // Cerchiamo una select per l'assetType
    const select = wrapper.find('select');
    if (select.exists()) {
      await select.setValue('hardware');
    } else if (inputs.length > 1) {
      await inputs[1].setValue('hardware');
    }

    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      await textarea.setValue('  Descrizione dettagliata  '); 
    }

    // Clicchiamo "Crea Asset"
    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // 1. Verifica chiamata fetch
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    const fetchCallArgs = global.fetch.mock.calls[0];
    expect(fetchCallArgs[0]).toBe(defaultProps.submitUrl);
    expect(fetchCallArgs[1].method).toBe('POST');
    
    // Verifica il payload pulito dagli spazi vuoti in eccesso
    const payload = JSON.parse(fetchCallArgs[1].body);
    expect(payload.name).toBe('Nuovo Server Asset');
    if (textarea.exists()) {
      expect(payload.description).toBe('Descrizione dettagliata');
    }

    // 2. Verifica redirect e sostituzione dell'ID nel template URL
    expect(window.location.href).toBe(`/assets/${mockAssetId}/details`);
  });

  it('dovrebbe gestire gli errori di validazione del server senza reindirizzare', async () => {
    const serverErrors = { name: 'Nome asset già esistente' };
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ errors: serverErrors })
    });

    const wrapper = mount(AssetCreateWidget, { props: defaultProps });
    
    // Compiliamo TUTTI i campi per superare la validazione locale (client-side)
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) await inputs[0].setValue('Asset Duplicato');
    
    const select = wrapper.find('select');
    if (select.exists()) {
      await select.setValue('hardware');
    } else if (inputs.length > 1) {
      await inputs[1].setValue('hardware');
    }

    const textarea = wrapper.find('textarea');
    if (textarea.exists()) await textarea.setValue('Descrizione test');

    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // Questa volta la validazione locale passa e la chiamata parte (ma il server la blocca)
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    // Il reindirizzamento NON deve avvenire
    expect(window.location.href).not.toContain('/details');
  });

  it('dovrebbe gestire i guasti generici del server in modo sicuro', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.reject() // Simula risposta server malformata
    });

    const wrapper = mount(AssetCreateWidget, { props: defaultProps });
    
    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) await inputs[0].setValue('Test');

    await wrapper.find('button.btn--primary').trigger('click');
    await flushPromises();

    // Il reindirizzamento NON deve avvenire, l'app non deve bloccarsi
    expect(window.location.href).not.toContain('/details');
  });
});