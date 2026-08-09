<template>
  <div class="dashboard">
    <header class="page-header">
      <div>
        <h1 class="page-title">世界库</h1>
        <p class="page-description">{{ overview.worlds }} 个独立世界观的资料总览</p>
      </div>
      <NuxtLink to="/settings" class="header-link">
        <span>管理世界</span>
        <ArrowRightIcon :size="15" aria-hidden="true" />
      </NuxtLink>
    </header>

    <section v-if="selectedSummary" class="world-overview">
      <div class="world-copy">
        <div class="world-kicker">
          <Globe2Icon :size="15" aria-hidden="true" />
          <span>当前世界</span>
        </div>
        <h2>{{ selectedSummary.name }}</h2>
        <p>{{ selectedSummary.description || "该世界观还没有基础描述。" }}</p>
      </div>
      <div class="world-overview-side">
        <div class="world-metrics">
          <span><strong>{{ selectedSummary.document_count }}</strong> 篇来源</span>
          <span><strong>{{ selectedSummary.entity_count }}</strong> 个 Lore</span>
        </div>
        <div class="world-actions">
          <a v-if="selectedSummary.source_url" :href="selectedSummary.source_url" target="_blank" rel="noreferrer" class="icon-link" title="打开原始设定中心">
            <ExternalLinkIcon :size="16" aria-hidden="true" />
          </a>
          <NuxtLink :to="worldTarget(selectedSummary)" class="primary-link">
            <span>进入世界观</span>
            <ArrowRightIcon :size="15" aria-hidden="true" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="stats-grid" aria-label="全库统计">
      <NuxtLink v-for="stat in stats" :key="stat.label" :to="stat.to" class="stat-card" :style="{ '--stat-color': stat.color }">
        <div class="stat-icon-wrapper">
          <component :is="stat.icon" :size="20" aria-hidden="true" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ formatNumber(stat.value) }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-note">{{ stat.note }}</span>
        </div>
        <ChevronRightIcon :size="15" class="stat-chevron" aria-hidden="true" />
      </NuxtLink>
    </section>

    <div class="content-grid">
      <section class="world-directory">
        <div class="section-header">
          <div>
            <h2>世界观目录</h2>
            <p>选择后可直接进入对应设定档案</p>
          </div>
          <div class="world-search">
            <SearchIcon :size="15" aria-hidden="true" />
            <input v-model="worldSearch" type="search" placeholder="搜索世界观" aria-label="搜索世界观" />
          </div>
        </div>

        <div v-if="loading" class="directory-state">正在汇总资料…</div>
        <div v-else-if="errorMessage" class="directory-state error">{{ errorMessage }}</div>
        <div v-else class="world-list">
          <button
            v-for="world in visibleWorlds"
            :key="world.id"
            type="button"
            class="world-row"
            :class="{ active: world.id === selectedWorldId }"
            @click="openWorld(world)"
          >
            <span class="world-status" aria-hidden="true" />
            <span class="world-row-copy">
              <strong>{{ world.name }}</strong>
              <small>{{ compactDescription(world.description) }}</small>
            </span>
            <span class="world-row-counts">
              <span>{{ world.document_count }} 文章</span>
              <span>{{ world.entity_count }} Lore</span>
            </span>
            <ArrowRightIcon :size="16" aria-hidden="true" />
          </button>

          <div v-if="!visibleWorlds.length" class="directory-state">没有匹配的世界观</div>
        </div>

        <button v-if="canToggleWorlds" type="button" class="toggle-worlds" @click="showAllWorlds = !showAllWorlds">
          <span>{{ showAllWorlds ? "收起目录" : `展开全部 ${filteredWorlds.length} 个世界观` }}</span>
          <ChevronDownIcon :size="15" :class="{ rotated: showAllWorlds }" aria-hidden="true" />
        </button>
      </section>

      <aside class="quick-panel">
        <div class="section-header compact">
          <div>
            <h2>快速前往</h2>
            <p>继续浏览当前资料域</p>
          </div>
        </div>
        <nav class="quick-actions" aria-label="快速操作">
          <NuxtLink v-for="action in quickActions" :key="action.title" :to="action.to" :no-prefetch="action.to === '/nexus'" class="action-row">
            <component :is="action.icon" :size="18" :style="{ color: action.color }" aria-hidden="true" />
            <span>
              <strong>{{ action.title }}</strong>
              <small>{{ action.desc }}</small>
            </span>
            <ChevronRightIcon :size="15" aria-hidden="true" />
          </NuxtLink>
        </nav>

        <div class="ingestion-status">
          <div class="status-heading">
            <CheckCircle2Icon :size="16" aria-hidden="true" />
            <span>来源读取</span>
          </div>
          <div class="progress-track" aria-hidden="true">
            <span :style="{ width: `${availabilityRate}%` }" />
          </div>
          <p>{{ formatNumber(overview.available_documents) }} / {{ formatNumber(overview.documents) }} 篇正文可用</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ alias: ["/worlds"] })

