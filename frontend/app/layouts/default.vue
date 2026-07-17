<template>
  <div class="nexus-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon-circle">
          <svg class="brand-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="6" />
            <circle cx="12" cy="12" r="2" />
            <line x1="2" y1="12" x2="6" y2="12" />
            <line x1="18" y1="12" x2="22" y2="12" />
            <line x1="12" y1="2" x2="12" y2="6" />
            <line x1="12" y1="18" x2="12" y2="22" />
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">Nexus</span>
          <span class="brand-sub">Lore</span>
        </div>
      </div>

      <nav class="sidebar-nav" role="navigation" aria-label="主导航">
        <NuxtLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item" :class="{ active: isActive(item.to) }" :aria-label="item.label">
          <component :is="item.icon" class="nav-icon" :size="18" aria-hidden="true" />
          <span class="nav-label">{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <div class="sidebar-footer">
        <NuxtLink to="/settings" class="nav-item" :class="{ active: isActive('/settings') }" aria-label="设置">
          <SettingsIcon class="nav-icon" :size="18" aria-hidden="true" />
          <span class="nav-label">Settings</span>
        </NuxtLink>
        <div class="version-badge">v0.1.0</div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content" role="main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router"
import {
  LayoutDashboard,
  BookOpen,
  Network,
  History,
  SearchCheck,
  Settings,
  type LucideIcon,
} from "lucide-vue-next"

const route = useRoute()

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/lore", label: "Lore", icon: BookOpen },
  { to: "/nexus", label: "Nexus", icon: Network },
  { to: "/chronicle", label: "Chronicle", icon: History },
  { to: "/linter", label: "Linter", icon: SearchCheck },
]

function isActive(path: string): boolean {
  if (path === "/") return route.path === "/"
  return route.path.startsWith(path)
}
</script>

<style scoped>
.nexus-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
}

/* ---- Sidebar ---- */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 10;
}

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.brand-icon-circle {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 170, 0.15));
  border: 1px solid rgba(0, 240, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent-cyan);
  flex-shrink: 0;
}

.brand-icon-svg {
  width: 20px;
  height: 20px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  background: linear-gradient(135deg, var(--color-accent-cyan), var(--color-accent-magenta));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-sub {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

/* Navigation */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: var(--space-3) var(--space-2);
  gap: 2px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-fast) var(--easing-default);
  position: relative;
}

.nav-item:hover {
  background: rgba(0, 240, 255, 0.06);
  color: var(--color-text-primary);
}

.nav-item:active {
  background: rgba(0, 240, 255, 0.1);
  transform: scale(0.98);
}

.nav-item.active {
  background: rgba(0, 240, 255, 0.1);
  color: var(--color-accent-cyan);
}

.nav-item.active::before {
  content: "";
  position: absolute;
  left: -2px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 2px 2px 0;
  background: var(--color-accent-cyan);
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

.nav-icon {
  flex-shrink: 0;
  opacity: 0.8;
}

.nav-item.active .nav-icon {
  opacity: 1;
  color: var(--color-accent-cyan);
}

.nav-label {
  line-height: 1;
}

/* Footer */
.sidebar-footer {
  padding: var(--space-2);
  border-top: 1px solid var(--color-border);
}

/* ---- Main Content ---- */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8);
  background: var(--color-bg-primary);
}
</style>
