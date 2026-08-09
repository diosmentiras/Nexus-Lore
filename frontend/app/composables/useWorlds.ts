export interface World {
  id: string
  name: string
  slug: string
  description?: string | null
  source_url?: string | null
  meta?: Record<string, any>
}

const API_BASE = ""
const SELECTED_WORLD_KEY = "nexus-lore:selected-world"

export function useApiBase() {
  return API_BASE
}

export function useWorlds() {
  const worlds = useState<World[]>("worlds", () => [])
  const selectedWorldId = useState<string>("selectedWorldId", () => "")
  const loadingWorlds = useState<boolean>("loadingWorlds", () => false)

  function applyWorldSelection() {
    if (!worlds.value.length) return
    const storedWorldId = import.meta.client ? localStorage.getItem(SELECTED_WORLD_KEY) : ""
    if (storedWorldId && worlds.value.some((world) => world.id === storedWorldId)) {
      selectedWorldId.value = storedWorldId
      return
    }
    if (!worlds.value.some((world) => world.id === selectedWorldId.value)) {
      selectedWorldId.value = worlds.value[0].id
    }
  }

  async function loadWorlds() {
    if (worlds.value.length) {
      applyWorldSelection()
      return
    }
    if (loadingWorlds.value) return
    loadingWorlds.value = true
    try {
      worlds.value = await $fetch<World[]>(`${API_BASE}/api/worlds`)
      applyWorldSelection()
    } finally {
      loadingWorlds.value = false
    }
  }

  async function createWorld(input: { name: string; slug: string; description?: string; source_url?: string }) {
    const world = await $fetch<World>(`${API_BASE}/api/worlds`, {
      method: "POST",
      body: input,
    })
    worlds.value = [world, ...worlds.value]
    selectedWorldId.value = world.id
    if (import.meta.client) localStorage.setItem(SELECTED_WORLD_KEY, world.id)
    return world
  }

  function selectWorld(worldId: string) {
    selectedWorldId.value = worldId
    if (import.meta.client) localStorage.setItem(SELECTED_WORLD_KEY, worldId)
  }

  return {
    worlds,
    selectedWorldId,
    loadingWorlds,
    loadWorlds,
    createWorld,
    selectWorld,
  }
}
