<script setup>
import { onMounted } from 'vue';
import { useDecisionTreeStore } from '../stores/decisionTreeStore.js';
import TreeCanvas from './TreeCanvas.vue';
import TreeSidebar from './TreeSidebar.vue';

const props = defineProps({
  /** JSON dell'albero decisionale */
  treeData: { type: Object, required: true },
  /** Risposte precedentemente salvate { nodeId: boolean } */
  savedAnswers: { type: Object, default: () => ({}) },
});

const store = useDecisionTreeStore();

onMounted(() => {
  store.init({
    treeData: props.treeData,
    savedAnswers: props.savedAnswers,
  });
});
</script>

<template>
  <div class="decision-tree-widget">
    <TreeCanvas />
    <TreeSidebar />
  </div>
</template>

<style scoped>
.decision-tree-widget {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid var(--dt-widget-border, #e2e8f0);
  font-family: system-ui, -apple-system, sans-serif;
}
</style>
