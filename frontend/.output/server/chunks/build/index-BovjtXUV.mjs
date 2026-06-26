import { defineComponent, ref, computed, resolveComponent, mergeProps, watchEffect, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderList, ssrRenderAttr, ssrInterpolate, ssrRenderClass, ssrRenderComponent } from 'vue/server-renderer';
import * as d3 from 'd3';
import { _ as _export_sfc } from './server.mjs';
import '../_/nitro.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'vue-router';

const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "EntityRelationGraph",
  __ssrInlineRender: true,
  props: {
    nodes: {},
    links: {}
  },
  emits: ["nodeClick"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const svgContainer = ref(null);
    watchEffect(() => {
      if (!svgContainer.value) return;
      renderGraph();
    });
    function renderGraph() {
      const container = svgContainer.value;
      const width = container.clientWidth || 800;
      const height = container.clientHeight || 500;
      container.innerHTML = "";
      const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
      const defs = svg.append("defs");
      const filter = defs.append("filter").attr("id", "glow");
      filter.append("feGaussianBlur").attr("stdDeviation", 3).attr("result", "blur");
      const merge = filter.append("feMerge");
      merge.append("feMergeNode").attr("in", "blur");
      merge.append("feMergeNode").attr("in", "SourceGraphic");
      svg.append("pattern").attr("id", "grid").attr("width", 40).attr("height", 40).attr("patternUnits", "userSpaceOnUse").append("path").attr("d", "M 40 0 L 0 0 0 40").attr("fill", "none").attr("stroke", "rgba(42,42,74,0.3)").attr("stroke-width", 0.5);
      svg.append("rect").attr("width", "100%").attr("height", "100%").attr("fill", "url(#grid)");
      defs.append("marker").attr("id", "arrow").attr("viewBox", "0 0 10 10").attr("refX", 20).attr("refY", 5).attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto").append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("fill", "#3a3a5a");
      const simulation = d3.forceSimulation(props.nodes).force("link", d3.forceLink(props.links).id((d) => d.id).distance(140)).force("charge", d3.forceManyBody().strength(-350)).force("center", d3.forceCenter(width / 2, height / 2)).force("collision", d3.forceCollide(30));
      const link = svg.append("g").selectAll("line").data(props.links).join("line").attr("stroke", (d) => d.color || "#2a2a4a").attr("stroke-width", 1.5).attr("stroke-opacity", 0.5).attr("marker-end", "url(#arrow)");
      const linkLabel = svg.append("g").selectAll("text").data(props.links).join("text").text((d) => d.relation || "").attr("font-size", 10).attr("fill", "#555577").attr("text-anchor", "middle");
      const nodeGroup = svg.append("g").selectAll("g").data(props.nodes).join("g").style("cursor", "pointer").call(
        d3.drag().on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        }).on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        }).on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );
      nodeGroup.append("circle").attr("r", (d) => d.size || 8).attr("fill", (d) => d.color || "var(--color-accent-cyan)").attr("filter", "url(#glow)").attr("stroke", (d) => d.color || "var(--color-accent-cyan)").attr("stroke-width", 2).attr("stroke-opacity", 0.3);
      nodeGroup.append("text").text((d) => d.name).attr("font-size", 11).attr("font-family", "var(--font-sans)").attr("fill", "#8888aa").attr("dx", 14).attr("dy", 4);
      nodeGroup.on("click", (event, d) => {
        emit("nodeClick", d);
      });
      nodeGroup.on("mouseenter", function() {
        d3.select(this).select("circle").attr("stroke-opacity", 1).attr("r", (d) => (d.size || 8) + 3);
      }).on("mouseleave", function() {
        d3.select(this).select("circle").attr("stroke-opacity", 0.3).attr("r", (d) => d.size || 8);
      });
      simulation.on("tick", () => {
        link.attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y).attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y);
        linkLabel.attr("x", (d) => (d.source.x + d.target.x) / 2).attr("y", (d) => (d.source.y + d.target.y) / 2 - 6);
        nodeGroup.attr("transform", (d) => `translate(${d.x},${d.y})`);
      });
    }
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        ref_key: "svgContainer",
        ref: svgContainer,
        class: "graph-container"
      }, _attrs))} data-v-2f3e5616></div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/EntityRelationGraph.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const __nuxt_component_0 = /* @__PURE__ */ Object.assign(_export_sfc(_sfc_main$1, [["__scopeId", "data-v-2f3e5616"]]), { __name: "EntityRelationGraph" });
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const factionFilter = ref("");
    const relationFilter = ref("");
    const tagFilter = ref("");
    const timeStart = ref(null);
    const timeEnd = ref(null);
    const factions = ref([]);
    const nodes = ref([]);
    const links = ref([]);
    const relationOptions = [
      { value: "", label: "全部" },
      { value: "ally", label: "盟友" },
      { value: "hostile", label: "敌对" },
      { value: "neutral", label: "中立" }
    ];
    const filteredNodes = computed(() => nodes.value);
    const filteredLinks = computed(() => links.value);
    function onNodeClick(node) {
      navigateTo("/lore/" + node.id);
    }
    return (_ctx, _push, _parent, _attrs) => {
      const _component_SearchIcon = resolveComponent("SearchIcon");
      const _component_EntityRelationGraph = __nuxt_component_0;
      const _component_NetworkIcon = resolveComponent("NetworkIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "nexus-page" }, _attrs))} data-v-329af2cd><header class="page-header" data-v-329af2cd><div data-v-329af2cd><h1 class="page-title" data-v-329af2cd>Nexus</h1><p class="page-description" data-v-329af2cd>动态拓扑星图 · 实体关系可视化</p></div></header><div class="filter-bar" data-v-329af2cd><div class="filter-group" data-v-329af2cd><label class="filter-label" data-v-329af2cd>阵营</label><select class="filter-select" data-v-329af2cd><option value="" data-v-329af2cd${ssrIncludeBooleanAttr(Array.isArray(factionFilter.value) ? ssrLooseContain(factionFilter.value, "") : ssrLooseEqual(factionFilter.value, "")) ? " selected" : ""}>全部</option><!--[-->`);
      ssrRenderList(factions.value, (f) => {
        _push(`<option${ssrRenderAttr("value", f)} data-v-329af2cd${ssrIncludeBooleanAttr(Array.isArray(factionFilter.value) ? ssrLooseContain(factionFilter.value, f) : ssrLooseEqual(factionFilter.value, f)) ? " selected" : ""}>${ssrInterpolate(f)}</option>`);
      });
      _push(`<!--]--></select></div><div class="filter-group" data-v-329af2cd><label class="filter-label" data-v-329af2cd>关系</label><div class="segmented-control" data-v-329af2cd><!--[-->`);
      ssrRenderList(relationOptions, (opt) => {
        _push(`<button class="${ssrRenderClass([{ active: relationFilter.value === opt.value }, "seg-btn"])}" data-v-329af2cd>${ssrInterpolate(opt.label)}</button>`);
      });
      _push(`<!--]--></div></div><div class="filter-group" data-v-329af2cd><label class="filter-label" data-v-329af2cd>标签</label><div class="search-wrapper" data-v-329af2cd>`);
      _push(ssrRenderComponent(_component_SearchIcon, {
        size: 14,
        class: "search-icon",
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<input${ssrRenderAttr("value", tagFilter.value)} class="filter-input" placeholder="筛选..." data-v-329af2cd></div></div><div class="filter-group" data-v-329af2cd><label class="filter-label" data-v-329af2cd>时间跨度</label><div class="time-range" data-v-329af2cd><input${ssrRenderAttr("value", timeStart.value)} type="number" class="time-input" placeholder="从" data-v-329af2cd><span class="range-sep" data-v-329af2cd>—</span><input${ssrRenderAttr("value", timeEnd.value)} type="number" class="time-input" placeholder="到" data-v-329af2cd></div></div></div><div class="graph-container" data-v-329af2cd>`);
      _push(ssrRenderComponent(_component_EntityRelationGraph, {
        nodes: filteredNodes.value,
        links: filteredLinks.value,
        onNodeClick
      }, null, _parent));
      if (!nodes.value.length) {
        _push(`<div class="graph-empty" data-v-329af2cd>`);
        _push(ssrRenderComponent(_component_NetworkIcon, {
          size: 40,
          class: "empty-icon",
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<p data-v-329af2cd>添加设定后星图将自动生成</p></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/nexus/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-329af2cd"]]);

export { index as default };
//# sourceMappingURL=index-BovjtXUV.mjs.map
