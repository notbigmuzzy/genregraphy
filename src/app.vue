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
	const descriptionContent = ref(null)

	const handleBarClick = (data) => {
		descriptionContent.value = data;
	}
</script>