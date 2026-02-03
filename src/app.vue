<template>
	<div class="info-panel" :class="isIntroVisible || isDescriptionVisible ? 'show' : 'hide'">
		<intro-screen
			v-model:isIntroVisible="isIntroVisible"
		/>
		<description-panel
			v-model:isDescriptionVisible="isDescriptionVisible"
		/>
	</div>
	<div class="record-wrapper" :class="isIntroVisible || isDescriptionVisible ? 'sided' : 'centered'">
		<record-panel
			v-model:isDescriptionVisible="isDescriptionVisible"
			@year-change="handleYear"
			@bar-click="handleBarClick"
		/>
	</div>
</template>

<script setup>
	import { ref } from 'vue'
	import IntroScreen from './components/introScreen.vue'
	import RecordPanel from './components/recordPanel.vue'
	import DescriptionPanel from './components/descriptionPanel.vue'

	const isIntroVisible = ref(false)
	const isDescriptionVisible = ref(false)

	const handleYear = (year) => {
		// console.log('Selected year:', year);
	}

	const handleBarClick = (data) => {
		console.log(data)
		console.log('Continent:', data.continent)
		console.log('Genre:', data.genre)
		console.log('Is Peak Genre:', data.isPeak)
	}
</script>