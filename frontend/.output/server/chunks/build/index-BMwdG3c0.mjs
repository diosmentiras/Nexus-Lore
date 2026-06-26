import { defineComponent, ref, computed, resolveComponent, mergeProps, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrIncludeBooleanAttr, ssrRenderComponent, ssrInterpolate, ssrRenderAttr, ssrRenderList, ssrRenderStyle } from 'vue/server-renderer';
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

const PADDING = 100;
const BASE_SPACING = 80;
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "TimelineTrack",
  __ssrInlineRender: true,
  props: {
    events: {},
    zoom: {}
  },
  emits: ["eventClick"],
  setup(__props) {
    const props = __props;
    const sortedEvents = computed(() => [...props.events].sort((a, b) => parseInt(a.date) - parseInt(b.date)));
    const ticks = computed(() => {
      if (!sortedEvents.value.length) return [];
      const min = parseInt(sortedEvents.value[0].date);
      const max = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date);
      const step = Math.max(1, Math.floor((max - min) / 8));
      const years = [];
      for (let y = min; y <= max; y += step) years.push(y);
      if (years[years.length - 1] !== max) years.push(max);
      const tw = trackWidth.value;
      const span = Math.max(max - min, 1);
      return years.map((year) => ({
        year,
        x: PADDING + (year - min) / span * (tw - PADDING * 2)
      }));
    });
    const trackWidth = computed(() => {
      if (!sortedEvents.value.length) return 800;
      const minYear = parseInt(sortedEvents.value[0].date);
      const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date);
      const span = Math.max(maxYear - minYear, 1);
      return span * BASE_SPACING * props.zoom + PADDING * 2;
    });
    function positionX(event) {
      if (!sortedEvents.value.length) return PADDING;
      const minYear = parseInt(sortedEvents.value[0].date);
      const maxYear = parseInt(sortedEvents.value[sortedEvents.value.length - 1].date);
      const span = Math.max(maxYear - minYear, 1);
      const year = parseInt(event.date);
      return PADDING + (year - minYear) / span * (trackWidth.value - PADDING * 2);
    }
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: "timeline-track",
        style: { width: trackWidth.value + "px" }
      }, _attrs))} data-v-5cc35c5e><div class="timeline-base" data-v-5cc35c5e></div><!--[-->`);
      ssrRenderList(ticks.value, (tick) => {
        _push(`<div class="tick" style="${ssrRenderStyle({ left: tick.x + "px" })}" data-v-5cc35c5e><div class="tick-line" data-v-5cc35c5e></div><span class="tick-label" data-v-5cc35c5e>${ssrInterpolate(tick.year)}</span></div>`);
      });
      _push(`<!--]--><!--[-->`);
      ssrRenderList(sortedEvents.value, (event) => {
        _push(`<div class="event-marker" style="${ssrRenderStyle({ left: positionX(event) + "px" })}" role="button"${ssrRenderAttr("tabindex", 0)} data-v-5cc35c5e><div class="marker-dot" data-v-5cc35c5e><div class="marker-pulse" data-v-5cc35c5e></div></div><div class="event-card" data-v-5cc35c5e><span class="event-date" data-v-5cc35c5e>${ssrInterpolate(event.date)}</span><span class="event-title" data-v-5cc35c5e>${ssrInterpolate(event.title)}</span>`);
        if (event.description) {
          _push(`<span class="event-desc" data-v-5cc35c5e>${ssrInterpolate(event.description)}</span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`</div></div>`);
      });
      _push(`<!--]--></div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/TimelineTrack.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const __nuxt_component_0 = /* @__PURE__ */ Object.assign(_export_sfc(_sfc_main$1, [["__scopeId", "data-v-5cc35c5e"]]), { __name: "TimelineTrack" });
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const zoom = ref(1);
    const rangeStart = ref(null);
    const rangeEnd = ref(null);
    ref(null);
    const events = ref([]);
    const filteredEvents = computed(() => {
      return events.value.filter((e) => {
        const year = parseInt(e.date);
        if (rangeStart.value && year < rangeStart.value) return false;
        if (rangeEnd.value && year > rangeEnd.value) return false;
        return true;
      });
    });
    function onEventClick(event) {
      navigateTo("/lore/" + event.id);
    }
    return (_ctx, _push, _parent, _attrs) => {
      const _component_ZoomInIcon = resolveComponent("ZoomInIcon");
      const _component_ZoomOutIcon = resolveComponent("ZoomOutIcon");
      const _component_RotateCcwIcon = resolveComponent("RotateCcwIcon");
      const _component_CalendarIcon = resolveComponent("CalendarIcon");
      const _component_TimelineTrack = __nuxt_component_0;
      const _component_TimelineIcon = resolveComponent("TimelineIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "chronicle-page" }, _attrs))} data-v-93d3df12><header class="page-header" data-v-93d3df12><div data-v-93d3df12><h1 class="page-title" data-v-93d3df12>Chronicle</h1><p class="page-description" data-v-93d3df12>编年史轨道 · 事件时间轴</p></div></header><div class="controls" data-v-93d3df12><div class="zoom-controls" data-v-93d3df12><button class="btn btn-icon"${ssrIncludeBooleanAttr(zoom.value >= 5) ? " disabled" : ""} aria-label="放大" data-v-93d3df12>`);
      _push(ssrRenderComponent(_component_ZoomInIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`</button><span class="zoom-level" data-v-93d3df12>${ssrInterpolate(Math.round(zoom.value * 100))}%</span><button class="btn btn-icon"${ssrIncludeBooleanAttr(zoom.value <= 0.2) ? " disabled" : ""} aria-label="缩小" data-v-93d3df12>`);
      _push(ssrRenderComponent(_component_ZoomOutIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`</button><button class="btn btn-icon" aria-label="重置缩放" data-v-93d3df12>`);
      _push(ssrRenderComponent(_component_RotateCcwIcon, {
        size: 14,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`</button></div><div class="year-range" data-v-93d3df12>`);
      _push(ssrRenderComponent(_component_CalendarIcon, {
        size: 14,
        class: "year-icon",
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<input${ssrRenderAttr("value", rangeStart.value)} type="number" class="year-input" placeholder="起始年" data-v-93d3df12><span class="range-sep" data-v-93d3df12>→</span><input${ssrRenderAttr("value", rangeEnd.value)} type="number" class="year-input" placeholder="结束年" data-v-93d3df12></div></div><div class="timeline-container" data-v-93d3df12>`);
      _push(ssrRenderComponent(_component_TimelineTrack, {
        events: filteredEvents.value,
        zoom: zoom.value,
        onEventClick
      }, null, _parent));
      if (!events.value.length) {
        _push(`<div class="timeline-empty" data-v-93d3df12>`);
        _push(ssrRenderComponent(_component_TimelineIcon, {
          size: 40,
          class: "empty-icon",
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<p data-v-93d3df12>添加带时间戳的事件后轨道将自动编织</p></div>`);
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
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/chronicle/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-93d3df12"]]);

export { index as default };
//# sourceMappingURL=index-BMwdG3c0.mjs.map
