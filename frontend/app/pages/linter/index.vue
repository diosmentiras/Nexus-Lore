<template>
  <div class="linter-page">
    <header class="page-header">
      <div>
        <span v-if="world" class="page-kicker">{{ world.name }}</span>
        <h1 class="page-title">设定检查</h1>
        <p class="page-description">检查实体、关系引用与时间线一致性</p>
      </div>
      <button class="btn btn-primary" :disabled="linting || !worldId" @click="runLint">
        <RefreshCwIcon v-if="linting" :size="16" class="spin" aria-hidden="true" />
        <SearchCheckIcon v-else :size="16" aria-hidden="true" />
        <span>{{ linting ? "分析中..." : "运行检查" }}</span>
      </button>
    </header>

    <section class="summary-strip" aria-label="检查结果统计">
      <button :class="{ active: !severityFilter }" @click="severityFilter = ''"><span>全部</span><strong>{{ issues.length }}</strong></button>
      <button :class="{ active: severityFilter === 'error' }" @click="severityFilter = 'error'"><span>错误</span><strong>{{ severityCount.error }}</strong></button>
      <button :class="{ active: severityFilter === 'warning' }" @click="severityFilter = 'warning'"><span>警告</span><strong>{{ severityCount.warning }}</strong></button>
      <button :class="{ active: severityFilter === 'info' }" @click="severityFilter = 'info'"><span>提示</span><strong>{{ severityCount.info }}</strong></button>
    </section>

    <div class="result-toolbar">
      <div class="segmented-control" aria-label="问题状态">
        <button :class="{ active: issueState === 'open' }" @click="issueState = 'open'">待处理</button>
        <button :class="{ active: issueState === 'resolved' }" @click="issueState = 'resolved'">已解决</button>
      </div>
      <span v-if="lastRunSummary" class="run-summary">本次发现 {{ lastRunTotal }} 项</span>
    </div>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <Transition name="fade" mode="out-in">
      <div v-if="loading || linting" key="linting" class="linting-status">
        <div class="spinner" />
        <div class="linting-text">
          <p class="linting-title">{{ linting ? "正在检查设定逻辑..." : "正在读取检查结果..." }}</p>
          <p class="linting-desc">实体引用、关系边界、时间顺序与角色生死状态</p>
        </div>
      </div>

      <div v-else-if="!filteredIssues.length" key="empty" class="empty-state">
        <ShieldCheckIcon :size="48" class="empty-icon" aria-hidden="true" />
        <p class="empty-title">{{ issueState === "open" ? "没有待处理问题" : "还没有已解决记录" }}</p>
        <p class="empty-desc">{{ issueState === "open" ? "运行检查可重新验证当前世界的数据一致性。" : "处理过的问题会保留在这里，便于回溯。" }}</p>
      </div>

      <div v-else key="issues" class="issues-list">
        <article v-for="issue in filteredIssues" :key="issue.id" class="issue-card" :class="issue.severity" :data-issue-id="issue.id">
          <div class="issue-icon-wrapper">
            <AlertCircleIcon v-if="issue.severity === 'error'" :size="18" aria-hidden="true" />
            <AlertTriangleIcon v-else-if="issue.severity === 'warning'" :size="18" aria-hidden="true" />
            <InfoIcon v-else :size="18" aria-hidden="true" />
          </div>
          <div class="issue-content">
            <div class="issue-header">
              <span class="severity-badge" :class="`severity-${issue.severity}`">{{ severityLabel(issue.severity) }}</span>
              <span class="issue-title">{{ issue.title }}</span>
            </div>
            <p class="issue-desc">{{ issue.description }}</p>
            <div v-if="issue.entity1_name || issue.entity2_name" class="issue-entities">
              <span v-if="issue.entity1_name" class="entity-tag">{{ issue.entity1_name }}</span>
              <ArrowRightIcon v-if="issue.entity1_name && issue.entity2_name" :size="12" class="entity-arrow" aria-hidden="true" />
              <span v-if="issue.entity2_name" class="entity-tag">{{ issue.entity2_name }}</span>
            </div>
          </div>
          <div class="issue-actions">
            <button v-if="canLocate(issue)" class="btn btn-link" title="定位相关设定" @click="navigateToIssue(issue)">
              <LocateFixedIcon :size="15" aria-hidden="true" />
              <span>定位</span>
            </button>
            <button v-if="issueState === 'open'" class="btn btn-resolve" @click="setResolved(issue, true)">
              <CircleCheckIcon :size="15" aria-hidden="true" />
              <span>解决</span>
            </button>
            <button v-else class="btn btn-resolve" @click="setResolved(issue, false)">
              <RotateCcwIcon :size="15" aria-hidden="true" />
              <span>重新打开</span>
            </button>
          </div>
        </article>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import {
  AlertCircle as AlertCircleIcon,
  AlertTriangle as AlertTriangleIcon,
  ArrowRight as ArrowRightIcon,
  CircleCheck as CircleCheckIcon,
  Info as InfoIcon,
  LocateFixed as LocateFixedIcon,
  RefreshCw as RefreshCwIcon,
  RotateCcw as RotateCcwIcon,
  SearchCheck as SearchCheckIcon,
  ShieldCheck as ShieldCheckIcon,
} from "lucide-vue-next"

