<template>
  <div class="detail-page">
    <NuxtLink :to="loreIndexPath" class="back-link">
      <ArrowLeftIcon :size="16" aria-hidden="true" />
      <span>返回设定库</span>
    </NuxtLink>

    <div v-if="loading" class="state-panel">
      <LoaderCircleIcon :size="28" class="spin" aria-hidden="true" />
      <p>正在读取设定详情…</p>
    </div>

    <div v-else-if="notFound" class="state-panel">
      <AlertCircleIcon :size="36" class="danger-icon" aria-hidden="true" />
      <h1>该设定不存在</h1>
      <p>这可能是之前页面缓存的旧链接，请返回设定库重新选择。</p>
    </div>

    <div v-else-if="errorMessage" class="state-panel">
      <AlertCircleIcon :size="36" class="danger-icon" aria-hidden="true" />
      <h1>详情读取失败</h1>
      <p>{{ errorMessage }}</p>
      <button class="retry-button" @click="loadDetail">重试</button>
    </div>

    <template v-else-if="entity">
      <header class="entity-header">
        <div class="header-main">
          <div class="entity-kicker">
            <span class="type-badge" :class="`type-${entity.entity_type}`">{{ typeLabel }}</span>
            <span v-if="entity.extracted_by_ai" class="ai-badge">AI</span>
          </div>
          <h1>{{ entity.name }}</h1>
          <p v-if="entity.summary" class="entity-summary">{{ entity.summary }}</p>
        </div>
      </header>

      <div class="detail-layout">
        <div class="primary-column">
          <section class="detail-section">
            <div class="section-heading">
              <DatabaseIcon :size="17" aria-hidden="true" />
              <h2>设定映射</h2>
            </div>
            <dl class="mapping-list">
              <div class="mapping-row">
                <dt>原型</dt>
                <dd>
                  <a v-if="canonicalUrl" :href="canonicalUrl" target="_blank" rel="noreferrer">
                    {{ canonicalName }}
                    <ExternalLinkIcon :size="13" aria-hidden="true" />
                  </a>
                  <span v-else>{{ canonicalName || "未标注" }}</span>
                </dd>
              </div>
              <div class="mapping-row">
                <dt>死者手牌版本</dt>
                <dd>{{ adaptation || entity.name }}</dd>
              </div>
              <div v-if="entity.date" class="mapping-row">
                <dt>时间</dt>
                <dd>{{ entity.date }}<span v-if="entity.date_context" class="muted"> · {{ entity.date_context }}</span></dd>
              </div>
            </dl>
          </section>

          <section v-if="entity.background" class="detail-section">
            <div class="section-heading">
              <FileTextIcon :size="17" aria-hidden="true" />
              <h2>设定档案</h2>
            </div>
            <p class="body-copy">{{ entity.background }}</p>
          </section>

          <section v-if="evidenceItems.length" class="detail-section">
            <div class="section-heading">
              <QuoteIcon :size="17" aria-hidden="true" />
              <h2>正文依据</h2>
              <span class="section-count">{{ evidenceItems.length }}</span>
            </div>
            <p class="section-intro">以下内容截取自已归档故事，用于核对该设定在正文中的身份、行动与语境。</p>
            <div class="evidence-list">
              <article v-for="item in evidenceItems" :key="`${item.document_id}-${item.excerpt}`" class="evidence-row">
                <div class="evidence-heading">
                  <a v-if="item.url" :href="item.url" target="_blank" rel="noreferrer">
                    {{ item.title }}
                    <ExternalLinkIcon :size="13" aria-hidden="true" />
                  </a>
                  <span v-else>{{ item.title }}</span>
                  <span class="match-label">命中：{{ item.matched_alias }}</span>
                </div>
                <blockquote>{{ item.excerpt }}</blockquote>
              </article>
            </div>
          </section>

          <section v-if="coEntities.length" class="detail-section">
            <div class="section-heading">
              <UsersIcon :size="17" aria-hidden="true" />
              <h2>共同出场</h2>
              <span class="section-count">{{ coEntities.length }}</span>
            </div>
            <p class="section-intro">这些已建档设定与本条目出现在同一篇或多篇故事中。</p>
            <div class="co-entity-list">
              <NuxtLink v-for="item in coEntities" :key="item.id" :to="loreDetailPath(item.id)" class="co-entity-row">
                <span class="co-entity-type">{{ typeLabels[item.entity_type] || item.entity_type }}</span>
                <span class="co-entity-main">
                  <strong>{{ item.name }}</strong>
                  <small>{{ sharedStoryText(item) }}</small>
                </span>
                <span class="shared-count">共 {{ item.shared_story_count }} 篇</span>
                <ChevronRightIcon :size="15" aria-hidden="true" />
              </NuxtLink>
            </div>
          </section>

          <section class="detail-section">
            <div class="section-heading">
              <BookOpenIcon :size="17" aria-hidden="true" />
              <h2>承载故事</h2>
              <span class="section-count">{{ stories.length }}</span>
            </div>
            <div v-if="stories.length" class="story-list">
              <article v-for="story in stories" :key="story.url" class="story-row">
                <div class="story-status" :class="storyState(story)">
                  <CircleCheckIcon v-if="storyState(story) === 'available'" :size="15" aria-hidden="true" />
                  <CircleOffIcon v-else :size="15" aria-hidden="true" />
                </div>
                <div class="story-main">
                  <a :href="story.url" target="_blank" rel="noreferrer" class="story-title">
                    {{ story.title }}
                    <ExternalLinkIcon :size="13" aria-hidden="true" />
                  </a>
                  <p v-if="storyDocument(story)?.analysis_summary || story.analysis_summary" class="story-summary">
                    {{ storyDocument(story)?.analysis_summary || story.analysis_summary }}
                  </p>
                  <p v-else class="story-summary">
                    {{ storyState(story) === "missing" ? "来源页面当前不可用，已保留设定中心中的映射。" : "设定中心收录的承载故事。" }}
                  </p>
                </div>
                <span class="story-state-label" :class="storyState(story)">
                  {{ storyState(story) === "missing" ? "失效" : "已读取" }}
                </span>
              </article>
            </div>
            <p v-else class="empty-copy">该映射没有标注独立故事。</p>
          </section>

          <section v-if="relatedRelations.length" class="detail-section">
            <div class="section-heading">
              <Link2Icon :size="17" aria-hidden="true" />
              <h2>关联设定</h2>
              <span class="section-count">{{ relatedRelations.length }}</span>
            </div>
            <div class="relation-list">
              <NuxtLink
                v-for="relation in relatedRelations"
                :key="relation.id"
                :to="loreDetailPath(relation.other.id)"
                class="relation-row"
              >
                <span class="relation-label">{{ relation.label || relationTypeLabel(relation.relation_type) }}</span>
                <span class="relation-name">{{ relation.other.name }}</span>
                <ChevronRightIcon :size="15" aria-hidden="true" />
              </NuxtLink>
            </div>
          </section>
        </div>

        <aside class="side-column">
          <section v-if="currentWorld" class="side-section">
            <h2>所属世界观</h2>
            <p class="world-name">{{ currentWorld.name }}</p>
            <p v-if="currentWorld.description" class="source-summary">{{ currentWorld.description }}</p>
          </section>

          <section class="side-section">
            <h2>标签</h2>
            <div v-if="entity.tags?.length" class="tag-list">
              <span v-for="tag in entity.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <p v-else class="empty-copy">无标签</p>
          </section>

          <section v-if="sourceDocument" class="side-section">
            <h2>原始来源</h2>
            <a v-if="sourceDocument.url" :href="sourceDocument.url" target="_blank" rel="noreferrer" class="source-link">
              <FileTextIcon :size="15" aria-hidden="true" />
              <span>{{ sourceDocument.title }}</span>
              <ExternalLinkIcon :size="13" aria-hidden="true" />
            </a>
            <p v-if="sourceDocument.analysis_summary" class="source-summary">{{ sourceDocument.analysis_summary }}</p>
          </section>

          <section v-if="dateMarkers.length" class="side-section">
            <h2>时间线索</h2>
            <div class="marker-list">
              <span v-for="marker in dateMarkers" :key="marker" class="date-marker">
                <CalendarDaysIcon :size="13" aria-hidden="true" />
                {{ marker }}
              </span>
            </div>
          </section>

          <section v-if="profile?.source_note" class="side-section source-note">
            <InfoIcon :size="15" aria-hidden="true" />
            <p>{{ profile.source_note }}</p>
          </section>

          <section class="side-section metadata-section">
            <h2>记录信息</h2>
            <dl>
              <div><dt>类型</dt><dd>{{ typeLabel }}</dd></div>
              <div><dt>创建</dt><dd>{{ formatDate(entity.created_at) }}</dd></div>
              <div><dt>更新</dt><dd>{{ formatDate(entity.updated_at) }}</dd></div>
            </dl>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import {
  AlertCircle as AlertCircleIcon,
  ArrowLeft as ArrowLeftIcon,
  BookOpen as BookOpenIcon,
  CalendarDays as CalendarDaysIcon,
  ChevronRight as ChevronRightIcon,
  CircleCheck as CircleCheckIcon,
  CircleOff as CircleOffIcon,
  Database as DatabaseIcon,
  ExternalLink as ExternalLinkIcon,
  FileText as FileTextIcon,
  Info as InfoIcon,
  Link2 as Link2Icon,
  LoaderCircle as LoaderCircleIcon,
  Quote as QuoteIcon,
  Users as UsersIcon,
} from "lucide-vue-next"

