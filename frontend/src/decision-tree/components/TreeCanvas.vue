<script setup>
import { computed, ref, onMounted } from 'vue';
import { useDecisionTreeStore } from '../stores/decisionTreeStore.js';
import UiDecisionNode from './UiDecisionNode.vue';
import UiLeafNode from './UiLeafNode.vue';

const store = useDecisionTreeStore();

// --- Pan & Zoom ---
const svgRef = ref(null);
const viewBox = ref({ x: 0, y: 0, w: 900, h: 500 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

function onWheel(e) {
  e.preventDefault();
  const scaleFactor = e.deltaY > 0 ? 1.1 : 0.9;
  const vb = viewBox.value;

  const svg = svgRef.value;
  const rect = svg.getBoundingClientRect();
  const mx = ((e.clientX - rect.left) / rect.width) * vb.w + vb.x;
  const my = ((e.clientY - rect.top) / rect.height) * vb.h + vb.y;

  const newW = vb.w * scaleFactor;
  const newH = vb.h * scaleFactor;

  viewBox.value = {
    x: mx - (mx - vb.x) * scaleFactor,
    y: my - (my - vb.y) * scaleFactor,
    w: newW,
    h: newH,
  };
}

function onPointerDown(e) {
  if (e.target.closest('.ui-decision-node, .ui-leaf-node')) return;
  isPanning.value = true;
  panStart.value = { x: e.clientX, y: e.clientY };
  svgRef.value?.setPointerCapture(e.pointerId);
}

function onPointerMove(e) {
  if (!isPanning.value) return;
  const svg = svgRef.value;
  const rect = svg.getBoundingClientRect();
  const vb = viewBox.value;

  const dx = ((e.clientX - panStart.value.x) / rect.width) * vb.w;
  const dy = ((e.clientY - panStart.value.y) / rect.height) * vb.h;

  viewBox.value = { ...vb, x: vb.x - dx, y: vb.y - dy };
  panStart.value = { x: e.clientX, y: e.clientY };
}

function onPointerUp() {
  isPanning.value = false;
}

// --- Layout ---
const nodes = computed(() => store.layoutResult?.nodes ?? []);
const edges = computed(() => store.layoutResult?.edges ?? []);
const activePathSet = computed(() => new Set(store.activePath));

function isEdgeActive(edge) {
  return activePathSet.value.has(edge.sourceId) && activePathSet.value.has(edge.targetId);
}

function generateBezierPath(edge) {
  const midY = (edge.startY + edge.endY) / 2;
  return `M ${edge.startX} ${edge.startY + 35} C ${edge.startX} ${midY}, ${edge.endX} ${midY}, ${edge.endX} ${edge.endY - 35}`;
}

function resolveComponent(type) {
  return type === 'decision' ? UiDecisionNode : UiLeafNode;
}

function selectNode(nodeId) {
  store.selectNode(nodeId);
}

// Centra la vista sul root all'avvio
onMounted(() => {
  if (nodes.value.length > 0) {
    const root = nodes.value[0];
    viewBox.value = {
      x: root.x - 450,
      y: root.y - 60,
      w: 900,
      h: 500,
    };
  }
});

const viewBoxStr = computed(
  () => `${viewBox.value.x} ${viewBox.value.y} ${viewBox.value.w} ${viewBox.value.h}`
);
</script>

<template>
  <svg
    ref="svgRef"
    class="tree-canvas"
    :viewBox="viewBoxStr"
    @wheel.prevent="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointerleave="onPointerUp"
  >
    <defs>
      <marker
        id="arrowhead"
        markerWidth="8"
        markerHeight="6"
        refX="8"
        refY="3"
        orient="auto"
      >
        <polygon points="0 0, 8 3, 0 6" fill="var(--dt-edge-color, #cbd5e1)" />
      </marker>
      <marker
        id="arrowhead-active"
        markerWidth="8"
        markerHeight="6"
        refX="8"
        refY="3"
        orient="auto"
      >
        <polygon points="0 0, 8 3, 0 6" fill="var(--dt-edge-active, #3b82f6)" />
      </marker>
    </defs>

    <!-- Edges -->
    <g class="edges">
      <g v-for="edge in edges" :key="edge.id">
        <path
          :d="generateBezierPath(edge)"
          fill="none"
          :stroke="isEdgeActive(edge) ? 'var(--dt-edge-active, #3b82f6)' : 'var(--dt-edge-color, #cbd5e1)'"
          :stroke-width="isEdgeActive(edge) ? 2.5 : 1.5"
          :marker-end="isEdgeActive(edge) ? 'url(#arrowhead-active)' : 'url(#arrowhead)'"
          class="edge-path"
        />
        <!-- Label Yes/No -->
        <text
          :x="(edge.startX + edge.endX) / 2 + (edge.endX > edge.startX ? 10 : -10)"
          :y="(edge.startY + edge.endY) / 2"
          text-anchor="middle"
          class="edge-label"
          :class="{ 'edge-label-active': isEdgeActive(edge) }"
        >
          {{ edge.label }}
        </text>
      </g>
    </g>

    <!-- Nodes -->
    <g class="nodes">
      <component
        v-for="node in nodes"
        :key="node.id"
        :is="resolveComponent(node.type)"
        v-bind="{
          id: node.id,
          text: node.text,
          resultState: node.resultState,
          isActive: activePathSet.has(node.id),
        }"
        :transform="`translate(${node.x}, ${node.y})`"
        @click="selectNode(node.id)"
      />
    </g>
  </svg>
</template>

<style scoped>
.tree-canvas {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: var(--dt-canvas-bg, #f8fafc);
  border-radius: 8px;
  user-select: none;
  touch-action: none;
}

.edge-path {
  transition: stroke 0.2s, stroke-width 0.2s;
}

.edge-label {
  font-size: 11px;
  font-weight: 600;
  fill: var(--dt-edge-label, #94a3b8);
  font-family: inherit;
}

.edge-label-active {
  fill: var(--dt-edge-active, #3b82f6);
}
</style>
