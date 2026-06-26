# Nexus-Lore

> **设定即数据 (Lore as Data)** —— 专为硬核创作者、科幻作家及跑团 DM 打造的自托管世界观构建终端。

不要再把宏大的世界观散落在凌乱的备忘录和沉重的数据库软件里了。Nexus-Lore 将"代码即基础设施"的极客理念引入创作领域，提供全套可视化、结构化、智能化的世界观管理方案。你可以通过 Docker 轻松实现本地一键部署，彻底掌控自己的数据隐私。

---

## 项目结构

`
nexus-lore/
├── frontend/                      # Nuxt.js 前端
│   ├── app.vue                    # 根组件
│   ├── pages/                     # 页面路由
│   │   ├── index.vue              # 仪表盘 / 总览
│   │   ├── lore/                  # 设定管理
│   │   │   ├── index.vue          # 设定列表/搜索
│   │   │   └── [id].vue           # 单张设定卡片详情
│   │   ├── nexus/                 # ★ 动态拓扑星图
│   │   │   └── index.vue          # 交互式关系图谱
│   │   ├── chronicle/             # ★ 编年史轨道
│   │   │   └── index.vue          # 时间轴视图
│   │   ├── linter/                # ★ 设定冲突检查
│   │   │   └── index.vue          # Linter 报告
│   │   └── settings.vue           # 系统设置
│   ├── components/                # 通用组件
│   │   ├── LoreCard.vue           # 设定卡片
│   │   ├── EntityRelationGraph.vue # 关系图谱 (D3.js)
│   │   ├── TimelineTrack.vue      # 时间轴组件
│   │   ├── LoreEditor.vue         # 双栏写作台
│   │   └── AiExtractPanel.vue     # AI 提取面板
│   ├── composables/               # Vue composables
│   │   ├── useLore.ts
│   │   ├── useNexus.ts
│   │   └── useChronicle.ts
│   ├── server/                    # Nuxt API 路由 (代理后端)
│   ├── assets/                    # 静态资源
│   │   ├── css/
│   │   │   └── cyberpunk.css      # Cyberpunk UI 主题
│   │   └── fonts/
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                       # FastAPI 后端
│   ├── app/
│   │   ├── main.py                # 入口 & 路由注册
│   │   ├── config.py              # 配置管理
│   │   ├── api/                   # API 路由层
│   │   │   ├── lore.py            # 设定 CRUD
│   │   │   ├── nexus.py           # 图谱查询
│   │   │   ├── chronicle.py       # 时间轴
│   │   │   ├── extract.py         # AI 提取接口 (SSE)
│   │   │   └── linter.py          # 冲突检查
│   │   ├── models/                # SQLAlchemy + JSONB 模型
│   │   │   ├── entity.py          # 实体 (人物/势力/物品...)
│   │   │   ├── relation.py        # 关系边
│   │   │   └── event.py           # 事件
│   │   ├── schemas/               # Pydantic 序列化
│   │   ├── services/              # 业务逻辑层
│   │   │   ├── harvester.py       # AI 逆向解析引擎
│   │   │   ├── nexus_builder.py   # 图谱构建
│   │   │   ├── chronicle.py       # 时间轴编织
│   │   │   └── lore_linter.py     # 语义冲突检查
│   │   └── db/
│   │       ├── session.py         # 数据库会话
│   │       └── migrations/        # Alembic 迁移
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── docker/                        # Docker 编排
│   ├── docker-compose.yml         # 主编排 (frontend + backend + db)
│   ├── docker-compose.override.yml # 开发环境覆盖
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
│
├── .env.example                   # 环境变量模板
├── .gitignore
├── LICENSE                        # MIT
└── README.md
`

---

## ⚡ 核心特性

### 🤖 AI 逆向解析引擎 (The Harvester)

- **文本一键降维**：扔给 AI 一篇粗糙的章节草稿或灵感大纲，系统会自动进行实体抽取（NER），洗出人物、势力、物品、收容物等设定。
- **自动结构化**：提取出的属性会自动转化为带元数据的结构化卡片，直接写入底层数据库。
- **隐私至上**：同时支持云端 API（OpenAI/DeepSeek 等）以及本地大模型（Ollama）。即使在完全断网的极客环境下，也能流畅进行 AI 解析。

