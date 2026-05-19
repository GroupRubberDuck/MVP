import { describe, it, expect } from 'vitest';
import { DecisionNode, LeafNode } from '../../../../src/widgets/requirement-evaluation/models/Node.js';

// ─── Node ───────────────────────────────────────────────────────

describe('DecisionNode', () => {
  const node = new DecisionNode({
    id: 'N1',
    question: 'Test?',
    parentId: null,
    yesChildId: 'N2',
    noChildId: 'L1',
  });

  it('Restituisce Il DTO Corretto Tramite getRenderData', () => {
    const dto = node.getRenderData();

    expect(dto.id).toBe('N1');
    expect(dto.type).toBe('decision');
    expect(dto.text).toBe('Test?');
    expect(dto.resultState).toBeNull();
    expect(dto.yesChildId).toBe('N2');
    expect(dto.noChildId).toBe('L1');
  });

  it('Restituisce yesChildId Quando getNext Riceve true', () => {
    expect(node.getNext(true)).toBe('N2');
  });

  it('Restituisce noChildId Quando getNext Riceve false', () => {
    expect(node.getNext(false)).toBe('L1');
  });

  it('Restituisce parentId Tramite getPrevious', () => {
    expect(node.getPrevious()).toBeNull();
  });
});

describe('LeafNode', () => {
  const leaf = new LeafNode({
    id: 'L1',
    result: 'pass',
    parentId: 'N1'
  });

  it('Restituisce Il DTO Corretto Tramite getRenderData', () => {
    const dto = leaf.getRenderData();

    expect(dto.id).toBe('L1');
    expect(dto.type).toBe('leaf');
    expect(dto.resultState).toBe('pass');
  });

  it('Restituisce Sempre null Tramite getNext', () => {
    expect(leaf.getNext(true)).toBeNull();
    expect(leaf.getNext(false)).toBeNull();
  });

  it('Restituisce parentId Tramite getPrevious', () => {
    expect(leaf.getPrevious()).toBe('N1');
  });
});