<template>
  <article v-if="document" class="document-page">
    <NuxtLink :to="`/worlds/${worldId}/sources`" class="back-link"><ArrowLeftIcon :size="15" /><span>返回来源文章</span></NuxtLink>
    <header class="document-header">
      <div>
        <span class="status-label" :class="document.status">{{ statusLabel(document.status) }}</span>
        <h1>{{ document.title }}</h1>
        <p>{{ document.analysis_summary || "尚无分析摘要" }}</p>
      </div>
      <a v-if="document.url" :href="document.url" target="_blank" rel="noreferrer" class="source-button"><ExternalLinkIcon :size="16" /><span>打开原文</span></a>
    </header>
    <dl class="document-meta">
      <div><dt>来源站点</dt><dd>{{ document.source_site || "未标注" }}</dd></div>
      <div><dt>目录分区</dt><dd>{{ document.meta?.catalog_section || document.meta?.document_kind || "未分类" }}</dd></div>
      <div><dt>更新时间</dt><dd>{{ formatDate(document.updated_at) }}</dd></div>
      <div><dt>日期标记</dt><dd>{{ document.meta?.date_markers?.length || 0 }} 个</dd></div>
    </dl>
    <section class="content-section">
      <div class="section-heading"><h2>归档正文</h2><span>{{ document.content.length.toLocaleString("zh-CN") }} 字符</span></div>
      <div class="document-content">{{ document.content }}</div>
    </section>
  </article>
  <div v-else class="page-state">来源文章不存在或读取失败。</div>
</template>

<script setup lang="ts">
import { ArrowLeft as ArrowLeftIcon, ExternalLink as ExternalLinkIcon } from "lucide-vue-next"
const route = useRoute()
const worldId = String(route.params.worldId)
const documentId = String(route.params.documentId)
const { selectWorld } = useWorlds()
selectWorld(worldId)
const { data: document } = await useFetch<any>(`/api/documents/${documentId}`)
function statusLabel(status: string) { return ({ analyzed: "已读取", imported: "已导入", missing: "待补来源", analyzing: "分析中" } as Record<string, string>)[status] || status }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium", timeStyle: "short" }).format(date) }
</script>

<style scoped>
.document-page { width: min(980px, 100%); min-width: 0; }
.back-link { display: inline-flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-5); color: var(--color-text-secondary); font-size: var(--font-size-sm); text-decoration: none; }
.back-link:hover { color: var(--color-accent-cyan); }
.document-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-6); padding-bottom: var(--space-6); border-bottom: 1px solid var(--color-border); }
.status-label { display: inline-block; padding: 2px 7px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-accent-green); font-size: var(--font-size-xs); }
.status-label.missing { color: var(--color-danger); }
.document-header h1 { margin-top: var(--space-3); font-size: var(--font-size-2xl); letter-spacing: 0; overflow-wrap: anywhere; }
.document-header p { margin-top: var(--space-2); color: var(--color-text-secondary); font-size: var(--font-size-sm); }
.source-button { display: inline-flex; min-height: 36px; align-items: center; gap: var(--space-2); padding: 0 var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); color: var(--color-text-primary); font-size: var(--font-size-sm); text-decoration: none; white-space: nowrap; }
.source-button:hover { border-color: var(--color-accent-cyan); color: var(--color-accent-cyan); }
.document-meta { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-bottom: 1px solid var(--color-border); }
.document-meta div { min-width: 0; padding: var(--space-4); border-right: 1px solid var(--color-border); }
.document-meta div:last-child { border-right: 0; }
.document-meta dt { color: var(--color-text-muted); font-size: var(--font-size-xs); }
.document-meta dd { margin-top: 4px; overflow: hidden; color: var(--color-text-secondary); font-size: var(--font-size-sm); text-overflow: ellipsis; white-space: nowrap; }
.content-section { margin-top: var(--space-7); border-top: 1px solid var(--color-border); }
.section-heading { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) 0; }
.section-heading h2 { font-size: var(--font-size-base); letter-spacing: 0; }
.section-heading span { color: var(--color-text-muted); font-family: var(--font-mono); font-size: var(--font-size-xs); }
.document-content { padding: var(--space-5) 0 var(--space-10); color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: 1.85; white-space: pre-wrap; overflow-wrap: anywhere; }
.page-state { padding: var(--space-12); color: var(--color-text-muted); text-align: center; }
@media (max-width: 700px) { .document-header { flex-direction: column; } .document-meta { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
