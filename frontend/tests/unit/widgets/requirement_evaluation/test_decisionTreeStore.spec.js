import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js';
import { EvaluationEngine } from '@/widgets/requirement-evaluation/engine/EvaluationEngine.js';
import { D3LayoutEngine } from '@/widgets/requirement-evaluation/layout/D3LayoutEngine.js';

// --- Mocking delle dipendenze algoritmiche -----------------------------------

vi.mock('@/widgets/requirement-evaluation/models/TreeStructure.js', () => {
  return {
    TreeStructure: class {
      getAllNodes = vi.fn();
      getRootId = vi.fn(() => 'N1');
    }
  };
});

vi.mock('@/widgets/requirement-evaluation/engine/EvaluationEngine.js', () => {
  return {
    EvaluationEngine: class {
      getEvaluationPath = vi.fn(() => ['N1', 'N2']);
      getTree = vi.fn(() => ({
        getAllNodes: vi.fn(),
        getRootId: vi.fn(() => 'N1')
      }));
      getNodeRenderData = vi.fn((id) => ({
        id,
        type: id === 'N2' ? 'decision' : 'leaf',
        text: 'Mocked Node Text'
      }));
    }
  };
});

vi.mock('@/widgets/requirement-evaluation/layout/D3LayoutEngine.js', () => {
  return {
    D3LayoutEngine: class {
      calculateLayout = vi.fn(() => ({
        nodes: [{ id: 'N1', x: 0, y: 0 }],
        edges: []
      }));
    }
  };
});

// --- Store Test Suite --------------------------------------------------------