interface StoryReference {
  title: string
  url: string
  document_id?: string | null
  status?: string | null
  analysis_summary?: string | null
}

interface EntityResponse {
  id: string
  world_id?: string | null
  source_document_id?: string | null
  name: string
  entity_type: string
  summary?: string | null
  background?: string | null
  tags: string[]
  meta: Record<string, any>
  date?: string | null
  date_context?: string | null
  extracted_by_ai: boolean
  created_at: string
  updated_at: string
}

interface SourceDocumentResponse {
  id: string
  title: string
  url?: string | null
  status: string
  analysis_summary?: string | null
  meta: Record<string, any>
}

interface RelationResponse {
  id: string
  source_id: string
  target_id: string
  relation_type: string
  label?: string | null
}

interface RelatedRelation extends RelationResponse {
  other: EntityResponse
}

interface EvidenceItem {
  document_id: string
  title: string
  url?: string | null
  matched_alias: string
  excerpt: string
}

interface CoEntityItem {
  id: string
  name: string
  entity_type: string
  shared_story_count: number
  shared_story_titles: string[]
}

interface EntityProfile {
  overview?: string
  adaptation_note?: string
  story_count?: number
  available_story_count?: number
  evidence?: EvidenceItem[]
  co_entities?: CoEntityItem[]
  date_markers?: string[]
  source_note?: string
}

