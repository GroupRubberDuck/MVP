// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// 1. Mockiamo la funzione esterna di blocco navigazione prima di caricare il componente
vi.mock('@/shared/navigationGuard.js', () => ({
  disableNavigationGuard: vi.fn()
}));

// 2. Importiamo il componente 
import SessionCommitAndCloseWidget from '../../../../src/widgets/session-commit-and-close/SessionCommitAndCloseWidget.vue';

// 3. Importiamo la spia per le nostre asserzioni
import { disableNavigationGuard } from '@/shared/navigationGuard.js';

// --- SessionCommitAndCloseWidget ---------------------------------------------

describe('SessionCommitAndCloseWidget', () => {
  const defaultProps = {
    commitAndCloseUrl: '/api/sessions/current/commit-and-close',
    redirectUrl: '/dashboard/summary'
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

  it('dovrebbe renderizzare il pulsante con le etichette iniziali corrette', () => {
    const wrapper = mount(SessionCommitAndCloseWidget, { props: defaultProps });
    
    const button = wrapper.find('button');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('Salva e Chiudi');
    expect(button.classes()).toContain('btn--primary');
  });

  it('dovrebbe inviare una richiesta POST, disabilitare la guardia di navigazione e reindirizzare in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(SessionCommitAndCloseWidget, { props: defaultProps });
    
    // Clicchiamo sul pulsante unico del widget (AsyncButton)
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // 1. Verifica che la chiamata fetch sia partita con il metodo POST
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.commitAndCloseUrl, {
      method: 'POST'
    });

    // 2. Verifica che la guardia di navigazione sia stata disattivata per permettere l'uscita
    expect(disableNavigationGuard).toHaveBeenCalledTimes(1);

    // 3. Verifica l'avvenuto redirect alla pagina finale
    expect(window.location.href).toBe(defaultProps.redirectUrl);
  });

  it('dovrebbe gestire gli errori del server in modo sicuro senza reindirizzare o disabilitare la guardia', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'Errore critico durante il consolidamento dati' })
    });

    const wrapper = mount(SessionCommitAndCloseWidget, { props: defaultProps });
    
    await wrapper.find('button').trigger('click');
    await flushPromises();

    // La fetch viene chiamata...
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    // ...ma l'azione fallisce, quindi la navigazione deve rimanere BLOCCATA per sicurezza
    expect(disableNavigationGuard).not.toHaveBeenCalled();
    
    // L'utente non deve essere spostato dalla pagina
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });
});