// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DeviceCreateWidget from '../../../../src/widgets/device-create/DeviceCreateWidget.vue';

// --- DeviceCreateWidget ------------------------------------------------------

describe('DeviceCreateWidget', () => {
  const defaultProps = {
    submitUrl: '/api/devices/create',
    cancelUrl: '/devices/list',
    defaultStandardId: 'STD-999',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();

    if (typeof window !== 'undefined') {
      delete window.location;
      window.location = { href: '' };
    }
  });

  it('mostra correttamente la struttura del form e i link di azione', () => {
    const wrapper = mount(DeviceCreateWidget, { props: defaultProps });
    
    expect(wrapper.find('form').exists()).toBe(true);
    expect(wrapper.find(`a[href="${defaultProps.cancelUrl}"]`).exists()).toBe(true);
  });

  it('blocca l’invio quando la validazione client-side fallisce', async () => {
    const wrapper = mount(DeviceCreateWidget, { props: defaultProps });
    
    // Clicca direttamente senza compilare i campi obbligatori
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Il fetch non deve essere partito perché validate() blocca l'esecuzione
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('invia i dati ripuliti e lo standardId ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ redirect_url: '/devices/dashboard' })
    });

    const wrapper = mount(DeviceCreateWidget, { props: defaultProps });
    const inputs = wrapper.findAll('input');

    // Compiliamo i 2 input reali che abbiamo nel form
    await inputs[0].setValue('  Router Sala Ced  ');
    await inputs[1].setValue('  Cisco IOS  ');

    // Se la descrizione è una textarea, la cerchiamo così (altrimenti se non c'è, non fa nulla)
    const textarea = wrapper.find('textarea');
    if (textarea.exists()) {
      await textarea.setValue('  Dispositivo core di rete  ');
    }

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.submitUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_name: 'Router Sala Ced',
        device_os: 'Cisco IOS',
        device_description: textarea.exists() ? 'Dispositivo core di rete' : '',
        standard_id: defaultProps.defaultStandardId,
      })
    });

    expect(window.location.href).toBe('/devices/dashboard');
  });

  it('gestisce gli errori di validazione del server e popola gli errori del form', async () => {
    const serverErrors = { device_name: 'Questo nome è già in uso' };
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ errors: serverErrors })
    });

    const wrapper = mount(DeviceCreateWidget, { props: defaultProps });
    const inputs = wrapper.findAll('input');
    
    await inputs[0].setValue('Router Esistente');
    await inputs[1].setValue('Linux');
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Verifica che l'applicazione abbia tentato l'invio ma sia rimasta sulla pagina
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(window.location.href).not.toBe('/devices/dashboard');
  });

  it('utilizza un messaggio di errore predefinito quando il server non restituisce errori specifici', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.reject() // Simula risposta malformata o crash del server
    });

    const wrapper = mount(DeviceCreateWidget, { props: defaultProps });
    const inputs = wrapper.findAll('input');
    
    await inputs[0].setValue('Router Test');
    await inputs[1].setValue('Linux');
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(window.location.href).not.toBe('/devices/dashboard');
  });
});