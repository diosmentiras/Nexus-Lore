# Nexus-Lore

> 设定即数据（Lore as Data）。一个面向长篇创作、跑团与共享世界的自托管世界观工作台。

Nexus-Lore 将文章来源、结构化设定、事件时间线和实体关系保存在同一个世界工作区中。它既可以管理原创资料，也可以把已有文章整理成可检索、可追溯的设定库。

## 已实现功能

### 世界库与来源归档

- 多个世界观完全隔离，工作区可快速切换。
- 每个世界拥有总览、来源、Lore、时间线、关系图和检查器。
- 来源文章保留标题、原文链接、正文、读取状态和分析摘要。
- 世界总览展示资料规模、基本设定纲要和待补来源。

### Lore 结构化设定

- 支持人物、势力、地点、物品、事件、异常与世界总档案。
- Lore 详情展示背景、标签、承载故事、正文证据、共同出场和关联实体。
- AI 提取结果可写入实体、事件和关系，并保留来源文档。
- 支持 Ollama、OpenAI 和 DeepSeek 兼容接口。

### Chronicle 时间线

- 按 `date_order` 稳定排序，不依赖日期字符串的字典序。
- 支持搜索与年份范围过滤。
- 保留模糊时间依据和来源语境。

### Nexus 3D 关系图

- 使用 Three.js / 3d-force-graph 渲染球状关系网络。
- 可在实体关系、故事脉络和全部网络之间切换。
- 支持节点类型、关系类型、名称、原型和标签过滤。
- 节点详情可跳转到 Lore 或打开来源文章。

### Lore Linter

- 疑似重复实体。
- 失效的势力、事件和关系引用。
- 跨世界关系与自关联。
- 关系开始/结束时间倒置。
- 角色在死亡事件后继续行动，并排除档案、回忆和纪念语境。
- 问题结果持久化，可定位、解决、重新打开和按严重级别筛选。

### 数据管理

- 按当前世界或全库导出 JSON 备份。
- 创建、切换和安全删除世界。
- 查看当前 AI Provider 配置并执行真实连接测试。
- Dashboard 与世界工作区均支持服务端首屏数据加载。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Nuxt 4、Vue 3、Lucide、Three.js、3d-force-graph |
| 后端 | FastAPI、Pydantic、SQLAlchemy Async |
| 数据库 | SQLite（本地默认）或 PostgreSQL 16（Docker） |
| AI | Ollama API、OpenAI-compatible API |

## 快速开始

### Docker

需要 Docker Desktop 或 Docker Engine + Compose。

```bash
git clone https://github.com/diosmentiras/Nexus-Lore.git
cd Nexus-Lore
cp .env.example .env
docker compose up --build -d
```

打开 <http://localhost:3000>。后端 OpenAPI 文档位于 <http://localhost:8000/docs>。

Docker 中的 Ollama 默认通过 `host.docker.internal:11434` 访问宿主机。需要其他地址时设置 `DOCKER_AI_ENDPOINT`。

### 本地开发

需要 Python 3.12+ 与 Node.js 22+。

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

另开终端：

```bash
cd frontend
npm ci
npm run dev
```

后端未配置 `.env` 时使用 `backend/data/dev.db`。若要使用 PostgreSQL，可从 `backend/.env.example` 创建 `backend/.env`。

## 验证

```bash
cd backend
.venv/bin/python -m compileall app tests
.venv/bin/python -m unittest discover -s tests -v

cd ../frontend
npm run build
```

`main` 分支的 GitHub Actions 会运行相同的后端测试和前端生产构建。

## 数据导入脚本

`backend/scripts/` 包含现有文章集的导入和整理工具：

- `import_all_canon_hubs.py`：导入多个设定中心及其文章目录。
- `import_aces_and_eights.py`：导入并整理“死者手牌”。
- `enrich_aces_and_eights_entities.py`：补充实体详情与正文证据。
- `build_chronicle_events.py`：从来源日期标记构建 Chronicle 事件。

这些脚本会修改目标数据库。运行前应先使用设置页导出备份，并在脚本参数或环境变量中确认数据库地址。

## 目录结构

```text
Nexus-Lore/
├── backend/
│   ├── app/api/          # FastAPI 路由
│   ├── app/models/       # SQLAlchemy 模型
│   ├── app/services/     # AI、抽取、Linter 与世界服务
│   ├── scripts/          # 文章导入与数据整理
│   └── tests/            # 标准库 unittest
├── frontend/
│   ├── app/components/   # 图谱、时间线、编辑器等组件
│   ├── app/composables/  # 世界状态与 API 配置
│   └── app/pages/        # 世界库与工作区路由
├── docker/               # Dockerfile 与兼容 Compose 配置
├── compose.yml           # 根目录一键部署
└── .github/workflows/    # 持续集成
```

## 路线图

- [x] 多世界来源归档、Lore、Chronicle 与 3D Nexus。
- [x] Ollama / OpenAI-compatible 结构化提取。
- [x] 可解释的确定性 Lore Linter。
- [x] JSON 备份、世界管理与 CI。
- [ ] AI token 级流式提取与可取消任务。
- [ ] 相对时间锚点推理与人工确认队列。
- [ ] 静态维基导出和 GitHub Pages 发布工作流。
- [ ] 数据导入预览、合并策略与回滚。

## 许可

项目代码使用 MIT License。导入的第三方文章仍遵循其原站点与作者规定的许可，不随项目代码重新授权。
