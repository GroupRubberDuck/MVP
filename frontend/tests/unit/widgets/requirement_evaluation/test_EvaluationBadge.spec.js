// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import EvaluationBadge from '../../../../src/widgets/requirement-evaluation/components/EvaluationBadge.vue';
import { useDecisionTreeStore } from '../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js';

vi.mock('../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js', () => ({
  useDecisionTreeStore: vi.fn(),
}));

// --- EvaluationBadge Component -----------------------------------------------

describe('EvaluationBadge', () => {
  // L'helper ora usa vi.mocked direttamente dal modulo 'vi' già presente
  const mockStoreState = (stateValue) => {
    vi.mocked(useDecisionTreeStore).mockReturnValue({
      evaluationState: stateValue,
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renderizza Correttamente Lo Stato Pass', () => {
    mockStoreState('pass');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-pass');
    expect(wrapper.find('.badge-icon').text()).toBe('✓');
    expect(wrapper.find('.badge-label').text()).toBe('Pass');
    expect(wrapper.attributes('title')).toBe('Evaluation: Pass');
  });

  it('renderizza Correttamente Lo Stato Fail', () => {
    mockStoreState('fail');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-fail');
    expect(wrapper.find('.badge-icon').text()).toBe('✗');
    expect(wrapper.find('.badge-label').text()).toBe('Fail');
  });

  it('renderizza Correttamente Lo Stato Not Applicable', () => {
    mockStoreState('not_applicable');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-na');
    expect(wrapper.find('.badge-icon').text()).toBe('—');
    expect(wrapper.find('.badge-label').text()).toBe('N/A');
  });

  it('renderizza Correttamente Lo Stato Pending', () => {
    mockStoreState('pending');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-pending');
    expect(wrapper.find('.badge-icon').text()).toBe('⏳');
    expect(wrapper.find('.badge-label').text()).toBe('Pending');
  });

  it('renderizza Correttamente Lo Stato Not Evaluated', () => {
    mockStoreState('not_evaluated');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-not-evaluated');
    expect(wrapper.find('.badge-icon').text()).toBe('○');
    expect(wrapper.find('.badge-label').text()).toBe('Not Evaluated');
  });

  it('mostra Il Fallback Unknown Quando Lo Stato È Mancante O Non Valido', () => {
    // Simuliamo che il backend invii uno stato non mappato nel tuo dizionario
    mockStoreState('stato_strano_e_non_previsto');
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-unknown');
    expect(wrapper.find('.badge-icon').text()).toBe('?');
    // Il label usa direttamente il nome dello stato sconosciuto per aiutarti a fare debug
    expect(wrapper.find('.badge-label').text()).toBe('stato_strano_e_non_previsto');
  });

  it('mostra Il Fallback Unknown Quando Lo Stato È Esplicitamente Null', () => {
    mockStoreState(null);
    const wrapper = mount(EvaluationBadge);

    expect(wrapper.classes()).toContain('badge-unknown');
    expect(wrapper.find('.badge-icon').text()).toBe('?');
    expect(wrapper.find('.badge-label').text()).toBe('Unknown');
  });
});