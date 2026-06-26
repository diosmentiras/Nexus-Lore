<template>
  <div class="settings-page">
    <header class="page-header">
      <h1>Settings</h1>
      <p class="subtitle">系统配置</p>
    </header>

    <div class="settings-sections">
      <section class="settings-section">
        <h2>AI Provider</h2>
        <div class="setting-row">
          <label>提供商</label>
          <select v-model="aiProvider" class="setting-input">
            <option value="ollama">Ollama (本地)</option>
            <option value="openai">OpenAI</option>
            <option value="deepseek">DeepSeek</option>
          </select>
        </div>
        <div class="setting-row" v-if="aiProvider !== 'ollama'">
          <label>API Key</label>
          <input v-model="apiKey" type="password" class="setting-input" placeholder="sk-..." />
        </div>
        <div class="setting-row">
          <label>API Endpoint</label>
          <input v-model="apiEndpoint" class="setting-input" :placeholder="aiProvider === 'ollama' ? 'http://localhost:11434' : 'https://api.openai.com/v1'" />
        </div>
        <div class="setting-row">
          <label>模型</label>
          <input v-model="modelName" class="setting-input" :placeholder="aiProvider === 'ollama' ? 'llama3' : 'gpt-4o-mini'" />
        </div>
      </section>

      <section class="settings-section">
        <h2>数据</h2>
        <div class="setting-row">
          <label>导出设定集</label>
          <button class="btn btn-secondary" @click="exportData">📦 导出 JSON</button>
        </div>
        <div class="setting-row">
          <label>清空所有数据</label>
          <button class="btn btn-danger" @click="confirmClear">🗑️ 清空</button>
        </div>
      </section>

      <section class="settings-section">
        <h2>关于</h2>
        <div class="about-info">
          <p>Nexus-Lore v0.1.0</p>
          <p>设定即数据 (Lore as Data)</p>
          <p>MIT License</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const aiProvider = ref('ollama')
const apiKey = ref('')
const apiEndpoint = ref('')
const modelName = ref('')

function exportData() {
  // TODO: call backend /api/export
}

function confirmClear() {
  // TODO: confirmation dialog + clear
}
</script>

<style scoped>
.settings-page { max-width: 700px; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 28px; font-weight: 700; }
.subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 2px; }
.settings-sections { display: flex; flex-direction: column; gap: 24px; }
.settings-section { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 24px; }
.settings-section h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.setting-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; gap: 16px; }
.setting-row + .setting-row { border-top: 1px solid rgba(42, 42, 74, 0.5); }
.setting-row label { font-size: 14px; color: var(--text-secondary); min-width: 100px; }
.setting-input { flex: 1; max-width: 360px; padding: 8px 12px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); font-size: 13px; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-secondary { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }
.btn-secondary:hover { border-color: var(--accent-cyan); }
.btn-danger { background: transparent; border: 1px solid var(--danger); color: var(--danger); }
.btn-danger:hover { background: rgba(255, 51, 85, 0.1); }
.about-info { display: flex; flex-direction: column; gap: 4px; }
.about-info p { font-size: 13px; color: var(--text-secondary); }
</style>
