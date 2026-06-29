// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss"],
  app: {
    head: {
      link: [
        { rel: "stylesheet", href: "/cyberpunk.css" },
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
