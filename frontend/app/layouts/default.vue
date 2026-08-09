<template>
  <div class="nexus-layout">
    <aside class="sidebar">
      <NuxtLink to="/worlds" class="sidebar-brand" aria-label="返回世界库">
        <div class="brand-icon-circle">
          <svg class="brand-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
            <line x1="2" y1="12" x2="6" y2="12" /><line x1="18" y1="12" x2="22" y2="12" />
            <line x1="12" y1="2" x2="12" y2="6" /><line x1="12" y1="18" x2="12" y2="22" />
          </svg>
        </div>
        <div class="brand-text"><span class="brand-name">Nexus</span><span class="brand-sub">Lore</span></div>
      </NuxtLink>

      <nav v-if="!inWorkspace" class="sidebar-nav global-nav" aria-label="全局导航">
        <NuxtLink to="/worlds" class="nav-item active">
          <Globe2Icon class="nav-icon" :size="18" aria-hidden="true" />
          <span class="nav-label">世界库</span>
        </NuxtLink>
      </nav>

      <div v-else class="workspace-shell">
        <div class="world-context">
          <NuxtLink to="/worlds" class="back-worlds" title="返回世界库"><ArrowLeftIcon :size="15" /></NuxtLink>
          <div class="world-context-copy"><span>当前世界</span><strong>{{ activeWorld?.name || "加载中" }}</strong></div>
          <select :value="routeWorldId" class="world-select" aria-label="切换世界" @change="onWorldChange">
            <option v-for="world in worlds" :key="world.id" :value="world.id">{{ world.name }}</option>
          </select>
        </div>

        <nav class="sidebar-nav workspace-nav" aria-label="世界工作区导航">
          <NuxtLink v-for="item in workspaceNav" :key="item.section" :to="item.to" :no-prefetch="item.section === 'nexus'" class="nav-item" :class="{ active: activeSection === item.section }">
            <component :is="item.icon" class="nav-icon" :size="18" aria-hidden="true" />
            <span class="nav-label">{{ item.label }}</span>
          </NuxtLink>
        </nav>
      </div>

      <div class="sidebar-footer">
        <NuxtLink to="/settings" class="nav-item" :class="{ active: route.path.startsWith('/settings') }" aria-label="设置">
          <SettingsIcon class="nav-icon" :size="18" aria-hidden="true" />
          <span class="nav-label">设置</span>
        </NuxtLink>
        <div class="version-badge">v0.1.0</div>
      </div>
    </aside>

    <main class="main-content" role="main"><slot /></main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import {
  ArrowLeft as ArrowLeftIcon,
  BookOpen as BookOpenIcon,
  Files as FilesIcon,
  Globe2 as Globe2Icon,
  History as HistoryIcon,
  LayoutDashboard as LayoutDashboardIcon,
  Network as NetworkIcon,
  Settings as SettingsIcon,
  type LucideIcon,
} from "lucide-vue-next"

const route = useRoute()
const { worlds, loadWorlds, selectWorld } = useWorlds()
await loadWorlds()
const routeWorldId = computed(() => typeof route.params.worldId === "string" ? route.params.worldId : "")
const inWorkspace = computed(() => Boolean(routeWorldId.value))
const activeWorld = computed(() => worlds.value.find((world) => world.id === routeWorldId.value))
const activeSection = computed(() => route.path.match(/^\/worlds\/[^/]+\/([^/]+)/)?.[1] || "overview")

interface WorkspaceNavItem { section: string; label: string; icon: LucideIcon; to: string }
const workspaceNav = computed<WorkspaceNavItem[]>(() => {
  const base = `/worlds/${routeWorldId.value}`
  return [
    { section: "overview", label: "总览", icon: LayoutDashboardIcon, to: `${base}/overview` },
    { section: "sources", label: "来源", icon: FilesIcon, to: `${base}/sources` },
    { section: "lore", label: "Lore", icon: BookOpenIcon, to: `${base}/lore` },
    { section: "chronicle", label: "时间线", icon: HistoryIcon, to: `${base}/chronicle` },
    { section: "nexus", label: "关系图", icon: NetworkIcon, to: `${base}/nexus` },
  ]
})

async function onWorldChange(event: Event) {
  const worldId = (event.target as HTMLSelectElement).value
  selectWorld(worldId)
  await navigateTo(`/worlds/${worldId}/${activeSection.value}`)
}
</script>

