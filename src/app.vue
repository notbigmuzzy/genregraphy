<template>
	<MusicMap v-if="genres" :genres="genres" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MusicMap from './components/MusicMap.vue'

const genres = ref(null)

onMounted(async () => {
	const response = await import('./api/genres.json')
	genres.value = response.default
})
</script>