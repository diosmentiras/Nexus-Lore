<template>
  <div class="dashboard">
    <header class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-description">世界观总览 · 快速了解你的宇宙全景</p>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div v-for="(stat, idx) in stats" :key="stat.label" class="stat-card" :style="{ '--stat-color': stat.color, '--delay': idx * 0.06 + 's' }">
        <div class="stat-icon-wrapper">
          <component :is="stat.icon" :size="20" aria-hidden="true" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Panels -->
    <div class="panels-grid">
      <section class="panel">
        <div class="panel-header">
          <ClockIcon :size="16" aria-hidden="true" />
          <h2 class="panel-title">最近的变更</h2>
        </div>
        <div class="panel-body">
          <div class="empty-state">
            <FileTextIcon :size="40" class="empty-icon" aria-hidden="true" />
            <p class="empty-text">还没有任何设定</p>
            <p class="empty-hint">前往 <NuxtLink to="/lore" class="link">Lore</NuxtLink> 开始创建你的第一个世界</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <ZapIcon :size="16" aria-hidden="true" />
          <h2 class="panel-title">快速操作</h2>
        </div>
        <div class="panel-body">
          <div class="quick-actions">
            <NuxtLink v-for="(action, idx) in quickActions" :key="action.to" :to="action.to" class="action-card" :style="{ '--delay': (6 + idx * 0.08) + 's' }">
              <component :is="action.icon" :size="18" class="action-icon" aria-hidden="true" :style="{ color: action.color }" />
              <div class="action-info">
                <span class="action-title">{{ action.title }}</span>
                <span class="action-desc">{{ action.desc }}</span>
              </div>
              <ChevronRightIcon :size="14" class="action-chevron" aria-hidden="true" />
            </NuxtLink>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Users,
  Building2,
  Package,
  Share2,
  Calendar,
  AlertTriangle,
  Clock,
  FileText,
  Zap,
  BookOpen,
  Network,
  History,
  ChevronRight,
  type LucideIcon,
} from "lucide-vue-next"

interface Stat {
  icon: LucideIcon
  value: number
  label: string
  color: string
}

const stats: Stat[] = [
  { icon: Users, value: 0, label: "人物", color: "var(--color-accent-cyan)" },
  { icon: Building2, value: 0, label: "势力", color: "var(--color-accent-magenta)" },
  { icon: Package, value: 0, label: "物品", color: "var(--color-accent-yellow)" },
  { icon: Share2, value: 0, label: "关系", color: "var(--color-accent-purple)" },
  { icon: Calendar, value: 0, label: "事件", color: "var(--color-accent-green)" },
  { icon: AlertTriangle, value: 0, label: "冲突", color: "var(--color-danger)" },
]

interface QuickAction {
  to: string
  title: string
  desc: string
  icon: LucideIcon
  color: string
}

const quickActions: QuickAction[] = [
  { to: "/lore", title: "浏览设定库", desc: "查看所有世界观设定", icon: BookOpen, color: "var(--color-accent-cyan)" },
  { to: "/nexus", title: "探索星图", desc: "查看实体关系图谱", icon: Network, color: "var(--color-accent-purple)" },
  { to: "/chronicle", title: "编年史轨道", desc: "查看时间轴事件", icon: History, color: "var(--color-accent-yellow)" },
]
</script>

<style scoped>
.dashboard {
  max-width: 1100px;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Page Header */
.page-header {
  margin-bottom: var(--space-8);
  animation: slideUp 0.4s var(--easing-spring) both;
  animation-delay: 0s;
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--duration-normal) var(--easing-default);
  cursor: default;
  animation: slideUp 0.4s var(--easing-spring) both;
  animation-delay: var(--delay, 0s);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(135deg, var(--stat-color), transparent 60%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity var(--duration-normal) var(--easing-default);
  pointer-events: none;
}

.stat-card:hover::before {
  opacity: 0.5;
}

.stat-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background: rgba(0, 240, 255, 0.06);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--stat-color, var(--color-accent-cyan));
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--easing-default);
}

.stat-card:hover .stat-icon-wrapper {
  background: rgba(0, 240, 255, 0.1);
  border-color: var(--color-border-focus);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--stat-color, var(--color-accent-cyan));
  line-height: var(--line-height-tight);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* Panels */
.panels-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}

@media (max-width: 768px) {
  .panels-grid {
    grid-template-columns: 1fr;
  }
}

.panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--duration-normal) var(--easing-default);
  animation: slideUp 0.4s var(--easing-spring) both;
  animation-delay: 0.12s;
}

.panel:hover {
  border-color: var(--color-border-hover);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.05);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.panel-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.panel-body {
  padding: var(--space-6);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10) 0;
  text-align: center;
  gap: var(--space-2);
}

.empty-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.empty-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.empty-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.link {
  color: var(--color-accent-cyan);
  font-weight: var(--font-weight-medium);
}

.link:hover {
  text-decoration: underline;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  color: var(--color-text-primary);
  text-decoration: none;
  transition: all var(--duration-fast) var(--easing-default);
}

.action-card:hover {
  background: rgba(0, 240, 255, 0.04);
  border-color: var(--color-border);
}

.action-card:active {
  transform: scale(0.99);
}

.action-icon {
  flex-shrink: 0;
}

.action-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.action-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.action-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.action-chevron {
  color: var(--color-text-muted);
  transition: all var(--duration-fast) var(--easing-default);
}

.action-card:hover .action-chevron {
  color: var(--color-accent-cyan);
  transform: translateX(2px);
}
</style>