### 🕸️ 动态拓扑星图 (The Nexus)

- **交互式关系网**：基于 D3.js 渲染的霓虹发光节点。不同阵营、派系一目了然。
- **多维过滤**：支持通过时间跨度、敌对/盟友关系或特定标签动态筛选图谱，鼠标悬浮即可实时预览角色羁绊与历史因果。

### ⏳ 编年史轨道 (The Chronicle)

- **时间轴自动编织**：提取设定中带有时间戳的事件，自动生成一条类似于视频剪辑软件的可缩放交互式历史轨道。
- **模糊时间对齐**：AI 会自动识别"三年后"、"企业战争爆发后"等上下文逻辑，帮你自动推算并对齐历史锚点。

### 🔍 全局语义级检查 (Linter for Lore)

- **逻辑漏洞告警**：像代码 Linter 一样检查你的设定冲突。如果一个角色在 2070 年的企业战争中牺牲，却又出现在 2077 年的某个事件中，系统会抛出 "设定冲突警告" 并定位到具体文档。

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 / Nuxt.js + Tailwind CSS + D3.js | Cyberpunk UI 风格，SSR 可选 |
| **后端** | FastAPI (Python) | 高性能异步 API，原生支持 SSE 流式输出 |
| **数据库** | PostgreSQL + JSONB | 关系查询与灵活的设定元数据兼顾 |
| **AI 驱动** | LangChain / Ollama / OpenAI API | 多 provider 支持，本地优先 |

---

## 🚀 快速开始 (Docker 一键部署)

### 前置条件
- Docker & Docker Compose

### 1. 克隆仓库
`ash
git clone git@github.com:diosmentiras/Nexus-Lore.git
cd Nexus-Lore
`

### 2. 配置环境 (可选)
`ash
cp .env.example .env
`
编辑 .env 填写你的 AI 密钥（若使用本地 Ollama 则无需配置云端 API）。

### 3. 启动
`ash
docker compose up -d
`

访问 [http://localhost:3000](http://localhost:3000) 开启你的宇宙。

---

## 📖 核心工作流演示

### Step 1: 喂给 AI 一段未整理的草稿
在双轨写作台左侧输入你的灵感：

> 在 2076 年的霓虹雨夜，黑客 Jane 潜入了荒坂集团的地下数据中心。她用刚安装的赛博义体"深网之眼"切断了警报，但她不知道，宿敌 John Doe 已经带着巨型企业的雇佣兵在出口堵她了……

### Step 2: AI 自动拆解并生成卡片
点击 [AI Extract]，右侧工作台将实时生成以下结构化设定并存入数据库：

`yaml
---
name: John Doe
type: character
faction: 巨型企业-荒坂
relations:
  - [Jane, 敌对, "2076年数据中心围剿"]
tags: [雇佣兵, 赛博义体]
---
背景故事:
  在 2076 年的数据中心事件中负责拦截黑客 Jane……
`

### Step 3: 静态维基与图谱同步更新
底层图谱与时间线会自动连线，生成 Jane 与 John Doe 的红线敌对图谱，并在 2076 年的时间轴上钉下一个名为"数据中心冲突"的锚点。

---

## 🎯 路线图 (Roadmap)

- [x] 基于 PostgreSQL (JSONB) 的自托管版本底座
- [x] 动态拓扑星图与交互式过滤器
- [ ] 接入 Ollama 本地大模型流式解析接口
- [ ] GitHub Actions 自动化工作流模板（一键将设定集打包发布为 GitHub Pages 静态维基）
- [ ] 类似 SCP 基金会风格的加密终端 UI 主题

---

## 📄 开源协议

本项目基于 **MIT License** 协议开源。欢迎任何硬核创作者、极客和开发者提交 Issue 或 Pull Request，一起编织更宏大的宇宙。