import { computed, onMounted, ref } from "vue"
import {
  AlertTriangle as AlertTriangleIcon,
  ArrowRight as ArrowRightIcon,
  BookOpen as BookOpenIcon,
  Calendar as CalendarIcon,
  CheckCircle2 as CheckCircle2Icon,
  ChevronDown as ChevronDownIcon,
  ChevronRight as ChevronRightIcon,
  ExternalLink as ExternalLinkIcon,
  Files as FilesIcon,
  Globe2 as Globe2Icon,
  History as HistoryIcon,
  Network as NetworkIcon,
  Search as SearchIcon,
  Share2 as Share2Icon,
  type LucideIcon,
} from "lucide-vue-next"

interface WorldSummary {
  id: string
  name: string
  slug: string
  description?: string | null
  source_url?: string | null
  document_count: number
  available_document_count: number
  entity_count: number
  dossier_id?: string | null
}

interface DashboardOverview {
  worlds: number
  documents: number
  available_documents: number
  missing_documents: number
  lore: number
  relations: number
  events: number
  issues: number
  world_summaries: WorldSummary[]
}

interface DashboardStat {
  icon: LucideIcon
  value: number
  label: string
  note: string
  color: string
  to: string
}

const emptyOverview = (): DashboardOverview => ({
  worlds: 0,
  documents: 0,
  available_documents: 0,
  missing_documents: 0,
  lore: 0,
  relations: 0,
  events: 0,
  issues: 0,
  world_summaries: [],
})

const { selectedWorldId, loadWorlds, selectWorld } = useWorlds()
const apiBase = useApiBase()
const {
  data: overview,
  status: overviewStatus,
  error: overviewError,
} = await useFetch<DashboardOverview>(`${apiBase}/api/dashboard/overview`, {
  key: "dashboard-overview",
  default: emptyOverview,
})
await loadWorlds()
const worldSearch = ref("")
const showAllWorlds = ref(false)
const loading = computed(() => overviewStatus.value === "pending")
const errorMessage = computed(() => overviewError.value ? "总览数据加载失败，请确认后端服务正在运行。" : "")

const selectedSummary = computed(() => overview.value.world_summaries.find((world) => world.id === selectedWorldId.value) || overview.value.world_summaries[0])
const selectedTarget = computed(() => selectedSummary.value ? worldTarget(selectedSummary.value) : "/lore")
const selectedLoreTarget = computed(() => selectedSummary.value ? `/worlds/${selectedSummary.value.id}/lore` : "/worlds")
const selectedChronicleTarget = computed(() => selectedSummary.value ? `/worlds/${selectedSummary.value.id}/chronicle` : "/worlds")
const selectedNexusTarget = computed(() => selectedSummary.value ? `/worlds/${selectedSummary.value.id}/nexus` : "/worlds")
const availabilityRate = computed(() => overview.value.documents ? Math.round(overview.value.available_documents / overview.value.documents * 100) : 0)

const stats = computed<DashboardStat[]>(() => [
  { icon: Globe2Icon, value: overview.value.worlds, label: "世界观", note: "独立资料域", color: "var(--color-accent-cyan)", to: "/worlds" },
  { icon: FilesIcon, value: overview.value.documents, label: "来源文章", note: `${formatNumber(overview.value.available_documents)} 篇可读`, color: "var(--color-accent-green)", to: selectedTarget.value },
  { icon: BookOpenIcon, value: overview.value.lore, label: "Lore 条目", note: "结构化设定", color: "var(--color-accent-magenta)", to: selectedLoreTarget.value },
  { icon: Share2Icon, value: overview.value.relations, label: "实体关系", note: "关系星图", color: "var(--color-accent-purple)", to: selectedNexusTarget.value },
  { icon: CalendarIcon, value: overview.value.events, label: "时间事件", note: "编年史轨道", color: "var(--color-accent-yellow)", to: selectedChronicleTarget.value },
  { icon: AlertTriangleIcon, value: overview.value.missing_documents, label: "待补来源", note: "失效或红链", color: "var(--color-danger)", to: selectedTarget.value },
])

const filteredWorlds = computed(() => {
  const query = worldSearch.value.trim().toLowerCase()
  if (!query) return overview.value.world_summaries
  return overview.value.world_summaries.filter((world) => `${world.name} ${world.description || ""}`.toLowerCase().includes(query))
})

