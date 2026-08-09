<template>
  <div class="sources-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">{{ world?.name || "世界工作区" }}</span>
        <h1>来源文章</h1>
        <p>查看原始资料、读取状态与结构化分析摘要</p>
      </div>
      <span class="total-count">{{ catalog.total }} 篇</span>
    </header>

    <section class="status-strip" aria-label="来源状态">
      <button :class="{ active: !statusFilter }" @click="setStatus('')"><span>全部</span><strong>{{ allCount }}</strong></button>
      <button :class="{ active: statusFilter === 'analyzed' }" @click="setStatus('analyzed')"><span>已读取</span><strong>{{ analyzedCount }}</strong></button>
      <button :class="{ active: statusFilter === 'missing' }" @click="setStatus('missing')"><span>待补来源</span><strong>{{ catalog.status_counts.missing || 0 }}</strong></button>
    </section>

    <div class="filter-row">
      <div class="search-box">
        <SearchIcon :size="16" aria-hidden="true" />
        <input v-model="search" type="search" placeholder="搜索文章标题" />
      </div>
      <select v-model="statusFilter" aria-label="读取状态">
        <option value="">全部状态</option>
        <option value="analyzed">已读取</option>
        <option value="imported">已导入</option>
        <option value="missing">失效或红链</option>
        <option value="analyzing">分析中</option>
      </select>
    </div>

    <div v-if="pending" class="page-state"><LoaderCircleIcon :size="24" class="spin" /><span>正在读取目录…</span></div>
    <div v-else-if="error" class="page-state error"><CircleAlertIcon :size="24" /><span>来源目录读取失败</span></div>
    <div v-else-if="catalog.items.length" class="source-list">
      <NuxtLink v-for="document in catalog.items" :key="document.id" :to="`/worlds/${worldId}/sources/${document.id}`" class="source-row">
        <span class="status-dot" :class="document.status" aria-hidden="true" />
        <span class="source-copy">
          <strong>{{ document.title }}</strong>
          <small>{{ document.analysis_summary || fallbackSummary(document) }}</small>
        </span>
        <span class="source-meta">
          <span class="status-label" :class="document.status">{{ statusLabel(document.status) }}</span>
          <time>{{ formatDate(document.updated_at) }}</time>
        </span>
        <ChevronRightIcon :size="16" aria-hidden="true" />
      </NuxtLink>
    </div>
    <div v-else class="page-state"><FilesIcon :size="28" /><span>没有符合条件的来源文章</span></div>

    <footer v-if="totalPages > 1" class="pagination">
      <button :disabled="page <= 1" title="上一页" @click="page--"><ChevronLeftIcon :size="17" /></button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button :disabled="page >= totalPages" title="下一页" @click="page++"><ChevronRightIcon :size="17" /></button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue"
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  CircleAlert as CircleAlertIcon,
  Files as FilesIcon,
  LoaderCircle as LoaderCircleIcon,
  Search as SearchIcon,
} from "lucide-vue-next"

interface CatalogItem {
  id: string
  title: string
  url?: string | null
  source_site?: string | null
  status: string
  analysis_summary?: string | null
  meta?: Record<string, any>
  updated_at: string
}

interface CatalogResponse {
  items: CatalogItem[]
  total: number
  page: number
  page_size: number
  status_counts: Record<string, number>
}

const emptyCatalog = (): CatalogResponse => ({ items: [], total: 0, page: 1, page_size: 30, status_counts: {} })
const route = useRoute()
const worldId = String(route.params.worldId)
const page = ref(1)
const pageSize = 30
const search = ref("")
const statusFilter = ref(typeof route.query.status === "string" ? route.query.status : "")
const { worlds, loadWorlds, selectWorld } = useWorlds()
await loadWorlds()
selectWorld(worldId)
const world = computed(() => worlds.value.find((item) => item.id === worldId))
const requestQuery = computed(() => ({ world_id: worldId, page: page.value, page_size: pageSize, status: statusFilter.value || undefined, search: search.value.trim() || undefined }))
const { data: catalogData, pending, error, refresh } = await useFetch<CatalogResponse>("/api/documents/catalog", {
  query: requestQuery,
  watch: false,
  default: emptyCatalog,
})
const catalog = computed(() => catalogData.value || emptyCatalog())
const allCount = computed(() => Object.values(catalog.value.status_counts).reduce((sum, count) => sum + count, 0))
const analyzedCount = computed(() => (catalog.value.status_counts.analyzed || 0) + (catalog.value.status_counts.imported || 0))
const totalPages = computed(() => Math.max(1, Math.ceil(catalog.value.total / pageSize)))
let searchTimer: ReturnType<typeof setTimeout> | undefined

watch([page, statusFilter], () => refresh())
watch(search, () => {
  clearTimeout(searchTimer)
  page.value = 1
  searchTimer = setTimeout(() => refresh(), 250)
})

