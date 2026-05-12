<script setup>
import { ref, watch } from 'vue';
import { useDecisionTreeStore } from '../stores/decisionTreeStore.js';

const store = useDecisionTreeStore();

/** Testo locale per l'editing (non scrive direttamente nello store fino al submit) */
const localText = ref(store.justification);

/** Sincronizza quando lo store cambia dall'esterno (es. init) */
watch(() => store.justification, (newVal) => {
  localText.value = newVal;
});

/** Il testo è cambiato rispetto allo store? */
const isDirty = ref(false);
watch(localText, (val) => {
  isDirty.value = val !== store.justification;
});

async function handleSubmit() {
  await store.saveJustification(localText.value);
  isDirty.value = false;
}

/** Reset al valore salvato */
function handleReset() {
  localText.value = store.justification;
  isDirty.value = false;
}
</script>

<template>
  <div class="justification-form">
    <label for="justification-textarea" class="form-label">
      Justification
    </label>

    <textarea
      id="justification-textarea"
      v-model="localText"
      class="form-textarea"
      rows="4"
      placeholder="Add a justification for this evaluation…"
    />

    <div class="form-footer">
      <span
        v-if="store.justificationStatus === 'saving'"
        class="status-text status-saving"
      >
        Saving…
      </span>
      <span
        v-else-if="store.justificationStatus === 'saved' && !isDirty"
        class="status-text status-saved"
      >
        ✓ Saved
      </span>
      <span
        v-else-if="store.justificationStatus === 'error'"
        class="status-text status-error"
      >
        ✗ Error saving
      </span>

      <div class="form-actions">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="!isDirty"
          @click="handleReset"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn btn-primary"
          :disabled="!isDirty || store.justificationStatus === 'saving'"
          @click="handleSubmit"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.justification-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--dt-form-label, #334155);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--dt-form-border, #e2e8f0);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.5;
  color: var(--dt-form-text, #1e293b);
  background: var(--dt-form-bg, #ffffff);
  resize: vertical;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--dt-form-focus-border, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.form-textarea::placeholder {
  color: var(--dt-form-placeholder, #94a3b8);
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 32px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

.status-saving { color: var(--dt-form-saving, #92400e); }
.status-saved  { color: var(--dt-form-saved, #15803d); }
.status-error  { color: var(--dt-form-error, #b91c1c); }

.form-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--dt-btn-bg, #ffffff);
  border-color: var(--dt-btn-border, #e2e8f0);
  color: var(--dt-btn-text, #475569);
}
.btn-secondary:not(:disabled):hover {
  background: var(--dt-btn-hover-bg, #f1f5f9);
}

.btn-primary {
  background: var(--dt-btn-primary-bg, #3b82f6);
  border-color: var(--dt-btn-primary-bg, #3b82f6);
  color: #ffffff;
}
.btn-primary:not(:disabled):hover {
  background: var(--dt-btn-primary-hover, #2563eb);
}
</style>
