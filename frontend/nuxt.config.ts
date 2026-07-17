// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss"],
  app: {
    head: {
      title: "Nexus-Lore",
      meta: [
        { name: "description", content: "Nexus-Lore - 自托管世界观构建终端 | 设定即数据" },
        { name: "theme-color", content: "#0a0a0f" },
      ],
      link: [
        { rel: "stylesheet", href: "/cyberpunk.css" },
        { rel: "icon", type: "image/svg+xml", href: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1f4a0;</text></svg>" },
      ],
    },
  },
  tailwindcss: {
    config: {
      theme: {
        extend: {
          colors: {
            "nexus-bg": "#0a0a0f",
            "nexus-card": "#1a1a2e",
            "nexus-border": "#2a2a4a",
            "nexus-cyan": "#00f0ff",
            "nexus-magenta": "#ff00aa",
            "nexus-yellow": "#ffd700",
          },
        },
      },
    },
  },
})