interface LintIssue {
  id: string
  world_id?: string | null
  severity: "error" | "warning" | "info"
  title: string
  description?: string | null
  entity1_id?: string | null
  entity2_id?: string | null
  entity1_name?: string | null
  entity2_name?: string | null
  source_lore_id?: string | null
  issue_type?: string | null
  resolved: boolean
  meta?: Record<string, any>
}

interface LintSummary { error: number; warning: number; info: number }
interface LintRunResponse { issues: LintIssue[]; summary: LintSummary }

const route = useRoute()
const apiBase = useApiBase()
const { worlds, selectedWorldId, loadWorlds, selectWorld } = useWorlds()
const worldId = computed(() => typeof route.params.worldId === "string" ? route.params.worldId : selectedWorldId.value)
const world = computed(() => worlds.value.find((item) => item.id === worldId.value))
const linting = ref(false)
const loading = ref(true)
const issues = ref<LintIssue[]>([])
const issueState = ref<"open" | "resolved">("open")
const severityFilter = ref("")
const errorMessage = ref("")
const lastRunSummary = ref<LintSummary | null>(null)

const filteredIssues = computed(() => issues.value.filter((issue) => !severityFilter.value || issue.severity === severityFilter.value))
const severityCount = computed(() => ({
  error: issues.value.filter((issue) => issue.severity === "error").length,
  warning: issues.value.filter((issue) => issue.severity === "warning").length,
  info: issues.value.filter((issue) => issue.severity === "info").length,
}))
const lastRunTotal = computed(() => lastRunSummary.value
  ? lastRunSummary.value.error + lastRunSummary.value.warning + lastRunSummary.value.info
  : 0)

async function loadIssues() {
  if (!worldId.value) return
  loading.value = true
  errorMessage.value = ""
  try {
    issues.value = await $fetch<LintIssue[]>(`${apiBase}/api/linter/issues`, {
      query: { world_id: worldId.value, resolved: issueState.value === "resolved" },
    })
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || "检查结果读取失败"
  } finally {
    loading.value = false
  }
}

async function runLint() {
  if (!worldId.value) return
  linting.value = true
  errorMessage.value = ""
  issueState.value = "open"
  issues.value = []
  try {
    const result = await $fetch<LintRunResponse>(`${apiBase}/api/linter/run`, {
      method: "POST",
      query: { world_id: worldId.value },
    })
    issues.value = result.issues
    lastRunSummary.value = result.summary
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || "设定检查运行失败"
  } finally {
    linting.value = false
  }
}

async function setResolved(issue: LintIssue, resolved: boolean) {
  try {
    await $fetch(`${apiBase}/api/linter/issues/${issue.id}`, { method: "PATCH", body: { resolved } })
    await loadIssues()
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || "问题状态更新失败"
  }
}

function canLocate(issue: LintIssue) {
  return Boolean(issue.source_lore_id || issue.entity1_id || issue.meta?.event_title)
}

function navigateToIssue(issue: LintIssue) {
  const loreId = issue.source_lore_id || issue.entity1_id
  if (loreId) return navigateTo(worldId.value ? `/worlds/${worldId.value}/lore/${loreId}` : `/lore/${loreId}`)
  if (worldId.value && issue.meta?.event_title) {
    return navigateTo({ path: `/worlds/${worldId.value}/chronicle`, query: { search: issue.meta.event_title } })
  }
}

function severityLabel(severity: string) {
  return ({ error: "错误", warning: "警告", info: "提示" } as Record<string, string>)[severity] || severity
}

onMounted(async () => {
  await loadWorlds()
  if (typeof route.params.worldId === "string") selectWorld(route.params.worldId)
  await loadIssues()
})

watch(issueState, loadIssues)
</script>

