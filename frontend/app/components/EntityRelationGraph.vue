<template>
  <div ref="svgContainer" class="graph-container"></div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from "vue"
import * as d3 from "d3"

const props = defineProps<{
  nodes: any[]
  links: any[]
}>()

const emit = defineEmits<{ nodeClick: [node: any] }>()
const svgContainer = ref<HTMLElement | null>(null)

watchEffect(() => {
  if (!svgContainer.value) return
  renderGraph()
})

function renderGraph() {
  const container = svgContainer.value!
  const width = container.clientWidth || 800
  const height = container.clientHeight || 500

  container.innerHTML = ""

  const svg = d3.select(container).append("svg").attr("width", width).attr("height", height)

  // Glow filter
  const defs = svg.append("defs")
  const filter = defs.append("filter").attr("id", "glow")
  filter.append("feGaussianBlur").attr("stdDeviation", 3).attr("result", "blur")
  const merge = filter.append("feMerge")
  merge.append("feMergeNode").attr("in", "blur")
  merge.append("feMergeNode").attr("in", "SourceGraphic")

  // Background grid
  svg.append("pattern").attr("id", "grid").attr("width", 40).attr("height", 40).attr("patternUnits", "userSpaceOnUse")
    .append("path").attr("d", "M 40 0 L 0 0 0 40").attr("fill", "none").attr("stroke", "rgba(42,42,74,0.3)").attr("stroke-width", 0.5)
  svg.append("rect").attr("width", "100%").attr("height", "100%").attr("fill", "url(#grid)")

  // Arrows
  defs.append("marker").attr("id", "arrow").attr("viewBox", "0 0 10 10").attr("refX", 20).attr("refY", 5).attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto")
    .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("fill", "#3a3a5a")

  const simulation = d3
    .forceSimulation(props.nodes)
    .force("link", d3.forceLink(props.links).id((d: any) => d.id).distance(140))
    .force("charge", d3.forceManyBody().strength(-350))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(30))

  // Links
  const link = svg
    .append("g")
    .selectAll("line")
    .data(props.links)
    .join("line")
    .attr("stroke", (d: any) => d.color || "#2a2a4a")
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.5)
    .attr("marker-end", "url(#arrow)")

  // Link labels
  const linkLabel = svg
    .append("g")
    .selectAll("text")
    .data(props.links)
    .join("text")
    .text((d: any) => d.relation || "")
    .attr("font-size", 10)
    .attr("fill", "#555577")
    .attr("text-anchor", "middle")

  // Nodes
  const nodeGroup = svg
    .append("g")
    .selectAll("g")
    .data(props.nodes)
    .join("g")
    .style("cursor", "pointer")
    .call(
      d3
        .drag<any, any>()
        .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y })
        .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )

  nodeGroup
    .append("circle")
    .attr("r", (d: any) => d.size || 8)
    .attr("fill", (d: any) => d.color || "var(--color-accent-cyan)")
    .attr("filter", "url(#glow)")
    .attr("stroke", (d: any) => d.color || "var(--color-accent-cyan)")
    .attr("stroke-width", 2)
    .attr("stroke-opacity", 0.3)

  nodeGroup
    .append("text")
    .text((d: any) => d.name)
    .attr("font-size", 11)
    .attr("font-family", "var(--font-sans)")
    .attr("fill", "#8888aa")
    .attr("dx", 14)
    .attr("dy", 4)

  nodeGroup.on("click", (event: any, d: any) => {
    emit("nodeClick", d)
  })

  nodeGroup
    .on("mouseenter", function (this: any) {
      d3.select(this).select("circle").attr("stroke-opacity", 1).attr("r", (d: any) => (d.size || 8) + 3)
    })
    .on("mouseleave", function (this: any) {
      d3.select(this).select("circle").attr("stroke-opacity", 0.3).attr("r", (d: any) => d.size || 8)
    })

  simulation.on("tick", () => {
    link.attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y).attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y)
    linkLabel.attr("x", (d: any) => (d.source.x + d.target.x) / 2).attr("y", (d: any) => (d.source.y + d.target.y) / 2 - 6)
    nodeGroup.attr("transform", (d: any) => `translate(${d.x},${d.y})`)
  })
}
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>
