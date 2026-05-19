// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import AssetDeleteWidget from '../../../../src/widgets/asset-delete/AssetDeleteWidget.vue';

// --- AssetDeleteWidget -------------------------------------------------------

describe('AssetDeleteWidget', () => {
  const defaultProps = {
    deleteUrl: '/api/assets/999/delete',
    redirectUrl: '/assets/dashboard'
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

  it('mostra il pulsante iniziale di eliminazione e mantiene nascosto il modale', () => {
    const wrapper = mount(AssetDeleteWidget, { props: defaultProps });
    
    // Inizialmente il modale non c'è, c'è solo il bottone rosso principale
    const openBtn = wrapper.find('button.btn-red');
    expect(openBtn.exists()).toBe(true);
    expect(openBtn.text()).toBe('Elimina');
    
    expect(wrapper.text()).not.toContain('Sei sicuro di voler eliminare questo asset?');
  });

  it('apre il modale al click e mostra il testo di avviso', async () => {
    const wrapper = mount(AssetDeleteWidget, { props: defaultProps });
    
    // Clicchiamo per aprire il modale
    await wrapper.find('button.btn-red').trigger('click');

    // Ora il modale dovrebbe essere visibile
    expect(wrapper.text()).toContain('Sei sicuro di voler eliminare questo asset?');
  });

  it('chiude il modale quando viene cliccato Annulla', async () => {
    const wrapper = mount(AssetDeleteWidget, { props: defaultProps });
    
    // Apriamo il modale
    await wrapper.find('button.btn-red').trigger('click');
    expect(wrapper.text()).toContain('Sei sicuro di voler eliminare questo asset?');

    // Troviamo e clicchiamo il bottone "Annulla"
    const buttons = wrapper.findAll('button');
    const cancelBtn = buttons.find(b => b.text() === 'Annulla');
    await cancelBtn.trigger('click');
    
    // Il modale deve sparire
    expect(wrapper.text()).not.toContain('Sei sicuro di voler eliminare questo asset?');
  });

  it('invia la richiesta DELETE ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(AssetDeleteWidget, { props: defaultProps });
    
    // Apriamo il modale
    await wrapper.find('button.btn-red').trigger('click');

    // Clicchiamo il bottone "Conferma eliminazione" gestito da AsyncButton
    const buttons = wrapper.findAll('button');
    const finalDeleteBtn = buttons.find(b => b.text() === 'Conferma eliminazione');
    await finalDeleteBtn.trigger('click');
    
    await flushPromises();

    // Verifichiamo che sia partita la chiamata DELETE corretta
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(defaultProps.deleteUrl, {
      method: 'DELETE'
    });

    // Verifichiamo il reindirizzamento finale
    expect(window.location.href).toBe(defaultProps.redirectUrl);
  });

  it('gestisce in sicurezza il fallimento del server senza effettuare il redirect', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: () => Promise.resolve({ error: 'Permesso negato' })
    });

    const wrapper = mount(AssetDeleteWidget, { props: defaultProps });
    
    await wrapper.find('button.btn-red').trigger('click');

    const buttons = wrapper.findAll('button');
    const finalDeleteBtn = buttons.find(b => b.text() === 'Conferma eliminazione');
    await finalDeleteBtn.trigger('click');
    
    await flushPromises();

    // L'errore è stato generato e gestito dal componente (o lanciato ad AsyncButton)
    expect(global.fetch).toHaveBeenCalledTimes(1);
    
    // La sicurezza prima di tutto: NON ci deve essere nessun redirect
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });
});