import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { TreeStructure } from '../models/TreeStructure.js';
import { EvaluationEngine } from '../models/EvaluationEngine.js';
import { D3LayoutEngine } from '../layout/D3LayoutEngine.js';

export const useDecisionTreeStore = defineStore('decisionTree', () => {
  // --- State ---
  /** @type {import('vue').Ref<EvaluationEngine|null>} */
  const evaluationEngine = ref(null);

  /** @type {import('vue').Ref<Map<string, boolean>>} */
  const answers = ref(new Map());

  /** @type {import('vue').Ref<string|null>} */
  const selectedNodeId = ref(null);

  /** @type {import('vue').Ref<boolean>} */
  const isSideBarOpen = ref(false);

  /** @type {import('vue').Ref<string[]>} */
  const activePath = ref([]);

  /** @type {import('vue').Ref<import('../layout/D3LayoutEngine.js').LayoutResult|null>} */
  const layoutResult = ref(null);

  /** @type {import('../api/EvaluationApiClient.js').EvaluationApiClient|null} */
  let apiClient = null;

  /** Contesto della valutazione corrente */
  let evaluationContext = { deviceId: '', assetId: '', requirementId: '' };

  // --- Private ---
  function refreshPath() {
    if (!evaluationEngine.value) return;
    activePath.value = evaluationEngine.value.getEvaluationPath(answers.value);
  }

  function calculateLayout() {
    if (!evaluationEngine.value) return;
    const tree = evaluationEngine.value.getTree();
    const engine = new D3LayoutEngine();
    layoutResult.value = engine.calculateLayout(tree.getAllNodes(), tree.getRootId());
  }

  // --- Actions ---

  /**
   * Inizializza lo store con i dati dell'albero e le risposte salvate.
   * @param {{ treeData: Object, savedAnswers?: Record<string, boolean>, apiClient?: import('../api/EvaluationApiClient.js').EvaluationApiClient, context?: { deviceId: string, assetId: string, requirementId: string } }} opts
   */
  function init({ treeData, savedAnswers = {}, apiClient: client = null, context = {} }) {
    const tree = new TreeStructure(treeData);
    evaluationEngine.value = new EvaluationEngine(tree);

    // Ripristina risposte salvate
    answers.value = new Map(Object.entries(savedAnswers));

    apiClient = client;
    evaluationContext = { deviceId: '', assetId: '', requirementId: '', ...context };

    calculateLayout();
    refreshPath();

    // Seleziona automaticamente l'ultimo nodo non risposto nel path
    if (activePath.value.length > 0) {
      const lastInPath = activePath.value[activePath.value.length - 1];
      const nodeData = evaluationEngine.value.getNodeRenderData(lastInPath);
      if (nodeData && nodeData.type === 'decision') {
        selectNode(lastInPath);
      }
    }
  }

  /**
   * Imposta la risposta per un nodo e aggiorna il path.
   * @param {string} nodeId
   * @param {boolean} answer
   */
  async function setAnswer(nodeId, answer) {
    // Crea una nuova Map per triggerare la reattività
    const newAnswers = new Map(answers.value);
    newAnswers.set(nodeId, answer);

    // Pulisci le risposte dei nodi che non sono più nel percorso
    answers.value = newAnswers;
    refreshPath();

    // Rimuovi risposte di nodi fuori dal path attivo
    const pathSet = new Set(activePath.value);
    for (const key of answers.value.keys()) {
      if (!pathSet.has(key)) {
        answers.value.delete(key);
      }
    }
    // Refresh di nuovo dopo la pulizia
    refreshPath();

    // Persisti se c'è un apiClient
    if (apiClient) {
      try {
        await apiClient.saveAnswer({
          answer,
          nodeId,
          ...evaluationContext,
        });
      } catch (err) {
        console.error('Failed to save answer:', err);
      }
    }
  }

  /**
   * Seleziona un nodo e apre la sidebar.
   * @param {string} nodeId
   */
  function selectNode(nodeId) {
    selectedNodeId.value = nodeId;
    isSideBarOpen.value = true;
  }

  /** Chiude la sidebar. */
  function closeSideBar() {
    isSideBarOpen.value = false;
    selectedNodeId.value = null;
  }

  // --- Getters ---
  const selectedNodeData = computed(() => {
    if (!evaluationEngine.value || !selectedNodeId.value) return null;
    return evaluationEngine.value.getNodeRenderData(selectedNodeId.value);
  });

  return {
    // state
    answers,
    selectedNodeId,
    isSideBarOpen,
    activePath,
    layoutResult,
    evaluationEngine,
    // actions
    init,
    setAnswer,
    selectNode,
    closeSideBar,
    // getters
    selectedNodeData,
  };
});
