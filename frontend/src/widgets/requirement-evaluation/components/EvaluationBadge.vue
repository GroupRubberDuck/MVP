<script setup>
import { computed } from 'vue';
import { useDecisionTreeStore } from '../store/decisionTreeStore.js';

const store = useDecisionTreeStore();

const stateConfig = {
  pass:           { label: 'Pass',           icon: '✓', cssClass: 'badge-pass' },
  fail:           { label: 'Fail',           icon: '✗', cssClass: 'badge-fail' },
  not_applicable: { label: 'N/A',            icon: '—', cssClass: 'badge-na' },
  pending:        { label: 'Pending',        icon: '⏳', cssClass: 'badge-pending' },
  not_evaluated:  { label: 'Not Evaluated',  icon: '○', cssClass: 'badge-not-evaluated' },
};

const config = computed(() => {
  const state = store.evaluationState;
  return stateConfig[state] ?? { label: state ?? 'Unknown', icon: '?', cssClass: 'badge-unknown' };
});
</script>

<template>
  <span
    class="evaluation-badge"
    :class="config.cssClass"
    :title="`Evaluation: ${config.label}`"
    role="status"
  >
    <span class="badge-icon" aria-hidden="true">{{ config.icon }}</span>
    <span class="badge-label">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.evaluation-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  line-height: 1;
  white-space: nowrap;
  user-select: none;
  transition: background 0.2s, color 0.2s;
}

.badge-icon {
  font-size: 14px;
}

/* --- Varianti --- */
.badge-pass {
  background: var(--dt-badge-pass-bg, #dcfce7);
  color: var(--dt-badge-pass-text, #15803d);
}

.badge-fail {
  background: var(--dt-badge-fail-bg, #fee2e2);
  color: var(--dt-badge-fail-text, #b91c1c);
}

.badge-na {
  background: var(--dt-badge-na-bg, #f1f5f9);
  color: var(--dt-badge-na-text, #475569);
}

.badge-pending {
  background: var(--dt-badge-pending-bg, #fef3c7);
  color: var(--dt-badge-pending-text, #92400e);
}

.badge-not-evaluated {
  background: var(--dt-badge-ne-bg, #f1f5f9);
  color: var(--dt-badge-ne-text, #94a3b8);
}

.badge-unknown {
  background: var(--dt-badge-unknown-bg, #f1f5f9);
  color: var(--dt-badge-unknown-text, #64748b);
}
</style>
