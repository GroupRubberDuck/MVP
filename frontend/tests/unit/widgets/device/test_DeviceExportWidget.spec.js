// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DeviceExportWidget from '../../../../src/widgets/device-export/DeviceExportWidget.vue';

// --- DeviceExportWidget ------------------------------------------------------

describe('DeviceExportWidget', () => {
  const defaultProps = {
    deviceName: 'Switch Core Sala CED',
    exportBaseUrl: '/api/devices/789/export'
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('Mostra inizialmente il pulsante di esportazione e mantiene nascosto il modale', () => {
    const wrapper = mount(DeviceExportWidget, { props: defaultProps });
    
    const openBtn = wrapper.find('button.btn--secondary');
    expect(openBtn.exists()).toBe(true);
    expect(openBtn.text()).toBe('Esporta dispositivo');
    
    // Il testo del modale non deve esserci all'avvio
    expect(wrapper.text()).not.toContain('Seleziona il formato per esportare');
  });

  it('Apre il modale al click, mostra il nome del dispositivo e reimposta il formato su json', async () => {
    const wrapper = mount(DeviceExportWidget, { props: defaultProps });
    
    await wrapper.find('button.btn--secondary').trigger('click');
    
    expect(wrapper.text()).toContain('Esporta Dispositivo');
    expect(wrapper.text()).toContain(defaultProps.deviceName);
    
    // Verifica che il menu a tendina sia resettato a 'json' di default
    const select = wrapper.find('select');
    expect(select.element.value).toBe('json');
  });

  it('Chiude il modale quando viene cliccato il pulsante Annulla', async () => {
    const wrapper = mount(DeviceExportWidget, { props: defaultProps });
    
    // Apriamo il modale
    await wrapper.find('button.btn--secondary').trigger('click');
    expect(wrapper.text()).toContain('Seleziona il formato per esportare');
    
    // Troviamo e clicchiamo "Annulla"
    const buttons = wrapper.findAll('button');
    const cancelBtn = buttons.find(b => b.text() === 'Annulla');
    await cancelBtn.trigger('click');
    
    // Il modale deve essere sparito
    expect(wrapper.text()).not.toContain('Seleziona il formato per esportare');
  });

  it('Genera il link di download corretto, esegue il click e chiude automaticamente il modale', async () => {
    const wrapper = mount(DeviceExportWidget, { props: defaultProps });
    
    const appendChildSpy = vi.spyOn(document.body, 'appendChild');
    const removeChildSpy = vi.spyOn(document.body, 'removeChild');
    
    // 1. Apriamo il modale
    await wrapper.find('button.btn--secondary').trigger('click');

    // 2. Cambiamo il formato in 'csv'
    const select = wrapper.find('select');
    await select.setValue('csv');

    // 3. Clicchiamo "Scarica File"
    const buttons = wrapper.findAll('button');
    const downloadBtn = buttons.find(b => b.text() === 'Scarica File');
    await downloadBtn.trigger('click');

    // 4. Verifichiamo la creazione del tag <a> con l'url composto correttamente
    const appendedLink = appendChildSpy.mock.calls.find(call => call[0].tagName === 'A')[0];
    expect(appendedLink).toBeDefined();
    expect(appendedLink.href).toContain(`${defaultProps.exportBaseUrl}?extension=csv`);
    expect(appendedLink.getAttribute('download')).toBe('');
    
    // 5. Verifichiamo che il link sia stato appeso e rimosso (pulizia)
    expect(appendChildSpy).toHaveBeenCalledWith(appendedLink);
    expect(removeChildSpy).toHaveBeenCalledWith(appendedLink);

    // 6. Verifichiamo che la funzione closeModal() sia stata chiamata alla fine
    expect(wrapper.text()).not.toContain('Seleziona il formato per esportare');
  });
});