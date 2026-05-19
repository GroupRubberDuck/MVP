// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import AsyncButton from '../../../src/components/AsyncButton.vue';

// --- AsyncButton Component ---------------------------------------------------

describe('AsyncButton', () => {
  it('dovrebbe renderizzare con le props predefinite', () => {
    const wrapper = mount(AsyncButton, {
      props: {
        action: vi.fn().mockResolvedValue(true)
      }
    });

    const button = wrapper.find('button');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('Conferma');
    expect(button.attributes('disabled')).toBeUndefined(); // Non è disabilitato all'inizio
    expect(wrapper.find('.error-text').exists()).toBe(false); // Nessun errore
  });

  it('dovrebbe renderizzare con etichette e classi personalizzate', () => {
    const wrapper = mount(AsyncButton, {
      props: {
        action: vi.fn().mockResolvedValue(true),
        label: 'Salva Dati',
        buttonClass: 'btn-primary custom-class'
      }
    });

    const button = wrapper.find('button');
    expect(button.text()).toBe('Salva Dati');
    expect(button.classes()).toContain('btn-primary');
    expect(button.classes()).toContain('custom-class');
  });

  it('dovrebbe disabilitare il pulsante e mostrare l\'etichetta di caricamento mentre l\'azione è in esecuzione', async () => {
    // Creiamo una Promise che non si risolve subito per poter ispezionare lo stato "Durante"
    let resolveAction;
    const pendingAction = vi.fn(() => new Promise(resolve => { resolveAction = resolve; }));

    const wrapper = mount(AsyncButton, {
      props: {
        action: pendingAction,
        label: 'Invia',
        loadingLabel: 'Attendere prego...'
      }
    });

    const button = wrapper.find('button');
    
    // Clicchiamo il bottone
    await button.trigger('click');

    // VERIFICA DELLO STATO INTERMEDIO (LOADING)
    expect(button.attributes('disabled')).toBeDefined(); // Il bottone ora è bloccato
    expect(button.text()).toBe('Attendere prego...');
    expect(pendingAction).toHaveBeenCalledTimes(1);

    // Ora sblocchiamo la Promise
    resolveAction('successo');
    await flushPromises();

    // VERIFICA DELLO STATO FINALE
    expect(button.attributes('disabled')).toBeUndefined(); // Bottone sbloccato
    expect(button.text()).toBe('Invia'); // Testo originale ripristinato
  });

  it('dovrebbe impedire clic multipli durante il caricamento (protezione della concorrenza)', async () => {
    const slowAction = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)));

    const wrapper = mount(AsyncButton, {
      props: { action: slowAction }
    });

    const button = wrapper.find('button');
    
    // L'utente clicca disperatamente 3 volte di fila velocissimo
    await button.trigger('click');
    await button.trigger('click');
    await button.trigger('click');

    // La funzione deve essere stata chiamata SOLO UNA volta, perché alla prima il bottone si è bloccato
    expect(slowAction).toHaveBeenCalledTimes(1);
  });

  it('dovrebbe emettere "success" con il risultato quando l\'azione si risolve con successo', async () => {
    const mockResult = { id: 42, status: 'ok' };
    const successAction = vi.fn().mockResolvedValue(mockResult);

    const wrapper = mount(AsyncButton, {
      props: { action: successAction }
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Verifica che l'evento custom @success sia stato emesso con i dati restituiti dall'azione
    expect(wrapper.emitted('success')).toBeTruthy();
    expect(wrapper.emitted('success')[0][0]).toEqual(mockResult);
    
    // Nessun errore visibile
    expect(wrapper.find('.error-text').exists()).toBe(false);
  });

  it('dovrebbe emettere "error" e mostrare il messaggio di errore quando l\'azione fallisce', async () => {
    const errorMessage = 'Connessione al server persa';
    const failingAction = vi.fn().mockRejectedValue(new Error(errorMessage));

    const wrapper = mount(AsyncButton, {
      props: { action: failingAction }
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    // 1. Verifica emissione evento di errore
    expect(wrapper.emitted('error')).toBeTruthy();
    expect(wrapper.emitted('error')[0][0]).toBeInstanceOf(Error);
    expect(wrapper.emitted('error')[0][0].message).toBe(errorMessage);

    // 2. Verifica feedback visivo 
    const errorSpan = wrapper.find('.error-text');
    expect(errorSpan.exists()).toBe(true);
    expect(errorSpan.text()).toBe(errorMessage);
  });

  it('dovrebbe cancellare gli errori precedenti quando viene avviata una nuova azione', async () => {
    // Prima fallisce, poi ha successo
    let shouldFail = true;
    const toggleAction = vi.fn(async () => {
      if (shouldFail) {
        shouldFail = false;
        throw new Error('Errore temporaneo');
      }
      return 'ok';
    });

    const wrapper = mount(AsyncButton, {
      props: { action: toggleAction }
    });

    // 1° Click: Fallisce
    await wrapper.find('button').trigger('click');
    await flushPromises();
    expect(wrapper.find('.error-text').exists()).toBe(true); // L'errore è visibile

    // 2° Click: Parte di nuovo, quindi l'errore deve sparire subito
    await wrapper.find('button').trigger('click');
    
    // Prima di attendere flushPromises, controlliamo che l'errore sia sparito (pulizia stato iniziale)
    expect(wrapper.find('.error-text').exists()).toBe(false); 
  });
});