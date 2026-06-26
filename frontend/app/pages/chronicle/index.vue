<template>
  <div class="chronicle-page">
    <header class="page-header">
      <h1>Chronicle</h1>
      <p class="subtitle">编年史轨道</p>
    </header>

    <div class="timeline-controls">
      <button class="btn btn-icon" @click="zoomIn">🔍+</button>
      <button class="btn btn-icon" @click="zoomOut">🔍−</button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <div class="timeline-range">
        <input v-model.number="rangeStart" type="number" class="year-input" placeholder="起始年" />
        <span class="range-sep">→</span>
        <input v-model.number="rangeEnd" type="number" class="year-input" placeholder="结束年" />
      </div>
    </div>

    <div class="timeline-container" ref="timelineRef">
      <TimelineTrack
        :events="filteredEvents"
        :zoom="zoom"
        @event-click="onEventClick"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const zoom = ref(1)
const rangeStart = ref<number | null>(null)
const rangeEnd = ref<number | null>(null)
const timelineRef = ref<HTMLElement | null>(null)

const events = ref<Array<{ id: string; title: string; date: string; description: string; entities: string[] }>>([])

const filteredEvents = computed(() => {
  return events.value.filter(e => {
    const year = parseInt(e.date)
    if (rangeStart.value && year < rangeStart.value) return false
    if (rangeEnd.value && year > rangeEnd.value) return false
    return true
  })
})

function zoomIn() { zoom.value = Math.min(zoom.value * 1.3, 5) }
function zoomOut() { zoom.value = Math.max(zoom.value / 1.3, 0.2) }

function onEventClick(event: any) {
  navigateTo('/lore/' + event.id)
}
</script>

<style scoped>
.chronicle-page { height: calc(100vh - 64px); display: flex; flex-direction: column; }
.page-header { margin-bottom: 16px; }
.page-header h1 { font-size: 28px; font-weight: 700; }
.subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 2px; }
.timeline-controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.btn-icon { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; cursor: pointer; font-size: 14px; color: var(--text-primary); }
.btn-icon:hover { border-color: var(--accent-cyan); }
.zoom-level { font-size: 12px; color: var(--text-secondary); min-width: 40px; }
.timeline-range { display: flex; align-items: center; gap: 6px; margin-left: auto; }
.year-input { width: 90px; padding: 8px 10px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); font-size: 13px; }
.range-sep { color: var(--text-dim); }
.timeline-container { flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; overflow-x: auto; overflow-y: hidden; position: relative; min-height: 400px; }
</style>
