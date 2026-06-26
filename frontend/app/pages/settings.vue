<template>
  <div class="settings-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-description">系统配置 · AI 提供商与数据管理</p>
      </div>
    </header>

    <div class="settings-sections">
      <!-- AI Provider -->
      <section class="settings-section">
        <div class="section-header">
          <CpuIcon :size="16" aria-hidden="true" />
          <h2 class="section-title">AI Provider</h2>
        </div>

        <div class="setting-row">
          <label class="setting-label">提供商</label>
          <div class="setting-control">
            <select v-model="aiProvider" class="setting-select">
              <option value="ollama">Ollama（本地）</option>
              <option value="openai">OpenAI</option>
              <option value="deepseek">DeepSeek</option>
            </select>
          </div>
        </div>

        <div v-if="aiProvider !== 'ollama'" class="setting-row">
          <label class="setting-label">API Key</label>
          <div class="setting-control">
            <div class="password-wrapper">
              <input v-model="apiKey" :type="showKey ? 'text' : 'password'" class="setting-input" placeholder="sk-..." />
              <button class="toggle-btn" @click="showKey = !showKey" :aria-label="showKey ? '隐藏' : '显示'">
                <EyeIcon v-if="!showKey" :size="14" aria-hidden="true" />
                <EyeOffIcon v-else :size="14" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <div class="setting-row">
          <label class="setting-label">Endpoint</label>
          <div class="setting-control">
            <input v-model="apiEndpoint" class="setting-input" :placeholder="aiProvider === 'ollama' ? 'http://localhost:11434' : 'https://api.openai.com/v1'" />
          </div>
        </div>

        <div class="setting-row">
          <label class="setting-label">模型</label>
          <div class="setting-control">
            <input v-model="modelName" class="setting-input" :placeholder="aiProvider === 'ollama' ? 'llama3' : 'gpt-4o-mini'" />
          </div>
        </div>
      </section>

      <!-- Data -->
      <section class="settings-section">
        <div class="section-header">
          <DatabaseIcon :size="16" aria-hidden="true" />
          <h2 class="section-title">数据管理</h2>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">导出设定集</span>
            <span class="setting-hint">将所有世界观数据导出为 JSON 文件</span>
          </div>
          <button class="btn btn-secondary" @click="exportData">
            <DownloadIcon :size="16" aria-hidden="true" />
            导出
          </button>
        </div>

        <div class="setting-row danger">
          <div class="setting-info">
            <span class="setting-label">清空数据</span>
            <span class="setting-hint danger-hint">此操作不可撤销</span>
          </div>
          <button class="btn btn-danger" @click="confirmClear">
            <Trash2Icon :size="16" aria-hidden="true" />
            清空
          </button>
        </div>
      </section>

      <!-- About -->
      <section class="settings-section">
        <div class="section-header">
          <InfoIcon :size="16" aria-hidden="true" />
          <h2 class="section-title">关于</h2>
        </div>

        <div class="about-grid">
          <div class="about-row">
            <span class="about-key">版本</span>
            <span class="about-value">v0.1.0</span>
          </div>
          <div class="about-row">
            <span class="about-key">协议</span>
            <span class="about-value">MIT License</span>
          </div>
          <div class="about-row">
            <span class="about-key">理念</span>
            <span class="about-value">设定即数据 (Lore as Data)</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import {
  Cpu,
  Eye,
  EyeOff,
  Database,
  Download,
  Trash2,
  Info,
} from "lucide-vue-next"

const aiProvider = ref("ollama")
const apiKey = ref("")
const apiEndpoint = ref("")
const modelName = ref("")
const showKey = ref(false)

function exportData() {
  // TODO: call backend /api/export
}

function confirmClear() {
  // TODO: confirmation dialog + clear
}
</script>

<style scoped>
.settings-page {
  max-width: 700px;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.02em;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* Sections */
.settings-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.settings-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.settings-section:hover {
  border-color: var(--color-border-hover);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* Setting Row */
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}

.setting-row + .setting-row {
  border-top: 1px solid rgba(42, 42, 74, 0.4);
}

.setting-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  min-width: 90px;
}

.setting-control {
  flex: 1;
  max-width: 360px;
}

.setting-input,
.setting-select {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.setting-input:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

.setting-select {
  cursor: pointer;
}

/* Password */
.password-wrapper {
  display: flex;
  align-items: center;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.password-wrapper:focus-within {
  border-color: var(--color-border-focus);
}

.password-wrapper .setting-input {
  border: none;
  background: transparent;
}

.password-wrapper .setting-input:focus {
  box-shadow: none;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--space-3);
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  height: 100%;
}

.toggle-btn:hover {
  color: var(--color-text-secondary);
}

/* Info row */
.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.danger-hint {
  color: var(--color-danger);
}

/* Buttons */
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
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  border-color: var(--color-accent-cyan);
  color: var(--color-accent-cyan);
}

.btn-danger {
  background: transparent;
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
}

.btn-danger:hover {
  background: rgba(255, 51, 85, 0.08);
}

/* About */
.about-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.about-row {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 0;
}

.about-key {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.about-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}
</style>
