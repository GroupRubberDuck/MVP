// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reactive } from 'vue';
import RequirementEvaluationWidget from '@/widgets/requirement-evaluation/RequirementEvaluationWidget.vue';
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js';
import { EvaluationApiClient } from '@/widgets/requirement-evaluation/api/EvaluationApiClient.js';

// 1. Mock dello store globale reattivo
const mockStore = reactive({
  isSideBarOpen: false,
  init: vi.fn(),
});

vi.mock('@/widgets/requirement-evaluation/store/decisionTreeStore.js', () => ({
  useDecisionTreeStore: () => mockStore,
}));

// 2. Mock della classe ApiClient
vi.mock('@/widgets/requirement-evaluation/api/EvaluationApiClient.js', () => {
  return {
    EvaluationApiClient: class {
      constructor(urls) {
        this.urls = urls;
      }
    }
  };
});

// --- RequirementEvaluationWidget Test Suite ---------------------------------

describe('RequirementEvaluationWidget', () => {
  
  const defaultProps = {
    treeData: { id: 'T1', nodes: [] },
    urls: {
      answer: '/api/ans',
      state: '/api/st',
      justification: '/api/just',
      detail: '/api/det'
    },
    savedAnswers: { N1: true },
    evaluationState: 'pending',
    justification: 'Nota iniziale di test',
    requirementsUrl: '/back-to-requirements'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.isSideBarOpen = false;
    mockStore.init.mockReset();
  });

  it('Istanzia EvaluationApiClient E Inizializza Lo Store Al Mounted', () => {
    mount(RequirementEvaluationWidget, {
      props: defaultProps,
      global: {
        stubs: {
          EvaluationBadge: true,
          DecisionTreeWidget: true,
          JustificationForm: true,
          TreeSidebar: true,
        }
      }
    });

    expect(mockStore.init).toHaveBeenCalledTimes(1);

    expect(mockStore.init).toHaveBeenCalledWith({
      treeData: defaultProps.treeData,
      savedAnswers: defaultProps.savedAnswers,
      evaluationState: defaultProps.evaluationState,
      justification: defaultProps.justification,
      requirementsUrl: defaultProps.requirementsUrl,
      apiClient: expect.any(EvaluationApiClient),
    });
  });

  it('Renderizza Correttamente I Moduli Principali Del Layout', () => {
    const wrapper = mount(RequirementEvaluationWidget, {
      props: defaultProps,
      global: {
        stubs: {
          EvaluationBadge: true,
          DecisionTreeWidget: true,
          JustificationForm: true,
          TreeSidebar: true,
        }
      }
    });

    expect(
      wrapper.findComponent({ name: 'EvaluationBadge' }).exists()
    ).toBe(true);

    expect(
      wrapper.findComponent({ name: 'DecisionTreeWidget' }).exists()
    ).toBe(true);

    expect(
      wrapper.findComponent({ name: 'JustificationForm' }).exists()
    ).toBe(true);
  });

  it('Mostra O Nasconde La Sidebar In Base Allo Stato Dello Store', async () => {
    const wrapper = mount(RequirementEvaluationWidget, {
      props: defaultProps,
      global: {
        stubs: {
          EvaluationBadge: true,
          DecisionTreeWidget: true,
          JustificationForm: true,
          TreeSidebar: true,
        }
      }
    });

    // Sidebar inizialmente nascosta
    expect(
      wrapper.find('.requirement-evaluation__sidebar').exists()
    ).toBe(false);

    // Apertura sidebar
    mockStore.isSideBarOpen = true;
    await wrapper.vm.$nextTick();

    const sidebarContainer = wrapper.find(
      '.requirement-evaluation__sidebar'
    );

    expect(sidebarContainer.exists()).toBe(true);

    expect(
      sidebarContainer.findComponent({ name: 'TreeSidebar' }).exists()
    ).toBe(true);
  });
});