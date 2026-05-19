// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import FileDropZone from '../../../src/components/FileDropZone.vue';

// --- FileDropZone Component --------------------------------------------------

describe('FileDropZone', () => {
  // Helper per creare un file fittizio per i test
  const createMockFile = (name, size = 1024, type = 'text/plain') => {
    const file = new File([''], name, { type });
    Object.defineProperty(file, 'size', { value: size });
    return file;
  };

  it('renders default placeholder and hidden file input', () => {
    const wrapper = mount(FileDropZone);
    
    // Verifica il testo di default
    expect(wrapper.text()).toContain('Clicca per caricare o trascina il file');
    
    // Verifica l'input nascosto
    const fileInput = wrapper.find('input[type="file"]');
    expect(fileInput.exists()).toBe(true);
    expect(fileInput.attributes('accept')).toBe('');
  });

  it('applies dragging classes during dragover and dragleave events', async () => {
    const wrapper = mount(FileDropZone);
    const dropZone = wrapper.find('.file-drop-zone');

    // Inizialmente non c'è la classe dragging
    expect(dropZone.classes()).not.toContain('file-drop-zone--dragging');

    // L'utente trascina un file sopra
    await dropZone.trigger('dragover');
    expect(dropZone.classes()).toContain('file-drop-zone--dragging');

    // L'utente esce dalla zona senza rilasciare il file
    await dropZone.trigger('dragleave');
    expect(dropZone.classes()).not.toContain('file-drop-zone--dragging');
  });

  it('handles standard file selection via click and emits "select"', async () => {
    const wrapper = mount(FileDropZone);
    const fileInput = wrapper.find('input[type="file"]');
    
    const mockFile = createMockFile('config.json');

    // In JSDOM, simulare la selezione di un file richiede la sovrascrittura manuale della proprietà 'files'
    Object.defineProperty(fileInput.element, 'files', {
      value: [mockFile]
    });

    // Simuliamo l'evento change
    await fileInput.trigger('change');

    // Verifica emissione evento
    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')[0][0].name).toBe('config.json');

    // Verifica aggiornamento UI (mostra nome e dimensione formattata)
    expect(wrapper.text()).toContain('config.json');
    expect(wrapper.text()).toContain('(1 KB)');
  });

  it('handles drag and drop of an accepted file and emits "select"', async () => {
    const wrapper = mount(FileDropZone, {
      props: { accept: '.json, .xml' }
    });
    const dropZone = wrapper.find('.file-drop-zone');
    
    const mockFile = createMockFile('data.json', 1048576); // 1 MB

    // Simuliamo l'evento drop includendo il finto dataTransfer
    await dropZone.trigger('drop', {
      dataTransfer: { files: [mockFile] }
    });

    // Evento emesso
    expect(wrapper.emitted('select')).toBeTruthy();
    // UI aggiornata
    expect(wrapper.text()).toContain('data.json');
    expect(wrapper.text()).toContain('(1 MB)'); // Verifica anche la conversione di formatSize
  });

  it('rejects a dropped file if the extension is not in the accept list and emits "error"', async () => {
    const wrapper = mount(FileDropZone, {
      props: { accept: '.csv, .xml' }
    });
    const dropZone = wrapper.find('.file-drop-zone');
    
    const mockFile = createMockFile('virus.exe');

    await dropZone.trigger('drop', {
      dataTransfer: { files: [mockFile] }
    });

    // NON deve emettere select
    expect(wrapper.emitted('select')).toBeFalsy();
    
    // DEVE emettere error con il messaggio appropriato
    expect(wrapper.emitted('error')).toBeTruthy();
    expect(wrapper.emitted('error')[0][0]).toBe('Formato file non valido.');
    
    // L'UI deve rimanere nello stato iniziale
    expect(wrapper.text()).not.toContain('virus.exe');
  });

  it('ignores drop events when the component is disabled', async () => {
    const wrapper = mount(FileDropZone, {
      props: { disabled: true }
    });
    const dropZone = wrapper.find('.file-drop-zone');
    
    const mockFile = createMockFile('test.txt');

    await dropZone.trigger('drop', {
      dataTransfer: { files: [mockFile] }
    });

    // Nessun evento emesso, il componente è morto per l'utente
    expect(wrapper.emitted('select')).toBeFalsy();
    expect(wrapper.emitted('error')).toBeFalsy();
  });

  it('resets the selection when the exposed reset() method is called', async () => {
    const wrapper = mount(FileDropZone);
    const mockFile = createMockFile('temp.txt');

    // 1. Inseriamo un file forzatamente
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', { value: [mockFile] });
    await wrapper.find('input[type="file"]').trigger('change');
    
    // Verifichiamo che sia stato preso
    expect(wrapper.text()).toContain('temp.txt');

    // 2. Chiamiamo il metodo reset esposto tramite defineExpose
    wrapper.vm.reset();
    
    // Dobbiamo attendere un tick di Vue per l'aggiornamento del DOM
    await wrapper.vm.$nextTick();

    // 3. Verifichiamo che l'UI sia tornata allo stato iniziale
    expect(wrapper.text()).not.toContain('temp.txt');
    expect(wrapper.text()).toContain('Clicca per caricare o trascina il file');
  });
});