<style scoped>
.nexus-layout { display: flex; width: 100vw; height: 100vh; }
.sidebar { z-index: 10; display: flex; width: var(--sidebar-width); min-width: var(--sidebar-width); flex-direction: column; border-right: 1px solid var(--color-border); background: var(--color-bg-secondary); }
.sidebar-brand { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-5); border-bottom: 1px solid var(--color-border); text-decoration: none; }
.brand-icon-circle { display: flex; width: 36px; height: 36px; flex-shrink: 0; align-items: center; justify-content: center; border: 1px solid rgba(0, 240, 255, .25); border-radius: var(--radius-md); background: rgba(0, 240, 255, .07); color: var(--color-accent-cyan); }
.brand-icon-svg { width: 20px; height: 20px; }
.brand-text { display: flex; flex-direction: column; line-height: 1.15; }
.brand-name { color: var(--color-accent-cyan); font-size: var(--font-size-lg); font-weight: var(--font-weight-bold); }
.brand-sub { color: var(--color-text-muted); font-size: 10px; letter-spacing: .8px; text-transform: uppercase; }
.workspace-shell { display: flex; min-height: 0; flex: 1; flex-direction: column; }
.world-context { position: relative; display: grid; grid-template-columns: 30px minmax(0, 1fr); align-items: center; gap: var(--space-2); padding: var(--space-4) var(--space-3); border-bottom: 1px solid var(--color-border); }
.back-worlds { display: inline-flex; width: 30px; height: 30px; align-items: center; justify-content: center; border-radius: var(--radius-sm); color: var(--color-text-secondary); }
.back-worlds:hover { background: rgba(0, 240, 255, .07); color: var(--color-accent-cyan); }
.world-context-copy { display: flex; min-width: 0; flex-direction: column; gap: 2px; }
.world-context-copy span { color: var(--color-text-muted); font-size: 9px; text-transform: uppercase; }
.world-context-copy strong { overflow: hidden; color: var(--color-text-primary); font-size: var(--font-size-sm); text-overflow: ellipsis; white-space: nowrap; }
.world-select { grid-column: 1 / -1; width: 100%; min-height: 32px; padding: 0 var(--space-2); border: 1px solid var(--color-border); border-radius: var(--radius-md); outline: none; background: var(--color-bg-card); color: var(--color-text-primary); font-size: var(--font-size-xs); }
.world-select:focus { border-color: var(--color-accent-cyan); }
.sidebar-nav { display: flex; flex-direction: column; gap: 2px; padding: var(--space-3) var(--space-2); }
.global-nav, .workspace-nav { flex: 1; }
.nav-item { position: relative; display: flex; min-height: 42px; align-items: center; gap: var(--space-3); padding: 0 var(--space-3); border-radius: var(--radius-md); color: var(--color-text-secondary); font-size: var(--font-size-sm); font-weight: var(--font-weight-medium); text-decoration: none; transition: color var(--duration-fast), background var(--duration-fast); }
.nav-item:hover { background: rgba(0, 240, 255, .05); color: var(--color-text-primary); }
.nav-item.active { background: rgba(0, 240, 255, .1); color: var(--color-accent-cyan); }
.nav-item.active::before { position: absolute; top: 50%; left: -2px; width: 3px; height: 20px; border-radius: 0 2px 2px 0; background: var(--color-accent-cyan); content: ""; transform: translateY(-50%); }
.nav-icon { flex-shrink: 0; }
.sidebar-footer { padding: var(--space-2); border-top: 1px solid var(--color-border); }
.version-badge { padding: var(--space-2) var(--space-3); color: var(--color-text-muted); font-family: var(--font-mono); font-size: 9px; }
.main-content { min-width: 0; flex: 1; overflow-y: auto; padding: var(--space-8); background: var(--color-bg-primary); }

@media (max-width: 720px) {
  .nexus-layout { flex-direction: column; }
  .sidebar { display: grid; width: 100%; min-width: 0; height: 102px; min-height: 102px; grid-template-columns: 54px minmax(0, 1fr) 46px; grid-template-rows: 56px 46px; border-right: 0; border-bottom: 1px solid var(--color-border); }
  .sidebar-brand { grid-column: 1; grid-row: 1; padding: 10px 9px; border-bottom: 0; }
  .brand-text, .version-badge { display: none; }
  .workspace-shell { display: contents; }
  .world-context { display: flex; min-width: 0; grid-column: 2; grid-row: 1; padding: 8px 4px; border-bottom: 0; }
  .back-worlds, .world-context-copy { display: none; }
  .world-select { width: 100%; max-width: 230px; }
  .sidebar-nav { grid-column: 1 / -1; grid-row: 2; flex-direction: row; gap: 2px; padding: 3px 6px 5px; }
  .sidebar-nav .nav-item { min-width: 0; flex: 1; justify-content: center; padding: 0; }
  .sidebar-nav .nav-label { display: none; }
  .nav-item.active::before { top: auto; bottom: -2px; left: 50%; width: 20px; height: 3px; border-radius: 2px 2px 0 0; transform: translateX(-50%); }
  .sidebar-footer { display: flex; grid-column: 3; grid-row: 1; align-items: center; justify-content: center; padding: 8px 6px; border-top: 0; }
  .sidebar-footer .nav-item { width: 36px; min-height: 36px; justify-content: center; padding: 0; }
  .sidebar-footer .nav-label { display: none; }
  .main-content { padding: var(--space-4); }
}
</style>
