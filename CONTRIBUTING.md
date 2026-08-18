# Contributing

## 开发环境

- Python 3.12+
- Node.js 22+
- Docker（仅 PostgreSQL 或完整容器环境需要）

## 本地启动

```bash
git clone https://github.com/diosmentiras/Nexus-Lore.git
cd Nexus-Lore

cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload

cd ../frontend
npm ci
npm run dev
```

## 提交流程

1. 从最新 `main` 创建功能分支。
2. 保持改动集中，不提交数据库、密钥、构建产物或抓取缓存。
3. 为新的后端规则或数据转换增加测试。
4. 运行后端测试与前端生产构建。
5. 在 Pull Request 中说明行为变化、数据影响和验证方式。

## 验证命令

```bash
cd backend
.venv/bin/python -m compileall app tests
.venv/bin/python -m unittest discover -s tests -v

cd ../frontend
npm run build
```

## 代码约定

- Python：类型标注、短函数、确定性业务规则优先。
- Vue / TypeScript：遵循现有 Composition API 与工作区路由结构。
- 数据库：新增字段需要兼顾 SQLite 与 PostgreSQL。
- API：世界级数据必须接受或验证 `world_id`，避免跨世界污染。
- UI：桌面端和 390px 宽度移动端都应无横向溢出。
