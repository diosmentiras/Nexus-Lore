import { _ as __nuxt_component_0 } from './nuxt-link-CD-PFrnI.mjs';
import { defineComponent, resolveComponent, mergeProps, withCtx, createVNode, resolveDynamicComponent, openBlock, createBlock, toDisplayString, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderList, ssrRenderComponent, ssrRenderVNode, ssrInterpolate, ssrRenderSlot } from 'vue/server-renderer';
import { useRoute } from 'vue-router';
import { LayoutDashboard, BookOpen, Network, History, SearchCheck } from 'lucide-vue-next';
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

const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "default",
  __ssrInlineRender: true,
  setup(__props) {
    const route = useRoute();
    const navItems = [
      { to: "/", label: "Dashboard", icon: LayoutDashboard },
      { to: "/lore", label: "Lore", icon: BookOpen },
      { to: "/nexus", label: "Nexus", icon: Network },
      { to: "/chronicle", label: "Chronicle", icon: History },
      { to: "/linter", label: "Linter", icon: SearchCheck }
    ];
    function isActive(path) {
      if (path === "/") return route.path === "/";
      return route.path.startsWith(path);
    }
    return (_ctx, _push, _parent, _attrs) => {
      const _component_NuxtLink = __nuxt_component_0;
      const _component_SettingsIcon = resolveComponent("SettingsIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "nexus-layout" }, _attrs))} data-v-2bb6143d><aside class="sidebar" data-v-2bb6143d><div class="sidebar-brand" data-v-2bb6143d><div class="brand-icon-circle" data-v-2bb6143d><svg class="brand-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" data-v-2bb6143d><circle cx="12" cy="12" r="10" data-v-2bb6143d></circle><circle cx="12" cy="12" r="6" data-v-2bb6143d></circle><circle cx="12" cy="12" r="2" data-v-2bb6143d></circle><line x1="2" y1="12" x2="6" y2="12" data-v-2bb6143d></line><line x1="18" y1="12" x2="22" y2="12" data-v-2bb6143d></line><line x1="12" y1="2" x2="12" y2="6" data-v-2bb6143d></line><line x1="12" y1="18" x2="12" y2="22" data-v-2bb6143d></line></svg></div><div class="brand-text" data-v-2bb6143d><span class="brand-name" data-v-2bb6143d>Nexus</span><span class="brand-sub" data-v-2bb6143d>Lore</span></div></div><nav class="sidebar-nav" role="navigation" aria-label="主导航" data-v-2bb6143d><!--[-->`);
      ssrRenderList(navItems, (item) => {
        _push(ssrRenderComponent(_component_NuxtLink, {
          key: item.to,
          to: item.to,
          class: ["nav-item", { active: isActive(item.to) }],
          "aria-label": item.label
        }, {
          default: withCtx((_, _push2, _parent2, _scopeId) => {
            if (_push2) {
              ssrRenderVNode(_push2, createVNode(resolveDynamicComponent(item.icon), {
                class: "nav-icon",
                size: 18,
                "aria-hidden": "true"
              }, null), _parent2, _scopeId);
              _push2(`<span class="nav-label" data-v-2bb6143d${_scopeId}>${ssrInterpolate(item.label)}</span>`);
            } else {
              return [
                (openBlock(), createBlock(resolveDynamicComponent(item.icon), {
                  class: "nav-icon",
                  size: 18,
                  "aria-hidden": "true"
                })),
                createVNode("span", { class: "nav-label" }, toDisplayString(item.label), 1)
              ];
            }
          }),
          _: 2
        }, _parent));
      });
      _push(`<!--]--></nav><div class="sidebar-footer" data-v-2bb6143d>`);
      _push(ssrRenderComponent(_component_NuxtLink, {
        to: "/settings",
        class: ["nav-item", { active: isActive("/settings") }],
        "aria-label": "设置"
      }, {
        default: withCtx((_, _push2, _parent2, _scopeId) => {
          if (_push2) {
            _push2(ssrRenderComponent(_component_SettingsIcon, {
              class: "nav-icon",
              size: 18,
              "aria-hidden": "true"
            }, null, _parent2, _scopeId));
            _push2(`<span class="nav-label" data-v-2bb6143d${_scopeId}>Settings</span>`);
          } else {
            return [
              createVNode(_component_SettingsIcon, {
                class: "nav-icon",
                size: 18,
                "aria-hidden": "true"
              }),
              createVNode("span", { class: "nav-label" }, "Settings")
            ];
          }
        }),
        _: 1
      }, _parent));
      _push(`</div></aside><main class="main-content" role="main" data-v-2bb6143d>`);
      ssrRenderSlot(_ctx.$slots, "default", {}, null, _push, _parent);
      _push(`</main></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("layouts/default.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const _default = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-2bb6143d"]]);

export { _default as default };
//# sourceMappingURL=default-BYylNG1D.mjs.map
