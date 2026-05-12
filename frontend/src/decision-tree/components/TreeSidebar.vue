<script setup>
import { computed } from 'vue';
import { useDecisionTreeStore } from '../stores/decisionTreeStore.js';

const store = useDecisionTreeStore();

const currentNode = computed(() => store.selectedNodeData);

const currentAnswer = computed(() => {
  if (!store.selectedNodeId) return undefined;
  return store.answers.get(store.selectedNodeId);
});

const hasNextNode = computed(() => {
  if (!currentNode.value || currentNode.value.type !== 'decision') return false;
  return currentAnswer.value !== undefined;
});

const hasPrevious = computed(() => {
  return currentNode.value?.parentId != null;
});

async function submit(answer) {
  if (!store.selectedNodeId) return;
  await store.setAnswer(store.selectedNodeId, answer);
}

function goPrevious() {
  if (currentNode.value?.parentId) {
    store.selectNode(currentNode.value.parentId);
  }
}

function goNext() {
  if (!currentNode.value || currentAnswer.value === undefined) return;
  const nextId =
    currentAnswer.value
      ? currentNode.value.yesChildId
      : currentNode.value.noChildId;
  if (nextId) {
    store.selectNode(nextId);
  }
}

function close() {
  store.closeSideBar();
}
</script>

<template>
  <Transition name="slide">
    <aside
      v-if="store.isSideBarOpen && currentNode"
      class="tree-sidebar"
    >
      <header class="sidebar-header">
        <span class="sidebar-title">{{ currentNode.type === 'decision' ? 'Question' : 'Result' }}</span>
        <button class="btn-close" @click="close" aria-label="Close sidebar">×</button>
      </header>

      <div class="sidebar-body">
        <!-- Decision Node -->
        <template v-if="currentNode.type === 'decision'">
          <p class="question-text">{{ currentNode.text }}</p>

          <div class="answer-buttons">
            <button
              class="btn-answer btn-yes"
              :class="{ selected: currentAnswer === true }"
              @click="submit(true)"
            >
              Yes
            </button>
            <button
              class="btn-answer btn-no"
              :class="{ selected: currentAnswer === false }"
              @click="submit(false)"
            >
              No
            </button>
          </div>
        </template>

        <!-- Leaf Node -->
        <template v-else>
          <div class="result-badge" :class="`result-${currentNode.resultState}`">
            {{ formatResult(currentNode.resultState) }}
          </div>
        </template>
      </div>

      <footer class="sidebar-footer">
        <button
          class="btn-nav"
          :disabled="!hasPrevious"
          @click="goPrevious"
        >
          ← Previous
        </button>
        <button
          class="btn-nav btn-nav-primary"
          :disabled="!hasNextNode"
          @click="goNext"
        >
          Next →
        </button>
      </footer>
    </aside>
  </Transition>
</template>

<script>
export default {
  methods: {
    formatResult(state) {
      const labels = {
        pass: '✓ Pass',
        fail: '✗ Fail',
        not_applicable: '— Not Applicable',
      };
      return labels[state] ?? state;
    },
  },
};
</script>

<style scoped>
.tree-sidebar {
  position: absolute;
  top: 0;
  right: 0;
  width: 340px;
  height: 100%;
  background: var(--dt-sidebar-bg, #ffffff);
  border-left: 1px solid var(--dt-sidebar-border, #e2e8f0);
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--dt-sidebar-border, #e2e8f0);
}

.sidebar-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--dt-sidebar-title, #334155);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-close {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--dt-sidebar-close, #94a3b8);
  line-height: 1;
  padding: 4px;
}
.btn-close:hover {
  color: var(--dt-sidebar-close-hover, #475569);
}

.sidebar-body {
  flex: 1;
  padding: 24px 20px;
  overflow-y: auto;
}

.question-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--dt-sidebar-text, #1e293b);
  margin: 0 0 24px;
}

.answer-buttons {
  display: flex;
  gap: 12px;
}

.btn-answer {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--dt-btn-border, #e2e8f0);
  border-radius: 8px;
  background: var(--dt-btn-bg, #ffffff);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--dt-btn-text, #475569);
}

.btn-answer:hover {
  border-color: var(--dt-btn-hover-border, #94a3b8);
}

.btn-yes.selected {
  background: var(--dt-btn-yes-active-bg, #dcfce7);
  border-color: var(--dt-btn-yes-active-border, #22c55e);
  color: var(--dt-btn-yes-active-text, #15803d);
}

.btn-no.selected {
  background: var(--dt-btn-no-active-bg, #fee2e2);
  border-color: var(--dt-btn-no-active-border, #ef4444);
  color: var(--dt-btn-no-active-text, #b91c1c);
}

/* Result badge */
.result-badge {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 15px;
}

.result-pass {
  background: var(--dt-pass-bg, #22c55e);
  color: #fff;
}
.result-fail {
  background: var(--dt-fail-bg, #ef4444);
  color: #fff;
}
.result-not_applicable {
  background: var(--dt-na-bg, #94a3b8);
  color: #fff;
}

/* Footer navigation */
.sidebar-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid var(--dt-sidebar-border, #e2e8f0);
}

.btn-nav {
  padding: 8px 16px;
  border: 1px solid var(--dt-btn-border, #e2e8f0);
  border-radius: 6px;
  background: var(--dt-btn-bg, #ffffff);
  font-size: 13px;
  cursor: pointer;
  color: var(--dt-btn-text, #475569);
  transition: all 0.15s;
}

.btn-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-nav:not(:disabled):hover {
  background: var(--dt-btn-hover-bg, #f1f5f9);
}

.btn-nav-primary {
  background: var(--dt-btn-primary-bg, #3b82f6);
  border-color: var(--dt-btn-primary-bg, #3b82f6);
  color: #ffffff;
}

.btn-nav-primary:not(:disabled):hover {
  background: var(--dt-btn-primary-hover, #2563eb);
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
