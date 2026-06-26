import { _ as __nuxt_component_0 } from './nuxt-link-CD-PFrnI.mjs';
import { defineComponent, resolveComponent, mergeProps, createVNode, resolveDynamicComponent, withCtx, createTextVNode, openBlock, createBlock, toDisplayString, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderList, ssrRenderStyle, ssrRenderVNode, ssrInterpolate, ssrRenderComponent } from 'vue/server-renderer';
import { Users, Building2, Package, Share2, Calendar, AlertTriangle, BookOpen, Network, History } from 'lucide-vue-next';
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

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const stats = [
      { icon: Users, value: 0, label: "人物", color: "var(--color-accent-cyan)" },
      { icon: Building2, value: 0, label: "势力", color: "var(--color-accent-magenta)" },
      { icon: Package, value: 0, label: "物品", color: "var(--color-accent-yellow)" },
      { icon: Share2, value: 0, label: "关系", color: "var(--color-accent-purple)" },
      { icon: Calendar, value: 0, label: "事件", color: "var(--color-accent-green)" },
      { icon: AlertTriangle, value: 0, label: "冲突", color: "var(--color-danger)" }
    ];
    const quickActions = [
      { to: "/lore", title: "浏览设定库", desc: "查看所有世界观设定", icon: BookOpen, color: "var(--color-accent-cyan)" },
      { to: "/nexus", title: "探索星图", desc: "查看实体关系图谱", icon: Network, color: "var(--color-accent-purple)" },
      { to: "/chronicle", title: "编年史轨道", desc: "查看时间轴事件", icon: History, color: "var(--color-accent-yellow)" }
    ];
    return (_ctx, _push, _parent, _attrs) => {
      const _component_ClockIcon = resolveComponent("ClockIcon");
      const _component_FileTextIcon = resolveComponent("FileTextIcon");
      const _component_NuxtLink = __nuxt_component_0;
      const _component_ZapIcon = resolveComponent("ZapIcon");
      const _component_ChevronRightIcon = resolveComponent("ChevronRightIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "dashboard" }, _attrs))} data-v-25baa8fb><header class="page-header" data-v-25baa8fb><div data-v-25baa8fb><h1 class="page-title" data-v-25baa8fb>Dashboard</h1><p class="page-description" data-v-25baa8fb>世界观总览 · 快速了解你的宇宙全景</p></div></header><div class="stats-grid" data-v-25baa8fb><!--[-->`);
      ssrRenderList(stats, (stat) => {
        _push(`<div class="stat-card" style="${ssrRenderStyle({ "--stat-color": stat.color })}" data-v-25baa8fb><div class="stat-icon-wrapper" data-v-25baa8fb>`);
        ssrRenderVNode(_push, createVNode(resolveDynamicComponent(stat.icon), {
          size: 20,
          "aria-hidden": "true"
        }, null), _parent);
        _push(`</div><div class="stat-info" data-v-25baa8fb><span class="stat-value" data-v-25baa8fb>${ssrInterpolate(stat.value)}</span><span class="stat-label" data-v-25baa8fb>${ssrInterpolate(stat.label)}</span></div></div>`);
      });
      _push(`<!--]--></div><div class="panels-grid" data-v-25baa8fb><section class="panel" data-v-25baa8fb><div class="panel-header" data-v-25baa8fb>`);
      _push(ssrRenderComponent(_component_ClockIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h2 class="panel-title" data-v-25baa8fb>最近的变更</h2></div><div class="panel-body" data-v-25baa8fb><div class="empty-state" data-v-25baa8fb>`);
      _push(ssrRenderComponent(_component_FileTextIcon, {
        size: 40,
        class: "empty-icon",
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<p class="empty-text" data-v-25baa8fb>还没有任何设定</p><p class="empty-hint" data-v-25baa8fb>前往 `);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/lore",
        class: "link"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(`Lore`);
          } else {
            return [
              createTextVNode("Lore")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(` 开始创建你的第一个世界</p></div></div></section><section class="panel" data-v-25baa8fb><div class="panel-header" data-v-25baa8fb>`);
      _push(ssrRenderComponent(_component_ZapIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h2 class="panel-title" data-v-25baa8fb>快速操作</h2></div><div class="panel-body" data-v-25baa8fb><div class="quick-actions" data-v-25baa8fb><!--[-->`);
      ssrRenderList(quickActions, (action) => {
        _push(ssrRenderComponent(_component_NuxtLink, {
          key: action.to,
          to: action.to,
          class: "action-card"
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              ssrRenderVNode(_push2, createVNode(resolveDynamicComponent(action.icon), {
                size: 18,
                class: "action-icon",
                "aria-hidden": "true",
                style: { color: action.color }
              }, null), _parent2, _scopeId);
              _push2(`<div class="action-info" data-v-25baa8fb${_scopeId}><span class="action-title" data-v-25baa8fb${_scopeId}>${ssrInterpolate(action.title)}</span><span class="action-desc" data-v-25baa8fb${_scopeId}>${ssrInterpolate(action.desc)}</span></div>`);
              _push2(ssrRenderComponent(_component_ChevronRightIcon, {
                size: 14,
                class: "action-chevron",
                "aria-hidden": "true"
              }, null, _parent2, _scopeId));
            } else {
              return [
                (openBlock(), createBlock(resolveDynamicComponent(action.icon), {
                  size: 18,
                  class: "action-icon",
                  "aria-hidden": "true",
                  style: { color: action.color }
                }, null, 8, ["style"])),
                createVNode("div", { class: "action-info" }, [
                  createVNode("span", { class: "action-title" }, toDisplayString(action.title), 1),
                  createVNode("span", { class: "action-desc" }, toDisplayString(action.desc), 1)
                ]),
                createVNode(_component_ChevronRightIcon, {
                  size: 14,
                  class: "action-chevron",
                  "aria-hidden": "true"
                })
              ];
            }
          }),
          _: 2
        }, _parent));
      });
      _push(`<!--]--></div></div></section></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-25baa8fb"]]);

export { index as default };
//# sourceMappingURL=index-rMx7oj5y.mjs.map
