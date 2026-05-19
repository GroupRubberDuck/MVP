// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, afterEach } from 'vitest';
import BaseModal from '../../../src/components/BaseModal.vue';

// --- BaseModal Component -----------------------------------------------------

describe('BaseModal', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('dovrebbe renderizzare il contenuto dello slot predefinito correttamente', () => {
    const wrapper = mount(BaseModal, {
      slots: {
        default: '<div class="test-content">Contenuto Dinamico Modal</div>'
      }
    });

    const content = wrapper.find('.test-content');
    expect(content.exists()).toBe(true);
    expect(content.text()).toBe('Contenuto Dinamico Modal');
  });

  it('dovrebbe applicare la prop personalizzata contentClass al div del contenuto interno', () => {
    const wrapper = mount(BaseModal, {
      props: {
        contentClass: 'custom-modal-size'
      }
    });

    const contentDiv = wrapper.find('.base-modal-content');
    expect(contentDiv.classes()).toContain('custom-modal-size');
  });

  it('dovrebbe emettere "close" quando l\'overlay viene cliccato direttamente', async () => {
    const wrapper = mount(BaseModal);
    
    const overlay = wrapper.find('.base-modal-overlay');
    // Vue Test Utils imposta target === currentTarget quando triggeriamo direttamente l'elemento
    await overlay.trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
    expect(wrapper.emitted('close').length).toBe(1);
  });

  it('non dovrebbe emettere "close" quando viene cliccato il contenuto interno (previene il collasso da bubbling)', async () => {
    const wrapper = mount(BaseModal, {
      slots: { default: '<button id="inner-btn">Cliccami</button>' }
    });

    // Clicchiamo un elemento figlio (simulando l'interazione col form interno)
    const innerBtn = wrapper.find('#inner-btn');
    await innerBtn.trigger('click');

    // Il click "rimbalza" fino all'overlay, ma siccome target !== currentTarget, la chiusura viene bloccata
    expect(wrapper.emitted('close')).toBeFalsy();
  });

  it('dovrebbe emettere "close" quando viene premuto il tasto Escape ovunque nel documento', () => {
    const wrapper = mount(BaseModal);

    // Creiamo un finto evento da tastiera
    const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
    document.dispatchEvent(escapeEvent); // Lo spariamo globalmente sul document

    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('non dovrebbe emettere "close" quando vengono premuti altri tasti', () => {
    const wrapper = mount(BaseModal);

    const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
    document.dispatchEvent(enterEvent);

    expect(wrapper.emitted('close')).toBeFalsy();
  });

  it('dovrebbe ripulire l\'event listener keydown quando il componente viene smontato', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener');
    
    const wrapper = mount(BaseModal);
    
    // Distruggiamo il componente (simulando v-if = false dal padre)
    wrapper.unmount();

    // Verifichiamo che abbia fatto pulizia rimuovendo l'ascoltatore di eventi
    expect(removeEventListenerSpy).toHaveBeenCalledTimes(1);
    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
  });
});