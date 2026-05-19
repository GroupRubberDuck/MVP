import { describe, it, expect } from 'vitest';
import { DecisionNode, LeafNode } from '../../../../src/widgets/requirement-evaluation/models/Node.js';
import { TreeStructure } from '../../../../src/widgets/requirement-evaluation/models/TreeStructure.js';
import { sampleTree, sampleTreeBackendFormat } from '../../../../src/widgets/requirement-evaluation/fixtures.js';

// ─── TreeStructure ──────────────────────────────────────────────

describe('TreeStructure', () => {
  const tree = new TreeStructure(sampleTree);

  it('dovrebbe restituire la radice tramite getRootId', () => {
    expect(tree.getRootId()).toBe('N1');
  });

  it('dovrebbe restituire un DecisionNode per i nodi decisionali tramite getNode', () => {
    const n1 = tree.getNode('N1');
    expect(n1).toBeInstanceOf(DecisionNode);
    expect(n1.getRenderData().text).toContain('public accessibility');
  });

  it('dovrebbe restituire un LeafNode per i nodi foglia tramite getNode', () => {
    const l1 = tree.getNode('L1');
    expect(l1).toBeInstanceOf(LeafNode);
    expect(l1.getRenderData().resultState).toBe('pass');
  });

  it('dovrebbe calcolare correttamente il parentId', () => {
    // N2 è figlio yes di N1
    const n2 = tree.getNode('N2');
    expect(n2.getPrevious()).toBe('N1');

    // L1 è figlio no di N1 (e anche yes di N2, ma il primo parent trovato sarà N1 o N2)
    // Il nostro codice mappa l'ultimo parent (N2 sovrascrive N1 per L1)
    const l1 = tree.getNode('L1');
    expect(l1.getPrevious()).not.toBeNull();
  });

  it('dovrebbe restituire null per un nodo sconosciuto', () => {
    expect(tree.getNode('NOPE')).toBeNull();
  });

  it('dovrebbe restituire tutti i nodi tramite getAllNodes', () => {
    expect(tree.getAllNodes().size).toBe(7);
  });
});

// ─── TreeStructure: Backend Map Format ──────────────────────────

describe('TreeStructure (formato mappa backend)', () => {
  const tree = new TreeStructure(sampleTreeBackendFormat);

  it('dovrebbe restituire la radice tramite getRootId', () => {
    expect(tree.getRootId()).toBe('N1');
  });

  it('dovrebbe analizzare correttamente i nodi decisionali', () => {
    const n1 = tree.getNode('N1');
    expect(n1).toBeInstanceOf(DecisionNode);
    const dto = n1.getRenderData();
    expect(dto.type).toBe('decision');
    expect(dto.yesChildId).toBe('N2');
    expect(dto.noChildId).toBe('L1');
  });

  it('dovrebbe analizzare correttamente i nodi foglia', () => {
    const l3 = tree.getNode('L3');
    expect(l3).toBeInstanceOf(LeafNode);
    expect(l3.getRenderData().resultState).toBe('fail');
  });

  it('dovrebbe preservare il parent_id proveniente dal backend', () => {
    const n2 = tree.getNode('N2');
    expect(n2.getPrevious()).toBe('N1');

    const l2 = tree.getNode('L2');
    expect(l2.getPrevious()).toBe('N3');
  });

  it('dovrebbe restituire tutti e 7 i nodi tramite getAllNodes', () => {
    expect(tree.getAllNodes().size).toBe(7);
  });
});