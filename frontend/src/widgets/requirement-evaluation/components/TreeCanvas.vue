<script setup>
import { computed, ref, onMounted , watch} from 'vue';
import { useDecisionTreeStore } from '../store/decisionTreeStore.js';
import UiDecisionNode from './UiDecisionNode.vue';
import UiLeafNode from './UiLeafNode.vue';

const store = useDecisionTreeStore();
const PADDING = 150
const NODE_HALF_WIDTH = 110
const NODE_MAX_HALF_HEIGHT = 80
const svgRef = ref(null);
const viewBox = ref({ x: 0, y: 0, w: 900, h: 500 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });



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
watch(nodes, (newNodes) => {
  if (newNodes.length === 0) return

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const node of newNodes) {
    minX = Math.min(minX, node.x - NODE_HALF_WIDTH)
    maxX = Math.max(maxX, node.x + NODE_HALF_WIDTH)
    minY = Math.min(minY, node.y - NODE_MAX_HALF_HEIGHT)
    maxY = Math.max(maxY, node.y + NODE_MAX_HALF_HEIGHT)
  }

  viewBox.value = {
    x: minX - PADDING,
    y: minY - PADDING,
    w: (maxX - minX) + PADDING * 2,
    h: (maxY - minY) + PADDING * 2,
  }
}, { immediate: true })
const viewBoxStr = computed(
  () => `${viewBox.value.x} ${viewBox.value.y} ${viewBox.value.w} ${viewBox.value.h}`
);
</script>

<template>
<svg
  ref="svgRef"
  class="tree-canvas"
  :viewBox="viewBoxStr"
  :style="{ height: viewBox.h + 'px' }"
  preserveAspectRatio="xMidYMin meet"
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
  @select="selectNode"
/>
    </g>
  </svg>
</template>

<style scoped>
.tree-canvas {
  width: 100%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  user-select: none;
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