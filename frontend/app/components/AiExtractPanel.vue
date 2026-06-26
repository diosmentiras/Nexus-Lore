<template>
  <div class="ai-extract-panel">
    <div class="panel-header">
      <h3>AI 提取</h3>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </div>
    <div class="panel-body">
      <textarea v-model="text" class="extract-input" placeholder="粘贴章节草稿或灵感大纲..." rows="6"></textarea>
      <div class="extract-options">
        <label class="option-row">
          <input type="checkbox" v-model="extractCharacters" />
          <span>人物</span>
        </label>
        <label class="option-row">
          <input type="checkbox" v-model="extractFactions" />
          <span>势力</span>
        </label>
        <label class="option-row">
          <input type="checkbox" v-model="extractItems" />
          <span>物品</span>
        </label>
        <label class="option-row">
          <input type="checkbox" v-model="extractEvents" />
          <span>事件</span>
        </label>
      </div>
      <button class="btn btn-primary" @click="runExtract" :disabled="!text.trim() || extracting">
        {{ extracting ? '解析中...' : '开始提取' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ close: []; extracted: [items: any[]] }>()

const text = ref('')
const extracting = ref(false)
const extractCharacters = ref(true)
const extractFactions = ref(true)
const extractItems = ref(true)
const extractEvents = ref(true)

async function runExtract() {
  extracting.value = true
  // TODO: call backend /api/extract with selected types
  await new Promise(r => setTimeout(r, 2000))
  extracting.value = false
  emit('extracted', [])
}
</script>

<style scoped>
.ai-extract-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; margin-bottom: 20px; overflow: hidden; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border-color); }
.panel-header h3 { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.close-btn { background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 16px; }
.close-btn:hover { color: var(--text-primary); }
.panel-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.extract-input { width: 100%; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; color: var(--text-primary); font-size: 14px; font-family: inherit; resize: vertical; line-height: 1.5; }
.extract-input::placeholder { color: var(--text-dim); }
.extract-options { display: flex; gap: 16px; flex-wrap: wrap; }
.option-row { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-secondary); cursor: pointer; }
.option-row input { accent-color: var(--accent-cyan); }
.btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; align-self: flex-start; transition: all 0.2s; }
.btn-primary { background: var(--accent-cyan); color: var(--bg-primary); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
