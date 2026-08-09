<template>
  <div class="nexus-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Nexus</h1>
        <p class="page-description">实体关系与故事来源的 3D 球状星图</p>
      </div>
      <div class="graph-stats" aria-label="当前星图统计">
        <span><strong>{{ filteredNodes.length }}</strong> 节点</span>
        <span><strong>{{ filteredLinks.length }}</strong> 连接</span>
      </div>
    </header>

    <div class="mode-row">
      <div class="segmented-control" aria-label="星图模式">
        <button v-for="mode in graphModes" :key="mode.value" :class="{ active: graphMode === mode.value }" @click="graphMode = mode.value">
          <component :is="mode.icon" :size="15" aria-hidden="true" />
          <span>{{ mode.label }}</span>
        </button>
      </div>
      <p class="mode-description">{{ currentModeDescription }}</p>
    </div>

    <div class="filter-row">
      <div class="search-wrapper">
        <SearchIcon :size="15" aria-hidden="true" />
        <input v-model="search" type="search" placeholder="搜索节点名称、原型或标签…" />
      </div>
      <select v-model="typeFilter" aria-label="节点类型">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
      </select>
      <select v-model="relationFilter" aria-label="关系类型">
        <option value="">全部关系</option>
        <option v-for="item in visibleRelationOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
      </select>
    </div>

    <div class="graph-shell">
      <div class="graph-toolbar">
        <div class="legend" aria-label="节点图例">
          <span v-for="item in activeLegend" :key="item.value"><i :style="{ background: item.color }"></i>{{ item.label }}</span>
        </div>
        <div class="view-controls">
          <button title="放大" aria-label="放大" @click="graphRef?.zoomIn()"><ZoomInIcon :size="16" /></button>
          <button title="缩小" aria-label="缩小" @click="graphRef?.zoomOut()"><ZoomOutIcon :size="16" /></button>
          <button title="复位视角" aria-label="复位视角" @click="graphRef?.resetView()"><ScanIcon :size="16" /></button>
          <button title="重建球面布局" aria-label="重建球面布局" @click="graphRef?.reheat()"><RefreshCwIcon :size="15" /></button>
        </div>
      </div>

      <EntityRelationGraph
        v-if="!loading && filteredNodes.length"
        ref="graphRef"
        class="graph-canvas"
        :nodes="filteredNodes"
        :links="filteredLinks"
        :selected-id="selectedNode?.id"
        @node-select="selectedNode = $event"
      />

      <div v-if="loading" class="graph-state">
        <LoaderCircleIcon :size="30" class="spin" aria-hidden="true" />
        <p>正在构建星图…</p>
      </div>
      <div v-else-if="errorMessage" class="graph-state">
        <CircleAlertIcon :size="34" class="danger" aria-hidden="true" />
        <p>{{ errorMessage }}</p>
        <button class="retry-button" @click="loadGraph">重试</button>
      </div>
      <div v-else-if="!filteredNodes.length" class="graph-state">
        <NetworkIcon :size="38" aria-hidden="true" />
        <p>当前筛选条件下没有可显示的关联节点</p>
      </div>

      <aside v-if="selectedNode" class="node-inspector">
        <button class="close-button" aria-label="关闭节点详情" @click="selectedNode = null"><XIcon :size="16" /></button>
        <span class="node-type"><i :style="{ background: selectedNode.color || '#00f0ff' }"></i>{{ typeLabel(selectedNode.entity_type) }}</span>
        <h2>{{ selectedNode.name }}</h2>
        <p v-if="selectedNode.canonical_name" class="canonical-name">原型：{{ selectedNode.canonical_name }}</p>
        <p v-if="selectedNode.summary" class="node-summary">{{ selectedNode.summary }}</p>
        <div v-if="selectedNode.tags?.length" class="tag-list">
          <span v-for="tag in selectedNode.tags.slice(0, 6)" :key="tag">{{ tag }}</span>
        </div>
        <div class="inspector-meta">
          <span>{{ nodeDegree(selectedNode.id) }} 条可见连接</span>
          <span v-if="selectedNode.status" :class="{ missing: selectedNode.status === 'missing' }">{{ selectedNode.status === "missing" ? "来源失效" : "来源已读取" }}</span>
        </div>
        <a v-if="selectedNode.entity_type === 'source' && selectedNode.url" :href="selectedNode.url" target="_blank" rel="noreferrer" class="detail-button">
          <ExternalLinkIcon :size="15" />
          <span>打开来源</span>
        </a>
        <NuxtLink v-else :to="loreDetailPath(selectedNode.id)" class="detail-button">
          <BookOpenIcon :size="15" />
          <span>查看设定详情</span>
        </NuxtLink>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import {
  BookOpen as BookOpenIcon,
  CircleAlert as CircleAlertIcon,
  ExternalLink as ExternalLinkIcon,
  Layers3,
  LoaderCircle as LoaderCircleIcon,
  Network as NetworkIcon,
  RefreshCw as RefreshCwIcon,
  Scan as ScanIcon,
  Search as SearchIcon,
  Waypoints,
  X as XIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  type LucideIcon,
} from "lucide-vue-next"

