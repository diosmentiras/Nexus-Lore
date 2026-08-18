<template>
  <div class="settings-page">
    <header class="page-header">
      <h1>设置</h1>
      <p>世界管理、AI 运行状态与数据备份</p>
    </header>

    <p v-if="notice" class="notice" :class="noticeType">{{ notice }}</p>

    <div class="settings-sections">
      <section class="settings-section">
        <div class="section-header">
          <Globe2Icon :size="17" aria-hidden="true" />
          <h2>世界观</h2>
        </div>

        <div class="setting-row stacked">
          <label class="setting-label" for="active-world">当前世界</label>
          <div class="inline-control">
            <select id="active-world" :value="selectedWorldId" class="setting-input" @change="changeWorld">
              <option v-for="world in worlds" :key="world.id" :value="world.id">{{ world.name }}</option>
            </select>
            <NuxtLink v-if="selectedWorld" :to="`/worlds/${selectedWorld.id}/overview`" class="icon-button" title="打开世界工作区">
              <ArrowUpRightIcon :size="16" aria-hidden="true" />
            </NuxtLink>
          </div>
        </div>

        <form class="setting-row stacked" @submit.prevent="addWorld">
          <label class="setting-label" for="world-name">新建世界</label>
          <div class="world-form">
            <input id="world-name" v-model="newWorldName" class="setting-input" placeholder="世界名称" />
            <input v-model="newWorldSlug" class="setting-input" placeholder="slug" />
            <button class="btn btn-secondary" :disabled="creatingWorld || !newWorldName.trim() || !newWorldSlug.trim()">
              <PlusIcon :size="16" aria-hidden="true" />
              <span>{{ creatingWorld ? "创建中" : "新建" }}</span>
            </button>
          </div>
        </form>
      </section>

      <section class="settings-section">
        <div class="section-header">
          <CpuIcon :size="17" aria-hidden="true" />
          <h2>AI Provider</h2>
          <span class="status-dot" :class="aiConnectionState" aria-hidden="true" />
        </div>
        <dl class="config-list">
          <div><dt>提供商</dt><dd>{{ aiConfig.provider || "读取中" }}</dd></div>
          <div><dt>模型</dt><dd>{{ aiConfig.model || "未配置" }}</dd></div>
          <div><dt>Endpoint</dt><dd>{{ aiConfig.endpoint || "未配置" }}</dd></div>
          <div v-if="aiConfig.provider !== 'ollama'"><dt>API Key</dt><dd>{{ aiConfig.has_api_key ? "已配置" : "未配置" }}</dd></div>
        </dl>
        <div class="section-actions">
          <button class="btn btn-secondary" :disabled="testingAi" @click="testAiConnection">
            <ActivityIcon :size="16" aria-hidden="true" />
            <span>{{ testingAi ? "测试中" : "测试连接" }}</span>
          </button>
        </div>
      </section>

      <section class="settings-section">
        <div class="section-header">
          <DatabaseIcon :size="17" aria-hidden="true" />
          <h2>数据管理</h2>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <strong>导出设定集</strong>
            <span>包含世界、来源正文、Lore、关系与时间线</span>
          </div>
          <div class="action-control">
            <select v-model="exportScope" class="compact-select" aria-label="导出范围">
              <option value="current">当前世界</option>
              <option value="all">全部世界</option>
            </select>
            <button class="btn btn-secondary" :disabled="exporting" @click="exportData">
              <DownloadIcon :size="16" aria-hidden="true" />
              <span>{{ exporting ? "导出中" : "导出" }}</span>
            </button>
          </div>
        </div>

        <div class="setting-row danger-row">
          <div class="setting-info">
            <strong>删除当前世界</strong>
            <span>{{ selectedWorld?.name || "未选择世界" }}及其所有资料将被永久删除</span>
          </div>
          <button v-if="!confirmingDelete" class="btn btn-danger" :disabled="!canDeleteWorld" @click="confirmingDelete = true">
            <Trash2Icon :size="16" aria-hidden="true" />
            <span>删除</span>
          </button>
          <div v-else class="confirm-actions">
            <button class="btn btn-ghost" @click="confirmingDelete = false">取消</button>
            <button class="btn btn-danger solid" :disabled="deletingWorld" @click="removeSelectedWorld">
              <Trash2Icon :size="16" aria-hidden="true" />
              <span>{{ deletingWorld ? "删除中" : "确认删除" }}</span>
            </button>
          </div>
        </div>
      </section>

      <section class="settings-section about-section">
        <div class="section-header">
          <InfoIcon :size="17" aria-hidden="true" />
          <h2>关于</h2>
        </div>
        <dl class="config-list">
          <div><dt>版本</dt><dd>v0.2.0</dd></div>
          <div><dt>协议</dt><dd>MIT License</dd></div>
          <div><dt>理念</dt><dd>设定即数据</dd></div>
        </dl>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import {
  Activity as ActivityIcon,
  ArrowUpRight as ArrowUpRightIcon,
  Cpu as CpuIcon,
  Database as DatabaseIcon,
  Download as DownloadIcon,
  Globe2 as Globe2Icon,
  Info as InfoIcon,
  Plus as PlusIcon,
  Trash2 as Trash2Icon,
} from "lucide-vue-next"

