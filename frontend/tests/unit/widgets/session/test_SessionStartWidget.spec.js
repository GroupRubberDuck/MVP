// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import SessionStartWidget from '../../../../src/widgets/open-session/OpenSessionWidget.vue';

// --- SessionStartWidget ------------------------------------------------------

describe('SessionStartWidget', () => {
  const defaultProps = {
    createSessionUrl: '/api/sessions/start',
    deviceId: 'DEVICE-999',
    redirectUrlTemplate: '/evaluations/__SESSION_ID__/dashboard'
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

  it('dovrebbe renderizzare il pulsante di avvio correttamente', () => {
    const wrapper = mount(SessionStartWidget, { props: defaultProps });
    
    const button = wrapper.find('button');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('Avvia Valutazione');
  });

  it('dovrebbe inviare il payload corretto tramite POST e sostituire __SESSION_ID__ al momento del reindirizzamento', async () => {
    // Simuliamo il server che risponde con successo inviando l'ID della nuova sessione
    const mockSessionId = 'SESS-12345-ABC';
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ session_id: mockSessionId })
    });

    const wrapper = mount(SessionStartWidget, { props: defaultProps });
    
    // Clicchiamo per avviare
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // 1.amp Verifica la chiamata fetch
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.createSessionUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: defaultProps.deviceId }) // Controlliamo il payload
    });

    // 2. Verifica che il template URL sia stato compilato correttamente con il replace()
    const expectedUrl = `/evaluations/${mockSessionId}/dashboard`;
    expect(window.location.href).toBe(expectedUrl);
  });

  it('dovrebbe gestire i guasti del server in modo sicuro senza reindirizzare', async () => {
    // Simuliamo un dispositivo non valido o offline
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'Dispositivo non trovato o non disponibile.' })
    });

    const wrapper = mount(SessionStartWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Verifichiamo che la chiamata sia partita ma che il redirect sia stato bloccato
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(window.location.href).not.toContain('/evaluations/');
  });

  it('dovrebbe gestire gli errori di rete generici o i JSON non analizzabili senza causare crash', async () => {
    // Simuliamo un crash del server senza risposta JSON
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.reject() 
    });

    const wrapper = mount(SessionStartWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // La sicurezza prima di tutto: l'applicazione non deve andare in crash fatale
    expect(window.location.href).not.toContain('/evaluations/');
  });
});