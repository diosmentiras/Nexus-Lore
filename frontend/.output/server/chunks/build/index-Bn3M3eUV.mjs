import { defineComponent, ref, computed, resolveComponent, mergeProps, reactive, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderTeleport, ssrRenderAttr, ssrIncludeBooleanAttr, ssrLooseContain, ssrLooseEqual, ssrRenderList, ssrInterpolate, ssrRenderClass } from 'vue/server-renderer';
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

const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "AiExtractPanel",
  __ssrInlineRender: true,
  emits: ["close", "extracted"],
  setup(__props, { emit: __emit }) {
    const text = ref("");
    const extracting = ref(false);
    const options = reactive([
      { key: "characters", label: "人物", value: true },
      { key: "factions", label: "势力", value: true },
      { key: "items", label: "物品", value: true },
      { key: "events", label: "事件", value: true }
    ]);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_SparklesIcon = resolveComponent("SparklesIcon");
      const _component_XIcon = resolveComponent("XIcon");
      const _component_LoaderIcon = resolveComponent("LoaderIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "ai-extract-panel" }, _attrs))} data-v-cf7157ba><div class="panel-header" data-v-cf7157ba><div class="panel-header-left" data-v-cf7157ba>`);
      _push(ssrRenderComponent(_component_SparklesIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<h3 class="panel-title" data-v-cf7157ba>AI Extract</h3></div><button class="close-btn" aria-label="关闭" data-v-cf7157ba>`);
      _push(ssrRenderComponent(_component_XIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`</button></div><div class="panel-body" data-v-cf7157ba><textarea class="extract-input" placeholder="粘贴章节草稿或灵感大纲..." data-v-cf7157ba>${ssrInterpolate(text.value)}</textarea><div class="extract-options" data-v-cf7157ba><span class="options-label" data-v-cf7157ba>提取类型</span><div class="options-grid" data-v-cf7157ba><!--[-->`);
      ssrRenderList(options, (opt) => {
        _push(`<label class="${ssrRenderClass([{ active: opt.value }, "option-chip"])}" data-v-cf7157ba><input type="checkbox"${ssrIncludeBooleanAttr(Array.isArray(opt.value) ? ssrLooseContain(opt.value, null) : opt.value) ? " checked" : ""} class="option-checkbox" data-v-cf7157ba><span data-v-cf7157ba>${ssrInterpolate(opt.label)}</span></label>`);
      });
      _push(`<!--]--></div></div><button class="btn btn-primary"${ssrIncludeBooleanAttr(!text.value.trim() || extracting.value) ? " disabled" : ""} data-v-cf7157ba>`);
      if (extracting.value) {
        _push(ssrRenderComponent(_component_LoaderIcon, {
          size: 16,
          class: "spin",
          "aria-hidden": "true"
        }, null, _parent));
      } else {
        _push(ssrRenderComponent(_component_SparklesIcon, {
          size: 16,
          "aria-hidden": "true"
        }, null, _parent));
      }
      _push(`<span data-v-cf7157ba>${ssrInterpolate(extracting.value ? "解析中..." : "开始提取")}</span></button></div></div>`);
    };
  }
});
const _sfc_setup$3 = _sfc_main$3.setup;
_sfc_main$3.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/AiExtractPanel.vue");
  return _sfc_setup$3 ? _sfc_setup$3(props, ctx) : void 0;
};
const __nuxt_component_0 = /* @__PURE__ */ Object.assign(_export_sfc(_sfc_main$3, [["__scopeId", "data-v-cf7157ba"]]), { __name: "AiExtractPanel" });
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "LoreEditor",
  __ssrInlineRender: true,
  emits: ["close"],
  setup(__props, { emit: __emit }) {
    const rawText = ref("");
    const extracting = ref(false);
    const results = ref([]);
    function formatYaml(item) {
      return JSON.stringify(item, null, 2);
    }
    return (_ctx, _push, _parent, _attrs) => {
      const _component_XIcon = resolveComponent("XIcon");
      const _component_FileTextIcon = resolveComponent("FileTextIcon");
      const _component_SparklesIcon = resolveComponent("SparklesIcon");
      const _component_LoaderIcon = resolveComponent("LoaderIcon");
      const _component_CodeIcon = resolveComponent("CodeIcon");
      const _component_FileJsonIcon = resolveComponent("FileJsonIcon");
      const _component_SaveIcon = resolveComponent("SaveIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "lore-editor" }, _attrs))} data-v-92b09593><div class="editor-header" data-v-92b09593><div class="editor-header-info" data-v-92b09593><h3 class="editor-title" data-v-92b09593>双轨写作台</h3><p class="editor-hint" data-v-92b09593>左侧输入草稿，右侧查看 AI 结构化提取结果</p></div><button class="btn-close" aria-label="关闭" data-v-92b09593>`);
      _push(ssrRenderComponent(_component_XIcon, {
        size: 18,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`</button></div><div class="editor-panels" data-v-92b09593><div class="editor-panel" data-v-92b09593><div class="panel-bar" data-v-92b09593>`);
      _push(ssrRenderComponent(_component_FileTextIcon, {
        size: 14,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<span data-v-92b09593>原始草稿</span></div><textarea class="raw-input" placeholder="在 2076 年的霓虹雨夜，黑客 Jane 潜入了荒坂集团的地下数据中心..." data-v-92b09593>${ssrInterpolate(rawText.value)}</textarea><button class="btn btn-primary"${ssrIncludeBooleanAttr(extracting.value || !rawText.value.trim()) ? " disabled" : ""} data-v-92b09593>`);
      if (!extracting.value) {
        _push(ssrRenderComponent(_component_SparklesIcon, {
          size: 16,
          "aria-hidden": "true"
        }, null, _parent));
      } else {
        _push(ssrRenderComponent(_component_LoaderIcon, {
          size: 16,
          class: "spin",
          "aria-hidden": "true"
        }, null, _parent));
      }
      _push(`<span data-v-92b09593>${ssrInterpolate(extracting.value ? "提取中..." : "AI Extract")}</span></button></div><div class="editor-panel" data-v-92b09593><div class="panel-bar" data-v-92b09593>`);
      _push(ssrRenderComponent(_component_CodeIcon, {
        size: 14,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<span data-v-92b09593>结构化输出</span></div>`);
      if (extracting.value) {
        _push(`<div class="panel-placeholder" data-v-92b09593><div class="spinner" data-v-92b09593></div><span data-v-92b09593>AI 正在解析文本...</span></div>`);
      } else if (!results.value.length) {
        _push(`<div class="panel-placeholder" data-v-92b09593>`);
        _push(ssrRenderComponent(_component_FileJsonIcon, {
          size: 32,
          class: "placeholder-icon",
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<span data-v-92b09593>点击 AI Extract 开始解析</span></div>`);
      } else {
        _push(`<div class="results-list" data-v-92b09593><!--[-->`);
        ssrRenderList(results.value, (item, i) => {
          _push(`<div class="result-item" data-v-92b09593><span class="${ssrRenderClass(["badge-" + item.type, "result-type-badge"])}" data-v-92b09593>${ssrInterpolate(item.type)}</span><pre class="result-yaml" data-v-92b09593>${ssrInterpolate(formatYaml(item))}</pre></div>`);
        });
        _push(`<!--]--></div>`);
      }
      _push(`</div></div><div class="editor-footer" data-v-92b09593><button class="btn btn-ghost" data-v-92b09593>取消</button><button class="btn btn-primary" data-v-92b09593>`);
      _push(ssrRenderComponent(_component_SaveIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(` 保存全部 </button></div></div>`);
    };
  }
});
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/LoreEditor.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const __nuxt_component_1 = /* @__PURE__ */ Object.assign(_export_sfc(_sfc_main$2, [["__scopeId", "data-v-92b09593"]]), { __name: "LoreEditor" });
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "LoreCard",
  __ssrInlineRender: true,
  props: {
    lore: {}
  },
  emits: ["click"],
  setup(__props) {
    const props = __props;
    const typeLabels = {
      character: "人物",
      faction: "势力",
      item: "物品",
      location: "地点",
      event: "事件",
      containment: "收容物"
    };
    const typeLabel = computed(() => typeLabels[props.lore.type] || props.lore.type);
    return (_ctx, _push, _parent, _attrs) => {
      const _component_Building2Icon = resolveComponent("Building2Icon");
      _push(`<div${ssrRenderAttrs(mergeProps({
        class: ["lore-card", [`type-${__props.lore.type}`, { clickable: _ctx.$attrs.onClick }]],
        role: "button",
        tabindex: 0,
        "aria-label": `查看 ${__props.lore.name}`
      }, _attrs))} data-v-00a1f2ea><div class="card-top" data-v-00a1f2ea><span class="${ssrRenderClass([`badge-${__props.lore.type}`, "card-type-badge"])}" data-v-00a1f2ea>${ssrInterpolate(typeLabel.value)}</span>`);
      if (__props.lore.faction) {
        _push(`<div class="card-faction" data-v-00a1f2ea>`);
        _push(ssrRenderComponent(_component_Building2Icon, {
          size: 12,
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<span data-v-00a1f2ea>${ssrInterpolate(__props.lore.faction)}</span></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div><h3 class="card-name" data-v-00a1f2ea>${ssrInterpolate(__props.lore.name)}</h3>`);
      if (__props.lore.summary) {
        _push(`<p class="card-summary" data-v-00a1f2ea>${ssrInterpolate(__props.lore.summary)}</p>`);
      } else {
        _push(`<!---->`);
      }
      if (__props.lore.tags?.length) {
        _push(`<div class="card-tags" data-v-00a1f2ea><!--[-->`);
        ssrRenderList(__props.lore.tags, (tag) => {
          _push(`<span class="tag" data-v-00a1f2ea>${ssrInterpolate(tag)}</span>`);
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<!---->`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/LoreCard.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const __nuxt_component_2 = /* @__PURE__ */ Object.assign(_export_sfc(_sfc_main$1, [["__scopeId", "data-v-00a1f2ea"]]), { __name: "LoreCard" });
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    const search = ref("");
    const typeFilter = ref("");
    const showEditor = ref(false);
    const showAiPanel = ref(false);
    const loreItems = ref([]);
    const filteredLore = computed(() => {
      return loreItems.value.filter((item) => {
        if (search.value) {
          const q = search.value.toLowerCase();
          if (!item.name.toLowerCase().includes(q) && !item.tags.some((t) => t.toLowerCase().includes(q))) return false;
        }
        if (typeFilter.value && item.type !== typeFilter.value) return false;
        return true;
      });
    });
    function onExtracted(items) {
      loreItems.value.push(...items);
      showAiPanel.value = false;
    }
    return (_ctx, _push, _parent, _attrs) => {
      const _component_SparklesIcon = resolveComponent("SparklesIcon");
      const _component_PlusIcon = resolveComponent("PlusIcon");
      const _component_AiExtractPanel = __nuxt_component_0;
      const _component_LoreEditor = __nuxt_component_1;
      const _component_SearchIcon = resolveComponent("SearchIcon");
      const _component_LoreCard = __nuxt_component_2;
      const _component_BookOpenIcon = resolveComponent("BookOpenIcon");
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "lore-page" }, _attrs))} data-v-d205bbc6><header class="page-header" data-v-d205bbc6><div data-v-d205bbc6><h1 class="page-title" data-v-d205bbc6>Lore</h1><p class="page-description" data-v-d205bbc6>世界观设定库 · 管理所有实体、关系和事件</p></div><div class="header-actions" data-v-d205bbc6><button class="btn btn-secondary" data-v-d205bbc6>`);
      _push(ssrRenderComponent(_component_SparklesIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<span data-v-d205bbc6>AI Extract</span></button><button class="btn btn-primary" data-v-d205bbc6>`);
      _push(ssrRenderComponent(_component_PlusIcon, {
        size: 16,
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<span data-v-d205bbc6>新建设定</span></button></div></header>`);
      if (showAiPanel.value) {
        _push(ssrRenderComponent(_component_AiExtractPanel, {
          onClose: ($event) => showAiPanel.value = false,
          onExtracted
        }, null, _parent));
      } else {
        _push(`<!---->`);
      }
      ssrRenderTeleport(_push, (_push2) => {
        if (showEditor.value) {
          _push2(`<div class="modal-overlay" data-v-d205bbc6>`);
          _push2(ssrRenderComponent(_component_LoreEditor, {
            onClose: ($event) => showEditor.value = false
          }, null, _parent));
          _push2(`</div>`);
        } else {
          _push2(`<!---->`);
        }
      }, "body", false, _parent);
      _push(`<div class="filter-bar" data-v-d205bbc6><div class="search-wrapper" data-v-d205bbc6>`);
      _push(ssrRenderComponent(_component_SearchIcon, {
        size: 16,
        class: "search-icon",
        "aria-hidden": "true"
      }, null, _parent));
      _push(`<input${ssrRenderAttr("value", search.value)} type="text" class="search-input" placeholder="搜索设定名称、标签..." data-v-d205bbc6></div><select class="filter-select" data-v-d205bbc6><option value="" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "") : ssrLooseEqual(typeFilter.value, "")) ? " selected" : ""}>全部类型</option><option value="character" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "character") : ssrLooseEqual(typeFilter.value, "character")) ? " selected" : ""}>人物</option><option value="faction" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "faction") : ssrLooseEqual(typeFilter.value, "faction")) ? " selected" : ""}>势力</option><option value="item" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "item") : ssrLooseEqual(typeFilter.value, "item")) ? " selected" : ""}>物品</option><option value="location" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "location") : ssrLooseEqual(typeFilter.value, "location")) ? " selected" : ""}>地点</option><option value="event" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "event") : ssrLooseEqual(typeFilter.value, "event")) ? " selected" : ""}>事件</option><option value="containment" data-v-d205bbc6${ssrIncludeBooleanAttr(Array.isArray(typeFilter.value) ? ssrLooseContain(typeFilter.value, "containment") : ssrLooseEqual(typeFilter.value, "containment")) ? " selected" : ""}>收容物</option></select></div>`);
      if (filteredLore.value.length) {
        _push(`<div class="lore-grid" data-v-d205bbc6><!--[-->`);
        ssrRenderList(filteredLore.value, (item) => {
          _push(ssrRenderComponent(_component_LoreCard, {
            key: item.id,
            lore: item,
            onClick: ($event) => _ctx.navigateTo("/lore/" + item.id)
          }, null, _parent));
        });
        _push(`<!--]--></div>`);
      } else {
        _push(`<div class="empty-state" data-v-d205bbc6>`);
        _push(ssrRenderComponent(_component_BookOpenIcon, {
          size: 48,
          class: "empty-icon",
          "aria-hidden": "true"
        }, null, _parent));
        _push(`<p class="empty-title" data-v-d205bbc6>还没有设定数据</p><p class="empty-desc" data-v-d205bbc6>点击「新建设定」手动创建，或使用「AI Extract」从草稿中自动提取</p></div>`);
      }
      _push(`</div>`);
    };
  }
});
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/lore/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-d205bbc6"]]);

export { index as default };
//# sourceMappingURL=index-Bn3M3eUV.mjs.map
