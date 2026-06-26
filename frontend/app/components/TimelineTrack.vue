<template>
  <div class="timeline-track" :style="{ width: trackWidth + 'px' }">
    <!-- 时间轴基线 -->
    <div class="timeline-base"></div>
    <!-- 事件标记 -->
    <div
      v-for="event in sortedEvents"
      :key="event.id"
      class="event-marker"
      :style="{ left: positionX(event) + 'px' }"
      @click="$emit('eventClick', event)"
    >
      <div class="marker-dot"></div>
      <div class="event-card">
        <span class="event-date">{{ event.date }}</span>
        <span class="event-title">{{ event.title }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  events: Array<{ id: string; title: string; date: string; description?: string; entities?: string[] }>
  zoom: number
}>()

defineEmits<{ eventClick: [event: any] }>()

const PADDING = 100
const BASE_SPACING = 80

const sortedEvents = computed(() => {
  return [...props.events].sort((a, b) => parseInt(a.date) - parseInt(b.date))
})

const trackWidth = computed(() => {
  if (sortedEvents.value.length === 0) return 800
  const minYear = parseInt(sortedEvents.value[0].date)
  const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date)
  const span = Math.max(maxYear - minYear, 1)
  return (span * BASE_SPACING * props.zoom) + PADDING * 2
})

function positionX(event: { date: string }): number {
  if (sortedEvents.value.length === 0) return PADDING
  const minYear = parseInt(sortedEvents.value[0].date)
  const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date)
  const span = Math.max(maxYear - minYear, 1)
  const year = parseInt(event.date)
  return PADDING + (year - minYear) / span * (trackWidth.value - PADDING * 2)
}
</script>

<style scoped>
.timeline-track { position: relative; height: 100%; min-height: 400px; }
.timeline-base { position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: var(--border-color); }
.event-marker { position: absolute; top: 0; cursor: pointer; }
.marker-dot { width: 12px; height: 12px; background: var(--accent-cyan); border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 8px var(--accent-cyan); }
.event-card { position: absolute; top: calc(50% + 16px); left: 50%; transform: translateX(-50%); background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px 12px; white-space: nowrap; display: flex; flex-direction: column; align-items: center; gap: 2px; opacity: 0.9; transition: opacity 0.2s; }
.event-marker:hover .event-card { opacity: 1; border-color: var(--accent-cyan); }
.event-date { font-size: 11px; color: var(--accent-cyan); font-weight: 600; }
.event-title { font-size: 13px; color: var(--text-primary); }
</style>
