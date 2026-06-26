<template>
  <div class="nexus-page">
    <header class="page-header">
      <h1>Nexus</h1>
      <p class="subtitle">动态拓扑星图</p>
    </header>

    <!-- 过滤栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>阵营</label>
        <select v-model="factionFilter" class="filter-select">
          <option value="">全部</option>
          <option v-for="f in factions" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>关系类型</label>
        <select v-model="relationFilter" class="filter-select">
          <option value="">全部</option>
          <option value="ally">盟友</option>
          <option value="hostile">敌对</option>
          <option value="neutral">中立</option>
        </select>
      </div>
      <div class="filter-group">
        <label>标签</label>
        <input v-model="tagFilter" class="search-input" placeholder="按标签筛选..." />
      </div>
      <div class="filter-group">
        <label>时间范围</label>
        <input v-model="timeStart" type="number" class="filter-input-sm" placeholder="从" />
        <span class="range-sep">—</span>
        <input v-model="timeEnd" type="number" class="filter-input-sm" placeholder="到" />
      </div>
    </div>

    <!-- 图谱容器 -->
    <div class="nexus-container">
      <EntityRelationGraph
        :nodes="filteredNodes"
        :links="filteredLinks"
        @node-click="onNodeClick"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const factionFilter = ref('')
const relationFilter = ref('')
const tagFilter = ref('')
const timeStart = ref<number | null>(null)
const timeEnd = ref<number | null>(null)

const factions = ref<string[]>([])
const nodes = ref<any[]>([])
const links = ref<any[]>([])

const filteredNodes = computed(() => nodes.value)
const filteredLinks = computed(() => links.value)

function onNodeClick(node: any) {
  navigateTo('/lore/' + node.id)
}
</script>

<style scoped>
.nexus-page { height: calc(100vh - 64px); display: flex; flex-direction: column; }
.page-header { margin-bottom: 16px; }
.page-header h1 { font-size: 28px; font-weight: 700; }
.subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 2px; }
.filter-bar { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.filter-select, .search-input { padding: 8px 12px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); font-size: 13px; }
.filter-input-sm { width: 80px; padding: 8px 10px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); font-size: 13px; }
.range-sep { color: var(--text-dim); }
.nexus-container { flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; position: relative; min-height: 500px; }
</style>
