<template>
  <div class="timeline-track" :style="{ width: trackWidth + 'px' }">
    <!-- 时间轴基线 -->
    <div class="timeline-base"></div>

    <!-- 刻度 -->
    <div v-for="tick in ticks" :key="tick.year" class="tick" :style="{ left: tick.x + 'px' }">
      <div class="tick-line"></div>
      <span class="tick-label">{{ tick.year }}</span>
    </div>

    <!-- 事件 -->
    <div
      v-for="event in sortedEvents"
      :key="event.id"
      class="event-marker"
      :style="{ left: positionX(event) + 'px' }"
      @click="$emit('eventClick', event)"
      role="button"
      :tabindex="0"
      @keydown.enter="$emit('eventClick', event)"
    >
      <div class="marker-dot">
        <div class="marker-pulse"></div>
      </div>
      <div class="event-card">
        <span class="event-date">{{ event.date }}</span>
        <span class="event-title">{{ event.title }}</span>
        <span v-if="event.description" class="event-desc">{{ event.description }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  events: Array<{ id: string; title: string; date: string; description?: string; entities?: string[] }>
  zoom: number
}>()

defineEmits<{ eventClick: [event: any] }>()

const PADDING = 100
const BASE_SPACING = 80

const sortedEvents = computed(() => [...props.events].sort((a, b) => parseInt(a.date) - parseInt(b.date)))

const ticks = computed(() => {
  if (!sortedEvents.value.length) return []
  const min = parseInt(sortedEvents.value[0].date)
  const max = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date)
  const step = Math.max(1, Math.floor((max - min) / 8))
  const years: number[] = []
  for (let y = min; y <= max; y += step) years.push(y)
  if (years[years.length - 1] !== max) years.push(max)
  const tw = trackWidth.value
  const span = Math.max(max - min, 1)
  return years.map((year) => ({
    year,
    x: PADDING + ((year - min) / span) * (tw - PADDING * 2),
  }))
})

const trackWidth = computed(() => {
  if (!sortedEvents.value.length) return 800
  const minYear = parseInt(sortedEvents.value[0].date)
  const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date)
  const span = Math.max(maxYear - minYear, 1)
  return span * BASE_SPACING * props.zoom + PADDING * 2
})

function positionX(event: { date: string }): number {
  if (!sortedEvents.value.length) return PADDING
  const minYear = parseInt(sortedEvents.value[0].date)
  const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date)
  const span = Math.max(maxYear - minYear, 1)
  const year = parseInt(event.date)
  return PADDING + ((year - minYear) / span) * (trackWidth.value - PADDING * 2)
}
</script>

<style scoped>
.timeline-track {
  position: relative;
  height: 100%;
  min-height: 400px;
  padding-top: 80px;
}

/* Base line */
.timeline-base {
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(to right, transparent, var(--color-accent-cyan), transparent);
  opacity: 0.3;
}

/* Ticks */
.tick {
  position: absolute;
  top: 50px;
  transform: translateX(-50%);
}

.tick-line {
  width: 1px;
  height: 20px;
  background: var(--color-border);
  margin: 0 auto;
}

.tick-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-align: center;
  margin-top: 2px;
  font-variant-numeric: tabular-nums;
}

/* Events */
.event-marker {
  position: absolute;
  top: 0;
  cursor: pointer;
}

.marker-dot {
  position: absolute;
  top: 56px;
  left: 50%;
  transform: translateX(-50%);
  width: 14px;
  height: 14px;
  background: var(--color-accent-cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
  z-index: 1;
}

.marker-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(0, 240, 255, 0.2);
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.event-card {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  white-space: nowrap;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  opacity: 0.85;
  transition: all var(--duration-fast) var(--easing-default);
  min-width: 120px;
}

.event-marker:hover .event-card {
  opacity: 1;
  border-color: var(--color-accent-cyan);
  box-shadow: var(--shadow-glow-cyan);
  transform: translateX(-50%) translateY(-2px);
}

.event-date {
  font-size: var(--font-size-xs);
  color: var(--color-accent-cyan);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
}

.event-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.event-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
