import { describe, it, expect } from 'vitest';
import { TreeStructure } from '../../../../src/widgets/requirement-evaluation/models/TreeStructure.js';
import { EvaluationEngine } from '../../../../src/widgets/requirement-evaluation/engine/EvaluationEngine.js';
import { sampleTree, sampleTreeBackendFormat } from '../../../../src/widgets/requirement-evaluation/fixtures.js';

// ─── EvaluationEngine ───────────────────────────────────────────

describe('EvaluationEngine', () => {
  const tree = new TreeStructure(sampleTree);
  const engine = new EvaluationEngine(tree);

  it('GetNodeRenderData Restituisce Il DTO Per Un Id Valido', () => {
    const dto = engine.getNodeRenderData('N1');
    expect(dto).not.toBeNull();
    expect(dto.id).toBe('N1');
  });

  it('GetNodeRenderData Restituisce Null Per Un Id Non Valido', () => {
    expect(engine.getNodeRenderData('INVALID')).toBeNull();
  });

  describe('getEvaluationPath', () => {
    it('Restituisce Solo La Radice Quando Non Ci Sono Risposte', () => {
      const path = engine.getEvaluationPath(new Map());
      expect(path).toEqual(['N1']);
    });

    it('Segue Il Percorso YES Da N1 A N2', () => {
      const answers = new Map([['N1', true]]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2']);
    });

    it('Segue Il Percorso NO Da N1 A L1 Pass', () => {
      const answers = new Map([['N1', false]]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'L1']);
    });

    it('Segue Il Percorso Completo Verso Fail Tramite N4 E L3', () => {
      const answers = new Map([
        ['N1', true],
        ['N2', false],
        ['N3', false],
        ['N4', false],
      ]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2', 'N3', 'N4', 'L3']);
    });

    it('Segue Il Percorso Completo Verso Not Applicable', () => {
      const answers = new Map([
        ['N1', true],
        ['N2', false],
        ['N3', true],
      ]);
      const path = engine.getEvaluationPath(answers);
      expect(path).toEqual(['N1', 'N2', 'N3', 'L2']);
    });

    it('Segue Il Percorso Completo Verso Pass Tramite N4 E L1', () => {
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

describe('EvaluationEngine (backend map format)', () => {
  const tree = new TreeStructure(sampleTreeBackendFormat);
  const engine = new EvaluationEngine(tree);

  it('Il Percorso Senza Risposte Si Ferma Alla Radice', () => {
    expect(engine.getEvaluationPath(new Map())).toEqual(['N1']);
  });

  it('Il Percorso Completo Verso Fail Corrisponde Al Comportamento Del Formato Array', () => {
    const answers = new Map([
      ['N1', true],
      ['N2', false],
      ['N3', false],
      ['N4', false],
    ]);
    expect(engine.getEvaluationPath(answers)).toEqual(['N1', 'N2', 'N3', 'N4', 'L3']);
  });

  it('Segue Il Percorso Completo Verso Not Applicable', () => {
    const answers = new Map([
      ['N1', true],
      ['N2', false],
      ['N3', true],
    ]);
    expect(engine.getEvaluationPath(answers)).toEqual(['N1', 'N2', 'N3', 'L2']);
  });
});