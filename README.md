# Nexus-Lore

> **设定即数据 (Lore as Data)** -- 专为硬核创作者打造的自托管世界观构建终端。

---

## 项目结构

`	ext
nexus-lore/
├── frontend/                  Nuxt.js 前端
│   ├── app/
│   │   ├── app.vue            入口
│   │   ├── layouts/           布局组件
│   │   ├── pages/             页面路由
│   │   ├── components/        通用组件
│   │   └── assets/css/        全局样式
├── backend/                   FastAPI 后端
│   ├── app/
│   │   ├── main.py            入口
│   │   ├── api/               API 路由
│   │   ├── models/            数据库模型
│   │   ├── schemas/           序列化
│   │   └── services/          业务逻辑
│   ├── requirements.txt
│   └── Dockerfile
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile.frontend
├── .env.example
└── README.md
`

---

MIT License
