<template>
  <div ref="containerRef" class="graph-root" role="application" :aria-label="`3D 关系星图，${nodes.length} 个节点，${links.length} 条连接`"></div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"
import * as THREE from "three"
import type { ForceGraph3DInstance, LinkObject, NodeObject } from "3d-force-graph"

interface GraphNode {
  id: string
  name: string
  entity_type: string
  color?: string | null
  size?: number
  summary?: string | null
  tags?: string[]
  url?: string | null
  status?: string | null
  canonical_name?: string | null
}

interface GraphLink {
  source: string
  target: string
  relation_type: string
  label?: string | null
  color?: string | null
}

type RenderNode = GraphNode & NodeObject & { degree: number }
type RenderLink = GraphLink & LinkObject<RenderNode>
type GraphInstance = ForceGraph3DInstance<RenderNode, RenderLink>
type ForceNode = RenderNode & { vx?: number; vy?: number; vz?: number }

const props = defineProps<{
  nodes: GraphNode[]
  links: GraphLink[]
  selectedId?: string | null
}>()

const emit = defineEmits<{ nodeSelect: [node: GraphNode | null] }>()
const containerRef = ref<HTMLElement | null>(null)
let graph: GraphInstance | null = null
let resizeObserver: ResizeObserver | null = null
let sphereGuide: THREE.Mesh | null = null
let haloGuide: THREE.Mesh | null = null
let sphereRadius = 170
let updateSequence = 0
let hoveredNodeId: string | null = null

function endpointId(value: string | RenderNode) {
  return typeof value === "string" ? value : value.id
}

function escapeHtml(value: string) {
  return value.replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[character] || character)
}

function createSphereForce(radius: number, strength = 0.11) {
  let nodes: ForceNode[] = []
  const force = (alpha: number) => {
    for (const node of nodes) {
      const x = node.x || 0.001
      const y = node.y || 0.001
      const z = node.z || 0.001
      const distance = Math.sqrt(x * x + y * y + z * z) || 1
      const pull = ((radius - distance) / distance) * strength * alpha
      node.vx = (node.vx || 0) + x * pull
      node.vy = (node.vy || 0) + y * pull
      node.vz = (node.vz || 0) + z * pull
    }
  }
  force.initialize = (nextNodes: ForceNode[]) => { nodes = nextNodes }
  return force
}

function createRenderData() {
  const degreeMap = new Map<string, number>()
  for (const link of props.links) {
    degreeMap.set(endpointId(link.source), (degreeMap.get(endpointId(link.source)) || 0) + 1)
    degreeMap.set(endpointId(link.target), (degreeMap.get(endpointId(link.target)) || 0) + 1)
  }

  const sortedNodes = [...props.nodes].sort((a, b) => a.entity_type.localeCompare(b.entity_type) || a.name.localeCompare(b.name))
  const goldenAngle = Math.PI * (3 - Math.sqrt(5))
  const nodes: RenderNode[] = sortedNodes.map((node, index) => {
    const y = 1 - ((index + 0.5) / Math.max(sortedNodes.length, 1)) * 2
    const radial = Math.sqrt(Math.max(0, 1 - y * y))
    const theta = goldenAngle * index
    return {
      ...node,
      degree: degreeMap.get(node.id) || 0,
      x: Math.cos(theta) * radial * sphereRadius,
      y: y * sphereRadius,
      z: Math.sin(theta) * radial * sphereRadius,
    }
  })

  const links: RenderLink[] = props.links.map((link) => ({
    ...link,
    source: endpointId(link.source),
    target: endpointId(link.target),
  }))
  return { nodes, links }
}

function disposeGuide(mesh: THREE.Mesh | null) {
  if (!mesh) return
  graph?.scene().remove(mesh)
  mesh.geometry.dispose()
  const material = mesh.material
  if (Array.isArray(material)) material.forEach((item) => item.dispose())
  else material.dispose()
}

function rebuildSphereGuide() {
  if (!graph) return
  disposeGuide(sphereGuide)
  disposeGuide(haloGuide)

  sphereGuide = new THREE.Mesh(
    new THREE.SphereGeometry(sphereRadius, 32, 20),
    new THREE.MeshBasicMaterial({
      color: 0x3a668a,
      wireframe: true,
      transparent: true,
      opacity: 0.075,
      depthWrite: false,
    }),
  )
  sphereGuide.renderOrder = -2

  haloGuide = new THREE.Mesh(
    new THREE.TorusGeometry(sphereRadius * 1.035, 0.35, 6, 96),
    new THREE.MeshBasicMaterial({ color: 0x00b8c8, transparent: true, opacity: 0.22, depthWrite: false }),
  )
  haloGuide.rotation.x = Math.PI / 2
  haloGuide.renderOrder = -1
  graph.scene().add(sphereGuide, haloGuide)
}

function nodeTooltip(node: RenderNode) {
  const type = escapeHtml(node.entity_type)
  return `<div class="nexus-tooltip"><strong>${escapeHtml(node.name)}</strong><span>${type} · ${node.degree} 条连接</span></div>`
}

