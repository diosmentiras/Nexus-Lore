<template>
  <div class="chronicle-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Chronicle</h1>
        <p class="page-description">编年史轨道 · 按设定顺序阅读事件</p>
      </div>
      <span class="event-count">{{ filteredEvents.length }} 事件</span>
    </header>

    <div class="controls">
      <div class="search-wrapper">
        <SearchIcon :size="16" aria-hidden="true" />
        <input v-model="search" type="search" placeholder="搜索事件…" />
      </div>
      <div class="year-range">
        <CalendarIcon :size="15" aria-hidden="true" />
        <input v-model.number="rangeStart" type="number" class="year-input" placeholder="起始年" />
        <span>至</span>
        <input v-model.number="rangeEnd" type="number" class="year-input" placeholder="结束年" />
      </div>
    </div>

    <div class="timeline-container">
      <TimelineTrack v-if="filteredEvents.length" :events="filteredEvents" />
      <div v-else class="timeline-empty">
        <HistoryIcon :size="40" aria-hidden="true" />
        <p>{{ events.length ? "没有匹配当前条件的事件" : "该世界观还没有时间线事件" }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import {
  Calendar as CalendarIcon,
  History as HistoryIcon,
  Search as SearchIcon,
} from "lucide-vue-next"

interface EventResponse {
  id: string
  title: string
  date: string
  date_order: number
  date_context?: string | null
  description?: string | null
  entity_ids: string[]
  tags: string[]
}

interface TimelineEvent {
  id: string
  title: string
  date: string
  date_order: number
  date_context: string
  description: string
  entities: string[]
  tags: string[]
}

const search = ref("")
const rangeStart = ref<number | null>(null)
const rangeEnd = ref<number | null>(null)
const route = useRoute()
const { selectedWorldId, loadWorlds, selectWorld } = useWorlds()
const apiBase = useApiBase()
const events = ref<TimelineEvent[]>([])

async function loadEvents() {
  if (!selectedWorldId.value) return
  const result = await $fetch<EventResponse[]>(`${apiBase}/api/events`, {
    query: { world_id: selectedWorldId.value },
  })
  events.value = result.map((event) => ({
    id: event.id,
    title: event.title,
    date: event.date,
    date_order: event.date_order,
    date_context: event.date_context || "",
    description: event.description || "",
    entities: event.entity_ids || [],
    tags: event.tags || [],
  }))
}

const filteredEvents = computed(() => events.value.filter((event) => {
  const year = Number.parseInt(event.date, 10)
  const query = search.value.trim().toLowerCase()
  if (query && !`${event.title} ${event.description}`.toLowerCase().includes(query)) return false
  if (rangeStart.value && year < rangeStart.value) return false
  if (rangeEnd.value && year > rangeEnd.value) return false
  return true
}))

onMounted(async () => {
  await loadWorlds()
  if (typeof route.params.worldId === "string") selectWorld(route.params.worldId)
  await loadEvents()
})

watch(selectedWorldId, loadEvents)
</script>

<style scoped>
.chronicle-page {
  max-width: 1080px;
  min-width: 0;
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
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.page-title { font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); letter-spacing: 0; }
.page-description { margin-top: var(--space-1); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.event-count { color: var(--color-accent-cyan); font-family: var(--font-mono); font-size: var(--font-size-sm); white-space: nowrap; }

.controls {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) 0;
  margin-bottom: var(--space-8);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.search-wrapper svg { position: absolute; left: var(--space-3); top: 50%; transform: translateY(-50%); color: var(--color-text-muted); }
.search-wrapper input, .year-input {
  min-height: 36px;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  font-size: var(--font-size-sm);
}
.search-wrapper input { width: 100%; padding: 0 var(--space-3) 0 36px; }
.year-input { width: 88px; padding: 0 var(--space-2); }
.search-wrapper input:focus, .year-input:focus { outline: none; border-color: var(--color-border-focus); }

.year-range { display: flex; align-items: center; gap: var(--space-2); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.timeline-container { min-height: 360px; }
.timeline-empty { min-height: 360px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-3); color: var(--color-text-muted); }

@media (max-width: 700px) {
  .controls { align-items: stretch; flex-direction: column; }
  .year-range { justify-content: flex-start; }
}
</style>
