<template>
	<div class="info-panel" :class="isIntroVisible || isDescriptionVisible ? 'show' : 'hide'">
		<intro-screen
			v-model:isIntroVisible="isIntroVisible"
		/>
		<description-panel
			v-model:isDescriptionVisible="isDescriptionVisible"
			:content="descriptionContent"
		/>
	</div>
	<div class="record-wrapper" :class="isIntroVisible || isDescriptionVisible ? 'sided' : 'centered'">
		<record-panel
			v-model:isDescriptionVisible="isDescriptionVisible"
			:is-intro-visible="isIntroVisible"
			:initial-year="initialYear"
			@bar-click="handleBarClick"
			@year-changed="handleYearChange"
		/>
	</div>
</template>

<script setup>
	import { ref } from 'vue'
	import IntroScreen from './components/introScreen.vue'
	import RecordPanel from './components/recordPanel.vue'
	import DescriptionPanel from './components/descriptionPanel.vue'

	const isIntroVisible = ref(true)
	const isDescriptionVisible = ref(false)
	const descriptionContent = ref(null)

	// URL parameter logic
	const urlParams = new URLSearchParams(window.location.search);
	const yearParam = parseInt(urlParams.get('year'));
	const initialYear = ref(yearParam && yearParam >= 1950 && yearParam <= 2025 ? yearParam : 1950);

	const handleBarClick = (data) => {
		descriptionContent.value = data;
	}

	const handleYearChange = (year) => {
		const url = new URL(window.location);
		url.searchParams.set('year', year);
		window.history.replaceState({}, '', url);

		if (descriptionContent.value) {
			isDescriptionVisible.value = false;
			descriptionContent.value = null;
		}
	}
</script>