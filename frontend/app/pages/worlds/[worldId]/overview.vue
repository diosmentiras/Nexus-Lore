<template>
  <div v-if="world && summary" class="world-overview-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">世界工作区</span>
        <h1>{{ world.name }}</h1>
        <p>{{ world.description || "该世界观还没有基础描述。" }}</p>
      </div>
      <div class="header-actions">
        <a v-if="world.source_url" :href="world.source_url" target="_blank" rel="noreferrer" class="icon-button" title="打开原始设定中心">
          <ExternalLinkIcon :size="17" aria-hidden="true" />
        </a>
        <NuxtLink v-if="summary.dossier_id" :to="`/worlds/${worldId}/lore/${summary.dossier_id}`" class="primary-button">
          <BookOpenIcon :size="16" aria-hidden="true" />
          <span>世界总档案</span>
        </NuxtLink>
      </div>
    </header>

    <section class="metric-strip" aria-label="世界资料统计">
      <NuxtLink :to="`/worlds/${world.id}/sources`">
        <FilesIcon :size="18" aria-hidden="true" />
        <span><strong>{{ summary.document_count }}</strong> 来源文章</span>
        <small>{{ summary.available_document_count }} 篇可读</small>
      </NuxtLink>
      <NuxtLink :to="`/worlds/${world.id}/lore`">
        <LibraryIcon :size="18" aria-hidden="true" />
        <span><strong>{{ summary.entity_count }}</strong> Lore</span>
        <small>结构化设定</small>
      </NuxtLink>
      <NuxtLink :to="`/worlds/${world.id}/chronicle`">
        <HistoryIcon :size="18" aria-hidden="true" />
        <span><strong>{{ eventCount }}</strong> 时间事件</span>
        <small>按原文日期整理</small>
      </NuxtLink>
      <NuxtLink :to="`/worlds/${world.id}/sources?status=missing`">
        <CircleAlertIcon :size="18" aria-hidden="true" />
        <span><strong>{{ missingCount }}</strong> 待补来源</span>
        <small>失效或红链</small>
      </NuxtLink>
    </section>

    <div class="overview-grid">
      <section class="setting-section">
        <div class="section-heading">
          <h2>基本设定</h2>
          <span>{{ premisePoints.length }} 条纲要</span>
        </div>
        <div v-if="premisePoints.length" class="premise-list">
          <div v-for="(point, index) in premisePoints" :key="point" class="premise-row">
            <span>{{ String(index + 1).padStart(2, "0") }}</span>
            <p>{{ point }}</p>
          </div>
        </div>
        <p v-else class="muted-state">尚未整理世界观纲要。</p>
      </section>

      <aside class="workflow-section">
        <div class="section-heading">
          <h2>资料状态</h2>
          <span>{{ availabilityRate }}% 可读取</span>
        </div>
        <div class="progress-track" aria-hidden="true"><span :style="{ width: `${availabilityRate}%` }" /></div>
        <dl>
          <div><dt>来源站点</dt><dd>{{ world.meta?.source_site || "未标注" }}</dd></div>
          <div><dt>目录分类</dt><dd>{{ world.meta?.catalog || "自建世界" }}</dd></div>
          <div><dt>最后导入</dt><dd>{{ formatDate(world.meta?.last_imported_at) }}</dd></div>
        </dl>
        <nav class="workflow-links" aria-label="世界工作流">
          <NuxtLink :to="`/worlds/${world.id}/sources`"><FilesIcon :size="16" /><span>检查来源文章</span><ChevronRightIcon :size="15" /></NuxtLink>
          <NuxtLink :to="`/worlds/${world.id}/lore`"><LibraryIcon :size="16" /><span>浏览结构化设定</span><ChevronRightIcon :size="15" /></NuxtLink>
          <NuxtLink :to="`/worlds/${world.id}/nexus`"><NetworkIcon :size="16" /><span>查看实体关系</span><ChevronRightIcon :size="15" /></NuxtLink>
        </nav>
      </aside>
    </div>
  </div>
  <div v-else class="page-state">世界观不存在或读取失败。</div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import {
  BookOpen as BookOpenIcon,
  ChevronRight as ChevronRightIcon,
  CircleAlert as CircleAlertIcon,
  ExternalLink as ExternalLinkIcon,
  Files as FilesIcon,
  History as HistoryIcon,
  Library as LibraryIcon,
  Network as NetworkIcon,
} from "lucide-vue-next"

interface WorldSummary {
  id: string
  document_count: number
  available_document_count: number
  entity_count: number
  event_count: number
  dossier_id?: string | null
}

interface OverviewResponse {
  events: number
  world_summaries: WorldSummary[]
}

