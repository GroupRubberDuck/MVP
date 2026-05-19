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

  it('restituisce il dto corretto tramite getRenderData', () => {
    const dto = node.getRenderData();

    expect(dto.id).toBe('N1');
    expect(dto.type).toBe('decision');
    expect(dto.text).toBe('Test?');
    expect(dto.resultState).toBeNull();
    expect(dto.yesChildId).toBe('N2');
    expect(dto.noChildId).toBe('L1');
  });

  it('restituisce yesChildId quando getNext riceve true', () => {
    expect(node.getNext(true)).toBe('N2');
  });

  it('restituisce noChildId quando getNext riceve false', () => {
    expect(node.getNext(false)).toBe('L1');
  });

  it('restituisce parentId tramite getPrevious', () => {
    expect(node.getPrevious()).toBeNull();
  });
});

describe('LeafNode', () => {
  const leaf = new LeafNode({
    id: 'L1',
    result: 'pass',
    parentId: 'N1'
  });

  it('restituisce il dto corretto tramite getRenderData', () => {
    const dto = leaf.getRenderData();

    expect(dto.id).toBe('L1');
    expect(dto.type).toBe('leaf');
    expect(dto.resultState).toBe('pass');
  });

  it('restituisce sempre null tramite getNext', () => {
    expect(leaf.getNext(true)).toBeNull();
    expect(leaf.getNext(false)).toBeNull();
  });

  it('restituisce parentId tramite getPrevious', () => {
    expect(leaf.getPrevious()).toBe('N1');
  });
});