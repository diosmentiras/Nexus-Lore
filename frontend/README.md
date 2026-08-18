# Nexus-Lore Frontend

Nuxt 4 前端，提供世界库和单世界工作区。

## 页面

- `/worlds`：世界库与全局统计。
- `/worlds/:worldId/overview`：世界总览。
- `/worlds/:worldId/sources`：来源目录与正文。
- `/worlds/:worldId/lore`：结构化设定与详情。
- `/worlds/:worldId/chronicle`：时间线。
- `/worlds/:worldId/nexus`：3D 关系图。
- `/worlds/:worldId/linter`：设定一致性检查。
- `/settings`：世界、AI 状态与数据管理。

## 开发

```bash
npm ci
npm run dev
```

默认将 `/api/**` 代理到 `http://127.0.0.1:8000/api/**`。容器构建可通过 `NUXT_API_PROXY` 指定后端地址。

## 构建

```bash
npm run build
node .output/server/index.mjs
```

提交前至少运行一次生产构建，并检查桌面端和 390px 宽度移动端的导航、文本溢出与控制台错误。
