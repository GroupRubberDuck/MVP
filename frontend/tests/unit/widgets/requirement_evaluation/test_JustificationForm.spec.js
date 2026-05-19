// @vitest-environment jsdom

import { mount, flushPromises } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reactive } from 'vue';
import JustificationForm from '../../../../src/widgets/requirement-evaluation/components/JustificationForm.vue';
import { useDecisionTreeStore } from '../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js';

// Creiamo uno store fittizio reattivo globale per il file di test
const mockStore = reactive({
  justification: 'Giustificazione iniziale',
  justificationStatus: 'idle',
  saveJustification: vi.fn()
});

// Mockiamo il modulo dello store restituendo l'oggetto reattivo controllabile
vi.mock('../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js', () => ({
  useDecisionTreeStore: () => mockStore,
}));

// --- JustificationForm Component --------------------------------------------

describe('JustificationForm', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
    // Ripristiniamo lo stato di default dello store prima di ogni test
    mockStore.justification = 'Giustificazione iniziale';
    mockStore.justificationStatus = 'idle';
    mockStore.saveJustification.mockReset().mockResolvedValue(true);
  });

  it('dovrebbe renderizzare la giustificazione iniziale dello store e disabilitare i pulsanti di azione', () => {
    const wrapper = mount(JustificationForm);

    const textarea = wrapper.find('textarea');
    expect(textarea.element.value).toBe('Giustificazione iniziale');

    // All'avvio, non essendoci modifiche (isDirty = false), i bottoni devono essere disabilitati
    const cancelBtn = wrapper.find('.btn-secondary');
    const saveBtn = wrapper.find('.btn-primary');
    
    expect(cancelBtn.attributes('disabled')).toBeDefined();
    expect(saveBtn.attributes('disabled')).toBeDefined();
    expect(wrapper.find('.status-text').exists()).toBe(false);
  });

  it('dovrebbe abilitare i pulsanti quando l\'utente digita delle modifiche (isDirty passa a true)', async () => {
    const wrapper = mount(JustificationForm);
    const textarea = wrapper.find('textarea');

    // L'utente modifica il testo
    await textarea.setValue('Nuova giustificazione modificata');

    const cancelBtn = wrapper.find('.btn-secondary');
    const saveBtn = wrapper.find('.btn-primary');

    // Ora lo stato è dirty: i bottoni si devono attivare
    expect(cancelBtn.attributes('disabled')).toBeUndefined();
    expect(saveBtn.attributes('disabled')).toBeUndefined();
  });

  it('dovrebbe sincronizzare il testo locale quando la giustificazione dello store cambia esternamente', async () => {
    const wrapper = mount(JustificationForm);
    
    // Simuliamo che lo store venga aggiornato da un'azione esterna (es. cambio nodo dell'albero)
    mockStore.justification = 'Aggiornato da fuori';
    
    // Attendiamo che i watcher di Vue processino la modifica reattiva
    await wrapper.vm.$nextTick();

    const textarea = wrapper.find('textarea');
    expect(textarea.element.value).toBe('Aggiornato da fuori');
  });

  it('dovrebbe chiamare store.saveJustification e aggiornare lo stato dirty al momento dell\'invio', async () => {
    const wrapper = mount(JustificationForm);
    const textarea = wrapper.find('textarea');

    await textarea.setValue('Testo da salvare');
    
    // Clicchiamo sul bottone di salvataggio
    await wrapper.find('.btn-primary').trigger('click');

    // 1. Deve aver chiamato il metodo del Pinia Store con il testo locale corretto
    expect(mockStore.saveJustification).toHaveBeenCalledTimes(1);
    expect(mockStore.saveJustification).toHaveBeenCalledWith('Testo da salvare');

    // 2. Dopo il submit, isDirty deve tornare false, rispegnete i bottoni
    expect(wrapper.find('.btn-primary').attributes('disabled')).toBeDefined();
  });

  it('dovrebbe ripristinare il testo locale al valore dello store quando viene cliccato il pulsante di annullamento', async () => {
    const wrapper = mount(JustificationForm);
    const textarea = wrapper.find('textarea');

    // Modifichiamo e poi ci ripensiamo
    await textarea.setValue('Scrivo una cavolata...');
    expect(textarea.element.value).toBe('Scrivo una cavolata...');

    // Clicchiamo su Cancel
    await wrapper.find('.btn-secondary').trigger('click');

    // Il testo deve essere tornato a quello presente originariamente nello store
    expect(textarea.element.value).toBe('Giustificazione iniziale');
    expect(wrapper.find('.btn-secondary').attributes('disabled')).toBeDefined();
  });

  it('dovrebbe renderizzare i messaggi di stato corretti in base alla configurazione dello stato dello store', async () => {
    const wrapper = mount(JustificationForm);

    // 1. Stato SAVING
    mockStore.justificationStatus = 'saving';
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.status-saving').text()).toBe('Saving…');
    // Il bottone Save deve bloccarsi durante il salvataggio per prevenire chiamate multiple
    expect(wrapper.find('.btn-primary').attributes('disabled')).toBeDefined();

    // 2. Stato SAVED (senza modifiche locali)
    mockStore.justificationStatus = 'saved';
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.status-saved').text()).toContain('✓ Saved');

    // 3. Stato ERROR
    mockStore.justificationStatus = 'error';
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.status-error').text()).toContain('✗ Error saving');
  });
});