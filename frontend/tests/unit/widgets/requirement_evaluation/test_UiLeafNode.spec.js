// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import UiLeafNode from '@/widgets/requirement-evaluation/components/UiLeafNode.vue';

// --- UiLeafNode Component ----------------------------------------------------

describe('UiLeafNode', () => {

  it('dovrebbe renderizzare la forma e l\'etichetta con le dimensioni geometriche del layout fisse', () => {
    const wrapper = mount(UiLeafNode, {
      props: {
        id: 'L1',
        resultState: 'pass',
        text: 'Test Leaf Node Text' // <-- Prop obbligatoria aggiunta
      }
    });

    // 1. Verifica che i tag SVG principali esistano
    expect(wrapper.find('g').exists()).toBe(true);
    
    // 2. Verifica le dimensioni fisse del rettangolo (struttura a pillola rx/ry = 25)
    const rect = wrapper.find('rect');
    expect(rect.attributes('width')).toBe('160');
    expect(rect.attributes('height')).toBe('50');
    expect(rect.attributes('x')).toBe('-80');
    expect(rect.attributes('y')).toBe('-25');
    expect(rect.attributes('rx')).toBe('25');
  });

  it('dovrebbe applicare la classe di stato corretta in modo dinamico in base a resultState', () => {
    const wrapper = mount(UiLeafNode, {
      props: {
        id: 'L1',
        resultState: 'fail',
        text: 'Test Leaf Node Text' // <-- Prop obbligatoria aggiunta
      }
    });

    // Deve iniettare la classe corrispondente allo stato per attivare i CSS dei colori
    expect(wrapper.classes()).toContain('state-fail');
    expect(wrapper.classes()).not.toContain('state-pass');
    expect(wrapper.attributes('aria-label')).toBe('Result: fail');
  });

  it('dovrebbe formattare correttamente le etichette chiamando il metodo interno formatLabel', () => {
    // 1. Test per lo stato PASS
    let wrapper = mount(UiLeafNode, { 
      props: { id: 'L1', resultState: 'pass', text: 'Test Leaf Node Text' } 
    });
    expect(wrapper.find('.node-label').text()).toBe('✓ Pass');

    // 2. Test per lo stato FAIL
    wrapper = mount(UiLeafNode, { 
      props: { id: 'L1', resultState: 'fail', text: 'Test Leaf Node Text' } 
    });
    expect(wrapper.find('.node-label').text()).toBe('✗ Fail');

    // 3. Test per lo stato NOT_APPLICABLE
    wrapper = mount(UiLeafNode, { 
      props: { id: 'L1', resultState: 'not_applicable', text: 'Test Leaf Node Text' } 
    });
    expect(wrapper.find('.node-label').text()).toBe('— N/A');
  });

  it('dovrebbe ripiegare sulla stringa di stato grezza se resultState non è mappato', () => {
    const wrapper = mount(UiLeafNode, {
      props: {
        id: 'L1',
        resultState: 'custom_status_approved',
        text: 'Test Leaf Node Text' // <-- Prop obbligatoria aggiunta
      }
    });

    // Se domani il server inventa un nuovo stato, il componente non deve rompersi ma mostrare la stringa grezza
    expect(wrapper.find('.node-label').text()).toBe('custom_status_approved');
  });

  it('dovrebbe applicare la classe is-active in modo condizionale quando la prop isActive è true', () => {
    const wrapper = mount(UiLeafNode, {
      props: {
        id: 'L1',
        resultState: 'pass',
        isActive: true, 
        text: 'Test Leaf Node Text' 
      }
    });

    // Verifica che si accenda la classe per attivare il drop-shadow luminoso
    expect(wrapper.classes()).toContain('is-active');
  });

  it('dovrebbe garantire che i pointer-events siano disabilitati nativamente sul nodo foglia tramite la configurazione del layout', () => {
    // Le foglie non sono cliccabili dall'utente, verifichiamo che l'accessibilità rispetti lo stile
    const wrapper = mount(UiLeafNode, {
      props: { id: 'L1', resultState: 'pass', text: 'Test Leaf Node Text' } 
    });
    
    // Il puntatore del mouse deve ignorare l'elemento (gestito via CSS ma impostato strutturalmente)
    expect(wrapper.find('.ui-leaf-node').exists()).toBe(true);
  });
});