const visibleWorlds = computed(() => worldSearch.value || showAllWorlds.value ? filteredWorlds.value : filteredWorlds.value.slice(0, 10))
const canToggleWorlds = computed(() => !worldSearch.value && filteredWorlds.value.length > 10)

const quickActions = computed(() => [
  { to: selectedTarget.value, title: "当前世界档案", desc: selectedSummary.value?.name || "选择世界观", icon: BookOpenIcon, color: "var(--color-accent-cyan)" },
  { to: selectedLoreTarget.value, title: "当前世界 Lore", desc: "浏览该世界全部设定", icon: Globe2Icon, color: "var(--color-accent-magenta)" },
  { to: selectedNexusTarget.value, title: "关系星图", desc: "查看当前世界实体连接", icon: NetworkIcon, color: "var(--color-accent-purple)" },
  { to: selectedChronicleTarget.value, title: "编年史", desc: "沿时间顺序查看事件", icon: HistoryIcon, color: "var(--color-accent-yellow)" },
])

function worldTarget(world: WorldSummary) {
  return `/worlds/${world.id}/overview`
}

function compactDescription(description?: string | null) {
  const normalized = (description || "尚无基础描述").replace(/\s+/g, " ").trim()
  return normalized.length > 68 ? `${normalized.slice(0, 68)}…` : normalized
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("zh-CN").format(value)
}

async function openWorld(world: WorldSummary) {
  selectWorld(world.id)
  await navigateTo(worldTarget(world))
}

onMounted(async () => {
  await loadWorlds()
  if (!overview.value.world_summaries.some((world) => world.id === selectedWorldId.value) && overview.value.world_summaries.length) {
    selectWorld(overview.value.world_summaries[0].id)
  }
})
</script>

<style scoped>
.dashboard {
  width: min(1180px, 100%);
  min-width: 0;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header,
.world-overview,
.section-header,
.header-link,
.primary-link,
.icon-link,
.world-actions,
.world-metrics,
.world-kicker,
.status-heading {
  display: flex;
  align-items: center;
}

.page-header {
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.page-title {
  color: var(--color-text-primary);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0;
}

.page-description {
  margin-top: var(--space-1);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.header-link,
.primary-link {
  gap: var(--space-2);
  min-height: 36px;
  padding: 0 var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  white-space: nowrap;
  transition: border-color var(--duration-fast), color var(--duration-fast), background var(--duration-fast);
}

.header-link:hover,
.primary-link:hover {
  border-color: var(--color-accent-cyan);
  color: var(--color-accent-cyan);
  background: rgba(0, 240, 255, 0.05);
}

.world-overview {
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-8);
  padding: var(--space-6) 0;
  margin-bottom: var(--space-6);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.world-copy {
  min-width: 0;
  max-width: 760px;
}

.world-kicker {
  gap: var(--space-2);
  margin-bottom: var(--space-2);
  color: var(--color-accent-cyan);
  font-size: var(--font-size-xs);
  text-transform: uppercase;
}

.world-copy h2 {
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  letter-spacing: 0;
}

.world-copy p {
  display: -webkit-box;
  margin-top: var(--space-2);
  overflow: hidden;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.world-overview-side {
  display: flex;
  min-width: 220px;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-4);
}

.world-metrics {
  gap: var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.world-metrics strong {
  color: var(--color-text-primary);
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
}

.world-actions { gap: var(--space-2); }

.icon-link {
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
}

.icon-link:hover { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

.stat-card {
  position: relative;
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) 16px;
  align-items: center;
  gap: var(--space-3);
  min-height: 86px;
  padding: var(--space-4);
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  color: inherit;
  text-decoration: none;
  transition: transform var(--duration-fast), border-color var(--duration-fast), background var(--duration-fast);
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--stat-color);
  background: var(--color-bg-secondary);
}

.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--stat-color);
  background: rgba(255, 255, 255, 0.02);
}

.stat-info { display: flex; min-width: 0; flex-direction: column; }
.stat-value { color: var(--color-text-primary); font-family: var(--font-mono); font-size: var(--font-size-xl); font-weight: var(--font-weight-bold); line-height: 1.1; }
.stat-label { margin-top: 3px; color: var(--color-text-secondary); font-size: var(--font-size-xs); }
.stat-note { overflow: hidden; color: var(--color-text-muted); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.stat-chevron { color: var(--color-text-muted); }
.stat-card:hover .stat-chevron { color: var(--stat-color); }

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(260px, 0.75fr);
  gap: var(--space-6);
  align-items: start;
}

.world-directory,
.quick-panel {
  min-width: 0;
  border-top: 1px solid var(--color-border);
}

.section-header {
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-5) 0;
}