const route = useRoute()
const apiBase = useApiBase()
const { worlds, selectedWorldId, loadWorlds } = useWorlds()
const entity = ref<EntityResponse | null>(null)
const sourceDocument = ref<SourceDocumentResponse | null>(null)
const storyDocuments = ref<Record<string, SourceDocumentResponse>>({})
const relatedRelations = ref<RelatedRelation[]>([])
const loading = ref(true)
const notFound = ref(false)
const errorMessage = ref("")

const typeLabels: Record<string, string> = {
  character: "人物",
  faction: "势力",
  item: "物品",
  location: "地点",
  event: "事件",
  containment: "异常",
  world: "世界观",
}

const typeLabel = computed(() => entity.value ? typeLabels[entity.value.entity_type] || entity.value.entity_type : "")
const canonicalName = computed(() => entity.value?.meta?.canonical_name || "")
const canonicalUrl = computed(() => entity.value?.meta?.canonical_url || "")
const adaptation = computed(() => entity.value?.meta?.adaptation || "")
const stories = computed<StoryReference[]>(() => Array.isArray(entity.value?.meta?.stories) ? entity.value!.meta.stories : [])
const profile = computed<EntityProfile | null>(() => entity.value?.meta?.profile || null)
const evidenceItems = computed(() => Array.isArray(profile.value?.evidence) ? profile.value!.evidence! : [])
const coEntities = computed(() => Array.isArray(profile.value?.co_entities) ? profile.value!.co_entities! : [])
const dateMarkers = computed(() => Array.isArray(profile.value?.date_markers) ? profile.value!.date_markers! : [])
const currentWorld = computed(() => worlds.value.find((world) => world.id === entity.value?.world_id))
const workspaceWorldId = computed(() => typeof route.params.worldId === "string" ? route.params.worldId : "")
const loreIndexPath = computed(() => workspaceWorldId.value ? `/worlds/${workspaceWorldId.value}/lore` : "/lore")