interface GraphNode {
  id: string
  name: string
  entity_type: string
  color?: string | null
  size?: number
  summary?: string | null
  tags?: string[]
  url?: string | null
  status?: string | null
  canonical_name?: string | null
}

interface GraphLink {
  source: string
  target: string
  relation_type: string
  label?: string | null
  color?: string | null
}

type GraphMode = "relations" | "stories" | "all"

interface GraphModeOption {
  value: GraphMode
  label: string
  description: string
  icon: LucideIcon
}

const graphMode = ref<GraphMode>("all")
const search = ref("")
const typeFilter = ref("")
const relationFilter = ref("")
const nodes = ref<GraphNode[]>([])
const links = ref<GraphLink[]>([])
const selectedNode = ref<GraphNode | null>(null)
const loading = ref(false)
const errorMessage = ref("")
const graphRef = ref<any>(null)
const route = useRoute()
const { selectedWorldId, loadWorlds, selectWorld } = useWorlds()
const apiBase = useApiBase()

const graphModes: GraphModeOption[] = [
  { value: "relations", label: "实体关系", description: "只显示隶属、地点、家庭等明确设定关系。", icon: Waypoints },
  { value: "stories", label: "故事脉络", description: "通过承载文章查看哪些设定出现在同一故事中。", icon: BookOpenIcon },
  { value: "all", label: "全部网络", description: "合并实体关系和文章脉络。", icon: Layers3 },
]

const typeOptions = [
  { value: "character", label: "人物", color: "#00f0ff" },
  { value: "faction", label: "势力", color: "#ff00aa" },
  { value: "location", label: "地点", color: "#00ff88" },
  { value: "item", label: "物品", color: "#ffd700" },
  { value: "containment", label: "异常", color: "#ff3355" },
  { value: "source", label: "来源文章", color: "#8b5cf6" },
]

const relationOptions = [
  { value: "member", label: "隶属" },
  { value: "located_at", label: "位于" },
  { value: "other", label: "家庭/其他" },
  { value: "ally", label: "同盟" },
  { value: "hostile", label: "敌对" },
  { value: "appears_in", label: "出现于" },
]

const currentModeDescription = computed(() => graphModes.find((mode) => mode.value === graphMode.value)?.description || "")
const visibleRelationOptions = computed(() => relationOptions.filter((option) => {
  if (graphMode.value === "relations") return option.value !== "appears_in"
  if (graphMode.value === "stories") return option.value === "appears_in"
  return true
}))
const activeLegend = computed(() => typeOptions.filter((item) => graphMode.value !== "relations" || item.value !== "source"))

const modeLinks = computed(() => links.value.filter((link) => {
  if (graphMode.value === "relations") return link.relation_type !== "appears_in"
  if (graphMode.value === "stories") return link.relation_type === "appears_in"
  return true
}).filter((link) => !relationFilter.value || link.relation_type === relationFilter.value))

