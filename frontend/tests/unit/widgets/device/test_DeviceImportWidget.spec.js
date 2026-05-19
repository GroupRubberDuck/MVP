// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DeviceImportWidget from '../../../../src/widgets/device-import/DeviceImportWidget.vue';

// --- DeviceImportWidget ------------------------------------------------------

describe('DeviceImportWidget', () => {
  const defaultProps = {
    importUrl: '/api/devices/import',
    redirectUrl: '/devices/dashboard'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();

    if (typeof window !== 'undefined') {
      delete window.location;
      window.location = { href: '' };
    }
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('Mostra il pulsante iniziale e mantiene nascosto il modale', () => {
    const wrapper = mount(DeviceImportWidget, { props: defaultProps });
    
    // Il pulsante principale di apertura deve esserci e contenere il testo giusto
    const openBtn = wrapper.find('button');
    expect(openBtn.text()).toContain('Importa Dispositivo');
    
    // Il modale non deve esserci
    expect(wrapper.text()).not.toContain('Seleziona un file di configurazione');
  });

  it('Apre il modale al click e pulisce lo stato precedente', async () => {
    const wrapper = mount(DeviceImportWidget, { props: defaultProps });
    
    // Clicchiamo il pulsante di apertura
    await wrapper.find('button').trigger('click');
    expect(wrapper.text()).toContain('Importa Dispositivo');
    expect(wrapper.text()).toContain('Seleziona un file di configurazione');
  });

  it('Gestisce correttamente gli eventi custom di FileDropZone', async () => {
    const wrapper = mount(DeviceImportWidget, { props: defaultProps });
    await wrapper.find('button').trigger('click');
    
    // Troviamo il componente FileDropZone tramite la sua ref
    const dropZone = wrapper.findComponent({ ref: 'dropZoneRef' });

    // 1. Simuliamo un errore proveniente dal caricamento file
    await dropZone.vm.$emit('error', 'Formato file non supportato. Usa solo JSON.');
    
    // Verifichiamo che appaia il div degli errori con il testo giusto
    const errorAlert = wrapper.find('.alert-error');
    expect(errorAlert.exists()).toBe(true);
    expect(errorAlert.text()).toBe('Formato file non supportato. Usa solo JSON.');

    // 2. Simuliamo la corretta selezione di un file
    const mockFile = new File(['{}'], 'config.json', { type: 'application/json' });
    await dropZone.vm.$emit('select', mockFile);

    // L'errore dovrebbe essere sparito
    expect(wrapper.find('.alert-error').exists()).toBe(false);
  });

  it('Invia correttamente il FormData ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(DeviceImportWidget, { props: defaultProps });
    await wrapper.find('button').trigger('click');

    // Selezioniamo il file
    const mockFile = new File(['{"device": "test"}'], 'test.json', { type: 'application/json' });
    const dropZone = wrapper.findComponent({ ref: 'dropZoneRef' });
    await dropZone.vm.$emit('select', mockFile);

    // Clicchiamo "Avvia Importazione"
    const buttons = wrapper.findAll('button');
    const submitBtn = buttons.find(b => b.text() === 'Avvia Importazione');
    await submitBtn.trigger('click');
    await flushPromises();

    // Verifichiamo la chiamata di rete
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    const fetchArgs = global.fetch.mock.calls[0];
    expect(fetchArgs[0]).toBe(defaultProps.importUrl);
    expect(fetchArgs[1].method).toBe('POST');
    
    // Verifichiamo che abbia usato il FormData e che contenga il nostro file
    const formData = fetchArgs[1].body;
    expect(formData).toBeInstanceOf(FormData);
    expect(formData.get('file')).toBe(mockFile);

    // Verifichiamo il reindirizzamento
    expect(window.location.href).toBe(defaultProps.redirectUrl);
  });

  it('Blocca l’invio se nessun file è selezionato e gestisce gli errori del server', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'File XML corrotto o malformato' })
    });

    const wrapper = mount(DeviceImportWidget, { props: defaultProps });
    await wrapper.find('button').trigger('click');

    const buttons = wrapper.findAll('button');
    const submitBtn = buttons.find(b => b.text() === 'Avvia Importazione');

    // 1. Proviamo a inviare senza aver prima selezionato un file
    await submitBtn.trigger('click');
    await flushPromises();
    
    // Il fetch NON deve partire e l'AsyncButton dovrebbe intercettare l'errore
    expect(global.fetch).not.toHaveBeenCalled();
    expect(wrapper.find('.alert-error').text()).toBe('Nessun file selezionato.');

    // 2. Ora selezioniamo un file ma il server ci restituisce errore
    const dropZone = wrapper.findComponent({ ref: 'dropZoneRef' });
    await dropZone.vm.$emit('select', new File(['bad xml'], 'file.xml'));
    
    await submitBtn.trigger('click');
    await flushPromises();

    // L'errore del server deve essere mostrato all'utente e il redirect bloccato
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(wrapper.find('.alert-error').text()).toBe('File XML corrotto o malformato');
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });

});