function loreDetailPath(id: string) {
  return workspaceWorldId.value ? `/worlds/${workspaceWorldId.value}/lore/${id}` : `/lore/${id}`
}

function storyDocument(story: StoryReference) {
  return story.document_id ? storyDocuments.value[story.document_id] : undefined
}

function storyState(story: StoryReference) {
  return (storyDocument(story)?.status || story.status) === "missing" ? "missing" : "available"
}

function relationTypeLabel(type: string) {
  return ({ member: "隶属", located_at: "位于", ally: "同盟", hostile: "敌对", neutral: "中立", owns: "拥有", other: "关联" } as Record<string, string>)[type] || type
}

function sharedStoryText(item: CoEntityItem) {
  const titles = item.shared_story_titles?.filter(Boolean) || []
  if (!titles.length) return "共享承载故事"
  const preview = titles.slice(0, 2).map((title) => `《${title}》`).join("、")
  return titles.length > 2 ? `${preview}等 ${titles.length} 篇` : preview
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(value))
}

async function loadDetail() {
  loading.value = true
  notFound.value = false
  errorMessage.value = ""
  entity.value = null
  relatedRelations.value = []
  storyDocuments.value = {}
  sourceDocument.value = null

  try {
    const result = await $fetch<EntityResponse>(`${apiBase}/api/entities/${route.params.id}`)
    entity.value = result
    if (result.world_id) selectedWorldId.value = result.world_id

    const [allEntities, outgoing, incoming] = await Promise.all([
      $fetch<EntityResponse[]>(`${apiBase}/api/entities`, { query: { world_id: result.world_id } }),
      $fetch<RelationResponse[]>(`${apiBase}/api/relations`, { query: { world_id: result.world_id, source_id: result.id } }),
      $fetch<RelationResponse[]>(`${apiBase}/api/relations`, { query: { world_id: result.world_id, target_id: result.id } }),
    ])
    const entityMap = new Map(allEntities.map((item) => [item.id, item]))
    const relations = [...outgoing, ...incoming].filter((item, index, list) => list.findIndex((candidate) => candidate.id === item.id) === index)
    relatedRelations.value = relations.flatMap((relation) => {
      const otherId = relation.source_id === result.id ? relation.target_id : relation.source_id
      const other = entityMap.get(otherId)
      return other ? [{ ...relation, other }] : []
    })

    const documentIds = [...new Set([
      result.source_document_id,
      ...stories.value.filter((story) => !story.status).map((story) => story.document_id),
    ].filter((id): id is string => Boolean(id)))]
    const documents = await Promise.all(documentIds.map((id) =>
      $fetch<SourceDocumentResponse>(`${apiBase}/api/documents/${id}`).catch(() => null),
    ))
    for (const document of documents) {
      if (document) storyDocuments.value[document.id] = document
    }
    sourceDocument.value = result.source_document_id ? storyDocuments.value[result.source_document_id] || null : null
  } catch (error: any) {
    if (error?.statusCode === 404 || error?.status === 404) {
      notFound.value = true
    } else {
      errorMessage.value = error?.data?.detail || error?.message || "未知错误"
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadWorlds()
  await loadDetail()
})

watch(() => route.params.id, loadDetail)
</script>

<style scoped>
.detail-page {
  max-width: 1120px;
  min-width: 0;
  animation: fadeIn var(--duration-normal) var(--easing-default);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
}

.back-link:hover { color: var(--color-accent-cyan); }

.state-panel {
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  text-align: center;
  color: var(--color-text-secondary);
}

.state-panel h1 { color: var(--color-text-primary); font-size: var(--font-size-2xl); }
.state-panel p { max-width: 520px; }
.danger-icon { color: var(--color-danger); }
.spin { animation: spin 0.8s linear infinite; color: var(--color-accent-cyan); }
@keyframes spin { to { transform: rotate(360deg); } }

.retry-button {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
}

.entity-header {
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-6);
}

