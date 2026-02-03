<template>
	<div class="record-elements">
		<div class="the-record">
			<div class="record-panel">
				<button @click="toggleDescription">See details</button>
			</div>
		</div>

		<Slider 
			v-model="yearValue"
			:min="1950"
			:max="2025"
			:step="1"
			:lazy="false"
			orientation="vertical"
		/>
	</div>
</template>

<script setup>
import Slider from '@vueform/slider'
import { ref, watch } from 'vue'

const yearValue = ref(1950)

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: true
	}
})

const emit = defineEmits(['update:isDescriptionVisible', 'year-change'])

const toggleDescription = () => {
	emit('update:isDescriptionVisible', !props.isDescriptionVisible);
}

watch(yearValue, (newYear) => {
	emit('year-change', newYear);
})

</script>

<style src="@vueform/slider/themes/default.css"></style>