interface AiConfig {
  provider: string
  endpoint: string
  model: string
  has_api_key: boolean
}

const apiBase = useApiBase()
const { worlds, selectedWorldId, loadWorlds, createWorld, deleteWorld, selectWorld } = useWorlds()
const newWorldName = ref("")
const newWorldSlug = ref("")
const creatingWorld = ref(false)
const exportScope = ref<"current" | "all">("current")
const exporting = ref(false)
const confirmingDelete = ref(false)
const deletingWorld = ref(false)
const testingAi = ref(false)
const aiConnectionState = ref<"idle" | "ok" | "error">("idle")
const aiConfig = ref<AiConfig>({ provider: "", endpoint: "", model: "", has_api_key: false })
const notice = ref("")
const noticeType = ref<"success" | "error">("success")

const selectedWorld = computed(() => worlds.value.find((world) => world.id === selectedWorldId.value))
const canDeleteWorld = computed(() => Boolean(selectedWorld.value && selectedWorld.value.slug !== "default"))

function showNotice(message: string, type: "success" | "error" = "success") {
  notice.value = message
  noticeType.value = type
}

function changeWorld(event: Event) {
  selectWorld((event.target as HTMLSelectElement).value)
  confirmingDelete.value = false
}

async function addWorld() {
  creatingWorld.value = true
  try {
    const world = await createWorld({ name: newWorldName.value.trim(), slug: newWorldSlug.value.trim() })
    newWorldName.value = ""
    newWorldSlug.value = ""
    showNotice(`已创建“${world.name}”`)
  } catch (error: any) {
    showNotice(error?.data?.detail || error?.message || "世界创建失败", "error")
  } finally {
    creatingWorld.value = false
  }
}

async function loadAiConfig() {
  try {
    aiConfig.value = await $fetch<AiConfig>(`${apiBase}/api/extract/status`)
  } catch {
    aiConnectionState.value = "error"
  }
}

async function testAiConnection() {
  testingAi.value = true
  try {
    const result = await $fetch<{ ok: boolean; detail?: string; model_available?: boolean }>(`${apiBase}/api/extract/test`, { method: "POST" })
    aiConnectionState.value = result.ok ? "ok" : "error"
    if (!result.ok) showNotice(result.detail || "AI 服务不可用", "error")
    else if (result.model_available === false) showNotice("服务连接成功，但当前模型尚未安装", "error")
    else showNotice("AI 服务连接正常")
  } catch (error: any) {
    aiConnectionState.value = "error"
    showNotice(error?.data?.detail || error?.message || "AI 连接测试失败", "error")
  } finally {
    testingAi.value = false
  }
}

