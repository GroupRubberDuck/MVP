// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Toast from '../../../src/components/Toast.vue';

// --- Toast Component ---------------------------------------------------------

describe('Toast', () => {
  beforeEach(() => {
    // Attiviamo i finti timer di Vitest prima di ogni test
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Ripristiniamo l'orologio reale alla fine
    vi.useRealTimers();
  });

  it('dovrebbe renderizzare il messaggio di testo fornito tramite la prop "message"', () => {
    const wrapper = mount(Toast, {
      props: {
        message: 'Salvataggio completato con successo!'
      }
    });

    // Verifica che il testo sia visualizzato nel DOM
    expect(wrapper.text()).toContain('Salvataggio completato con successo!');
    // Verifica che abbia la classe corretta
    expect(wrapper.classes()).toContain('toast');
  });

  it('dovrebbe emettere l\'evento "close" automaticamente dopo la durata predefinita (3000ms)', () => {
    const wrapper = mount(Toast, {
      props: {
        message: 'Timeout standard'
      }
    });

    // Appena montato, l'evento 'close' NON deve essere stato emesso
    expect(wrapper.emitted('close')).toBeUndefined();

    // Mandiamo avanti il tempo artificialmente di 2999 millisecondi (manca 1ms)
    vi.advanceTimersByTime(2999);
    expect(wrapper.emitted('close')).toBeUndefined();

    // Mandiamo avanti il tempo dell'ultimo millisecondo (totale 3000)
    vi.advanceTimersByTime(1);

    //  Ora l'evento deve essere partito per dire al padre di rimuovere il componente
    expect(wrapper.emitted('close')).toBeTruthy();
    expect(wrapper.emitted('close').length).toBe(1);
  });

  it('dovrebbe emettere l\'evento "close" correttamente quando viene fornita una durata personalizzata', () => {
    const customTime = 1500;
    const wrapper = mount(Toast, {
      props: {
        message: 'Timeout veloce',
        duration: customTime
      }
    });

    // Viaggiamo nel tempo fermandoci 1ms prima della durata custom
    vi.advanceTimersByTime(customTime - 1);
    expect(wrapper.emitted('close')).toBeUndefined();

    // Passato l'ultimo millisecondo...
    vi.advanceTimersByTime(1);
    
    // Il toast emette l'evento chiusura al nuovo tempo stabilito
    expect(wrapper.emitted('close')).toBeTruthy();
  });
});