<template>
  <div class="lore-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Lore</h1>
        <p class="page-description">世界观设定库 · 管理所有实体、关系和事件</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="showAiPanel = !showAiPanel">
          <SparklesIcon :size="16" aria-hidden="true" />
          <span>AI Extract</span>
        </button>
        <button class="btn btn-primary" @click="showEditor = true">
          <PlusIcon :size="16" aria-hidden="true" />
          <span>新建设定</span>
        </button>
      </div>
    </header>

    <!-- AI Extract Panel -->
    <transition name="slide">
      <AiExtractPanel v-if="showAiPanel" @close="showAiPanel = false" @extracted="onExtracted" />
    </transition>

    <!-- Lore Editor Modal -->
    <Teleport to="body">
      <transition name="fade">
        <div v-if="showEditor" class="modal-overlay" @click.self="showEditor = false">
          <LoreEditor @close="showEditor = false" @saved="loadLore" />
        </div>
      </transition>
    </Teleport>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-wrapper">
        <SearchIcon :size="16" class="search-icon" aria-hidden="true" />
        <input v-model="search" type="text" class="search-input" placeholder="搜索设定名称、标签..." />
      </div>
      <select v-model="typeFilter" class="filter-select">
        <option value="">全部类型</option>
        <option value="character">人物</option>
        <option value="faction">势力</option>
        <option value="item">物品</option>
        <option value="location">地点</option>
        <option value="event">事件</option>
        <option value="containment">收容物</option>
        <option value="world">世界观</option>
      </select>
    </div>

    <!-- Lore Grid -->
    <transition name="list" mode="out-in">
      <div v-if="filteredLore.length" class="lore-grid" :key="'grid'">
        <LoreCard v-for="item in filteredLore" :key="item.id" :lore="item" @click="openLore(item.id)" />
      </div>
      <div v-else class="empty-state" :key="'empty'">
        <BookOpenIcon :size="48" class="empty-icon" aria-hidden="true" />
        <p class="empty-title">还没有设定数据</p>
        <p class="empty-desc">点击「新建设定」手动创建，或使用「AI Extract」从草稿中自动提取</p>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue"
import { useRoute } from "vue-router"
import {
  Sparkles as SparklesIcon,
  Plus as PlusIcon,
  Search as SearchIcon,
  BookOpen as BookOpenIcon,
} from "lucide-vue-next"

const search = ref("")
const typeFilter = ref("")
const showEditor = ref(false)
const showAiPanel = ref(false)
const route = useRoute()

interface EntityResponse {
  id: string
  name: string
  entity_type: string
  tags: string[]
  summary?: string | null
}

const { selectedWorldId, loadWorlds, selectWorld } = useWorlds()
const apiBase = useApiBase()
const loreItems = ref<Array<{ id: string; name: string; type: string; tags: string[]; summary: string }>>([])
const loading = ref(false)

function openLore(id: string) {
  const worldId = typeof route.params.worldId === "string" ? route.params.worldId : ""
  return navigateTo(worldId ? `/worlds/${worldId}/lore/${id}` : `/lore/${id}`)
}

async function loadLore() {
  if (!selectedWorldId.value) return
  loading.value = true
  try {
    const query: Record<string, string> = {}
    if (route.query.scope !== "all") query.world_id = selectedWorldId.value
    if (typeof route.query.type === "string" && route.query.type) query.type = route.query.type
    const entities = await $fetch<EntityResponse[]>(`${apiBase}/api/entities`, {
      query,
    })
    loreItems.value = entities.map((entity) => ({
      id: entity.id,
      name: entity.name,
      type: entity.entity_type,
      tags: entity.tags || [],
      summary: entity.summary || "",
    }))
  } finally {
    loading.value = false
  }
}

const filteredLore = computed(() => {
  return loreItems.value.filter((item) => {
    if (search.value) {
      const q = search.value.toLowerCase()
      if (
        !item.name.toLowerCase().includes(q) &&
        !item.tags.some((t) => t.toLowerCase().includes(q))
      ) return false
    }
    if (typeFilter.value && item.type !== typeFilter.value) return false
    return true
  })
})

function onExtracted(items: any[]) {
  loreItems.value.push(...items)
  showAiPanel.value = false
  loadLore()
}

onMounted(async () => {
  await loadWorlds()
  const requestedWorldId = typeof route.params.worldId === "string"
    ? route.params.worldId
    : (typeof route.query.world_id === "string" ? route.query.world_id : "")
  if (requestedWorldId) selectWorld(requestedWorldId)
  if (typeof route.query.type === "string") typeFilter.value = route.query.type
  if (typeof route.query.search === "string") search.value = route.query.search
  await loadLore()
})

watch(selectedWorldId, () => {
  if (route.query.scope !== "all") loadLore()
})
</script>

<style scoped>
.lore-page {
  max-width: 1100px;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  gap: var(--space-4);
  flex-wrap: wrap;
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
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
}

.btn-primary {
  background: var(--color-accent-cyan);
  color: var(--color-text-inverse);
}

.btn-primary:hover {
  box-shadow: var(--shadow-glow-cyan);
}

.btn-primary:active {
  transform: scale(0.97);
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

.btn-secondary:active {
  transform: scale(0.97);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.search-wrapper {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-3) var(--space-2) 36px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  transition: border-color var(--duration-fast) var(--easing-default);
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: var(--shadow-glow-cyan);
}

.filter-select {
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  cursor: pointer;
  transition: border-color var(--duration-fast) var(--easing-default);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

/* Lore Grid */
.lore-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

/* Empty */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16) 0;
  text-align: center;
  gap: var(--space-3);
}

.empty-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.empty-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.empty-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  max-width: 360px;
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--easing-default);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all var(--duration-slow) var(--easing-default);
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.list-enter-active,
.list-leave-active {
  transition: all var(--duration-normal) var(--easing-default);
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
