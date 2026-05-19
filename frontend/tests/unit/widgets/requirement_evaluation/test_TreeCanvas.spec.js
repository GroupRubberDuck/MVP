// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reactive } from 'vue';
import TreeCanvas from '../../../../src/widgets/requirement-evaluation/components/TreeCanvas.vue';
import { useDecisionTreeStore } from '../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js';

// Prepariamo dati fittizi strutturati accuratamente per testare i calcoli matematici
const mockStore = reactive({
  layoutResult: {
    nodes: [
      { id: 'N1', type: 'decision', text: 'Is it public?', x: 200, y: 100, resultState: null },
      { id: 'L1', type: 'leaf', text: 'Pass Leaf', x: 400, y: 300, resultState: 'pass' }
    ],
    edges: [
      { id: 'E1', sourceId: 'N1', targetId: 'L1', startX: 200, startY: 100, endX: 400, endY: 300, label: 'Yes' }
    ]
  },
  activePath: ['N1'],
  selectNode: vi.fn()
});

vi.mock('../../../../src/widgets/requirement-evaluation/store/decisionTreeStore.js', () => ({
  useDecisionTreeStore: () => mockStore,
}));

// --- TreeCanvas Component ----------------------------------------------------

describe('TreeCanvas', () => {

  beforeEach(() => {
    vi.clearAllMocks();

    mockStore.layoutResult.nodes = [
      { id: 'N1', type: 'decision', text: 'Is it public?', x: 200, y: 100, resultState: null },
      { id: 'L1', type: 'leaf', text: 'Pass Leaf', x: 400, y: 300, resultState: 'pass' }
    ];

    mockStore.layoutResult.edges = [
      { id: 'E1', sourceId: 'N1', targetId: 'L1', startX: 200, startY: 100, endX: 400, endY: 300, label: 'Yes' }
    ];

    mockStore.activePath = ['N1'];
    mockStore.selectNode.mockReset();
  });

  it('calcola correttamente il viewBox iniziale centrando tutti i nodi', () => {
    const wrapper = mount(TreeCanvas);
    const svg = wrapper.find('svg');

    expect(svg.attributes('viewBox')).toBe('-60 -130 720 660');
    expect(svg.element.style.height).toBe('660px');
  });

  it('renderizza gli archi con path Bezier e label corrette', () => {
    const wrapper = mount(TreeCanvas);

    const path = wrapper.find('.edge-path');
    expect(path.exists()).toBe(true);

    expect(path.attributes('d')).toBe('M 200 135 C 200 200, 400 200, 400 265');

    const textLabel = wrapper.find('.edge-label');
    expect(textLabel.text()).toBe('Yes');
  });

  it('evidenzia gli archi solo quando entrambi i nodi sono attivi nel path', async () => {
    const wrapper = mount(TreeCanvas);

    let path = wrapper.find('.edge-path');
    let label = wrapper.find('.edge-label');

    expect(path.attributes('stroke')).toBe('var(--dt-edge-color, #cbd5e1)');
    expect(label.classes()).not.toContain('edge-label-active');

    mockStore.activePath = ['N1', 'L1'];
    await wrapper.vm.$nextTick();

    expect(path.attributes('stroke')).toBe('var(--dt-edge-active, #3b82f6)');
    expect(label.classes()).toContain('edge-label-active');
  });

  it('renderizza correttamente i componenti dinamici dei nodi con posizione SVG', () => {
    const wrapper = mount(TreeCanvas, {
      global: {
        stubs: {
          UiDecisionNode: true,
          UiLeafNode: true
        }
      }
    });

    const decisionComponent = wrapper.findComponent({ name: 'UiDecisionNode' });
    const leafComponent = wrapper.findComponent({ name: 'UiLeafNode' });

    expect(decisionComponent.exists()).toBe(true);
    expect(leafComponent.exists()).toBe(true);

    expect(decisionComponent.attributes('transform')).toBe('translate(200, 100)');
    expect(leafComponent.attributes('transform')).toBe('translate(400, 300)');
  });

  it('chiama lo store.selectNode quando un nodo emette select', async () => {
    const wrapper = mount(TreeCanvas, {
      global: {
        stubs: { UiDecisionNode: true, UiLeafNode: true }
      }
    });

    const decisionComponent = wrapper.findComponent({ name: 'UiDecisionNode' });

    await decisionComponent.vm.$emit('select', 'N1');

    expect(mockStore.selectNode).toHaveBeenCalledWith('N1');
  });

  it('gestisce correttamente i calcoli matematici della funzione generateBezierPath', () => {
    const wrapper = mount(TreeCanvas);

    const edgeCase = { startX: 0, startY: 0, endX: 100, endY: 100 };
    const pathString = wrapper.vm.generateBezierPath(edgeCase);

    expect(pathString).toBe('M 0 35 C 0 50, 100 50, 100 65');
  });
});