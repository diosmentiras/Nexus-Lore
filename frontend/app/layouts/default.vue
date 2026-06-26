<template>
  <div class="nexus-layout">
    <!-- 霓虹侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🪐</span>
        <span class="brand-text">Nexus-Lore</span>
      </div>
      <nav class="sidebar-nav">
        <NuxtLink to="/" class="nav-item" exact-active-class="active">
          <span class="nav-icon">📊</span>
          <span class="nav-label">Dashboard</span>
        </NuxtLink>
        <NuxtLink to="/lore" class="nav-item" active-class="active">
          <span class="nav-icon">📖</span>
          <span class="nav-label">Lore</span>
        </NuxtLink>
        <NuxtLink to="/nexus" class="nav-item" active-class="active">
          <span class="nav-icon">🕸️</span>
          <span class="nav-label">Nexus</span>
        </NuxtLink>
        <NuxtLink to="/chronicle" class="nav-item" active-class="active">
          <span class="nav-icon">⏳</span>
          <span class="nav-label">Chronicle</span>
        </NuxtLink>
        <NuxtLink to="/linter" class="nav-item" active-class="active">
          <span class="nav-icon">🔍</span>
          <span class="nav-label">Linter</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item" active-class="active">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">Settings</span>
        </NuxtLink>
      </nav>
    </aside>
    <!-- 主内容区 -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style>
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card: #1a1a2e;
  --border-color: #2a2a4a;
  --accent-cyan: #00f0ff;
  --accent-magenta: #ff00aa;
  --accent-yellow: #ffd700;
  --text-primary: #e0e0f0;
  --text-secondary: #8888aa;
  --text-dim: #555577;
  --danger: #ff3355;
  --success: #00ff88;
  --warning: #ffaa00;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
}

.nexus-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 20px;
  border-bottom: 1px solid var(--border-color);
}

.brand-icon {
  font-size: 24px;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-magenta));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 12px 10px;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(0, 240, 255, 0.06);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(0, 240, 255, 0.1);
  color: var(--accent-cyan);
  box-shadow: inset 3px 0 0 var(--accent-cyan);
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}
</style>
