<template>
  <div
    class="lore-card"
    :class="[`type-${lore.type}`, { clickable: $attrs.onClick }]"
    @click="$emit('click')"
    role="button"
    :tabindex="0"
    @keydown.enter="$emit('click')"
    :aria-label="`查看 ${lore.name}`"
  >
    <div class="card-top">
      <span class="card-type-badge" :class="`badge-${lore.type}`">{{ typeLabel }}</span>
      <div v-if="lore.faction" class="card-faction">
        <Building2Icon :size="12" aria-hidden="true" />
        <span>{{ lore.faction }}</span>
      </div>
    </div>

    <h3 class="card-name">{{ lore.name }}</h3>

    <p v-if="lore.summary" class="card-summary">{{ lore.summary }}</p>

    <div v-if="lore.tags?.length" class="card-tags">
      <span v-for="tag in lore.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { Building2 } from "lucide-vue-next"

const props = defineProps<{
  lore: {
    id: string
    name: string
    type: string
    tags?: string[]
    summary?: string
    faction?: string
  }
}>()

defineEmits<{ click: [] }>()

const typeLabels: Record<string, string> = {
  character: "人物",
  faction: "势力",
  item: "物品",
  location: "地点",
  event: "事件",
  containment: "收容物",
}

const typeLabel = computed(() => typeLabels[props.lore.type] || props.lore.type)
</script>

<style scoped>
.lore-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: all var(--duration-normal) var(--easing-default);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.lore-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity var(--duration-normal) var(--easing-default);
}

.lore-card.type-character::before { background: var(--color-accent-cyan); }
.lore-card.type-faction::before { background: var(--color-accent-magenta); }
.lore-card.type-item::before { background: var(--color-accent-yellow); }
.lore-card.type-location::before { background: var(--color-success); }
.lore-card.type-event::before { background: var(--color-warning); }
.lore-card.type-containment::before { background: var(--color-danger); }

.lore-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.lore-card:hover::before {
  opacity: 1;
}

.lore-card:focus-visible {
  border-color: var(--color-border-focus);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.card-type-badge {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  line-height: 1.4;
}

.badge-character { background: rgba(0, 240, 255, 0.1); color: var(--color-accent-cyan); }
.badge-faction { background: rgba(255, 0, 170, 0.1); color: var(--color-accent-magenta); }
.badge-item { background: rgba(255, 215, 0, 0.1); color: var(--color-accent-yellow); }
.badge-location { background: rgba(0, 255, 136, 0.1); color: var(--color-success); }
.badge-event { background: rgba(255, 170, 0, 0.1); color: var(--color-warning); }
.badge-containment { background: rgba(255, 51, 85, 0.1); color: var(--color-danger); }

.card-faction {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-accent-magenta);
  max-width: 50%;
}

.card-faction span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.card-summary {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: auto;
}

.tag {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: rgba(136, 136, 170, 0.08);
  border: 1px solid rgba(42, 42, 74, 0.5);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  line-height: 1.4;
}
</style>
