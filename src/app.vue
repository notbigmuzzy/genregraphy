<template>
	<MusicMap v-if="genres" :genres="genres" :year="currentYear" />
	<YearSlider v-model="currentYear" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MusicMap from './components/MusicMap.vue'
import YearSlider from './components/YearSlider.vue'

const genres = ref(null)
const currentYear = ref(1950)

onMounted(async () => {
	const response = await import('./api/genres.json')
	genres.value = response.default
})
</script>