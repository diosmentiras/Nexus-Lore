<template>
  <div class="nexus-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Nexus</h1>
        <p class="page-description">动态拓扑星图 · 实体关系可视化</p>
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <label class="filter-label">阵营</label>
        <select v-model="factionFilter" class="filter-select">
          <option value="">全部</option>
          <option v-for="f in factions" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">关系</label>
        <div class="segmented-control">
          <button v-for="opt in relationOptions" :key="opt.value" class="seg-btn" :class="{ active: relationFilter === opt.value }" @click="relationFilter = opt.value">
            {{ opt.label }}
          </button>
        </div>
      </div>
      <div class="filter-group">
        <label class="filter-label">标签</label>
        <div class="search-wrapper">
          <SearchIcon :size="14" class="search-icon" aria-hidden="true" />
          <input v-model="tagFilter" class="filter-input" placeholder="筛选..." />
        </div>
      </div>
      <div class="filter-group">
        <label class="filter-label">时间跨度</label>
        <div class="time-range">
          <input v-model.number="timeStart" type="number" class="time-input" placeholder="从" />
          <span class="range-sep">—</span>
          <input v-model.number="timeEnd" type="number" class="time-input" placeholder="到" />
        </div>
      </div>
    </div>

    <!-- Graph -->
    <div class="graph-container">
      <EntityRelationGraph
        :nodes="filteredNodes"
        :links="filteredLinks"
        @node-click="onNodeClick"
      />
      <div v-if="!nodes.length" class="graph-empty">
        <NetworkIcon :size="40" class="empty-icon" aria-hidden="true" />
        <p>添加设定后星图将自动生成</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { Search, Network } from "lucide-vue-next"

const factionFilter = ref("")
const relationFilter = ref("")
const tagFilter = ref("")
const timeStart = ref<number | null>(null)
const timeEnd = ref<number | null>(null)

const factions = ref<string[]>([])
const nodes = ref<any[]>([])
const links = ref<any[]>([])

const relationOptions = [
  { value: "", label: "全部" },
  { value: "ally", label: "盟友" },
  { value: "hostile", label: "敌对" },
  { value: "neutral", label: "中立" },
]

const filteredNodes = computed(() => nodes.value)
const filteredLinks = computed(() => links.value)

function onNodeClick(node: any) {
  navigateTo("/lore/" + node.id)
}
</script>

<style scoped>
.nexus-page {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: var(--space-4);
  flex-shrink: 0;
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

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  flex-shrink: 0;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.filter-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: var(--font-weight-medium);
}

.filter-select,
.filter-input {
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.filter-input {
  padding-left: 30px;
}

/* Segmented Control */
.segmented-control {
  display: flex;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.seg-btn {
  padding: var(--space-1) var(--space-3);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
}

.seg-btn:hover {
  color: var(--color-text-primary);
}

.seg-btn.active {
  background: rgba(0, 240, 255, 0.1);
  color: var(--color-accent-cyan);
}

/* Time Range */
.time-range {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.time-input {
  width: 80px;
  padding: var(--space-1) var(--space-2);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
}

.time-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

.range-sep {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Graph Container */
.graph-container {
  flex: 1;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  min-height: 400px;
}

.graph-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.empty-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}
</style>
