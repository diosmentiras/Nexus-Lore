<template>
  <div class="linter-page">
    <header class="page-header">
      <h1>Linter</h1>
      <p class="subtitle">设定冲突检查器</p>
      <button class="btn btn-primary" @click="runLint">🔍 运行检查</button>
    </header>

    <div v-if="linting" class="linting-status">
      <div class="spinner"></div>
      <span>正在分析设定逻辑...</span>
    </div>

    <div v-else-if="issues.length === 0" class="empty-state">
      <p>✅ 尚未发现设定冲突。世界观逻辑一致。</p>
    </div>

    <div v-else class="issues-list">
      <div v-for="issue in issues" :key="issue.id" class="issue-card" :class="issue.severity">
        <div class="issue-header">
          <span class="severity-badge">{{ issue.severity }}</span>
          <span class="issue-title">{{ issue.title }}</span>
        </div>
        <p class="issue-description">{{ issue.description }}</p>
        <div class="issue-meta">
          <span class="issue-location" v-if="issue.entity1">{{ issue.entity1 }}</span>
          <span class="issue-arrow">⟷</span>
          <span class="issue-location" v-if="issue.entity2">{{ issue.entity2 }}</span>
        </div>
        <button class="btn btn-link" @click="navigateToIssue(issue)">定位到文档 →</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const linting = ref(false)
const issues = ref<Array<{ id: string; severity: string; title: string; description: string; entity1?: string; entity2?: string }>>([
  // 示例数据供 UI 展示用
  // { id: "1", severity: "error", title: "时间线冲突", description: "角色 Jane 在 2070 年已牺牲，但仍在 2077 年的事件中出现", entity1: "Jane", entity2: "2077 赛博酒吧事件" }
])

async function runLint() {
  linting.value = true
  // TODO: call backend /api/linter/run
  await new Promise(r => setTimeout(r, 1500))
  linting.value = false
}

function navigateToIssue(issue: any) {
  // TODO: navigate to relevant lore detail
}

function severityClass(severity: string) {
  return severity === 'error' ? 'severity-error' : severity === 'warning' ? 'severity-warning' : 'severity-info'
}
</script>

<style scoped>
.linter-page { max-width: 900px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.page-header h1 { font-size: 28px; font-weight: 700; }
.subtitle { font-size: 14px; color: var(--text-secondary); }
.btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: var(--accent-cyan); color: var(--bg-primary); }
.btn-primary:hover { box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); }
.btn-link { background: none; border: none; color: var(--accent-cyan); font-size: 13px; cursor: pointer; padding: 0; margin-top: 8px; }
.linting-status { display: flex; align-items: center; gap: 12px; padding: 40px; color: var(--text-secondary); }
.spinner { width: 20px; height: 20px; border: 2px solid var(--border-color); border-top-color: var(--accent-cyan); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: 60px; color: var(--text-secondary); font-size: 15px; }
.issues-list { display: flex; flex-direction: column; gap: 12px; }
.issue-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; }
.issue-card.error { border-left: 3px solid var(--danger); }
.issue-card.warning { border-left: 3px solid var(--warning); }
.issue-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.severity-badge { font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; }
.issue-card.error .severity-badge { background: rgba(255, 51, 85, 0.15); color: var(--danger); }
.issue-card.warning .severity-badge { background: rgba(255, 170, 0, 0.15); color: var(--warning); }
.issue-title { font-size: 15px; font-weight: 600; }
.issue-description { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.issue-meta { display: flex; align-items: center; gap: 8px; margin-top: 8px; font-size: 13px; }
.issue-location { background: rgba(0, 240, 255, 0.08); padding: 2px 8px; border-radius: 4px; color: var(--accent-cyan); }
.issue-arrow { color: var(--text-dim); }
</style>