function hashNumber(value: string) {
  let hash = 2166136261
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function starColor(node: RenderNode) {
  const color = new THREE.Color(node.color || "#00f0ff")
  const hsl = { h: 0, s: 0, l: 0 }
  color.getHSL(hsl)
  const hash = hashNumber(node.id)
  const hueShift = ((hash % 17) - 8) / 180
  const lightness = 0.46 + ((hash >>> 5) % 20) / 100
  color.setHSL((hsl.h + hueShift + 1) % 1, Math.min(1, Math.max(0.72, hsl.s)), lightness)
  return color
}

function coreGeometry(node: RenderNode, radius: number): THREE.BufferGeometry {
  if (node.entity_type === "source") return new THREE.OctahedronGeometry(radius, 0)
  if (node.entity_type === "faction") return new THREE.IcosahedronGeometry(radius, 0)
  if (node.entity_type === "location") return new THREE.BoxGeometry(radius * 1.45, radius * 1.45, radius * 1.45)
  if (node.entity_type === "item") return new THREE.TetrahedronGeometry(radius, 0)
  if (node.entity_type === "containment") return new THREE.DodecahedronGeometry(radius, 0)
  return new THREE.SphereGeometry(radius, 12, 10)
}

function createStarObject(node: RenderNode) {
  const selected = node.id === props.selectedId
  const radius = (1.8 + Math.min(Math.sqrt(node.degree), 3.2) * 0.48) * (selected ? 1.35 : 1)
  const color = starColor(node)
  const group = new THREE.Group()

  const corona = new THREE.Mesh(
    new THREE.SphereGeometry(radius * 1.65, 12, 10),
    new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: selected ? 0.24 : 0.12,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  )
  corona.renderOrder = 1

  const shell = new THREE.Mesh(
    coreGeometry(node, radius),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 }),
  )
  shell.renderOrder = 2

  const core = new THREE.Mesh(
    new THREE.SphereGeometry(Math.max(0.65, radius * 0.34), 10, 8),
    new THREE.MeshBasicMaterial({ color: selected ? 0xffffff : 0xeafcff }),
  )
  core.renderOrder = 3
  group.add(corona, shell, core)

  if (selected || node.entity_type === "source" || node.entity_type === "faction") {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(radius * 1.38, selected ? 0.13 : 0.08, 5, 28),
      new THREE.MeshBasicMaterial({
        color: selected ? 0xffffff : color,
        transparent: true,
        opacity: selected ? 0.9 : 0.55,
        depthWrite: false,
      }),
    )
    const rotation = (hashNumber(node.id) % 100) / 100 * Math.PI
    ring.rotation.set(rotation, rotation * 0.63, 0)
    ring.renderOrder = 4
    group.add(ring)
  }
  return group
}

function linkTouchesNode(link: RenderLink, nodeId: string) {
  return endpointId(link.source as string | RenderNode) === nodeId || endpointId(link.target as string | RenderNode) === nodeId
}

function linkDisplayColor(link: RenderLink) {
  const base = new THREE.Color(link.color || (link.relation_type === "appears_in" ? "#9d7cff" : "#4de8f2"))
  if (hoveredNodeId && !linkTouchesNode(link, hoveredNodeId)) base.multiplyScalar(0.24)
  return `#${base.getHexString()}`
}

function linkDisplayWidth(link: RenderLink) {
  const base = link.relation_type === "appears_in" ? 0.5 : 1.2
  if (!hoveredNodeId) return base
  return linkTouchesNode(link, hoveredNodeId) ? base * 2.35 : Math.max(0.12, base * 0.28)
}

function updateSelection() {
  if (!graph) return
  graph
    .nodeThreeObject(createStarObject)
    .nodeColor((node) => node.id === props.selectedId ? "#ffffff" : node.color || "#00f0ff")
    .nodeVal((node) => {
      const base = node.entity_type === "source" ? 3.8 : 5.2
      const degree = Math.min(node.degree, 10) * 0.75
      return node.id === props.selectedId ? base + degree + 8 : base + degree
    })
    .refresh()
}

function resetView(duration = 650) {
  const bounds = containerRef.value?.getBoundingClientRect()
  const aspect = bounds ? bounds.width / Math.max(bounds.height, 1) : 1
  const narrowScreenFactor = aspect < 1 ? 1 / aspect : 1
  graph?.cameraPosition(
    { x: 0, y: 0, z: sphereRadius * 2.85 * narrowScreenFactor },
    { x: 0, y: 0, z: 0 },
    duration,
  )
}

function focusNode(node: RenderNode) {
  if (!graph || node.x == null || node.y == null || node.z == null) return
  const distance = Math.hypot(node.x, node.y, node.z) || 1
  const offset = 72
  const ratio = 1 + offset / distance
  graph.cameraPosition(
    { x: node.x * ratio, y: node.y * ratio, z: node.z * ratio },
    { x: node.x, y: node.y, z: node.z },
    700,
  )
}

