import { describe, it, expect } from 'vitest';
import { DecisionNode, LeafNode } from '../src/widgets/requirement-evaluation/models/Node.js';
import { TreeStructure } from '../src/widgets/requirement-evaluation/models/TreeStructure.js';
import { EvaluationEngine } from '../src/widgets/requirement-evaluation/engine/EvaluationEngine.js';
import { sampleTree, sampleTreeBackendFormat } from '../src/widgets/requirement-evaluation/fixtures.js';
// ─── Node ───────────────────────────────────────────────────────

describe('DecisionNode', () => {
  const node = new DecisionNode({
    id: 'N1',
    question: 'Test?',
    parentId: null,
    yesChildId: 'N2',
    noChildId: 'L1',
  });

  it('getRenderData returns correct DTO', () => {
    const dto = node.getRenderData();
    expect(dto.id).toBe('N1');
    expect(dto.type).toBe('decision');
    expect(dto.text).toBe('Test?');
    expect(dto.resultState).toBeNull();
    expect(dto.yesChildId).toBe('N2');
    expect(dto.noChildId).toBe('L1');
  });

  it('getNext(true) returns yesChildId', () => {
    expect(node.getNext(true)).toBe('N2');
  });

  it('getNext(false) returns noChildId', () => {
    expect(node.getNext(false)).toBe('L1');
  });

  it('getPrevious returns parentId', () => {
    expect(node.getPrevious()).toBeNull();
  });
});

describe('LeafNode', () => {
  const leaf = new LeafNode({ id: 'L1', result: 'pass', parentId: 'N1' });

  it('getRenderData returns correct DTO', () => {
    const dto = leaf.getRenderData();
    expect(dto.id).toBe('L1');
    expect(dto.type).toBe('leaf');
    expect(dto.resultState).toBe('pass');
  });

  it('getNext always returns null', () => {
    expect(leaf.getNext(true)).toBeNull();
    expect(leaf.getNext(false)).toBeNull();
  });

  it('getPrevious returns parentId', () => {
    expect(leaf.getPrevious()).toBe('N1');
  });
});

// ─── TreeStructure ──────────────────────────────────────────────

describe('TreeStructure', () => {
  const tree = new TreeStructure(sampleTree);

  it('getRootId returns the root', () => {
    expect(tree.getRootId()).toBe('N1');
  });

  it('getNode returns DecisionNode for decision nodes', () => {
    const n1 = tree.getNode('N1');
    expect(n1).toBeInstanceOf(DecisionNode);
    expect(n1.getRenderData().text).toContain('public accessibility');
  });

  it('getNode returns LeafNode for leaf nodes', () => {
    const l1 = tree.getNode('L1');
    expect(l1).toBeInstanceOf(LeafNode);
    expect(l1.getRenderData().resultState).toBe('pass');
  });

  it('calculates parentId correctly', () => {
    // N2 è figlio yes di N1
    const n2 = tree.getNode('N2');
    expect(n2.getPrevious()).toBe('N1');

    // L1 è figlio no di N1 (e anche yes di N2, ma il primo parent trovato sarà N1 o N2)
    // Il nostro codice mappa l'ultimo parent (N2 sovrascrive N1 per L1)
    const l1 = tree.getNode('L1');
    expect(l1.getPrevious()).not.toBeNull();
  });

  it('returns null for unknown node', () => {
    expect(tree.getNode('NOPE')).toBeNull();
  });

  it('getAllNodes returns all nodes', () => {
    expect(tree.getAllNodes().size).toBe(7);
  });
});

// ─── EvaluationEngine ───────────────────────────────────────────

describe('EvaluationEngine', () => {
  const tree = new TreeStructure(sampleTree);
  const engine = new EvaluationEngine(tree);

  it('getNodeRenderData returns DTO for valid id', () => {
    const dto = engine.getNodeRenderData('N1');
    expect(dto).not.toBeNull();
    expect(dto.id).toBe('N1');
  });

  it('getNodeRenderData returns null for invalid id', () => {
    expect(engine.getNodeRenderData('INVALID')).toBeNull();
  });

  describe('getEvaluationPath', () => {
    it('returns only root when no answers', () => {
      const path = engine.getEvaluationPath(new Map());
      expect(path).toEqual(['N1']);
    });

    it('follows YES path: N1=yes → N2', () => {
      const answers = new Map([['N1', true]]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2']);
    });

    it('follows NO path: N1=no → L1 (pass)', () => {
      const answers = new Map([['N1', false]]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'L1']);
    });

    it('full path to fail: N1=yes, N2=no, N3=no, N4=no → L3', () => {
      const answers = new Map([
        ['N1', true],
        ['N2', false],
        ['N3', false],
        ['N4', false],
      ]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2', 'N3', 'N4', 'L3']);
    });

    it('full path to not_applicable: N1=yes, N2=no, N3=yes → L2', () => {
      const answers = new Map([
        ['N1', true],
        ['N2', false],
        ['N3', true],
      ]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2', 'N3', 'L2']);
    });

    it('full path to pass via N4: N1=yes, N2=no, N3=no, N4=yes → L1', () => {
      const answers = new Map([
        ['N1', true],
        ['N2', false],
        ['N3', false],
        ['N4', true],
      ]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2', 'N3', 'N4', 'L1']);
    });
  });
});

// ─── TreeStructure: Backend Map Format ──────────────────────────

describe('TreeStructure (backend map format)', () => {
  const tree = new TreeStructure(sampleTreeBackendFormat);

  it('getRootId returns the root', () => {
    expect(tree.getRootId()).toBe('N1');
  });

  it('parses decision nodes correctly', () => {
    const n1 = tree.getNode('N1');
    expect(n1).toBeInstanceOf(DecisionNode);
    const dto = n1.getRenderData();
    expect(dto.type).toBe('decision');
    expect(dto.yesChildId).toBe('N2');
    expect(dto.noChildId).toBe('L1');
  });

  it('parses leaf nodes correctly', () => {
    const l3 = tree.getNode('L3');
    expect(l3).toBeInstanceOf(LeafNode);
    expect(l3.getRenderData().resultState).toBe('fail');
  });

  it('preserves parent_id from backend', () => {
    const n2 = tree.getNode('N2');
    expect(n2.getPrevious()).toBe('N1');

    const l2 = tree.getNode('L2');
    expect(l2.getPrevious()).toBe('N3');
  });

  it('getAllNodes returns all 7 nodes', () => {
    expect(tree.getAllNodes().size).toBe(7);
  });
});

describe('EvaluationEngine (backend map format)', () => {
  const tree = new TreeStructure(sampleTreeBackendFormat);
  const engine = new EvaluationEngine(tree);

  it('path with no answers stops at root', () => {
    expect(engine.getEvaluationPath(new Map())).toEqual(['N1']);
  });

  it('full path to fail matches array format behavior', () => {
    const answers = new Map([
      ['N1', true],
      ['N2', false],
      ['N3', false],
      ['N4', false],
    ]);
    expect(engine.getEvaluationPath(answers)).toEqual(['N1', 'N2', 'N3', 'N4', 'L3']);
  });

  it('full path to not_applicable', () => {
    const answers = new Map([
      ['N1', true],
      ['N2', false],
      ['N3', true],
    ]);
    expect(engine.getEvaluationPath(answers)).toEqual(['N1', 'N2', 'N3', 'L2']);
  });
});
