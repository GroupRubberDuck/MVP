// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import RequirementEvaluationWidget from '@/widgets/requirement-evaluation/RequirementEvaluationWidget.vue';
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js';
import { sampleTree } from '@/widgets/requirement-evaluation/fixtures.js';

vi.mock('@/widgets/requirement-evaluation/api/EvaluationApiClient.js', () => {
  return {
    EvaluationApiClient: class {
      saveAnswer = vi.fn().mockResolvedValue({ success: true });
      fetchState = vi.fn().mockResolvedValue({ evaluation: 'in_progress' });
      saveJustification = vi.fn().mockResolvedValue({ saved: true });
    }
  };
});

// --- RequirementEvaluationWidget (Integrazione Navigazione) ------------------

describe('Ecosistema RequirementEvaluation (Integrazione Navigazione)', () => {
  
  const defaultProps = {
    treeData: sampleTree,
    urls: { answer: '/api/a', state: '/api/s', justification: '/api/j', detail: '/api/d' },
    savedAnswers: {},
    evaluationState: 'not_evaluated',
    justification: '',
    requirementsUrl: '/custom-requirements-page-url' // L'URL di ritorno simulato
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Inizializziamo Pinia reale per l'integrazione dei componenti
    setActivePinia(createPinia());
  });

  // ─── FLUSSO 1: INTEGRAZIONE E TRASMISSIONE DELL'URL ALLA SIDEBAR ───

  it('dovrebbe trasmettere la prop requirementsUrl fino al tag anchor reale all\'interno della sidebar', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick(); // Attendiamo l'onMounted del widget

    // 1. Verifichiamo che lo store reale abbia assorbito l'URL dalle props del Widget padre
    const store = useDecisionTreeStore();
    expect(store.requirementsUrl).toBe('/custom-requirements-page-url');

    // 2. Cambiamo l'ID del nodo per spostarci su un nodo foglia (Esito)
    store.selectedNodeId = 'L1'; 
    await wrapper.vm.$nextTick(); // Attendiamo il re-render della Sidebar

    // 3. Andiamo a caccia del tag <a> reale dentro la Sidebar
    const backLink = wrapper.find('.tree-sidebar a');
    expect(backLink.exists()).toBe(true);

    // 4. CERTIFICAZIONE: Il tag HTML deve puntare esattamente all'indirizzo configurato
    expect(backLink.attributes('href')).toBe('/custom-requirements-page-url');
    expect(backLink.text()).toContain('Torna alla lista Requisiti');
  });

  // ─── FLUSSO 2: INTERCETTAZIONE DEL CLICK DI NAVIGAZIONE ───

  it('dovrebbe consentire il comportamento di navigazione predefinito quando il link di ritorno viene attivato dall\'utente', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick();

    const store = useDecisionTreeStore();
    // Impostiamo l'ID del nodo foglia per mostrare il link di ritorno
    store.selectedNodeId = 'L1';
    await wrapper.vm.$nextTick();

    const backLink = wrapper.find('.tree-sidebar a');
    
    // Simula il click sul link nativo
    const clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true });
    backLink.element.dispatchEvent(clickEvent);

    // Il test conferma che l'evento non viene bloccato da un e.preventDefault() errato 
    // all'interno della Sidebar, lasciando libero il browser di cambiare pagina
    expect(clickEvent.defaultPrevented).toBe(false);
  });
});