describe('decisionTreeStore', () => {
  // Dichiariamo la variabile del client che verrà istanziata fresca prima di ogni test
  let mockApiClient;

  beforeEach(() => {
    vi.clearAllMocks();
    // Inizializza un'istanza fresca di Pinia prima di ogni singolo test
    setActivePinia(createPinia());

    // FIX 1: Isola l'istanza dei mock per evitare perdite di stato tra test diversi
    mockApiClient = {
      saveAnswer: vi.fn().mockResolvedValue({ success: true }),
      fetchState: vi.fn().mockResolvedValue({ evaluation: 'pass' }),
      saveJustification: vi.fn().mockResolvedValue({ saved: true })
    };
  });

  describe('inizializzazione tramite init', () => {
    it('configura lo stato iniziale, aggiorna il layout e attiva il calcolo del percorso', () => {
      const store = useDecisionTreeStore();
      
      store.init({
        treeData: {},
        savedAnswers: { N1: true },
        evaluationState: 'pending',
        justification: 'Nota iniziale',
        requirementsUrl: '/requirements'
      });

      // Verifica la corretta transizione dello stato iniziale
      expect(store.evaluationState).toBe('pending');
      expect(store.justification).toBe('Nota iniziale');
      expect(store.requirementsUrl).toBe('/requirements');
      expect(store.justificationStatus).toBe('idle');
      
      // Verifica la conversione dell'oggetto 'savedAnswers' in una mappa nativa Map
      expect(store.answers.get('N1')).toBe(true);
      
      // Verifica l'attivazione dei motori di calcolo
      expect(store.layoutResult).toEqual({ nodes: [{ id: 'N1', x: 0, y: 0 }], edges: [] });
      expect(store.activePath).toEqual(['N1', 'N2']);
    });

    it('apre automaticamente la sidebar e seleziona l’ultimo nodo decisionale del percorso attivo', () => {
      const store = useDecisionTreeStore();

      store.init({ treeData: {} });

      // Il nostro mock di EvaluationEngine restituisce path = ['N1', 'N2']. 
      // L'ultimo elemento è 'N2', che il nostro mock dichiara essere di tipo 'decision'.
      // Di conseguenza lo store deve averlo pre-selezionato all'avvio.
      expect(store.selectedNodeId).toBe('N2');
      expect(store.isSideBarOpen).toBe(true);
    });
  });

  describe('gestione delle risposte tramite setAnswer', () => {
    it('aggiorna la mappa locale delle risposte e ricalcola il percorso attivo', async () => {
      const store = useDecisionTreeStore();
      store.init({ treeData: {} });

      await store.setAnswer('N2', false);

      // La nuova risposta deve essere registrata reattivamente nello stato
      expect(store.answers.get('N2')).toBe(false);
    });

    it('salva le modifiche sul backend e aggiorna lo stato globale quando apiClient è attivo', async () => {
      const store = useDecisionTreeStore();
      store.init({ treeData: {}, apiClient: mockApiClient });

      await store.setAnswer('N1', true);

      // 1. Deve invocare il salvataggio sul server
      expect(mockApiClient.saveAnswer).toHaveBeenCalledWith({ nodeId: 'N1', answer: true });
      
      // 2. Deve recuperare lo stato aggiornato dal backend
      expect(mockApiClient.fetchState).toHaveBeenCalled();
      
      // 3. Lo stato della valutazione deve essersi allineato con la risposta del server
      expect(store.evaluationState).toBe('pass');
    });

    it('intercetta e registra correttamente gli errori se il salvataggio backend fallisce', async () => {
      // FIX 2: Creiamo lo spy ma assicuriamoci di pulirlo alla fine del blocco
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockApiClient.saveAnswer.mockRejectedValueOnce(new Error('Network Crash'));

      const store = useDecisionTreeStore();
      store.init({ treeData: {}, apiClient: mockApiClient, evaluationState: 'pending' });

      await store.setAnswer('N1', true);

      // Lo store non deve fare crashare l'app, ma registrare l'errore in console
      expect(consoleSpy).toHaveBeenCalledWith('Failed to save answer:', expect.any(Error));
      // Lo stato locale non deve corrompersi rimanendo quello precedente
      expect(store.evaluationState).toBe('pending');

      consoleSpy.mockRestore(); // Rilascia la console per i test futuri
    });
  });

  describe('interazioni UI', () => {
    it('gestisce correttamente lo stato della sidebar durante le operazioni di selezione', () => {
      const store = useDecisionTreeStore();

      // Verifica apertura e selezione manuale
      store.selectNode('N5');
      expect(store.selectedNodeId).toBe('N5');
      expect(store.isSideBarOpen).toBe(true);

      // Verifica chiusura e cleanup dello stato delle Sidebar
      store.closeSideBar();
      expect(store.isSideBarOpen).toBe(false);
      expect(store.selectedNodeId).toBeNull();
    });

    it('aggiorna immediatamente evaluationState tramite l’azione setEvaluationState', () => {
      const store = useDecisionTreeStore();
      
      // FIX 3: Rimosso il controllo restrittivo sul valore pre-inizializzato
      store.setEvaluationState('fail');
      expect(store.evaluationState).toBe('fail');
    });
  });

  describe('gestione delle giustificazioni tramite saveJustification', () => {
    it('gestisce correttamente gli stati e passa a "saved" dopo il successo API', async () => {
      const store = useDecisionTreeStore();
      store.init({ treeData: {} , apiClient: mockApiClient });

      const savePromise = store.saveJustification('Nuova nota tecnica');

      // Durante l'attesa asincrona il flag di stato deve essere in caricamento ('saving')
      expect(store.justificationStatus).toBe('saving');
      expect(store.justification).toBe('Nuova nota tecnica');

      await savePromise;

      // Al termine della promise, lo stato deve passare a 'saved'
      expect(mockApiClient.saveJustification).toHaveBeenCalledWith({ justification: 'Nuova nota tecnica' });
      expect(store.justificationStatus).toBe('saved');
    });

    it('passa allo stato "error" quando il client API restituisce un errore', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockApiClient.saveJustification.mockRejectedValueOnce(new Error('500 Internal Error'));

      const store = useDecisionTreeStore();
      store.init({ treeData: {}, apiClient: mockApiClient });

      await store.saveJustification('Nota errata');

      expect(store.justificationStatus).toBe('error');
      consoleSpy.mockRestore();
    });
  });

  describe('Getter computed selectedNodeData', () => {
    it('restituisce la struttura dati del nodo selezionato quando il motore e la selezione coincidono', () => {
      const store = useDecisionTreeStore();
      store.init({ treeData: {} });

      store.selectNode('N2');

      // Il getter computed deve interrogare l'evaluationEngine iniettato internamente
      expect(store.selectedNodeData).toEqual({
        id: 'N2',
        type: 'decision',
        text: 'Mocked Node Text'
      });
    });

    it('restituisce null quando nessun nodo è selezionato nella UI', () => {
      const store = useDecisionTreeStore();
      store.init({ treeData: {} });

      store.closeSideBar(); // Annulla selezioni

      expect(store.selectedNodeData).toBeNull();
    });
  });
});