async function exportData() {
  exporting.value = true
  try {
    const query = exportScope.value === "current" && selectedWorldId.value
      ? `?world_id=${encodeURIComponent(selectedWorldId.value)}`
      : ""
    const response = await fetch(`${apiBase}/api/export${query}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement("a")
    const slug = exportScope.value === "current" ? selectedWorld.value?.slug || "world" : "all-worlds"
    anchor.href = url
    anchor.download = `nexus-lore-${slug}-${new Date().toISOString().slice(0, 10)}.json`
    anchor.click()
    URL.revokeObjectURL(url)
    showNotice("设定集已导出")
  } catch (error: any) {
    showNotice(error?.message || "数据导出失败", "error")
  } finally {
    exporting.value = false
  }
}

async function removeSelectedWorld() {
  if (!selectedWorld.value || !canDeleteWorld.value) return
  const worldName = selectedWorld.value.name
  deletingWorld.value = true
  try {
    await deleteWorld(selectedWorld.value.id)
    confirmingDelete.value = false
    showNotice(`已删除“${worldName}”`)
  } catch (error: any) {
    showNotice(error?.data?.detail || error?.message || "世界删除失败", "error")
  } finally {
    deletingWorld.value = false
  }
}

onMounted(async () => {
  await loadWorlds()
  await loadAiConfig()
})
</script>

<style scoped>
.settings-page { width: min(780px, 100%); min-width: 0; }
.page-header { padding-bottom: var(--space-6); border-bottom: 1px solid var(--color-border); }
.page-header h1 { font-size: var(--font-size-3xl); letter-spacing: 0; }
.page-header p { margin-top: var(--space-1); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.notice { margin-top: var(--space-4); padding: var(--space-3) var(--space-4); border: 1px solid rgba(0, 255, 136, .3); color: var(--color-success); font-size: var(--font-size-sm); }
.notice.error { border-color: rgba(255, 51, 85, .35); color: var(--color-danger); }
.settings-sections { display: flex; flex-direction: column; }
.settings-section { padding: var(--space-7) 0; border-bottom: 1px solid var(--color-border); }
.section-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-4); color: var(--color-accent-cyan); }
.section-header h2 { color: var(--color-text-primary); font-size: var(--font-size-base); letter-spacing: 0; }
.status-dot { width: 7px; height: 7px; margin-left: auto; border-radius: 50%; background: var(--color-text-muted); }
.status-dot.ok { background: var(--color-success); box-shadow: 0 0 8px rgba(0, 255, 136, .5); }
.status-dot.error { background: var(--color-danger); }
.setting-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-5); padding: var(--space-4) 0; }
.setting-row + .setting-row { border-top: 1px solid rgba(42, 42, 74, .6); }
.setting-row.stacked { align-items: stretch; flex-direction: column; gap: var(--space-2); }
.setting-label { color: var(--color-text-primary); font-size: var(--font-size-sm); font-weight: var(--font-weight-medium); }
.inline-control { display: grid; grid-template-columns: minmax(0, 1fr) 38px; gap: var(--space-2); }
.world-form { display: grid; grid-template-columns: minmax(0, 1fr) 150px auto; gap: var(--space-2); }
.setting-input, .compact-select { min-height: 38px; border: 1px solid var(--color-border); border-radius: var(--radius-md); outline: none; background: var(--color-bg-input); color: var(--color-text-primary); font: inherit; font-size: var(--font-size-sm); }
.setting-input { width: 100%; padding: 0 var(--space-3); }
.compact-select { padding: 0 var(--space-2); }
.setting-input:focus, .compact-select:focus { border-color: var(--color-accent-cyan); }
.icon-button { display: inline-flex; width: 38px; height: 38px; align-items: center; justify-content: center; border: 1px solid var(--color-border); border-radius: var(--radius-md); color: var(--color-text-secondary); }
.icon-button:hover { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }
.config-list { border-top: 1px solid var(--color-border); }
.config-list div { display: grid; grid-template-columns: 130px minmax(0, 1fr); gap: var(--space-4); padding: var(--space-3) 0; border-bottom: 1px solid var(--color-border); font-size: var(--font-size-sm); }
.config-list dt { color: var(--color-text-muted); }
.config-list dd { overflow-wrap: anywhere; color: var(--color-text-secondary); text-align: right; }
.section-actions { display: flex; justify-content: flex-end; padding-top: var(--space-4); }
.setting-info { display: flex; min-width: 0; flex-direction: column; gap: 3px; }
.setting-info strong { color: var(--color-text-primary); font-size: var(--font-size-sm); }
.setting-info span { color: var(--color-text-muted); font-size: var(--font-size-xs); line-height: var(--line-height-normal); }
.action-control, .confirm-actions { display: flex; flex-shrink: 0; align-items: center; gap: var(--space-2); }
.btn { display: inline-flex; min-height: 38px; align-items: center; justify-content: center; gap: var(--space-2); padding: 0 var(--space-3); border-radius: var(--radius-md); font: inherit; font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); cursor: pointer; }
.btn:disabled { opacity: .4; cursor: not-allowed; }
.btn-secondary { border: 1px solid var(--color-border); background: transparent; color: var(--color-text-primary); }
.btn-secondary:hover:not(:disabled) { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }
.btn-danger { border: 1px solid var(--color-danger); background: transparent; color: var(--color-danger); }
.btn-danger.solid { background: var(--color-danger); color: white; }
.btn-ghost { border: 0; background: transparent; color: var(--color-text-secondary); }
.danger-row { border-top-color: rgba(255, 51, 85, .25) !important; }
.about-section { padding-bottom: var(--space-10); }
@media (max-width: 680px) {
  .world-form { grid-template-columns: 1fr; }
  .setting-row { align-items: stretch; flex-direction: column; }
  .action-control, .confirm-actions { justify-content: flex-end; }
  .config-list div { grid-template-columns: 95px minmax(0, 1fr); }
}
</style>
