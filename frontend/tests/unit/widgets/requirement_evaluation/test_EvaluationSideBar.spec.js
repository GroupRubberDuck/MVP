// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reactive } from 'vue';
import EvaluationSideBar from '@/widgets/requirement-evaluation/components/TreeSidebar.vue';
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js';

// Prepariamo uno store fittizio reattivo completo
const mockStore = reactive({
  isSideBarOpen: false,
  selectedNodeId: null,
  selectedNodeData: null,
  requirementsUrl: '/mock-requirements-path',
  answers: new Map(),
  setAnswer: vi.fn(),
  selectNode: vi.fn(),
  closeSideBar: vi.fn()
});

// Mockiamo il modulo dello store
vi.mock('@/widgets/requirement-evaluation/store/decisionTreeStore.js', () => ({
  useDecisionTreeStore: () => mockStore,
}));

// --- EvaluationSideBar Component --------------------------------------------

describe('EvaluationSideBar', () => {

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset dello stato iniziale dello store
    mockStore.isSideBarOpen = false;
    mockStore.selectedNodeId = null;
    mockStore.selectedNodeData = null;
    mockStore.answers.clear();
    mockStore.setAnswer.mockReset().mockResolvedValue(true);
    mockStore.selectNode.mockReset();
    mockStore.closeSideBar.mockReset();
  });

  it('Non Renderizza La Sidebar Se IsSideBarOpen È False O CurrentNode È Assente', () => {
    mockStore.isSideBarOpen = false;
    mockStore.selectedNodeData = { id: 'N1', type: 'decision' };
    
    let wrapper = mount(EvaluationSideBar);
    expect(wrapper.find('.tree-sidebar').exists()).toBe(false);

    mockStore.isSideBarOpen = true;
    mockStore.selectedNodeData = null;
    
    wrapper = mount(EvaluationSideBar);
    expect(wrapper.find('.tree-sidebar').exists()).toBe(false);
  });

  it('Renderizza Correttamente Un Nodo Decision Con Domanda E Stati Di Selezione', async () => {
    mockStore.isSideBarOpen = true;
    mockStore.selectedNodeId = 'N1';
    mockStore.selectedNodeData = {
      id: 'N1',
      type: 'decision',
      text: 'Il sistema tratta dati personali?',
      parentId: null
    };

    const wrapper = mount(EvaluationSideBar);

    expect(wrapper.find('.sidebar-title').text()).toBe('Question');
    expect(wrapper.find('.question-text').text()).toBe('Il sistema tratta dati personali?');
    
    // All'inizio nessun bottone deve avere la classe 'selected'
    expect(wrapper.find('.btn-yes').classes()).not.toContain('selected');
    expect(wrapper.find('.btn-no').classes()).not.toContain('selected');

    // Simuliamo che l'utente abbia risposto "Sì" in precedenza
    mockStore.answers.set('N1', true);
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.btn-yes').classes()).toContain('selected');
    expect(wrapper.find('.btn-no').classes()).not.toContain('selected');
  });

  it('Richiama StoreSetAnswer Quando Si Cliccano I Pulsanti Di Risposta', async () => {
    mockStore.isSideBarOpen = true;
    mockStore.selectedNodeId = 'N1';
    mockStore.selectedNodeData = { id: 'N1', type: 'decision', text: 'Test?' };

    const wrapper = mount(EvaluationSideBar);

    // Clicchiamo su No
    await wrapper.find('.btn-no').trigger('click');
    expect(mockStore.setAnswer).toHaveBeenCalledWith('N1', false);

    // Clicchiamo su Sì
    await wrapper.find('.btn-yes').trigger('click');
    expect(mockStore.setAnswer).toHaveBeenCalledWith('N1', true);
  });

  it('Renderizza Correttamente Un Nodo Leaf Con Risultati Formattati E Link Di Reindirizzamento', () => {
    mockStore.isSideBarOpen = true;
    mockStore.selectedNodeId = 'L1';
    mockStore.selectedNodeData = {
      id: 'L1',
      type: 'leaf',
      resultState: 'not_applicable',
      parentId: 'N1'
    };

    const wrapper = mount(EvaluationSideBar);

    expect(wrapper.find('.sidebar-title').text()).toBe('Result');
    
    // Verifica il badge dell'esito formattato dal metodo del componente
    const badge = wrapper.find('.result-badge');
    expect(badge.text()).toBe('— Not Applicable');
    expect(badge.classes()).toContain('result-not_applicable');

    // Verifica il link di ritorno ai requisiti
    const link = wrapper.find('a');
    expect(link.attributes('href')).toBe('/mock-requirements-path');
  });

  describe('Navigation Logic', () => {
    it('Abilita O Disabilita Il Pulsante Previous In Base Alla Presenza Del ParentId', async () => {
      mockStore.isSideBarOpen = true;
      mockStore.selectedNodeId = 'N1';
      mockStore.selectedNodeData = { id: 'N1', type: 'decision', parentId: null };

      const wrapper = mount(EvaluationSideBar);
      
      // Senza parentId, il bottone Previous deve essere bloccato
      expect(wrapper.find('.btn-nav:first-child').attributes('disabled')).toBeDefined();

      // Forziamo la presenza di un nodo genitore
      mockStore.selectedNodeData.parentId = 'N0';
      await wrapper.vm.$nextTick();

      // Ora deve essere abilitato
      const prevBtn = wrapper.findAll('.btn-nav')[0];
      expect(prevBtn.attributes('disabled')).toBeUndefined();

      // Cliccando, deve richiamare la selezione del nodo padre nello store
      await prevBtn.trigger('click');
      expect(mockStore.selectNode).toHaveBeenCalledWith('N0');
    });

    it('Gestisce La Validazione Del Pulsante Next E La Navigazione Basata Su YES E NO', async () => {
      mockStore.isSideBarOpen = true;
      mockStore.selectedNodeId = 'N1';
      mockStore.selectedNodeData = {
        id: 'N1',
        type: 'decision',
        yesChildId: 'N2_YES',
        noChildId: 'L1_NO'
      };

      const wrapper = mount(EvaluationSideBar);
      const nextBtn = wrapper.find('.btn-nav-primary');

      // 1. Senza una risposta fornita, il bottone Next deve essere disabilitato
      expect(nextBtn.attributes('disabled')).toBeDefined();

      // 2. Simuliamo risposta FALSE (No) -> Deve sbloccare il bottone e puntare a noChildId
      mockStore.answers.set('N1', false);
      await wrapper.vm.$nextTick();
      expect(nextBtn.attributes('disabled')).toBeUndefined();

      await nextBtn.trigger('click');
      expect(mockStore.selectNode).toHaveBeenCalledWith('L1_NO');

      // 3. Simuliamo risposta TRUE (Sì) -> Deve puntare a yesChildId
      mockStore.answers.set('N1', true);
      await wrapper.vm.$nextTick();

      await nextBtn.trigger('click');
      expect(mockStore.selectNode).toHaveBeenCalledWith('N2_YES');
    });
  });

  it('Richiama StoreCloseSideBar Quando Si Clicca Il Pulsante Di Chiusura', async () => {
    mockStore.isSideBarOpen = true;
    mockStore.selectedNodeData = { id: 'N1', type: 'decision' };

    const wrapper = mount(EvaluationSideBar);
    
    await wrapper.find('.btn-close').trigger('click');
    expect(mockStore.closeSideBar).toHaveBeenCalledTimes(1);
  });
});