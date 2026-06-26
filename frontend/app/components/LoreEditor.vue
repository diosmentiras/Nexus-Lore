<template>
  <div class="lore-editor">
    <div class="editor-header">
      <div class="editor-header-info">
        <h3 class="editor-title">双轨写作台</h3>
        <p class="editor-hint">左侧输入草稿，右侧查看 AI 结构化提取结果</p>
      </div>
      <button class="btn-close" @click="$emit('close')" aria-label="关闭">
        <XIcon :size="18" aria-hidden="true" />
      </button>
    </div>

    <div class="editor-panels">
      <!-- Left: Raw Input -->
      <div class="editor-panel">
        <div class="panel-bar">
          <FileTextIcon :size="14" aria-hidden="true" />
          <span>原始草稿</span>
        </div>
        <textarea
          v-model="rawText"
          class="raw-input"
          placeholder="在 2076 年的霓虹雨夜，黑客 Jane 潜入了荒坂集团的地下数据中心..."
        ></textarea>
        <button class="btn btn-primary" @click="extract" :disabled="extracting || !rawText.trim()">
          <SparklesIcon v-if="!extracting" :size="16" aria-hidden="true" />
          <LoaderIcon v-else :size="16" class="spin" aria-hidden="true" />
          <span>{{ extracting ? "提取中..." : "AI Extract" }}</span>
        </button>
      </div>

      <!-- Right: Output -->
      <div class="editor-panel">
        <div class="panel-bar">
          <CodeIcon :size="14" aria-hidden="true" />
          <span>结构化输出</span>
        </div>

        <transition name="fade" mode="out-in">
          <div v-if="extracting" class="panel-placeholder" key="loading">
            <div class="spinner"></div>
            <span>AI 正在解析文本...</span>
          </div>
          <div v-else-if="!results.length" class="panel-placeholder" key="empty">
            <FileJsonIcon :size="32" class="placeholder-icon" aria-hidden="true" />
            <span>点击 AI Extract 开始解析</span>
          </div>
          <div v-else class="results-list" key="results">
            <div v-for="(item, i) in results" :key="i" class="result-item">
              <span class="result-type-badge" :class="'badge-' + item.type">{{ item.type }}</span>
              <pre class="result-yaml">{{ formatYaml(item) }}</pre>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <div class="editor-footer">
      <button class="btn btn-ghost" @click="$emit('close')">取消</button>
      <button class="btn btn-primary" @click="saveAll">
        <SaveIcon :size="16" aria-hidden="true" />
        保存全部
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import {
  X,
  FileText,
  Sparkles,
  Loader,
  Code,
  FileJson,
  Save,
} from "lucide-vue-next"

const emit = defineEmits<{ close: [] }>()

const rawText = ref("")
const extracting = ref(false)
const results = ref<any[]>([])

async function extract() {
  extracting.value = true
  await new Promise((r) => setTimeout(r, 2000))
  extracting.value = false
  results.value = []
}

function formatYaml(item: any): string {
  return JSON.stringify(item, null, 2)
}

function saveAll() {
  emit("close")
}
</script>

<style scoped>
.lore-editor {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  width: 90vw;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

/* Header */
.editor-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.editor-header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.editor-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.editor-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
}

/* Panels */
.editor-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  flex: 1;
  min-height: 0;
}

.editor-panel {
  display: flex;
  flex-direction: column;
  padding: var(--space-5) var(--space-6);
}

.editor-panel + .editor-panel {
  border-left: 1px solid var(--color-border);
}

.panel-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* Raw Input */
.raw-input {
  flex: 1;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-mono);
  resize: vertical;
  min-height: 200px;
  line-height: var(--line-height-relaxed);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.raw-input::placeholder {
  color: var(--color-text-muted);
  font-family: var(--font-sans);
}

.raw-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

/* Button */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
}

.btn-primary {
  background: var(--color-accent-cyan);
  color: var(--color-text-inverse);
  margin-top: var(--space-3);
  align-self: flex-start;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--shadow-glow-cyan);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover {
  color: var(--color-text-primary);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Placeholder */
.panel-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.placeholder-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Results */
.results-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.result-item {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.result-type-badge {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  display: inline-block;
  margin-bottom: var(--space-2);
}

.badge-character { background: rgba(0, 240, 255, 0.1); color: var(--color-accent-cyan); }
.badge-faction { background: rgba(255, 0, 170, 0.1); color: var(--color-accent-magenta); }
.badge-item { background: rgba(255, 215, 0, 0.1); color: var(--color-accent-yellow); }

.result-yaml {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  font-family: var(--font-mono);
  line-height: var(--line-height-normal);
}

/* Footer */
.editor-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--easing-default);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
