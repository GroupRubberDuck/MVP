// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import UiDecisionNode from '@/widgets/requirement-evaluation/components/UiDecisionNode.vue';

// --- UiDecisionNode Component ------------------------------------------------

describe('UiDecisionNode', () => {

  it('dovrebbe renderizzare correttamente con le props predefinite', () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Domanda breve'
      }
    });

    // 1. Verifica che i testi siano presenti nel foreignObject
    expect(wrapper.find('.node-id').text()).toBe('N1');
    expect(wrapper.find('.node-text').text()).toContain('Domanda breve');

    // 2. Di default, non deve avere la classe attiva
    expect(wrapper.classes()).not.toContain('is-active');
  });

  it('dovrebbe calcolare le altezze e le coordinate in modo dinamico per un testo breve su una riga singola', () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Short',
        fontSize: 12 // charsPerLine = (200 - 40) / (12 * 0.6) = 160 / 7.2 = 22 caratteri
      }
    });

    // Spiegazione matematica del calcolo interno:
    // text length = 5 <= 22 -> 1 linea
    // textHeight = 1 * 12 * 1.4 = 16.8
    // nodeHeight = 16.8 + 40 = 56.8
    // rect :y = -56.8 / 2 = -28.4
    
    const rect = wrapper.find('rect');
    expect(rect.attributes('width')).toBe('200');
    expect(rect.attributes('height')).toBe('56.8');
    expect(rect.attributes('y')).toBe('-28.4');
  });

  it('dovrebbe incrementare l\'altezza del nodo correttamente quando il testo si estende su più righe', () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Questa è una stringa di testo volutamente molto lunga che supererà sicuramente i ventidue caratteri per riga impostati dall algoritmo',
        fontSize: 12
      }
    });

    // Essendo un testo molto lungo, deve generare più linee incrementando l'altezza del rect
    const rect = wrapper.find('rect');
    const height = parseFloat(rect.attributes('height'));
    
    // L'altezza per una riga sola era 56.8. Con questo testo deve essere decisamente maggiore
    expect(height).toBeGreaterThan(56.8);
  });

  it('dovrebbe applicare le classi attive quando la prop isActive è true', () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Test attivo',
        isActive: true
      }
    });

    // Deve agganciare la classe per cambiare colore al bordo/sfondo del nodo SVG
    expect(wrapper.classes()).toContain('is-active');
  });

  it('dovrebbe emettere "select" con l\'ID del nodo quando viene cliccato mentre è attivo', async () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Cliccami',
        isActive: true // Stato fondamentale per sbloccare il click
      }
    });

    // Clicchiamo sul gruppo <g> principale
    await wrapper.trigger('click');

    // Deve aver emesso l'evento verso il TreeCanvas padre passando il proprio ID
    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')[0][0]).toBe('N1');
  });

  it('non dovrebbe emettere "select" quando viene cliccato se isActive è false', async () => {
    const wrapper = mount(UiDecisionNode, {
      props: {
        id: 'N1',
        text: 'Non puoi cliccarmi',
        isActive: false // Blocco di sicurezza attivo
      }
    });

    await wrapper.trigger('click');

    // L'evento NON deve essere partito (protezione condizionale di onClick)
    expect(wrapper.emitted('select')).toBeFalsy();
  });
});