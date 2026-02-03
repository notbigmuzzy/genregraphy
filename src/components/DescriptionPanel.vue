<template>
	<div class="description-panel" :class="props.isDescriptionVisible ? 'visible' : 'hidden'">
		<h2>Description Panel</h2>
		<hr/>
		<p class="description">
			This is the description panel content.
			It provides additional details about the application.
		</p>
		<button class="start-button" @click="hideDescription">Close Description</button>
	</div>
</template>

<script setup>

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: false
	}
})

const emit = defineEmits(['update:isDescriptionVisible'])

const hideDescription = () => {
	emit('update:isDescriptionVisible', false);
};

</script>