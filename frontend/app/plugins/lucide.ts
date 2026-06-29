import { defineNuxtPlugin } from "#app"
import * as LucideIcons from "lucide-vue-next"

export default defineNuxtPlugin((nuxtApp) => {
  for (const [name, component] of Object.entries(LucideIcons)) {
    if (
      name !== "default" &&
      name !== "createIcons" &&
      typeof component === "object" &&
      component.render
    ) {
      nuxtApp.vueApp.component(name, component)
    }
  }
})
