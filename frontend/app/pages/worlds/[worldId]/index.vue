<script setup lang="ts">
const route = useRoute()
await navigateTo(`/worlds/${route.params.worldId}/overview`, { redirectCode: 302 })
</script>
