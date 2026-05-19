// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import SessionCommitWidget from '../../../../src/widgets/session-commit/SessionCommitWidget.vue';
import AsyncButton from '@/components/AsyncButton.vue';
import Toast from '@/components/Toast.vue';

// --- SessionCommitWidget -----------------------------------------------------

describe('SessionCommitWidget', () => {
  const defaultProps = {
    commitUrl: '/api/sessions/current/commit'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('dovrebbe renderizzare il pulsante di salvataggio e mantenere il toast inizialmente nascosto', () => {
    const wrapper = mount(SessionCommitWidget, { props: defaultProps });
    
    // Il bottone asincrono deve esserci
    const button = wrapper.find('button');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('Salva Sessione');
    
    // Il componente Toast NON deve esistere all'avvio (v-if="toastMessage")
    const toast = wrapper.findComponent(Toast);
    expect(toast.exists()).toBe(false);
  });

  it('dovrebbe inviare una richiesta POST e mostrare il toast di successo quando il server risponde correttamente', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(SessionCommitWidget, { props: defaultProps });
    
    // Clicchiamo per avviare il salvataggio
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // 1. Verifichiamo che la chiamata di rete sia partita correttamente
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.commitUrl, {
      method: 'POST'
    });

    // 2. Verifichiamo che il Toast sia apparso con il messaggio corretto
    const toast = wrapper.findComponent(Toast);
    expect(toast.exists()).toBe(true);
    expect(toast.props('message')).toBe('Sessione salvata con successo.');
  });

  it('dovrebbe cancellare il messaggio del toast quando il componente Toast emette un evento close', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({})
    });

    const wrapper = mount(SessionCommitWidget, { props: defaultProps });
    
    // Scateniamo il successo per far apparire il toast
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Verifichiamo che il toast esista
    let toast = wrapper.findComponent(Toast);
    expect(toast.exists()).toBe(true);

    // Simuliamo l'emissione dell'evento @close da parte del componente Toast
    await toast.vm.$emit('close');

    // Il Toast dovrebbe essere sparito
    toast = wrapper.findComponent(Toast);
    expect(toast.exists()).toBe(false);
  });

  it('non dovrebbe mostrare il toast di successo se il server restituisce un errore', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'Sessione scaduta o non valida' })
    });

    const wrapper = mount(SessionCommitWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // La chiamata è stata fatta
    expect(global.fetch).toHaveBeenCalledTimes(1);

    // But siccome è fallita, il Toast di successo NON deve apparire
    const toast = wrapper.findComponent(Toast);
    expect(toast.exists()).toBe(false);
  });
});