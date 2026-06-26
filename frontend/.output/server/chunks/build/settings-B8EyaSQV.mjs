import { defineComponent, ref, resolveComponent, mergeProps, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderDynamicModel, ssrRenderAttr } from 'vue/server-renderer';
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
  __name: "settings",
  __ssrInlineRender: true,
  setup(__props) {
    const aiProvider = ref("ollama");
    const apiKey = ref("");
    const apiEndpoint = ref("");
    const modelName = ref("");
    const showKey = ref(false);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_CpuIcon = resolveComponent("CpuIcon");
      const _component_EyeIcon = resolveComponent("EyeIcon");
      const _component_EyeOffIcon = resolveComponent("EyeOffIcon");
      const _component_DatabaseIcon = resolveComponent("DatabaseIcon");
      const _component_DownloadIcon = resolveComponent("DownloadIcon");
      const _component_Trash2Icon = resolveComponent("Trash2Icon");
      const _component_InfoIcon = resolveComponent("InfoIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "settings-page" }, _attrs))} data-v-95a164bc><header class="page-header" data-v-95a164bc><div data-v-95a164bc><h1 class="page-title" data-v-95a164bc>Settings</h1><p class="page-description" data-v-95a164bc>系统配置 · AI 提供商与数据管理</p></div></header><div class="settings-sections" data-v-95a164bc><section class="settings-section" data-v-95a164bc><div class="section-header" data-v-95a164bc>`);
      _push(ssrRenderComponent(_component_CpuIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h2 class="section-title" data-v-95a164bc>AI Provider</h2></div><div class="setting-row" data-v-95a164bc><label class="setting-label" data-v-95a164bc>提供商</label><div class="setting-control" data-v-95a164bc><select class="setting-select" data-v-95a164bc><option value="ollama" data-v-95a164bc${ssrIncludeBooleanAttr(Array.isArray(aiProvider.value) ? ssrLooseContain(aiProvider.value, "ollama") : ssrLooseEqual(aiProvider.value, "ollama")) ? " selected" : ""}>Ollama（本地）</option><option value="openai" data-v-95a164bc${ssrIncludeBooleanAttr(Array.isArray(aiProvider.value) ? ssrLooseContain(aiProvider.value, "openai") : ssrLooseEqual(aiProvider.value, "openai")) ? " selected" : ""}>OpenAI</option><option value="deepseek" data-v-95a164bc${ssrIncludeBooleanAttr(Array.isArray(aiProvider.value) ? ssrLooseContain(aiProvider.value, "deepseek") : ssrLooseEqual(aiProvider.value, "deepseek")) ? " selected" : ""}>DeepSeek</option></select></div></div>`);
      if (aiProvider.value !== "ollama") {
        _push(`<div class="setting-row" data-v-95a164bc><label class="setting-label" data-v-95a164bc>API Key</label><div class="setting-control" data-v-95a164bc><div class="password-wrapper" data-v-95a164bc><input${ssrRenderDynamicModel(showKey.value ? "text" : "password", apiKey.value, null)}${ssrRenderAttr("type", showKey.value ? "text" : "password")} class="setting-input" placeholder="sk-..." data-v-95a164bc><button class="toggle-btn"${ssrRenderAttr("aria-label", showKey.value ? "隐藏" : "显示")} data-v-95a164bc>`);
        if (!showKey.value) {
          _push(ssrRenderComponent(_component_EyeIcon, {
            size: 14,
            "aria-hidden": "true"
          }, null, _parent));
        } else {
          _push(ssrRenderComponent(_component_EyeOffIcon, {
            size: 14,
            "aria-hidden": "true"
          }, null, _parent));
        }
        _push(`</button></div></div></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`<div class="setting-row" data-v-95a164bc><label class="setting-label" data-v-95a164bc>Endpoint</label><div class="setting-control" data-v-95a164bc><input${ssrRenderAttr("value", apiEndpoint.value)} class="setting-input"${ssrRenderAttr("placeholder", aiProvider.value === "ollama" ? "http://localhost:11434" : "https://api.openai.com/v1")} data-v-95a164bc></div></div><div class="setting-row" data-v-95a164bc><label class="setting-label" data-v-95a164bc>模型</label><div class="setting-control" data-v-95a164bc><input${ssrRenderAttr("value", modelName.value)} class="setting-input"${ssrRenderAttr("placeholder", aiProvider.value === "ollama" ? "llama3" : "gpt-4o-mini")} data-v-95a164bc></div></div></section><section class="settings-section" data-v-95a164bc><div class="section-header" data-v-95a164bc>`);
      _push(ssrRenderComponent(_component_DatabaseIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h2 class="section-title" data-v-95a164bc>数据管理</h2></div><div class="setting-row" data-v-95a164bc><div class="setting-info" data-v-95a164bc><span class="setting-label" data-v-95a164bc>导出设定集</span><span class="setting-hint" data-v-95a164bc>将所有世界观数据导出为 JSON 文件</span></div><button class="btn btn-secondary" data-v-95a164bc>`);
      _push(ssrRenderComponent(_component_DownloadIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(` 导出 </button></div><div class="setting-row danger" data-v-95a164bc><div class="setting-info" data-v-95a164bc><span class="setting-label" data-v-95a164bc>清空数据</span><span class="setting-hint danger-hint" data-v-95a164bc>此操作不可撤销</span></div><button class="btn btn-danger" data-v-95a164bc>`);
      _push(ssrRenderComponent(_component_Trash2Icon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(` 清空 </button></div></section><section class="settings-section" data-v-95a164bc><div class="section-header" data-v-95a164bc>`);
      _push(ssrRenderComponent(_component_InfoIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h2 class="section-title" data-v-95a164bc>关于</h2></div><div class="about-grid" data-v-95a164bc><div class="about-row" data-v-95a164bc><span class="about-key" data-v-95a164bc>版本</span><span class="about-value" data-v-95a164bc>v0.1.0</span></div><div class="about-row" data-v-95a164bc><span class="about-key" data-v-95a164bc>协议</span><span class="about-value" data-v-95a164bc>MIT License</span></div><div class="about-row" data-v-95a164bc><span class="about-key" data-v-95a164bc>理念</span><span class="about-value" data-v-95a164bc>设定即数据 (Lore as Data)</span></div></div></section></div></div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/settings.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const settings = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-95a164bc"]]);

export { settings as default };
//# sourceMappingURL=settings-B8EyaSQV.mjs.map
