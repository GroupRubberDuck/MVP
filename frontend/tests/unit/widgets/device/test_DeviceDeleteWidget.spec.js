// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DeviceDeleteWidget from '../../../../src/DeviceDeleteWidget.vue';

// --- DeviceDeleteWidget ------------------------------------------------------

describe('DeviceDeleteWidget', () => {
  const defaultProps = {
    deviceName: 'Firewall Principale',
    deleteUrl: '/api/devices/456/delete',
    exportBaseUrl: '/api/devices/456/export',
    redirectUrl: '/devices/dashboard'
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

  it('Mostra il pulsante iniziale di eliminazione e apre il modale al click', async () => {
    const wrapper = mount(DeviceDeleteWidget, { props: defaultProps });
    
    // Inizialmente il modale non c'è, c'è solo il bottone principale
    const openBtn = wrapper.find('button.btn-red');
    expect(openBtn.exists()).toBe(true);
    expect(wrapper.text()).not.toContain('Questa operazione è irreversibile.');

    // Clicchiamo per aprire il modale
    await openBtn.trigger('click');

    // Ora il modale dovrebbe essere visibile con il nome del dispositivo
    expect(wrapper.text()).toContain('Questa operazione è irreversibile.');
    expect(wrapper.text()).toContain(defaultProps.deviceName);
  });

  it('Chiude il modale quando viene cliccato Annulla', async () => {
    const wrapper = mount(DeviceDeleteWidget, { props: defaultProps });
    
    // Apriamo il modale
    await wrapper.find('button.btn-red').trigger('click');
    expect(wrapper.text()).toContain('Questa operazione è irreversibile.');

    // Troviamo il bottone "Annulla" (è l'ultimo bottone del modale nel template)
    const buttons = wrapper.findAll('button');
    const cancelBtn = buttons[buttons.length - 1];
    
    // Clicchiamo annulla e verifichiamo che il testo del modale sparisca
    await cancelBtn.trigger('click');
    expect(wrapper.text()).not.toContain('Questa operazione è irreversibile.');
  });

 it('Genera il link di download corretto ed esegue il click per l’esportazione', async () => {
    const wrapper = mount(DeviceDeleteWidget, { props: defaultProps });
    
    // Spiamo appendChild e removeChild ma li lasciamo funzionare normalmente
    const appendChildSpy = vi.spyOn(document.body, 'appendChild');
    const removeChildSpy = vi.spyOn(document.body, 'removeChild');
    
    await wrapper.find('button.btn-red').trigger('click');

    // Cambiamo il formato nel menu a tendina da 'json' a 'xml'
    const select = wrapper.find('select');
    await select.setValue('xml');

    // Clicchiamo il bottone "Esporta"
    const buttons = wrapper.findAll('button');
    const exportBtn = buttons.find(b => b.text() === 'Esporta');
    await exportBtn.trigger('click');

    // Troviamo il link tra tutti gli elementi che sono stati "appesi" (append) al body
    const appendedLink = appendChildSpy.mock.calls.find(call => call[0].tagName === 'A')[0];
    
    // Verifichiamo che esista e abbia l'url corretto
    expect(appendedLink).toBeDefined();
    expect(appendedLink.href).toContain(`${defaultProps.exportBaseUrl}?extension=xml`);
    expect(appendedLink.getAttribute('download')).toBe('');
    
    // Verifica che sia stato rimosso per fare pulizia
    expect(removeChildSpy).toHaveBeenCalledWith(appendedLink);
  });
  
  it('Invia la richiesta DELETE ed esegue il redirect in caso di successo', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const wrapper = mount(DeviceDeleteWidget, { props: defaultProps });
    await wrapper.find('button.btn-red').trigger('click');

    // Clicchiamo il bottone finale "Elimina" gestito da AsyncButton
    const buttons = wrapper.findAll('button');
    const finalDeleteBtn = buttons.find(b => b.text() === 'Elimina');
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

  it('Gestisce in sicurezza il fallimento del server durante l’eliminazione senza effettuare il redirect', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: 'Dispositivo protetto, impossibile eliminare' })
    });

    const wrapper = mount(DeviceDeleteWidget, { props: defaultProps });
    await wrapper.find('button.btn-red').trigger('click');

    const buttons = wrapper.findAll('button');
    const finalDeleteBtn = buttons.find(b => b.text() === 'Elimina');
    await finalDeleteBtn.trigger('click');
    await flushPromises();

    // L'errore è stato generato e gestito da AsyncButton (o lanciato), ma non c'è stato redirect
    expect(window.location.href).not.toBe(defaultProps.redirectUrl);
  });
});