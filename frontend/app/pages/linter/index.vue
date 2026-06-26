<template>
  <div class="linter-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Linter</h1>
        <p class="page-description">设定冲突检查器 · 自动检测逻辑漏洞</p>
      </div>
      <button class="btn btn-primary" @click="runLint" :disabled="linting">
        <RefreshCwIcon v-if="linting" :size="16" class="spin" aria-hidden="true" />
        <SearchCheckIcon v-else :size="16" aria-hidden="true" />
        <span>{{ linting ? "分析中..." : "运行检查" }}</span>
      </button>
    </header>

    <transition name="fade" mode="out-in">
      <!-- Loading -->
      <div v-if="linting" class="linting-status" key="linting">
        <div class="spinner"></div>
        <div class="linting-text">
          <p class="linting-title">正在分析设定逻辑...</p>
          <p class="linting-desc">检查时间线一致性、实体关系和事件冲突</p>
        </div>
      </div>

      <!-- Empty (no issues) -->
      <div v-else-if="!issues.length" class="empty-state" key="empty">
        <ShieldCheckIcon :size="48" class="empty-icon success-icon" aria-hidden="true" />
        <p class="empty-title">世界观逻辑一致</p>
        <p class="empty-desc">尚未发现设定冲突，点击「运行检查」进行验证</p>
      </div>

      <!-- Issues List -->
      <div v-else class="issues-list" key="issues">
        <div v-for="issue in issues" :key="issue.id" class="issue-card" :class="issue.severity">
          <div class="issue-icon-wrapper">
            <AlertCircleIcon v-if="issue.severity === 'error'" :size="18" aria-hidden="true" />
            <AlertTriangleIcon v-else :size="18" aria-hidden="true" />
          </div>
          <div class="issue-content">
            <div class="issue-header">
              <span class="severity-badge" :class="`severity-${issue.severity}`">{{ issue.severity === "error" ? "错误" : "警告" }}</span>
              <span class="issue-title">{{ issue.title }}</span>
            </div>
            <p class="issue-desc">{{ issue.description }}</p>
            <div v-if="issue.entity1 || issue.entity2" class="issue-entities">
              <span v-if="issue.entity1" class="entity-tag">{{ issue.entity1 }}</span>
              <ArrowRightIcon v-if="issue.entity1 && issue.entity2" :size="12" class="entity-arrow" aria-hidden="true" />
              <span v-if="issue.entity2" class="entity-tag">{{ issue.entity2 }}</span>
            </div>
          </div>
          <button class="btn btn-link" @click="navigateToIssue(issue)">
            定位
            <ChevronRightIcon :size="14" aria-hidden="true" />
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import {
  SearchCheck,
  RefreshCw,
  ShieldCheck,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  ChevronRight,
} from "lucide-vue-next"

const linting = ref(false)
const issues = ref<Array<{ id: string; severity: string; title: string; description: string; entity1?: string; entity2?: string }>>([])

async function runLint() {
  linting.value = true
  await new Promise((r) => setTimeout(r, 2000))
  linting.value = false
}

function navigateToIssue(issue: any) {
  // TODO: navigate to relevant lore detail
}
</script>

<style scoped>
.linter-page {
  max-width: 900px;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  gap: var(--space-4);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.02em;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
  white-space: nowrap;
}

.btn-primary {
  background: var(--color-accent-cyan);
  color: var(--color-text-inverse);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--shadow-glow-cyan);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--color-accent-cyan);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  padding: var(--space-1);
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--easing-default);
}

.btn-link:hover {
  gap: 6px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Linting Status */
.linting-status {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding: var(--space-12);
  justify-content: center;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

.linting-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.linting-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.linting-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* Empty */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16) 0;
  text-align: center;
  gap: var(--space-3);
}

.empty-icon {
  margin-bottom: var(--space-2);
}

.success-icon {
  color: var(--color-success);
}

.empty-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.empty-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* Issues List */
.issues-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.issue-card {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: all var(--duration-fast) var(--easing-default);
}

.issue-card.error {
  border-left: 3px solid var(--color-danger);
}

.issue-card.warning {
  border-left: 3px solid var(--color-warning);
}

.issue-card:hover {
  border-color: var(--color-border-hover);
}

.issue-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.issue-card.error .issue-icon-wrapper {
  background: rgba(255, 51, 85, 0.1);
  color: var(--color-danger);
}

.issue-card.warning .issue-icon-wrapper {
  background: rgba(255, 170, 0, 0.1);
  color: var(--color-warning);
}

.issue-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.issue-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.severity-badge {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  padding: 1px 8px;
  border-radius: var(--radius-sm);
  line-height: 1.5;
}

.severity-error {
  background: rgba(255, 51, 85, 0.12);
  color: var(--color-danger);
}

.severity-warning {
  background: rgba(255, 170, 0, 0.12);
  color: var(--color-warning);
}

.issue-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.issue-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.issue-entities {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.entity-tag {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: rgba(0, 240, 255, 0.06);
  border: 1px solid rgba(0, 240, 255, 0.15);
  border-radius: var(--radius-sm);
  color: var(--color-accent-cyan);
}

.entity-arrow {
  color: var(--color-text-muted);
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--easing-default);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