const route = useRoute()
const worldId = String(route.params.worldId)
const { worlds, loadWorlds, selectWorld } = useWorlds()
await loadWorlds()
selectWorld(worldId)
const world = computed(() => worlds.value.find((item) => item.id === worldId))
const { data: overview } = await useFetch<OverviewResponse>("/api/dashboard/overview", { key: "dashboard-overview" })
const summary = computed(() => overview.value?.world_summaries.find((item) => item.id === worldId))
const premisePoints = computed<string[]>(() => Array.isArray(world.value?.meta?.premise_points) ? world.value!.meta!.premise_points : [])
const missingCount = computed(() => Math.max(0, (summary.value?.document_count || 0) - (summary.value?.available_document_count || 0)))
const availabilityRate = computed(() => summary.value?.document_count ? Math.round(summary.value.available_document_count / summary.value.document_count * 100) : 0)
const eventCount = computed(() => summary.value?.event_count || 0)

function formatDate(value?: string) {
  if (!value) return "未记录"
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium" }).format(date)
}
</script>

<style scoped>
.world-overview-page { width: min(1120px, 100%); min-width: 0; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-6); padding-bottom: var(--space-6); border-bottom: 1px solid var(--color-border); }
.page-kicker { color: var(--color-accent-cyan); font-size: var(--font-size-xs); }
.page-header h1 { margin-top: var(--space-1); color: var(--color-text-primary); font-size: var(--font-size-3xl); letter-spacing: 0; }
.page-header p { max-width: 780px; margin-top: var(--space-2); color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: var(--line-height-relaxed); }
.header-actions { display: flex; align-items: center; gap: var(--space-2); flex-shrink: 0; }
.icon-button, .primary-button { display: inline-flex; align-items: center; justify-content: center; min-height: 36px; border: 1px solid var(--color-border); border-radius: var(--radius-md); color: var(--color-text-primary); text-decoration: none; }
.icon-button { width: 36px; }
.primary-button { gap: var(--space-2); padding: 0 var(--space-3); font-size: var(--font-size-sm); }
.icon-button:hover, .primary-button:hover { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }
.metric-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-bottom: 1px solid var(--color-border); }
.metric-strip a { display: grid; grid-template-columns: 24px minmax(0, 1fr); gap: 2px var(--space-2); min-height: 92px; padding: var(--space-5) var(--space-3); border-right: 1px solid var(--color-border); color: var(--color-accent-cyan); text-decoration: none; }
.metric-strip a:last-child { border-right: 0; }
.metric-strip a:hover { background: rgba(0, 240, 255, 0.04); }
.metric-strip span { color: var(--color-text-secondary); font-size: var(--font-size-xs); }
.metric-strip strong { color: var(--color-text-primary); font-family: var(--font-mono); font-size: var(--font-size-lg); }
.metric-strip small { grid-column: 2; color: var(--color-text-muted); font-size: 10px; }
.overview-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.7fr); gap: var(--space-8); padding-top: var(--space-7); }
.setting-section, .workflow-section { min-width: 0; border-top: 1px solid var(--color-border); }
.section-heading { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); padding: var(--space-4) 0; }
.section-heading h2 { font-size: var(--font-size-base); letter-spacing: 0; }
.section-heading span { color: var(--color-text-muted); font-family: var(--font-mono); font-size: var(--font-size-xs); }
.premise-row { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: var(--space-3); padding: var(--space-4) 0; border-top: 1px solid var(--color-border); }
.premise-row > span { color: var(--color-accent-cyan); font-family: var(--font-mono); font-size: var(--font-size-xs); }
.premise-row p { color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: var(--line-height-relaxed); }
.progress-track { height: 5px; overflow: hidden; border-radius: 3px; background: var(--color-border); }
.progress-track span { display: block; height: 100%; background: var(--color-accent-green); }
.workflow-section dl { margin-top: var(--space-4); }
.workflow-section dl div { display: flex; justify-content: space-between; gap: var(--space-4); padding: var(--space-2) 0; color: var(--color-text-muted); font-size: var(--font-size-xs); }
.workflow-section dd { color: var(--color-text-secondary); text-align: right; }
.workflow-links { display: flex; flex-direction: column; margin-top: var(--space-5); border-bottom: 1px solid var(--color-border); }
.workflow-links a { display: grid; grid-template-columns: 22px minmax(0, 1fr) 16px; align-items: center; gap: var(--space-2); min-height: 48px; border-top: 1px solid var(--color-border); color: var(--color-text-secondary); font-size: var(--font-size-sm); text-decoration: none; }
.workflow-links a:hover { color: var(--color-accent-cyan); }
.muted-state, .page-state { padding: var(--space-10) 0; color: var(--color-text-muted); text-align: center; }
@media (max-width: 800px) { .metric-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } .metric-strip a:nth-child(2) { border-right: 0; } .overview-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .page-header { flex-direction: column; } .metric-strip { grid-template-columns: 1fr; } .metric-strip a { border-right: 0; } }
</style>
