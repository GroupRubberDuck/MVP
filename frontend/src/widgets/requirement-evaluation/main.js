// widgets/requirement-evaluation/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import RequirementEvaluationWidget from './RequirementEvaluationWidget.vue'

const mountPoint = document.getElementById('requirement-evaluation-widget')

if (mountPoint) {
  
  const {
    treeData,
    savedAnswers,
    evaluationState,
    justification,
    
    answerUrl,
    justificationUrl,
    detailUrl,
    stateUrl,
    requirementsUrl
  } = mountPoint.dataset

  const app = createApp(RequirementEvaluationWidget, {
    treeData: JSON.parse(treeData),
    savedAnswers: JSON.parse(savedAnswers),
    evaluationState,
    justification: justification || '',
requirementsUrl: requirementsUrl,    
    urls: {
      answer: answerUrl,
      justification: justificationUrl,
      detail: detailUrl,
      state: stateUrl,
    },
  })
  app.use(createPinia())
  app.mount(mountPoint)
}