<style scoped>
.linter-page { width: min(1000px, 100%); min-width: 0; animation: fadeIn var(--duration-normal) var(--easing-default); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-6); }
.page-kicker { color: var(--color-accent-cyan); font-size: var(--font-size-xs); }
.page-title { margin-top: 2px; font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); letter-spacing: 0; }
.page-description { margin-top: var(--space-1); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.btn { display: inline-flex; min-height: 34px; align-items: center; gap: var(--space-2); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-md); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); cursor: pointer; white-space: nowrap; }
.btn-primary { background: var(--color-accent-cyan); color: var(--color-text-inverse); }
.btn-primary:hover:not(:disabled) { box-shadow: var(--shadow-glow-cyan); }
.btn:disabled { opacity: .45; cursor: not-allowed; }
.summary-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: var(--space-4); border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border); }
.summary-strip button { display: flex; min-height: 54px; align-items: center; justify-content: space-between; padding: 0 var(--space-4); border: 0; border-right: 1px solid var(--color-border); background: transparent; color: var(--color-text-secondary); cursor: pointer; }
.summary-strip button:last-child { border-right: 0; }
.summary-strip button:hover, .summary-strip button.active { background: rgba(0, 240, 255, .05); color: var(--color-accent-cyan); }
.summary-strip strong { font-family: var(--font-mono); }
.result-toolbar { display: flex; min-height: 44px; align-items: center; justify-content: space-between; margin-bottom: var(--space-5); }
.segmented-control { display: inline-flex; min-height: 34px; overflow: hidden; border: 1px solid var(--color-border); border-radius: var(--radius-md); }
.segmented-control button { padding: 0 var(--space-3); border: 0; border-right: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-secondary); cursor: pointer; }
.segmented-control button:last-child { border-right: 0; }
.segmented-control button.active { background: rgba(0, 240, 255, .09); color: var(--color-accent-cyan); }
.run-summary { color: var(--color-text-muted); font-size: var(--font-size-xs); }
.error-banner { margin-bottom: var(--space-4); padding: var(--space-3); border: 1px solid rgba(255, 51, 85, .35); color: var(--color-danger); font-size: var(--font-size-sm); }
.linting-status { display: flex; min-height: 300px; align-items: center; justify-content: center; gap: var(--space-5); }
.spinner { width: 30px; height: 30px; flex-shrink: 0; border: 2px solid var(--color-border); border-top-color: var(--color-accent-cyan); border-radius: 50%; animation: spin .8s linear infinite; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.linting-text { display: flex; flex-direction: column; gap: 2px; }
.linting-title { color: var(--color-text-primary); font-weight: var(--font-weight-medium); }
.linting-desc { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.empty-state { display: flex; min-height: 340px; align-items: center; justify-content: center; flex-direction: column; gap: var(--space-3); color: var(--color-text-muted); text-align: center; }
.empty-icon { color: var(--color-success); }
.empty-title { color: var(--color-text-secondary); font-size: var(--font-size-lg); font-weight: var(--font-weight-semibold); }
.empty-desc { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.issues-list { border-bottom: 1px solid var(--color-border); }
.issue-card { display: grid; grid-template-columns: 36px minmax(0, 1fr) auto; align-items: start; gap: var(--space-4); padding: var(--space-5) var(--space-3); border-top: 1px solid var(--color-border); }
.issue-card.error { border-left: 3px solid var(--color-danger); }
.issue-card.warning { border-left: 3px solid var(--color-warning); }
.issue-card.info { border-left: 3px solid var(--color-accent-cyan); }
.issue-icon-wrapper { display: flex; width: 36px; height: 36px; align-items: center; justify-content: center; border-radius: var(--radius-md); }
.issue-card.error .issue-icon-wrapper { background: rgba(255, 51, 85, .1); color: var(--color-danger); }
.issue-card.warning .issue-icon-wrapper { background: rgba(255, 170, 0, .1); color: var(--color-warning); }
.issue-card.info .issue-icon-wrapper { background: rgba(0, 240, 255, .08); color: var(--color-accent-cyan); }
.issue-content { display: flex; min-width: 0; flex-direction: column; gap: var(--space-2); }
.issue-header { display: flex; align-items: center; gap: var(--space-2); }
.severity-badge { padding: 1px 7px; border-radius: var(--radius-sm); font-size: var(--font-size-xs); font-weight: var(--font-weight-semibold); }
.severity-error { background: rgba(255, 51, 85, .12); color: var(--color-danger); }
.severity-warning { background: rgba(255, 170, 0, .12); color: var(--color-warning); }
.severity-info { background: rgba(0, 240, 255, .09); color: var(--color-accent-cyan); }
.issue-title { color: var(--color-text-primary); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); }
.issue-desc { color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: var(--line-height-normal); }
.issue-entities { display: flex; align-items: center; gap: var(--space-2); }
.entity-tag { padding: 2px 7px; border: 1px solid rgba(0, 240, 255, .15); border-radius: var(--radius-sm); color: var(--color-accent-cyan); font-size: var(--font-size-xs); }
.entity-arrow { color: var(--color-text-muted); }
.issue-actions { display: flex; flex-shrink: 0; align-items: center; gap: var(--space-2); }
.btn-link { background: transparent; color: var(--color-text-secondary); }
.btn-link:hover { color: var(--color-accent-cyan); }
.btn-resolve { border: 1px solid var(--color-border); background: transparent; color: var(--color-text-secondary); }
.btn-resolve:hover { border-color: var(--color-success); color: var(--color-success); }
.fade-enter-active, .fade-leave-active { transition: opacity var(--duration-normal); }
.fade-leave-active { pointer-events: none; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@media (max-width: 680px) {
  .page-header { flex-direction: column; }
  .summary-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .summary-strip button:nth-child(2) { border-right: 0; }
  .issue-card { grid-template-columns: 36px minmax(0, 1fr); }
  .issue-actions { grid-column: 2; justify-content: flex-start; }
}
</style>
