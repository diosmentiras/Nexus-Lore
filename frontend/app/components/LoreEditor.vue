<template>
  <div class="lore-editor">
    <div class="editor-panels">
      <!-- 左侧：原始文本输入 -->
      <div class="editor-panel">
        <div class="panel-header">
          <h3>原始草稿</h3>
          <span class="panel-hint">输入灵感大纲或章节草稿</span>
        </div>
        <textarea
          v-model="rawText"
          class="raw-input"
          placeholder="在 2076 年的霓虹雨夜，黑客 Jane 潜入了荒坂集团的地下数据中心..."
          rows="15"
        ></textarea>
        <button class="btn btn-primary" @click="extract" :disabled="extracting || !rawText.trim()">
          {{ extracting ? '提取中...' : '🤖 AI Extract' }}
        </button>
      </div>

      <!-- 右侧：提取结果 -->
      <div class="editor-panel">
        <div class="panel-header">
          <h3>结构化输出</h3>
          <span class="panel-hint">AI 提取的设定将显示在此处</span>
        </div>
        <div class="result-area">
          <div v-if="extracting" class="extracting-placeholder">
            <div class="spinner"></div>
            <span>AI 正在解析文本...</span>
          </div>
          <div v-else-if="results.length === 0" class="empty-result">
            <p>点击左侧的 AI Extract 按钮开始解析</p>
          </div>
          <div v-else class="results-list">
            <div v-for="(item, i) in results" :key="i" class="result-item">
              <div class="result-type-badge" :class="'type-' + item.type">{{ item.type }}</div>
              <pre class="result-yaml">{{ formatYaml(item) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="editor-footer">
      <button class="btn btn-secondary" @click="$emit('close')">取消</button>
      <button class="btn btn-primary" @click="saveAll">保存全部设定</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ close: [] }>()

const rawText = ref('')
const extracting = ref(false)
const results = ref<any[]>([])

async function extract() {
  extracting.value = true
  // TODO: call backend /api/extract
  await new Promise(r => setTimeout(r, 2000))
  extracting.value = false
}

function formatYaml(item: any): string {
  return JSON.stringify(item, null, 2)
}

function saveAll() {
  // TODO: batch save to backend
  emit('close')
}
</script>

<style scoped>
.lore-editor { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; width: 90vw; max-width: 1200px; max-height: 90vh; display: flex; flex-direction: column; }
.editor-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 0; flex: 1; overflow: hidden; }
.editor-panel { display: flex; flex-direction: column; padding: 24px; }
.editor-panel + .editor-panel { border-left: 1px solid var(--border-color); }
.panel-header { margin-bottom: 16px; }
.panel-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.panel-hint { font-size: 12px; color: var(--text-dim); }
.raw-input { flex: 1; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; color: var(--text-primary); font-size: 14px; font-family: inherit; resize: vertical; min-height: 200px; line-height: 1.6; }
.raw-input::placeholder { color: var(--text-dim); }
.btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; margin-top: 12px; align-self: flex-start; }
.btn-primary { background: var(--accent-cyan); color: var(--bg-primary); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }
.result-area { flex: 1; overflow-y: auto; }
.extracting-placeholder, .empty-result { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; height: 100%; color: var(--text-dim); font-size: 14px; }
.spinner { width: 24px; height: 24px; border: 2px solid var(--border-color); border-top-color: var(--accent-cyan); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.results-list { display: flex; flex-direction: column; gap: 12px; }
.result-item { background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; }
.result-type-badge { font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
.type-character { background: rgba(0, 240, 255, 0.12); color: var(--accent-cyan); }
.result-yaml { font-size: 12px; color: var(--text-secondary); white-space: pre-wrap; font-family: 'Consolas', monospace; line-height: 1.5; }
.editor-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px; border-top: 1px solid var(--border-color); }
</style>
