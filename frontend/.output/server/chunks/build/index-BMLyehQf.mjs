import { defineComponent, ref, resolveComponent, mergeProps, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrIncludeBooleanAttr, ssrRenderComponent, ssrInterpolate, ssrRenderList, ssrRenderClass } from 'vue/server-renderer';
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
    const linting = ref(false);
    const issues = ref([]);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_RefreshCwIcon = resolveComponent("RefreshCwIcon");
      const _component_SearchCheckIcon = resolveComponent("SearchCheckIcon");
      const _component_ShieldCheckIcon = resolveComponent("ShieldCheckIcon");
      const _component_AlertCircleIcon = resolveComponent("AlertCircleIcon");
      const _component_AlertTriangleIcon = resolveComponent("AlertTriangleIcon");
      const _component_ArrowRightIcon = resolveComponent("ArrowRightIcon");
      const _component_ChevronRightIcon = resolveComponent("ChevronRightIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "linter-page" }, _attrs))} data-v-baf0255f><header class="page-header" data-v-baf0255f><div data-v-baf0255f><h1 class="page-title" data-v-baf0255f>Linter</h1><p class="page-description" data-v-baf0255f>设定冲突检查器 · 自动检测逻辑漏洞</p></div><button class="btn btn-primary"${ssrIncludeBooleanAttr(linting.value) ? " disabled" : ""} data-v-baf0255f>`);
      if (linting.value) {
        _push(ssrRenderComponent(_component_RefreshCwIcon, {
          size: 16,
          class: "spin",
          "aria-hidden": "true"
        }, null, _parent));
      } else {
        _push(ssrRenderComponent(_component_SearchCheckIcon, {
          size: 16,
          "aria-hidden": "true"
        }, null, _parent));
      }
      _push(`<span data-v-baf0255f>${ssrInterpolate(linting.value ? "分析中..." : "运行检查")}</span></button></header>`);
      if (linting.value) {
        _push(`<div class="linting-status" data-v-baf0255f><div class="spinner" data-v-baf0255f></div><div class="linting-text" data-v-baf0255f><p class="linting-title" data-v-baf0255f>正在分析设定逻辑...</p><p class="linting-desc" data-v-baf0255f>检查时间线一致性、实体关系和事件冲突</p></div></div>`);
      } else if (!issues.value.length) {
        _push(`<div class="empty-state" data-v-baf0255f>`);
        _push(ssrRenderComponent(_component_ShieldCheckIcon, {
          size: 48,
          class: "empty-icon success-icon",
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<p class="empty-title" data-v-baf0255f>世界观逻辑一致</p><p class="empty-desc" data-v-baf0255f>尚未发现设定冲突，点击「运行检查」进行验证</p></div>`);
      } else {
        _push(`<div class="issues-list" data-v-baf0255f><!--[-->`);
        ssrRenderList(issues.value, (issue) => {
          _push(`<div class="${ssrRenderClass([issue.severity, "issue-card"])}" data-v-baf0255f><div class="issue-icon-wrapper" data-v-baf0255f>`);
          if (issue.severity === "error") {
            _push(ssrRenderComponent(_component_AlertCircleIcon, {
              size: 18,
              "aria-hidden": "true"
            }, null, _parent));
          } else {
            _push(ssrRenderComponent(_component_AlertTriangleIcon, {
              size: 18,
              "aria-hidden": "true"
            }, null, _parent));
          }
          _push(`</div><div class="issue-content" data-v-baf0255f><div class="issue-header" data-v-baf0255f><span class="${ssrRenderClass([`severity-${issue.severity}`, "severity-badge"])}" data-v-baf0255f>${ssrInterpolate(issue.severity === "error" ? "错误" : "警告")}</span><span class="issue-title" data-v-baf0255f>${ssrInterpolate(issue.title)}</span></div><p class="issue-desc" data-v-baf0255f>${ssrInterpolate(issue.description)}</p>`);
          if (issue.entity1 || issue.entity2) {
            _push(`<div class="issue-entities" data-v-baf0255f>`);
            if (issue.entity1) {
              _push(`<span class="entity-tag" data-v-baf0255f>${ssrInterpolate(issue.entity1)}</span>`);
            } else {
              _push(`<!---->`);
            }
            if (issue.entity1 && issue.entity2) {
              _push(ssrRenderComponent(_component_ArrowRightIcon, {
                size: 12,
                class: "entity-arrow",
                "aria-hidden": "true"
              }, null, _parent));
            } else {
              _push(`<!---->`);
            }
            if (issue.entity2) {
              _push(`<span class="entity-tag" data-v-baf0255f>${ssrInterpolate(issue.entity2)}</span>`);
            } else {
              _push(`<!---->`);
            }
            _push(`</div>`);
          } else {
            _push(`<!---->`);
          }
          _push(`</div><button class="btn btn-link" data-v-baf0255f> 定位 `);
          _push(ssrRenderComponent(_component_ChevronRightIcon, {
            size: 14,
            "aria-hidden": "true"
          }, null, _parent));
          _push(`</button></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/linter/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-baf0255f"]]);

export { index as default };
//# sourceMappingURL=index-BMLyehQf.mjs.map
