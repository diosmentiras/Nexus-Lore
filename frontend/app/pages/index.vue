<template>
  <div class="dashboard">
    <header class="page-header">
      <h1>Dashboard</h1>
      <p class="subtitle">世界观总览</p>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-icon">👤</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">人物</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🏛️</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">势力</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">📦</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">物品</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🔗</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">关系</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">📅</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">事件</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">⚠️</span>
        <div class="stat-info">
          <span class="stat-value">0</span>
          <span class="stat-label">冲突</span>
        </div>
      </div>
    </div>

    <div class="panels-grid">
      <section class="panel">
        <h2>最近的变更</h2>
        <div class="panel-empty">还没有任何设定，前往 Lore 开始创建吧</div>
      </section>
      <section class="panel">
        <h2>快速操作</h2>
        <div class="quick-actions">
          <NuxtLink to="/lore" class="action-btn">📖 浏览设定</NuxtLink>
          <NuxtLink to="/nexus" class="action-btn">🕸️ 查看星图</NuxtLink>
          <NuxtLink to="/chronicle" class="action-btn">⏳ 探索编年史</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard { max-width: 1200px; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 28px; font-weight: 700; color: var(--text-primary); }
.subtitle { font-size: 14px; color: var(--text-secondary); margin-top: 4px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; margin-bottom: 28px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; display: flex; align-items: center; gap: 14px; }
.stat-icon { font-size: 28px; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--accent-cyan); }
.stat-label { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.panels-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 24px; }
.panel h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); }
.panel-empty { font-size: 13px; color: var(--text-dim); text-align: center; padding: 40px 0; }
.quick-actions { display: flex; flex-direction: column; gap: 10px; }
.action-btn { display: block; padding: 12px 16px; background: rgba(0, 240, 255, 0.06); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-primary); text-decoration: none; font-size: 14px; transition: all 0.2s; }
.action-btn:hover { background: rgba(0, 240, 255, 0.12); border-color: var(--accent-cyan); }
</style>