function zoomBy(factor: number) {
  if (!graph) return
  const position = graph.cameraPosition()
  graph.cameraPosition({ x: position.x * factor, y: position.y * factor, z: position.z * factor }, undefined, 220)
}

function updateGraphData() {
  if (!graph) return
  const sequence = ++updateSequence
  sphereRadius = Math.max(135, Math.min(225, 92 + Math.sqrt(Math.max(props.nodes.length, 1)) * 12))
  graph.pauseAnimation()
  rebuildSphereGuide()
  graph.graphData(createRenderData())
  window.setTimeout(() => {
    if (!graph || sequence !== updateSequence) return
    graph.d3Force("sphere", createSphereForce(sphereRadius))
    graph.d3Force("charge")?.strength(-78)
    graph.d3Force("link")?.distance((link: RenderLink) => link.relation_type === "appears_in" ? 48 : 72).strength(0.16)
    graph.d3ReheatSimulation()
    updateSelection()
    graph.resumeAnimation()
    window.setTimeout(() => {
      if (sequence === updateSequence) resetView(700)
    }, 500)
  }, 60)
}

async function initializeGraph() {
  await nextTick()
  const container = containerRef.value
  if (!container || graph) return
  const { default: ForceGraph3D } = await import("3d-force-graph")
  if (!containerRef.value) return
  const bounds = container.getBoundingClientRect()
  const instance = new ForceGraph3D<RenderNode, RenderLink>(container, {
    controlType: "orbit",
    rendererConfig: { antialias: true, alpha: true, powerPreference: "low-power" },
  })
  instance.pauseAnimation()
  graph = instance
    .width(Math.max(320, Math.floor(bounds.width)))
    .height(Math.max(480, Math.floor(bounds.height)))
    .backgroundColor("#08080d")
    .showNavInfo(false)
    .numDimensions(3)
    .nodeId("id")
    .nodeResolution(14)
    .nodeOpacity(0.92)
    .nodeThreeObject(createStarObject)
    .nodeThreeObjectExtend(false)
    .nodeLabel(nodeTooltip)
    .linkLabel((link) => escapeHtml(link.label || link.relation_type))
    .linkColor(linkDisplayColor)
    .linkOpacity(0.62)
    .linkWidth(linkDisplayWidth)
    .linkDirectionalArrowLength((link) => link.relation_type === "appears_in" ? 2.2 : 4.2)
    .linkDirectionalArrowColor(linkDisplayColor)
    .linkDirectionalArrowRelPos(0.7)
    .linkDirectionalParticles((link) => link.relation_type === "appears_in" ? 0 : 1)
    .linkDirectionalParticleColor(linkDisplayColor)
    .linkDirectionalParticleWidth((link) => link.relation_type === "appears_in" ? 0.8 : 1.45)
    .linkDirectionalParticleSpeed((link) => link.relation_type === "appears_in" ? 0.0022 : 0.004)
    .warmupTicks(40)
    .cooldownTime(8000)
    .onNodeClick((node) => {
      emit("nodeSelect", { ...node })
      focusNode(node)
    })
    .onNodeHover((node) => {
      hoveredNodeId = node?.id || null
      graph?.linkColor(linkDisplayColor).linkWidth(linkDisplayWidth).refresh()
    })
    .onBackgroundClick(() => emit("nodeSelect", null))

  const controls = graph.controls() as { autoRotate?: boolean; autoRotateSpeed?: number; enableDamping?: boolean; dampingFactor?: number }
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.32
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  graph.renderer().setPixelRatio(Math.min(window.devicePixelRatio, 1.5))

  resizeObserver = new ResizeObserver(([entry]) => {
    if (!graph || !entry) return
    graph.width(Math.max(320, Math.floor(entry.contentRect.width))).height(Math.max(480, Math.floor(entry.contentRect.height)))
  })
  resizeObserver.observe(container)
  updateGraphData()
}

defineExpose({
  zoomIn: () => zoomBy(0.78),
  zoomOut: () => zoomBy(1.28),
  resetView,
  reheat: () => {
    resetView(450)
    graph?.d3ReheatSimulation()
  },
})

watch(() => [props.nodes, props.links], updateGraphData, { deep: true })
watch(() => props.selectedId, updateSelection)

onMounted(initializeGraph)

onBeforeUnmount(() => {
  updateSequence += 1
  resizeObserver?.disconnect()
  disposeGuide(sphereGuide)
  disposeGuide(haloGuide)
  graph?._destructor()
  graph = null
})
</script>

<style scoped>
.graph-root {
  position: relative;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 480px;
  overflow: hidden;
  background: #08080d;
}

.graph-root :deep(canvas) {
  display: block;
  outline: none;
}

.graph-root :deep(.scene-tooltip) {
  z-index: 6;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-text-primary);
  pointer-events: none;
}

.graph-root :deep(.nexus-tooltip) {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-width: 240px;
  padding: 7px 9px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: rgba(18, 18, 26, 0.96);
  box-shadow: var(--shadow-md);
}

.graph-root :deep(.nexus-tooltip strong) {
  overflow-wrap: anywhere;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.graph-root :deep(.nexus-tooltip span) {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}
</style>
