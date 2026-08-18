<template>
  <div class="ai-extract-panel">
    <div class="panel-header">
      <div class="panel-header-left">
        <SparklesIcon :size="16" aria-hidden="true" />
        <h3 class="panel-title">AI Extract</h3>
      </div>
      <button class="close-btn" @click="$emit('close')" aria-label="关闭">
        <XIcon :size="16" aria-hidden="true" />
      </button>
    </div>

    <div class="panel-body">
      <textarea
        v-model="text"
        class="extract-input"
        placeholder="粘贴章节草稿或灵感大纲..."
      ></textarea>

      <div class="extract-options">
        <span class="options-label">提取类型</span>
        <div class="options-grid">
          <label v-for="opt in options" :key="opt.key" class="option-chip" :class="{ active: opt.value }">
            <input type="checkbox" v-model="opt.value" class="option-checkbox" />
            <span>{{ opt.label }}</span>
          </label>
        </div>
      </div>

      <button class="btn btn-primary" @click="runExtract" :disabled="!text.trim() || extracting">
        <LoaderIcon v-if="extracting" :size="16" class="spin" aria-hidden="true" />
        <SparklesIcon v-else :size="16" aria-hidden="true" />
        <span>{{ extracting ? "解析中..." : "开始提取" }}</span>
      </button>
      <p v-if="errorMessage" class="extract-error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue"
import {
  Loader as LoaderIcon,
  Sparkles as SparklesIcon,
  X as XIcon,
} from "lucide-vue-next"

const emit = defineEmits<{ close: []; extracted: [items: any[]] }>()

const text = ref("")
const extracting = ref(false)
const errorMessage = ref("")
const apiBase = useApiBase()
const { selectedWorldId } = useWorlds()

const options = reactive([
  { key: "character", label: "人物", value: true },
  { key: "faction", label: "势力", value: true },
  { key: "item", label: "物品", value: true },
  { key: "location", label: "地点", value: true },
  { key: "event", label: "事件", value: true },
  { key: "containment", label: "异常", value: true },
])

async function runExtract() {
  extracting.value = true
  errorMessage.value = ""
  try {
    const result = await $fetch<{ entities: any[]; events: any[] }>(`${apiBase}/api/extract`, {
      method: "POST",
      body: {
        text: text.value,
        world_id: selectedWorldId.value || undefined,
        types: options.filter((opt) => opt.value).map((opt) => opt.key),
      },
    })
    emit("extracted", [
      ...result.entities.map((entity) => ({
        id: entity.name,
        name: entity.name,
        type: entity.entity_type,
        tags: entity.tags || [],
        summary: entity.summary || "",
      })),
    ])
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || "AI 提取失败，请先在设置页测试连接"
  } finally {
    extracting.value = false
  }
}
</script>

<style scoped>
.ai-extract-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-5);
  overflow: hidden;
  transition: border-color var(--duration-fast) var(--easing-default);
}

.ai-extract-panel:hover {
  border-color: var(--color-border-hover);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.panel-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-accent-cyan);
}

.panel-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
}

.panel-body {
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.extract-input {
  width: 100%;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-mono);
  resize: vertical;
  min-height: 120px;
  line-height: var(--line-height-relaxed);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.extract-input::placeholder {
  color: var(--color-text-muted);
  font-family: var(--font-sans);
}

.extract-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

/* Options */
.extract-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.options-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: var(--font-weight-medium);
}

.options-grid {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.option-chip {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
  user-select: none;
}

.option-chip:hover {
  border-color: var(--color-border-hover);
}

.option-chip.active {
  border-color: var(--color-accent-cyan);
  color: var(--color-accent-cyan);
  background: rgba(0, 240, 255, 0.06);
}

.option-checkbox {
  display: none;
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
  align-self: flex-start;
}

.btn-primary {
  background: var(--color-accent-cyan);
  color: var(--color-text-inverse);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--shadow-glow-cyan);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

.extract-error { color: var(--color-danger); font-size: var(--font-size-xs); line-height: var(--line-height-normal); }

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
