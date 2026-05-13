<!-- UiDecisionNode.vue -->
<script setup>
import { computed } from 'vue'

const NODE_WIDTH = 200
const TEXT_PADDING = 20
const LINE_HEIGHT = 1.4

const props = defineProps({
  id: { type: String, required: true },
  text: { type: String, required: true },
  isActive: { type: Boolean, default: false },
  fontSize: { type: Number, default: 12 },
})

const emit = defineEmits(['select'])

const estimatedLines = computed(() => {
  const charsPerLine = Math.floor((NODE_WIDTH - TEXT_PADDING * 2) / (props.fontSize * 0.6))
  return Math.max(1, Math.ceil(props.text.length / charsPerLine))
})

const nodeHeight = computed(() => {
  const textHeight = estimatedLines.value * props.fontSize * LINE_HEIGHT
  return textHeight + TEXT_PADDING * 2
})

function onClick() {
  if (props.isActive) {
    emit('select', props.id)
  }
}
</script>

<template>
  <g
    class="ui-decision-node"
    :class="{ 'is-active': isActive }"
    @click="onClick"
    role="button"
    tabindex="0"
  >
    <rect
      :x="-NODE_WIDTH / 2"
      :y="-nodeHeight / 2"
      :width="NODE_WIDTH"
      :height="nodeHeight"
      rx="8"
      ry="8"
      class="node-bg"
    />
    <foreignObject
      :x="-NODE_WIDTH / 2 + TEXT_PADDING / 2"
      :y="-nodeHeight / 2 + TEXT_PADDING / 2"
      :width="NODE_WIDTH - TEXT_PADDING"
      :height="nodeHeight - TEXT_PADDING"
    >
      <div
        xmlns="http://www.w3.org/1999/xhtml"
        class="node-text"
        :style="{ fontSize: fontSize + 'px' }"
      >
      <span class="node-id">
        {{ id  }}
      </span>
      <span class="id-question-separator"></span>
      <span>
        {{ text }}
      </span>
      </div>
    </foreignObject>
  </g>
</template>

<style scoped>
.node-id{
  font-weight: bold;
}

.ui-decision-node {
  cursor: default;
}

.is-active {
  cursor: pointer;
}

.node-bg {
  fill: #ffffff;
  stroke: #94a3b8;
  stroke-width: 2;
}

.is-active .node-bg {
  fill: #eff6ff;
  stroke: #3b82f6;
  stroke-width: 2.5;
}

.node-text {
  line-height: 1.4;
  color: #1e293b;
  text-align: center;
  font-family: inherit;
  overflow: hidden;
}
</style>