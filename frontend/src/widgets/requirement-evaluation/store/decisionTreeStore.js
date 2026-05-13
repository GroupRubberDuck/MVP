import { ref, shallowRef, computed } from 'vue'
import { defineStore } from 'pinia'
import { TreeStructure } from '../models/TreeStructure.js'
import { EvaluationEngine } from '../engine/EvaluationEngine.js'
import { D3LayoutEngine } from '../layout/D3LayoutEngine.js'

export const useDecisionTreeStore = defineStore('decisionTree', () => {
  // Oggetti con campi privati: NON reattivi
  // Vue non deve wrappare questi in Proxy
  let evaluationEngine = null
  let apiClient = null

  // Stato UI: reattivo
  const answers = ref(new Map())
  const selectedNodeId = ref(null)
  const isSideBarOpen = ref(false)
  const activePath = ref([])
  const layoutResult = ref(null)
  const evaluationState = ref(null)
  const justification = ref('')
  const justificationStatus = ref('idle')


  function refreshPath() {
    if (!evaluationEngine) return
    activePath.value = evaluationEngine.getEvaluationPath(answers.value)
  }

  function calculateLayout() {
    if (!evaluationEngine) return
    const tree = evaluationEngine.getTree()
    const engine = new D3LayoutEngine()
    layoutResult.value = engine.calculateLayout(tree.getAllNodes(), tree.getRootId())
  }

  function init({ treeData, savedAnswers = {}, evaluationState: initialState = null, justification: initialJustification = '', apiClient: client = null }) {
    const tree = new TreeStructure(treeData)
    evaluationEngine = new EvaluationEngine(tree)

    answers.value = new Map(Object.entries(savedAnswers))
    evaluationState.value = initialState
    justification.value = initialJustification
    justificationStatus.value = 'idle'

    apiClient = client

    calculateLayout()
    refreshPath()

    if (activePath.value.length > 0) {
      const lastInPath = activePath.value[activePath.value.length - 1]
      const nodeData = evaluationEngine.getNodeRenderData(lastInPath)
      if (nodeData && nodeData.type === 'decision') {
        selectNode(lastInPath)
      }
    }
  }

  async function setAnswer(nodeId, answer) {
    const newAnswers = new Map(answers.value)
    newAnswers.set(nodeId, answer)
    answers.value = newAnswers
    refreshPath()

    const pathSet = new Set(activePath.value)
    for (const key of answers.value.keys()) {
      if (!pathSet.has(key)) {
        answers.value.delete(key)
      }
    }
    refreshPath()

    if (apiClient) {
      try {
        await apiClient.saveAnswer({ nodeId, answer })
        const { evaluation } = await apiClient.fetchState()
        evaluationState.value = evaluation
      } catch (err) {
        console.error('Failed to save answer:', err)
      }
    }
  }

  function selectNode(nodeId) {
    selectedNodeId.value = nodeId
    isSideBarOpen.value = true
  }

  function closeSideBar() {
    isSideBarOpen.value = false
    selectedNodeId.value = null
  }

  async function saveJustification(text) {
    justification.value = text
    if (!apiClient) return

    justificationStatus.value = 'saving'
    try {
      await apiClient.saveJustification({ justification: text })
      justificationStatus.value = 'saved'
    } catch (err) {
      console.error('Failed to save justification:', err)
      justificationStatus.value = 'error'
    }
  }

  function setEvaluationState(state) {
    evaluationState.value = state
  }

  const selectedNodeData = computed(() => {
    if (!evaluationEngine || !selectedNodeId.value) return null
    return evaluationEngine.getNodeRenderData(selectedNodeId.value)
  })

  return {
    answers,
    selectedNodeId,
    isSideBarOpen,
    activePath,
    layoutResult,
    evaluationEngine,
    evaluationState,
    justification,
    justificationStatus,
    init,
    setAnswer,
    selectNode,
    closeSideBar,
    saveJustification,
    setEvaluationState,
    selectedNodeData,
  }
})