function setStatus(status: string) {
  page.value = 1
  statusFilter.value = status
}

function statusLabel(status: string) {
  return ({ analyzed: "已读取", imported: "已导入", missing: "待补", analyzing: "分析中" } as Record<string, string>)[status] || status
}

function fallbackSummary(document: CatalogItem) {
  const section = document.meta?.catalog_section
  return section ? `设定中心分区：${section}` : "尚无分析摘要"
}

function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? "" : new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric" }).format(date)
}
</script>

<style scoped>
.sources-page { width: min(1080px, 100%); min-width: 0; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-5); }
.page-kicker { color: var(--color-accent-cyan); font-size: var(--font-size-xs); }
.page-header h1 { margin-top: 2px; font-size: var(--font-size-3xl); letter-spacing: 0; }
.page-header p { margin-top: var(--space-1); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.total-count { color: var(--color-accent-cyan); font-family: var(--font-mono); font-size: var(--font-size-sm); }
.status-strip { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border); }
.status-strip button { display: flex; align-items: center; justify-content: space-between; min-height: 52px; padding: 0 var(--space-4); border: 0; border-right: 1px solid var(--color-border); background: transparent; color: var(--color-text-secondary); font: inherit; font-size: var(--font-size-sm); cursor: pointer; }
.status-strip button:last-child { border-right: 0; }
.status-strip button:hover, .status-strip button.active { background: rgba(0, 240, 255, 0.05); color: var(--color-accent-cyan); }
.status-strip strong { font-family: var(--font-mono); }
.filter-row { display: grid; grid-template-columns: minmax(220px, 1fr) 160px; gap: var(--space-3); padding: var(--space-4) 0; }
.search-box { position: relative; }
.search-box svg { position: absolute; top: 50%; left: var(--space-3); color: var(--color-text-muted); transform: translateY(-50%); }
.search-box input, .filter-row select { width: 100%; min-height: 36px; border: 1px solid var(--color-border); border-radius: var(--radius-md); outline: none; background: var(--color-bg-input); color: var(--color-text-primary); font: inherit; font-size: var(--font-size-sm); }
.search-box input { padding: 0 var(--space-3) 0 36px; }
.filter-row select { padding: 0 var(--space-2); }
.search-box input:focus, .filter-row select:focus { border-color: var(--color-accent-cyan); }
.source-list { border-bottom: 1px solid var(--color-border); }
.source-row { display: grid; grid-template-columns: 8px minmax(0, 1fr) 150px 16px; align-items: center; gap: var(--space-3); min-height: 70px; padding: var(--space-3) var(--space-2); border-top: 1px solid var(--color-border); color: var(--color-text-muted); text-decoration: none; }
.source-row:hover { background: rgba(0, 240, 255, 0.04); color: var(--color-accent-cyan); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-text-muted); }
.status-dot.analyzed, .status-dot.imported { background: var(--color-accent-green); }
.status-dot.missing { background: var(--color-danger); }
.status-dot.analyzing { background: var(--color-accent-yellow); }
.source-copy { display: flex; min-width: 0; flex-direction: column; gap: 4px; }
.source-copy strong { overflow: hidden; color: var(--color-text-primary); font-size: var(--font-size-sm); text-overflow: ellipsis; white-space: nowrap; }
.source-copy small { overflow: hidden; color: var(--color-text-muted); font-size: var(--font-size-xs); text-overflow: ellipsis; white-space: nowrap; }
.source-meta { display: flex; align-items: flex-end; flex-direction: column; gap: 4px; }
.status-label { padding: 2px 6px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 10px; }
.status-label.missing { border-color: rgba(255, 51, 85, 0.3); color: var(--color-danger); }
.source-meta time { color: var(--color-text-muted); font-family: var(--font-mono); font-size: 10px; }
.page-state { display: flex; min-height: 260px; align-items: center; justify-content: center; gap: var(--space-3); color: var(--color-text-muted); }
.page-state.error { color: var(--color-danger); }
.spin { animation: spin .8s linear infinite; } @keyframes spin { to { transform: rotate(360deg); } }
.pagination { display: flex; align-items: center; justify-content: center; gap: var(--space-4); padding: var(--space-5); color: var(--color-text-muted); font-family: var(--font-mono); font-size: var(--font-size-xs); }
.pagination button { display: inline-flex; width: 34px; height: 34px; align-items: center; justify-content: center; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: transparent; color: var(--color-text-secondary); cursor: pointer; }
.pagination button:hover:not(:disabled) { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }
.pagination button:disabled { opacity: .35; cursor: not-allowed; }
@media (max-width: 680px) { .status-strip { grid-template-columns: 1fr; } .status-strip button { border-right: 0; border-bottom: 1px solid var(--color-border); } .filter-row { grid-template-columns: 1fr; } .source-row { grid-template-columns: 8px minmax(0, 1fr) 16px; } .source-meta { display: none; } }
</style>
