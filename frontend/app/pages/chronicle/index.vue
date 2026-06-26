<template>
  <div class="chronicle-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Chronicle</h1>
        <p class="page-description">编年史轨道 · 事件时间轴</p>
      </div>
    </header>

    <!-- Controls -->
    <div class="controls">
      <div class="zoom-controls">
        <button class="btn btn-icon" @click="zoomIn" :disabled="zoom >= 5" aria-label="放大">
          <ZoomInIcon :size="16" aria-hidden="true" />
        </button>
        <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
        <button class="btn btn-icon" @click="zoomOut" :disabled="zoom <= 0.2" aria-label="缩小">
          <ZoomOutIcon :size="16" aria-hidden="true" />
        </button>
        <button class="btn btn-icon" @click="zoom = 1" aria-label="重置缩放">
          <RotateCcwIcon :size="14" aria-hidden="true" />
        </button>
      </div>
      <div class="year-range">
        <CalendarIcon :size="14" class="year-icon" aria-hidden="true" />
        <input v-model.number="rangeStart" type="number" class="year-input" placeholder="起始年" />
        <span class="range-sep">→</span>
        <input v-model.number="rangeEnd" type="number" class="year-input" placeholder="结束年" />
      </div>
    </div>

    <!-- Timeline -->
    <div class="timeline-container" ref="timelineRef">
      <TimelineTrack
        :events="filteredEvents"
        :zoom="zoom"
        @event-click="onEventClick"
      />
      <div v-if="!events.length" class="timeline-empty">
        <TimelineIcon :size="40" class="empty-icon" aria-hidden="true" />
        <p>添加带时间戳的事件后轨道将自动编织</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Calendar,
  Timeline,
} from "lucide-vue-next"

const zoom = ref(1)
const rangeStart = ref<number | null>(null)
const rangeEnd = ref<number | null>(null)
const timelineRef = ref<HTMLElement | null>(null)

const events = ref<Array<{ id: string; title: string; date: string; description: string; entities: string[] }>>([])

const filteredEvents = computed(() => {
  return events.value.filter((e) => {
    const year = parseInt(e.date)
    if (rangeStart.value && year < rangeStart.value) return false
    if (rangeEnd.value && year > rangeEnd.value) return false
    return true
  })
})

function zoomIn() { zoom.value = Math.min(zoom.value * 1.3, 5) }
function zoomOut() { zoom.value = Math.max(zoom.value / 1.3, 0.2) }

function onEventClick(event: any) {
  navigateTo("/lore/" + event.id)
}
</script>

<style scoped>
.chronicle-page {
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

/* Controls */
.controls {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  flex-shrink: 0;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 2px;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
}

.btn-icon:hover:not(:disabled) {
  background: rgba(0, 240, 255, 0.08);
  color: var(--color-accent-cyan);
}

.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.zoom-level {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  min-width: 36px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

/* Year Range */
.year-range {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-left: auto;
}

.year-icon {
  color: var(--color-text-muted);
}

.year-input {
  width: 90px;
  padding: var(--space-1) var(--space-2);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
}

.year-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
}

.range-sep {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Timeline Container */
.timeline-container {
  flex: 1;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  overflow-y: hidden;
  position: relative;
  min-height: 400px;
}

.timeline-empty {
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