const filteredGraph = computed(() => {
  const query = search.value.trim().toLowerCase()
  const focusIds = new Set(nodes.value.filter((node) => {
    if (typeFilter.value && node.entity_type !== typeFilter.value) return false
    if (!query) return true
    return `${node.name} ${node.canonical_name || ""} ${(node.tags || []).join(" ")}`.toLowerCase().includes(query)
  }).map((node) => node.id))

  const hasFocusFilter = Boolean(query || typeFilter.value)
  const visibleIds = new Set<string>()
  for (const link of modeLinks.value) {
    const source = typeof link.source === "string" ? link.source : (link.source as any).id
    const target = typeof link.target === "string" ? link.target : (link.target as any).id
    if (!hasFocusFilter || focusIds.has(source) || focusIds.has(target)) {
      visibleIds.add(source)
      visibleIds.add(target)
    }
  }
  if (hasFocusFilter) focusIds.forEach((id) => visibleIds.add(id))

  const visibleNodes = nodes.value.filter((node) => visibleIds.has(node.id))
  const visibleNodeIds = new Set(visibleNodes.map((node) => node.id))
  const visibleLinks = modeLinks.value.filter((link) => {
    const source = typeof link.source === "string" ? link.source : (link.source as any).id
    const target = typeof link.target === "string" ? link.target : (link.target as any).id
    return visibleNodeIds.has(source) && visibleNodeIds.has(target)
  })
  return { nodes: visibleNodes, links: visibleLinks }
})

const filteredNodes = computed(() => filteredGraph.value.nodes)
const filteredLinks = computed(() => filteredGraph.value.links)

function typeLabel(type: string) {
  return typeOptions.find((item) => item.value === type)?.label || type
}

function loreDetailPath(id: string) {
  const worldId = typeof route.params.worldId === "string" ? route.params.worldId : ""
  return worldId ? `/worlds/${worldId}/lore/${id}` : `/lore/${id}`
}

function nodeDegree(id: string) {
  return filteredLinks.value.filter((link) => {
    const source = typeof link.source === "string" ? link.source : (link.source as any).id
    const target = typeof link.target === "string" ? link.target : (link.target as any).id
    return source === id || target === id
  }).length
}

async function loadGraph() {
  if (!selectedWorldId.value) return
  loading.value = true
  errorMessage.value = ""
  selectedNode.value = null
  try {
    const graph = await $fetch<{ nodes: GraphNode[]; links: GraphLink[] }>(`${apiBase}/api/relations/graph`, {
      query: { world_id: selectedWorldId.value, include_documents: true },
    })
    nodes.value = graph.nodes
    links.value = graph.links
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || "星图数据读取失败"
  } finally {
    loading.value = false
  }
}

watch(graphMode, () => {
  relationFilter.value = ""
  selectedNode.value = null
})
watch([search, typeFilter, relationFilter], () => { selectedNode.value = null })
watch(selectedWorldId, loadGraph)

onMounted(async () => {
  await loadWorlds()
  if (typeof route.params.worldId === "string") selectWorld(route.params.worldId)
  await loadGraph()
})
</script>

<style scoped>
.nexus-page {
  height: calc(100vh - 64px);
  min-height: 620px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-4); flex-shrink: 0; }
.page-title { font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); letter-spacing: 0; }
.page-description { color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-top: var(--space-1); }
.graph-stats { display: flex; gap: var(--space-4); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.graph-stats strong { color: var(--color-accent-cyan); font-family: var(--font-mono); }

.mode-row { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-3); flex-shrink: 0; }
.segmented-control { display: flex; min-height: 36px; border: 1px solid var(--color-border); border-radius: var(--radius-md); overflow: hidden; flex-shrink: 0; }
.segmented-control button { display: inline-flex; align-items: center; gap: 6px; padding: 0 var(--space-3); border: 0; border-right: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-secondary); font: inherit; font-size: var(--font-size-sm); cursor: pointer; }
.segmented-control button:last-child { border-right: 0; }
.segmented-control button.active { background: rgba(0, 240, 255, 0.1); color: var(--color-accent-cyan); }
.mode-description { color: var(--color-text-muted); font-size: var(--font-size-xs); }

.filter-row { display: grid; grid-template-columns: minmax(240px, 1fr) 150px 150px; gap: var(--space-2); padding-bottom: var(--space-3); flex-shrink: 0; }
.search-wrapper { position: relative; min-width: 0; }
.search-wrapper svg { position: absolute; left: var(--space-3); top: 50%; transform: translateY(-50%); color: var(--color-text-muted); }
.search-wrapper input, .filter-row select { width: 100%; min-height: 36px; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-bg-input); color: var(--color-text-primary); font: inherit; font-size: var(--font-size-sm); }
.search-wrapper input { padding: 0 var(--space-3) 0 36px; }
.filter-row select { padding: 0 var(--space-2); }
.search-wrapper input:focus, .filter-row select:focus { outline: none; border-color: var(--color-border-focus); }