.section-header.compact { align-items: flex-start; }
.section-header h2 { color: var(--color-text-primary); font-size: var(--font-size-base); letter-spacing: 0; }
.section-header p { margin-top: 2px; color: var(--color-text-muted); font-size: var(--font-size-xs); }

.world-search {
  position: relative;
  width: min(220px, 45%);
}

.world-search svg {
  position: absolute;
  top: 50%;
  left: var(--space-3);
  color: var(--color-text-muted);
  transform: translateY(-50%);
  pointer-events: none;
}

.world-search input {
  width: 100%;
  min-height: 34px;
  padding: 0 var(--space-3) 0 34px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  outline: none;
  background: var(--color-bg-input);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  font-size: var(--font-size-xs);
}

.world-search input:focus { border-color: var(--color-accent-cyan); }
.world-list { border-bottom: 1px solid var(--color-border); }

.world-row {
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr) auto 16px;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  min-height: 66px;
  padding: var(--space-3) var(--space-2);
  border: 0;
  border-top: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  font-family: var(--font-sans);
  text-align: left;
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast);
}

.world-row:hover,
.world-row.active { background: rgba(0, 240, 255, 0.04); color: var(--color-accent-cyan); }
.world-status { width: 6px; height: 6px; border-radius: 50%; background: var(--color-accent-green); box-shadow: 0 0 6px rgba(0, 255, 170, 0.45); }
.world-row.active .world-status { background: var(--color-accent-cyan); }
.world-row-copy { display: flex; min-width: 0; flex-direction: column; gap: 3px; }
.world-row-copy strong { overflow: hidden; color: var(--color-text-primary); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); text-overflow: ellipsis; white-space: nowrap; }
.world-row-copy small { overflow: hidden; color: var(--color-text-muted); font-size: var(--font-size-xs); text-overflow: ellipsis; white-space: nowrap; }
.world-row-counts { display: flex; gap: var(--space-3); color: var(--color-text-muted); font-family: var(--font-mono); font-size: 10px; white-space: nowrap; }

.directory-state { padding: var(--space-10) var(--space-3); border-top: 1px solid var(--color-border); color: var(--color-text-muted); font-size: var(--font-size-sm); text-align: center; }
.directory-state.error { color: var(--color-danger); }

.toggle-worlds {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  min-height: 40px;
  border: 0;
  background: transparent;
  color: var(--color-text-secondary);
  font-family: var(--font-sans);
  font-size: var(--font-size-xs);
  cursor: pointer;
}

.toggle-worlds:hover { color: var(--color-accent-cyan); }
.toggle-worlds svg { transition: transform var(--duration-fast); }
.toggle-worlds svg.rotated { transform: rotate(180deg); }

.quick-actions { display: flex; flex-direction: column; border-bottom: 1px solid var(--color-border); }
.action-row { display: grid; grid-template-columns: 24px minmax(0, 1fr) 16px; align-items: center; gap: var(--space-3); min-height: 62px; padding: var(--space-3) var(--space-2); border-top: 1px solid var(--color-border); color: var(--color-text-muted); text-decoration: none; }
.action-row:hover { background: rgba(0, 240, 255, 0.04); color: var(--color-accent-cyan); }
.action-row span { display: flex; min-width: 0; flex-direction: column; gap: 2px; }
.action-row strong { color: var(--color-text-primary); font-size: var(--font-size-sm); font-weight: var(--font-weight-medium); }
.action-row small { overflow: hidden; color: var(--color-text-muted); font-size: var(--font-size-xs); text-overflow: ellipsis; white-space: nowrap; }

.ingestion-status { padding: var(--space-5) var(--space-2); }
.status-heading { gap: var(--space-2); color: var(--color-accent-green); font-size: var(--font-size-xs); font-weight: var(--font-weight-semibold); }
.progress-track { height: 4px; margin: var(--space-3) 0 var(--space-2); overflow: hidden; border-radius: 2px; background: var(--color-border); }
.progress-track span { display: block; height: 100%; border-radius: inherit; background: var(--color-accent-green); }
.ingestion-status p { color: var(--color-text-muted); font-family: var(--font-mono); font-size: 10px; }

@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .content-grid { grid-template-columns: 1fr; }
}

@media (max-width: 700px) {
  .page-header { align-items: flex-start; }
  .world-overview { flex-direction: column; gap: var(--space-4); }
  .world-overview-side { width: 100%; min-width: 0; align-items: flex-start; }
  .stats-grid { grid-template-columns: 1fr; }
  .section-header { align-items: flex-start; flex-direction: column; }
  .world-search { width: 100%; }
  .world-row { grid-template-columns: 8px minmax(0, 1fr) 16px; }
  .world-row-counts { display: none; }
}
</style>