.header-main { max-width: 820px; }
.entity-kicker { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.entity-header h1 { font-size: var(--font-size-3xl); line-height: var(--line-height-tight); overflow-wrap: anywhere; }
.entity-summary { margin-top: var(--space-3); color: var(--color-text-secondary); line-height: var(--line-height-relaxed); }

.type-badge, .ai-badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.type-character { color: var(--color-accent-cyan); background: rgba(0, 240, 255, 0.1); }
.type-faction { color: var(--color-accent-magenta); background: rgba(255, 0, 170, 0.1); }
.type-item { color: var(--color-accent-yellow); background: rgba(255, 215, 0, 0.1); }
.type-location { color: var(--color-success); background: rgba(0, 255, 136, 0.1); }
.type-event { color: var(--color-warning); background: rgba(255, 170, 0, 0.1); }
.type-containment { color: var(--color-danger); background: rgba(255, 51, 85, 0.1); }
.type-world { color: var(--color-accent-purple); background: rgba(168, 85, 247, 0.12); }
.ai-badge { color: var(--color-accent-purple); border: 1px solid rgba(168, 85, 247, 0.35); }

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 300px);
  gap: var(--space-8);
  align-items: start;
}

.primary-column, .side-column { min-width: 0; }
.primary-column { display: flex; flex-direction: column; gap: var(--space-8); }
.side-column { display: flex; flex-direction: column; gap: var(--space-6); border-left: 1px solid var(--color-border); padding-left: var(--space-6); }

.detail-section, .side-section { min-width: 0; }
.section-heading { display: flex; align-items: center; gap: var(--space-2); color: var(--color-accent-cyan); margin-bottom: var(--space-4); }
.section-heading h2, .side-section h2 { font-size: var(--font-size-base); color: var(--color-text-primary); font-weight: var(--font-weight-semibold); }
.section-count { color: var(--color-text-muted); font-size: var(--font-size-xs); }

.mapping-list { border-top: 1px solid var(--color-border); }
.mapping-row { display: grid; grid-template-columns: 140px minmax(0, 1fr); gap: var(--space-4); padding: var(--space-3) 0; border-bottom: 1px solid var(--color-border); }
.mapping-row dt { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.mapping-row dd { color: var(--color-text-primary); overflow-wrap: anywhere; }
.mapping-row a, .story-title { display: inline-flex; align-items: center; gap: 5px; }
.muted { color: var(--color-text-muted); }
.body-copy { color: var(--color-text-secondary); line-height: var(--line-height-relaxed); overflow-wrap: anywhere; white-space: pre-line; }
.section-intro { margin: calc(var(--space-2) * -1) 0 var(--space-3); color: var(--color-text-muted); font-size: var(--font-size-sm); line-height: var(--line-height-normal); }

.evidence-list, .co-entity-list { border-top: 1px solid var(--color-border); }
.evidence-row { padding: var(--space-4) 0; border-bottom: 1px solid var(--color-border); }
.evidence-heading { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-3); }
.evidence-heading a { display: inline-flex; align-items: center; gap: 5px; min-width: 0; font-weight: var(--font-weight-medium); overflow-wrap: anywhere; }
.match-label { flex: 0 0 auto; padding: 2px 7px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: var(--font-size-xs); }
.evidence-row blockquote { margin: 0; padding-left: var(--space-4); border-left: 2px solid var(--color-accent-cyan); color: var(--color-text-secondary); font-size: var(--font-size-sm); line-height: var(--line-height-relaxed); white-space: pre-line; overflow-wrap: anywhere; }