.graph-shell { position: relative; flex: 1; min-height: 500px; border: 1px solid var(--color-border); overflow: hidden; }
.graph-toolbar { position: absolute; z-index: 3; top: 0; left: 0; right: 0; min-height: 42px; display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); padding: 0 var(--space-3); background: rgba(10, 10, 15, 0.88); border-bottom: 1px solid var(--color-border); backdrop-filter: blur(8px); }
.graph-canvas { padding-top: 42px; }
.legend { display: flex; align-items: center; gap: var(--space-3); min-width: 0; overflow-x: auto; scrollbar-width: none; }
.legend span { display: inline-flex; align-items: center; gap: 5px; color: var(--color-text-muted); font-size: var(--font-size-xs); white-space: nowrap; }
.legend i, .node-type i { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.view-controls { display: flex; gap: 2px; flex-shrink: 0; }
.view-controls button, .close-button { width: 30px; height: 30px; display: inline-flex; align-items: center; justify-content: center; border: 0; border-radius: var(--radius-sm); background: transparent; color: var(--color-text-secondary); cursor: pointer; }
.view-controls button:hover, .close-button:hover { background: rgba(0, 240, 255, 0.08); color: var(--color-accent-cyan); }

.graph-state { position: absolute; inset: 42px 0 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-3); color: var(--color-text-muted); }
.spin { animation: spin 0.8s linear infinite; color: var(--color-accent-cyan); }
@keyframes spin { to { transform: rotate(360deg); } }
.danger { color: var(--color-danger); }
.retry-button { padding: var(--space-2) var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-bg-card); color: var(--color-text-primary); cursor: pointer; }

.node-inspector { position: absolute; z-index: 5; top: 58px; right: var(--space-4); width: min(320px, calc(100% - 32px)); max-height: calc(100% - 76px); overflow-y: auto; padding: var(--space-5); border: 1px solid var(--color-border); border-radius: var(--radius-md); background: rgba(18, 18, 26, 0.96); box-shadow: var(--shadow-lg); }
.close-button { position: absolute; top: var(--space-2); right: var(--space-2); }
.node-type { display: flex; align-items: center; gap: 6px; color: var(--color-text-muted); font-size: var(--font-size-xs); margin-bottom: var(--space-2); }
.node-inspector h2 { padding-right: var(--space-6); font-size: var(--font-size-xl); letter-spacing: 0; overflow-wrap: anywhere; }
.canonical-name { margin-top: var(--space-2); color: var(--color-accent-cyan); font-size: var(--font-size-sm); }
.node-summary { margin-top: var(--space-3); color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: var(--line-height-relaxed); }
.tag-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: var(--space-3); }
.tag-list span { padding: 2px 7px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: var(--font-size-xs); }
.inspector-meta { display: flex; justify-content: space-between; gap: var(--space-3); padding: var(--space-3) 0; margin-top: var(--space-4); border-top: 1px solid var(--color-border); color: var(--color-text-muted); font-size: var(--font-size-xs); }
.inspector-meta .missing { color: var(--color-danger); }
.detail-button { min-height: 36px; display: flex; align-items: center; justify-content: center; gap: var(--space-2); border: 1px solid var(--color-border-focus); border-radius: var(--radius-md); color: var(--color-accent-cyan); font-size: var(--font-size-sm); }
.detail-button:hover { background: rgba(0, 240, 255, 0.08); }

@media (max-width: 860px) {
  .mode-row { align-items: flex-start; flex-direction: column; gap: var(--space-2); }
  .filter-row { grid-template-columns: 1fr 1fr; }
  .search-wrapper { grid-column: 1 / -1; }
}

@media (max-width: 620px) {
  .nexus-page { height: auto; min-height: calc(100vh - 134px); }
  .mode-row { min-width: 0; overflow: hidden; }
  .segmented-control { width: 100%; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .segmented-control button { width: 100%; min-width: 0; justify-content: center; gap: 3px; padding: 0 2px; }
  .segmented-control button span { white-space: nowrap; }
  .filter-row { grid-template-columns: 1fr; }
  .search-wrapper { grid-column: auto; }
  .graph-stats { display: none; }
  .graph-shell { height: 540px; flex: none; min-height: 540px; }
}
</style>
