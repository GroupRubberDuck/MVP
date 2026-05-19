import { describe, it, expect } from 'vitest';
import { D3LayoutEngine } from '@/widgets/requirement-evaluation/layout/D3LayoutEngine.js';

// --- D3LayoutEngine Test Suite -----------------------------------------------

describe('D3LayoutEngine', () => {
  
  // Helper per creare nodi fittizi che simulano il comportamento di DecisionNode/LeafNode
  const createMockNode = (data) => ({
    getRenderData: () => data
  });

  // Prepariamo una mappa piatta di nodi (Mock di un albero completo)
  const createSampleTreeMap = () => {
    const treeMap = new Map();
    
    treeMap.set('N1', createMockNode({
      id: 'N1',
      type: 'decision',
      text: 'Tratta dati sensibili?',
      resultState: null,
      yesChildId: 'N2',
      noChildId: 'L1'
    }));

    treeMap.set('N2', createMockNode({
      id: 'N2',
      type: 'decision',
      text: 'I dati sono crittografati?',
      resultState: null,
      yesChildId: 'L2',
      noChildId: null
    }));

    treeMap.set('L1', createMockNode({
      id: 'L1',
      type: 'leaf',
      text: 'Requisito Non Applicabile',
      resultState: 'not_applicable'
    }));

    treeMap.set('L2', createMockNode({
      id: 'L2',
      type: 'leaf',
      text: 'Requisito Superato',
      resultState: 'pass'
    }));

    return treeMap;
  };

  it('inizializza correttamente la configurazione predefinita con il costruttore vuoto', () => {
    const engine = new D3LayoutEngine();
    const treeMap = createSampleTreeMap();
    
    const layout = engine.calculateLayout(treeMap, 'N1');
    
    // Se non crasha e genera nodi ed archi, significa che i fallback interni
    // sono stati presi correttamente
    expect(layout.nodes.length).toBe(4);
    expect(layout.edges.length).toBe(3);
  });

  it('mappa correttamente le coordinate assolute e i risultati del layout', () => {
    const customConfig = { nodeWidth: 100, nodeHeight: 100 };
    const engine = new D3LayoutEngine(customConfig);
    const treeMap = createSampleTreeMap();

    const { nodes, edges } = engine.calculateLayout(treeMap, 'N1');

    // 1. Verifica la traduzione dei nodi DTO flattati
    const rootNode = nodes.find(n => n.id === 'N1');
    expect(rootNode).toBeDefined();
    expect(rootNode.type).toBe('decision');
    expect(rootNode.text).toBe('Tratta dati sensibili?');
    expect(rootNode.resultState).toBeNull();

    // 2. Verifica che le coordinate Y crescano a ogni livello di profondità dell'albero (D3 Tree Top-Down)
    const level1Node = nodes.find(n => n.id === 'N2'); // Figlio diretto
    const level2Node = nodes.find(n => n.id === 'L2'); // Nipote
    
    expect(level1Node.y).toBeGreaterThan(rootNode.y);
    expect(level2Node.y).toBeGreaterThan(level1Node.y);
  });

  it('rispetta i vincoli di design con i figli YES a sinistra e NO a destra', () => {
    const engine = new D3LayoutEngine();
    const treeMap = createSampleTreeMap();

    const { nodes } = engine.calculateLayout(treeMap, 'N1');

    const yesChild = nodes.find(n => n.id === 'N2'); // Collegato al ramo YES
    const noChild = nodes.find(n => n.id === 'L1');  // Collegato al ramo NO

    // Nel piano cartesiano di D3, la coordinata X cresce andando da sinistra a destra.
    // Di conseguenza, il figlio 'Yes' (sinistra) deve avere una X minore del figlio 'No' (destra).
    expect(yesChild.x).toBeLessThan(noChild.x);
  });

  it('estrae le connessioni con tracciamento semantico e identificatori accurati', () => {
    const engine = new D3LayoutEngine();
    const treeMap = createSampleTreeMap();

    const { edges } = engine.calculateLayout(treeMap, 'N1');

    // Ci devono essere 3 archi totali: N1->N2, N1->L1, N2->L2
    expect(edges.length).toBe(3);

    // Ispezioniamo l'arco che porta da N1 a L1 (ramo No della radice)
    const noEdge = edges.find(e => e.id === 'N1->L1');
    expect(noEdge).toBeDefined();
    expect(noEdge.sourceId).toBe('N1');
    expect(noEdge.targetId).toBe('L1');
    expect(noEdge.label).toBe('No'); // Ha agganciato l'etichetta temporanea ricorsiva

    // Ispezioniamo l'arco che porta da N1 a N2 (ramo Yes della radice)
    const yesEdge = edges.find(e => e.id === 'N1->N2');
    expect(yesEdge.label).toBe('Yes');

    // Le coordinate di inizio dell'arco devono coincidere al millimetro con le coordinate spaziali del nodo sorgente
    expect(noEdge.startX).toBe(yesEdge.startX); // Entrambi partono dalla stessa X della radice N1
    expect(noEdge.startY).toBe(yesEdge.startY); // Entrambi partono dalla stessa Y della radice N1
  });

  it('gestisce correttamente i casi con rami mancanti senza generare archi fantasma', () => {
    const engine = new D3LayoutEngine();
    const treeMap = createSampleTreeMap();

    const { edges } = engine.calculateLayout(treeMap, 'N1');

    // Il nodo N2 ha yesChildId: 'L2' ma noChildId: null.
    // L'engine deve estrarre l'arco per il ramo Yes ma non deve generare anomalie o archi 'fantasmi' per il ramo No.
    const yesBranchFromN2 = edges.find(e => e.id === 'N2->L2');
    expect(yesBranchFromN2).toBeDefined();
    expect(yesBranchFromN2.label).toBe('Yes');

    // Verifichiamo che non esistano archi orfani in uscita da N2 verso entità inesistenti
    const ghostBranchFromN2 = edges.filter(e => e.sourceId === 'N2');
    expect(ghostBranchFromN2.length).toBe(1); // Esiste solo il ramo verso L2
  });
});