<template>
  <div class="lore-card" @click="$emit('click')">
    <div class="card-type-badge" :class="'type-' + lore.type">{{ typeLabel }}</div>
    <h3 class="card-name">{{ lore.name }}</h3>
    <p class="card-summary" v-if="lore.summary">{{ lore.summary }}</p>
    <div class="card-tags" v-if="lore.tags && lore.tags.length">
      <span v-for="tag in lore.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
    <div class="card-faction" v-if="lore.faction">
      <span class="faction-label">{{ lore.faction }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
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
  character: '人物',
  faction: '势力',
  item: '物品',
  location: '地点',
  event: '事件',
  containment: '收容物'
}

const typeLabel = computed(() => typeLabels[props.lore.type] || props.lore.type)
</script>

<style scoped>
.lore-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; gap: 8px; }
.lore-card:hover { border-color: var(--accent-cyan); box-shadow: 0 0 20px rgba(0, 240, 255, 0.08); transform: translateY(-2px); }
.card-type-badge { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 3px 8px; border-radius: 4px; align-self: flex-start; }
.type-character { background: rgba(0, 240, 255, 0.12); color: var(--accent-cyan); }
.type-faction { background: rgba(255, 0, 170, 0.12); color: var(--accent-magenta); }
.type-item { background: rgba(255, 215, 0, 0.12); color: var(--accent-yellow); }
.type-location { background: rgba(0, 255, 136, 0.12); color: var(--success); }
.type-event { background: rgba(255, 170, 0, 0.12); color: var(--warning); }
.type-containment { background: rgba(255, 51, 85, 0.12); color: var(--danger); }
.card-name { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.card-summary { font-size: 13px; color: var(--text-secondary); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.tag { font-size: 11px; padding: 2px 8px; background: rgba(136, 136, 170, 0.1); border-radius: 4px; color: var(--text-secondary); }
.card-faction { font-size: 12px; color: var(--accent-magenta); }
</style>
