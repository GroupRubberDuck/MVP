<!-- RequirementEvaluationWidget.vue
  Widget smart di alto livello: orchestra la valutazione di un requisito.

  Responsabilità (SRP):
    - Inizializzare lo store Pinia con i dati ricevuti dal Livello 3
    - Creare e iniettare l'ApiClient nello store
    - Comporre i sotto-componenti (EvaluationBadge, DecisionTreeWidget, JustificationForm)

  NON è responsabile di:
    - Logica dell'albero decisionale (delegata allo store e ai sotto-componenti)
    - Rendering dei nodi (delegato a TreeCanvas, UiDecisionNode, UiLeafNode)
    - Costruzione degli URL (iniettati dal Livello 3)
-->

<script setup>
import { onMounted } from 'vue'
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js'
import { EvaluationApiClient } from '@/widgets/requirement-evaluation/api/EvaluationApiClient.js'
import DecisionTreeWidget from '@/widgets/requirement-evaluation/components/DecisionTreeWidget.vue'
import EvaluationBadge from '@/widgets/requirement-evaluation/components/EvaluationBadge.vue'
import JustificationForm from '@/widgets/requirement-evaluation/components/JustificationForm.vue'
import TreeSidebar from './components/TreeSidebar.vue'

const props = defineProps({
  treeData: {
    type: Object,
    required: true,
  },
  savedAnswers: {
    type: Object,
    default: () => ({}),
  },
  evaluationState: {
    type: String,
    default: null,
  },
  justification: {
    type: String,
    default: '',
  },
  urls: {
    type: Object,
    required: true,
  },
})

const store = useDecisionTreeStore()

onMounted(() => {
  const apiClient = new EvaluationApiClient(props.urls)

  store.init({
    treeData: props.treeData,
    savedAnswers: props.savedAnswers,
    evaluationState: props.evaluationState,
    justification: props.justification,
    apiClient,
  })
})
</script>
<template>
  <div class="requirement-evaluation">
    <header class="requirement-evaluation__header">
      <EvaluationBadge />
    </header>

    <main class="requirement-evaluation__body">
      <section class="requirement-evaluation__tree">
        <DecisionTreeWidget />
      </section>

      <aside v-if="store.isSideBarOpen" class="requirement-evaluation__sidebar">
        <TreeSidebar />
      </aside>

      <section class="requirement-evaluation__justification">
        <JustificationForm />
      </section>
    </main>
  </div>
</template>

<style>
.requirement-evaluation__body {
  display: grid;
  grid-template-areas:
    "tree sidebar"
    "tree justification"
    "tree .";
  grid-template-columns: 1fr 320px;
  grid-template-rows: auto auto 1fr;
  gap: 16px;
  align-items: start;
}
.requirement-evaluation__tree {
  grid-area: tree;
}

.requirement-evaluation__sidebar {
  grid-area: sidebar;
}

.requirement-evaluation__justification {
  grid-area: justification;
}
</style>