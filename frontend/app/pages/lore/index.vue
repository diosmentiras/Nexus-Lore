<template>
  <div class="lore-page">
    <header class="page-header">
      <h1>Lore</h1>
      <p class="subtitle">世界观设定库</p>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showEditor = true">+ 新建设定</button>
      </div>
    </header>

    <!-- 双轨写作台 -->
    <div v-if="showEditor" class="lore-editor-overlay" @click.self="showEditor = false">
      <LoreEditor @close="showEditor = false" />
    </div>

    <!-- 搜索过滤 -->
    <div class="filter-bar">
      <input v-model="search" type="text" class="search-input" placeholder="搜索设定名称、标签..." />
      <select v-model="typeFilter" class="filter-select">
        <option value="">全部类型</option>
        <option value="character">人物</option>
        <option value="faction">势力</option>
        <option value="item">物品</option>
        <option value="location">地点</option>
        <option value="event">事件</option>
        <option value="containment">收容物</option>
      </select>
      <button class="btn btn-secondary" @click="showAiPanel = !showAiPanel">🤖 AI Extract</button>
    </div>

    <!-- AI 提取面板 -->
    <AiExtractPanel v-if="showAiPanel" @close="showAiPanel = false" @extracted="onExtracted" />

    <!-- 设定卡片网格 -->
    <div class="lore-grid">
      <LoreCard v-for="item in filteredLore" :key="item.id" :lore="item" @click="navigateTo('/lore/' + item.id)" />
    </div>

    <div v-if="filteredLore.length === 0" class="empty-state">
      <p>还没有设定数据。点击「+ 新建设定」或使用「AI Extract」从草稿中提取。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const search = ref('')
const typeFilter = ref('')
const showEditor = ref(false)
const showAiPanel = ref(false)

const loreItems = ref<Array<{ id: string; name: string; type: string; tags: string[]; summary: string }>>([])

const filteredLore = computed(() => {
  return loreItems.value.filter(item => {
    if (search.value && !item.name.toLowerCase().includes(search.value.toLowerCase()) && !item.tags.some(t => t.toLowerCase().includes(search.value.toLowerCase()))) return false
    if (typeFilter.value && item.type !== typeFilter.value) return false
    return true
  })
})

function onExtracted(items: any[]) {
  loreItems.value.push(...items)
  showAiPanel.value = false
}
</script>

<style scoped>
.lore-page { max-width: 1200px; }
.page-header { margin-bottom: 24px; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.page-header h1 { font-size: 28px; font-weight: 700; }
.subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 2px; }
.header-actions { display: flex; gap: 8px; }
.btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: var(--accent-cyan); color: var(--bg-primary); }
.btn-primary:hover { box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); }
.btn-secondary { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }
.btn-secondary:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }
.filter-bar { display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; padding: 10px 14px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 14px; }
.search-input::placeholder { color: var(--text-dim); }
.filter-select { padding: 10px 14px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 14px; }
.lore-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.empty-state { text-align: center; padding: 60px 0; color: var(--text-dim); font-size: 14px; }
.lore-editor-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 100; display: flex; align-items: center; justify-content: center; }
</style>
