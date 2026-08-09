<template>
  <ol class="timeline-list" aria-label="世界观时间线">
    <li v-for="(event, index) in sortedEvents" :key="event.id" class="timeline-event">
      <div class="timeline-rail" aria-hidden="true">
        <span class="event-index">{{ String(index + 1).padStart(2, "0") }}</span>
        <span v-if="index < sortedEvents.length - 1" class="rail-line"></span>
      </div>
      <article class="event-content">
        <header class="event-header">
          <time class="event-date">{{ event.date }}</time>
          <span v-if="event.date_context" class="date-context">{{ event.date_context }}</span>
        </header>
        <h3>{{ event.title }}</h3>
        <p v-if="event.description" class="event-description">{{ event.description }}</p>
        <div v-if="event.tags?.length" class="event-tags">
          <span v-for="tag in event.tags" :key="tag">{{ tag }}</span>
        </div>
      </article>
    </li>
  </ol>
</template>

<script setup lang="ts">
import { computed } from "vue"

interface TimelineEvent {
  id: string
  title: string
  date: string
  date_order?: number
  date_context?: string
  description?: string
  entities?: string[]
  tags?: string[]
}

const props = defineProps<{ events: TimelineEvent[] }>()

const sortedEvents = computed(() => [...props.events].sort((a, b) => {
  const orderDifference = sortableDate(a) - sortableDate(b)
  if (orderDifference) return orderDifference
  return a.date.localeCompare(b.date, "zh-CN")
}))

function sortableDate(event: TimelineEvent) {
  const parts = event.date.match(/\d+/g)?.map(Number) || []
  if (parts.length) return parts[0] * 10000 + (parts[1] || 0) * 100 + (parts[2] || 0)
  return event.date_order || Number.MAX_SAFE_INTEGER
}
</script>

<style scoped>
.timeline-list {
  list-style: none;
  width: min(920px, 100%);
  margin: 0 auto;
}

.timeline-event {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  gap: var(--space-4);
  min-width: 0;
}

.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100%;
}

.event-index {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-focus);
  border-radius: 50%;
  color: var(--color-accent-cyan);
  background: var(--color-bg-primary);
  font-family: var(--font-mono);
  font-size: var(--font-size-xs);
  flex-shrink: 0;
}

.rail-line {
  width: 1px;
  min-height: 48px;
  flex: 1;
  background: var(--color-border);
}

.event-content {
  min-width: 0;
  padding: 2px 0 var(--space-8);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-6);
}

.timeline-event:last-child .event-content {
  margin-bottom: 0;
}

.event-header {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-bottom: var(--space-2);
}

.event-date {
  color: var(--color-accent-cyan);
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.date-context {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.event-content h3 {
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.event-description {
  margin-top: var(--space-2);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--space-3);
}

.event-tags span {
  padding: 2px 7px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

@media (max-width: 560px) {
  .timeline-event { grid-template-columns: 40px minmax(0, 1fr); gap: var(--space-2); }
  .event-index { width: 30px; height: 30px; }
}
</style>
