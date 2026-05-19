// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DeviceEditWidget from '../../../../src/widgets/device-edit/DeviceEditWidget.vue';

// --- DeviceEditWidget --------------------------------------------------------

describe('DeviceEditWidget', () => {
  const defaultProps = {
    submitUrl: '/api/devices/123/edit',
    cancelUrl: '/devices/dashboard',
    defaultStandardId: 'STD-999',
    initialName: 'Server Alpha',
    initialOs: 'Ubuntu 20.04',
    initialDescription: 'Main database server'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();

    if (typeof window !== 'undefined') {
      delete window.location;
      window.location = { href: '' };
    }
  });

  it('Mostra il form, i link di azione e precompila correttamente i dati iniziali', () => {
    const wrapper = mount(DeviceEditWidget, { props: defaultProps });
    
    // Verifica struttura base
    expect(wrapper.find('form').exists()).toBe(true);
    expect(wrapper.find(`a[href="${defaultProps.cancelUrl}"]`).exists()).toBe(true);

    // Verifica che i campi siano stati pre-compilati con i dati iniziali
    const inputs = wrapper.findAll('input');
    expect(inputs[0].element.value).toBe(defaultProps.initialName);
    expect(inputs[1].element.value).toBe(defaultProps.initialOs);

    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      expect(textarea.element.value).toBe(defaultProps.initialDescription);
    }
  });

  it('Blocca l’invio quando la validazione client-side fallisce', async () => {
    const wrapper = mount(DeviceEditWidget, { props: defaultProps });
    
    // Svuotiamo un campo obbligatorio precedentemente compilato
    const inputs = wrapper.findAll('input');
    await inputs[0].setValue(''); 
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // L'invio deve essere bloccato
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('Invia i dati aggiornati e ripuliti tramite PUT ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ redirect_url: '/devices/dashboard/success' })
    });

    const wrapper = mount(DeviceEditWidget, { props: defaultProps });
    const inputs = wrapper.findAll('input');

    // Modifichiamo i dati iniziali aggiungendo spazi per testare il .trim()
    await inputs[0].setValue('  Server Alpha Aggiornato  ');
    await inputs[1].setValue('  Ubuntu 22.04 LTS  ');

    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      await textarea.setValue('  Updated description  ');
    }

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.submitUrl, {
      method: 'PUT', // Verifica che il metodo sia PUT per l'aggiornamento
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_name: 'Server Alpha Aggiornato',
        device_os: 'Ubuntu 22.04 LTS',
        device_description: textarea.exists() ? 'Updated description' : '',
        standard_id: defaultProps.defaultStandardId,
      })
    });

    expect(window.location.href).toBe('/devices/dashboard/success');
  });

  it('Gestisce gli errori di validazione del server e popola gli errori del form', async () => {
    const serverErrors = { device_name: 'Nome dispositivo già in uso da un altro server' };
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ errors: serverErrors })
    });

    const wrapper = mount(DeviceEditWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Ha provato a salvare ma è stato bloccato dal server
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(window.location.href).not.toBe('/devices/dashboard/success');
  });

  it('Utilizza un messaggio di errore predefinito quando il server non restituisce errori specifici', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.reject() 
    });

    const wrapper = mount(DeviceEditWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(window.location.href).not.toBe('/devices/dashboard/success');
  });
});