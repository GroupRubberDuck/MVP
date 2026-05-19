// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// 1. Mockiamo la funzione esterna di blocco navigazione PRIMA di importare il componente
vi.mock('@/shared/navigationGuard.js', () => ({
  disableNavigationGuard: vi.fn()
}));

// 2. Importiamo il componente 
import CloseSessionWidget from '../../../../src/widgets/session-close/SessionCloseWidget.vue';

// 3. Importiamo la finta funzione per poterla testare
import { disableNavigationGuard } from '@/shared/navigationGuard.js';

// --- CloseSessionWidget ------------------------------------------------------

describe('CloseSessionWidget', () => {
  const defaultProps = {
    closeUrl: '/api/sessions/current/close',
    redirectUrl: '/dashboard/home'
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

  it('dovrebbe renderizzare il pulsante iniziale e mantenere il modale nascosto', () => {
    const wrapper = mount(CloseSessionWidget, { props: defaultProps });
    
    const openBtn = wrapper.find('button.btn--danger');
    expect(openBtn.exists()).toBe(true);
    expect(openBtn.text()).toBe('Chiudi Sessione');
    
    // Il modale non deve esserci
    expect(wrapper.text()).not.toContain('Sei sicuro di voler chiudere la sessione?');
  });

  it('dovrebbe aprire il modale al clic', async () => {
    const wrapper = mount(CloseSessionWidget, { props: defaultProps });
    
    await wrapper.find('button.btn--danger').trigger('click');
    
    expect(wrapper.text()).toContain('Sei sicuro di voler chiudere la sessione?');
    expect(wrapper.text()).toContain('I dati non salvati andranno persi.');
  });

  it('dovrebbe chiudere il modale quando viene cliccato il pulsante annulla', async () => {
    const wrapper = mount(CloseSessionWidget, { props: defaultProps });
    
    await wrapper.find('button.btn--danger').trigger('click');
    
    // Troviamo e clicchiamo "Annulla"
    const buttons = wrapper.findAll('button');
    const cancelBtn = buttons.find(b => b.text() === 'Annulla');
    await cancelBtn.trigger('click');
    
    expect(wrapper.text()).not.toContain('Sei sicuro di voler chiudere la sessione?');
  });

  it('dovrebbe inviare una richiesta DELETE, disabilitare la guardia di navigazione e reindirizzare in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(CloseSessionWidget, { props: defaultProps });
    await wrapper.find('button.btn--danger').trigger('click');

    // Clicchiamo "Conferma chiusura"
    const buttons = wrapper.findAll('button');
    const confirmBtn = buttons.find(b => b.text() === 'Conferma chiusura');
    await confirmBtn.trigger('click');
    await flushPromises();

    // 1. Verifica chiamata API
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.closeUrl, {
      method: 'DELETE'
    });

    // 2. Verifica che la guardia di navigazione sia stata disabilitata
    expect(disableNavigationGuard).toHaveBeenCalledTimes(1);

    // 3. Verifica il redirect
    expect(window.location.href).toBe(defaultProps.redirectUrl);
  });

  it('dovrebbe gestire i guasti del server in modo sicuro senza reindirizzare o disabilitare la guardia', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'Sessione già chiusa o non valida.' })
    });

    const wrapper = mount(CloseSessionWidget, { props: defaultProps });
    await wrapper.find('button.btn--danger').trigger('click');

    const buttons = wrapper.findAll('button');
    const confirmBtn = buttons.find(b => b.text() === 'Conferma chiusura');
    await confirmBtn.trigger('click');
    await flushPromises();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    // Se c'è un errore, NON deve sganciare la sicurezza di navigazione
    expect(disableNavigationGuard).not.toHaveBeenCalled();
    
    // NON deve fare redirect
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });
});