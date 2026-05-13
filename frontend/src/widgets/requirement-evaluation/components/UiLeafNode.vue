<script setup>
defineProps({
  id: { type: String, required: true },
  text: { type: String, required: true },
  resultState: { type: String, default: null },
  isActive: { type: Boolean, default: false },
});
</script>

<template>
  <g
    class="ui-leaf-node"
    :class="[
      `state-${resultState}`,
      { 'is-active': isActive },
    ]"
    :aria-label="`Result: ${resultState}`"
  >
    <rect
      :x="-80"
      :y="-25"
      width="160"
      height="50"
      rx="25"
      ry="25"
      class="node-bg"
    />
    <text
      y="5"
      text-anchor="middle"
      class="node-label"
    >
      {{ formatLabel(resultState) }}
    </text>
  </g>
</template>

<script>
export default {
  methods: {
    formatLabel(state) {
      const labels = {
        pass: '✓ Pass',
        fail: '✗ Fail',
        not_applicable: '— N/A',
      };
      return labels[state] ?? state;
    },
  },
};
</script>

<style scoped>
.ui-leaf-node {
  pointer-events: none;
}

.node-bg {
  stroke-width: 2;
  transition: fill 0.2s, stroke 0.2s;
}

.node-label {
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  fill: var(--dt-leaf-text, #ffffff);
}

/* Pass */
.state-pass .node-bg {
  fill: var(--dt-pass-bg, #22c55e);
  stroke: var(--dt-pass-border, #16a34a);
}

/* Fail */
.state-fail .node-bg {
  fill: var(--dt-fail-bg, #ef4444);
  stroke: var(--dt-fail-border, #dc2626);
}

/* Not Applicable */
.state-not_applicable .node-bg {
  fill: var(--dt-na-bg, #94a3b8);
  stroke: var(--dt-na-border, #64748b);
}

/* Active (raggiunto nel percorso) */
.is-active .node-bg {
  filter: drop-shadow(0 0 12px currentColor);
}

.is-active.state-pass .node-bg {
  filter: drop-shadow(0 0 12px rgba(34, 197, 94, 0.5));
}
.is-active.state-fail .node-bg {
  filter: drop-shadow(0 0 12px rgba(239, 68, 68, 0.5));
}
.is-active.state-not_applicable .node-bg {
  filter: drop-shadow(0 0 12px rgba(148, 163, 184, 0.5));
}
</style>
