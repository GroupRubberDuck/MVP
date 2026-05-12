<script setup>
defineProps({
  id: { type: String, required: true },
  text: { type: String, required: true },
  isActive: { type: Boolean, default: false },
});

const emit = defineEmits(['click']);
</script>

<template>
  <g
    class="ui-decision-node"
    :class="{ 'is-active': isActive }"
    @click="emit('click', id)"
    role="button"
    tabindex="0"
    :aria-label="`Decision: ${text}`"
  >
    <!-- Nodo rombo stilizzato come rettangolo arrotondato -->
    <rect
      :x="-100"
      :y="-35"
      width="200"
      height="70"
      rx="8"
      ry="8"
      class="node-bg"
    />
    <foreignObject :x="-90" :y="-28" width="180" height="56">
      <div xmlns="http://www.w3.org/1999/xhtml" class="node-text">
        {{ text }}
      </div>
    </foreignObject>
  </g>
</template>

<style scoped>
.ui-decision-node {
  cursor: pointer;
}

.node-bg {
  fill: var(--dt-node-bg, #ffffff);
  stroke: var(--dt-node-border, #94a3b8);
  stroke-width: 2;
  transition: fill 0.2s, stroke 0.2s, filter 0.2s;
}

.ui-decision-node:hover .node-bg,
.ui-decision-node:focus .node-bg {
  stroke: var(--dt-node-hover-border, #3b82f6);
  filter: drop-shadow(0 2px 8px rgba(59, 130, 246, 0.2));
}

.is-active .node-bg {
  fill: var(--dt-node-active-bg, #eff6ff);
  stroke: var(--dt-node-active-border, #3b82f6);
  stroke-width: 2.5;
}

.node-text {
  font-size: 11px;
  line-height: 1.3;
  color: var(--dt-node-text, #1e293b);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  text-align: center;
  font-family: inherit;
}
</style>