.co-entity-row { display: grid; grid-template-columns: 64px minmax(0, 1fr) auto 16px; align-items: center; gap: var(--space-3); padding: var(--space-3) 0; border-bottom: 1px solid var(--color-border); }
.co-entity-type { color: var(--color-text-muted); font-size: var(--font-size-xs); }
.co-entity-main { display: flex; min-width: 0; flex-direction: column; gap: 2px; }
.co-entity-main strong { color: var(--color-text-primary); font-size: var(--font-size-sm); overflow-wrap: anywhere; }
.co-entity-main small { color: var(--color-text-muted); overflow-wrap: anywhere; }
.shared-count { color: var(--color-text-muted); font-size: var(--font-size-xs); white-space: nowrap; }
.co-entity-row:hover strong { color: var(--color-accent-cyan); }

.story-list, .relation-list { border-top: 1px solid var(--color-border); }
.story-row { display: grid; grid-template-columns: 22px minmax(0, 1fr) auto; gap: var(--space-3); align-items: start; padding: var(--space-4) 0; border-bottom: 1px solid var(--color-border); }
.story-status { padding-top: 2px; color: var(--color-success); }
.story-status.missing { color: var(--color-danger); }
.story-main { min-width: 0; }
.story-title { font-weight: var(--font-weight-medium); overflow-wrap: anywhere; }
.story-summary, .source-summary { margin-top: var(--space-1); color: var(--color-text-muted); font-size: var(--font-size-sm); line-height: var(--line-height-normal); }
.story-state-label { font-size: var(--font-size-xs); color: var(--color-success); white-space: nowrap; }
.story-state-label.missing { color: var(--color-danger); }

.relation-row { display: grid; grid-template-columns: minmax(90px, auto) minmax(0, 1fr) 16px; gap: var(--space-3); align-items: center; padding: var(--space-3) 0; border-bottom: 1px solid var(--color-border); }
.relation-label { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.relation-name { color: var(--color-text-primary); overflow-wrap: anywhere; }
.relation-row:hover .relation-name { color: var(--color-accent-cyan); }

.side-section h2 { margin-bottom: var(--space-3); }
.world-name { color: var(--color-text-primary); font-weight: var(--font-weight-semibold); }
.tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { padding: 3px 8px; border-radius: var(--radius-sm); border: 1px solid var(--color-border); color: var(--color-text-secondary); font-size: var(--font-size-xs); overflow-wrap: anywhere; }
.source-link { display: grid; grid-template-columns: 16px minmax(0, 1fr) 14px; align-items: start; gap: var(--space-2); overflow-wrap: anywhere; }
.marker-list { display: flex; flex-wrap: wrap; gap: 6px; }
.date-marker { display: inline-flex; align-items: center; gap: 5px; padding: 4px 7px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-text-secondary); font-size: var(--font-size-xs); overflow-wrap: anywhere; }
.source-note { display: grid; grid-template-columns: 16px minmax(0, 1fr); gap: var(--space-2); color: var(--color-text-muted); font-size: var(--font-size-xs); line-height: var(--line-height-normal); }
.metadata-section dl { display: flex; flex-direction: column; gap: var(--space-2); }
.metadata-section dl div { display: flex; justify-content: space-between; gap: var(--space-3); font-size: var(--font-size-sm); }
.metadata-section dt { color: var(--color-text-muted); }
.metadata-section dd { color: var(--color-text-secondary); text-align: right; }
.empty-copy { color: var(--color-text-muted); font-size: var(--font-size-sm); }

@media (max-width: 820px) {
  .detail-layout { grid-template-columns: 1fr; }
  .side-column { border-left: 0; border-top: 1px solid var(--color-border); padding-left: 0; padding-top: var(--space-6); }
}

@media (max-width: 560px) {
  .mapping-row { grid-template-columns: 1fr; gap: var(--space-1); }
  .story-row { grid-template-columns: 20px minmax(0, 1fr); }
  .story-state-label { grid-column: 2; }
  .evidence-heading { align-items: flex-start; flex-direction: column; }
  .co-entity-row { grid-template-columns: 52px minmax(0, 1fr) 16px; }
  .shared-count { grid-column: 2; }
  .co-entity-row > svg { grid-column: 3; grid-row: 1 / span 2; }
}
</style>
