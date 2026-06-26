<template>
  <div ref="svgContainer" class="graph-container"></div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'

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

  container.innerHTML = ''

  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  const defs = svg.append('defs')

  // 霓虹发光滤镜
  const filter = defs.append('filter').attr('id', 'glow')
  filter.append('feGaussianBlur').attr('stdDeviation', 3).attr('result', 'blur')
  const merge = filter.append('feMerge')
  merge.append('feMergeNode').attr('in', 'blur')
  merge.append('feMergeNode').attr('in', 'SourceGraphic')

  const simulation = d3.forceSimulation(props.nodes)
    .force('link', d3.forceLink(props.links).id((d: any) => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))

  const link = svg.append('g')
    .selectAll('line')
    .data(props.links)
    .join('line')
    .attr('stroke', (d: any) => d.color || '#2a2a4a')
    .attr('stroke-width', 1.5)
    .attr('stroke-opacity', 0.6)

  const node = svg.append('g')
    .selectAll('circle')
    .data(props.nodes)
    .join('circle')
    .attr('r', 10)
    .attr('fill', (d: any) => d.color || '#00f0ff')
    .attr('filter', 'url(#glow)')
    .style('cursor', 'pointer')
    .call(d3.drag<any, any>()
      .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
      .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )

  const label = svg.append('g')
    .selectAll('text')
    .data(props.nodes)
    .join('text')
    .text((d: any) => d.name)
    .attr('font-size', 11)
    .attr('fill', '#8888aa')
    .attr('dx', 14)
    .attr('dy', 4)

  node.on('click', (event: any, d: any) => {
    emit('nodeClick', d)
  })

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)

    node
      .attr('cx', (d: any) => d.x)
      .attr('cy', (d: any) => d.y)

    label
      .attr('x', (d: any) => d.x)
      .attr('y', (d: any) => d.y)
  })
}
</script>

<style scoped>
.graph-container { width: 100%; height: 100%; }
</style>
