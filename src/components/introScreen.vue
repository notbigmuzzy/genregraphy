<template>
	<div class="intro-screen" :class="props.isIntroVisible ? 'visible' : 'hidden'">
		<div class="panel-text-block">
			<h2>
				<span>Genre-</span>
				<span>-graphy</span>
			</h2>
			<hr/>
			<p class="description">
				The sonic pulse of history, etched into vinyl. Spin the record to navigate 75 years of musical evolution—from the raw garage of '63 to the digital waves of today.
			</p>
			<button class="start-button" @click="showHideIntro">
				Press PLAY to start
			</button>
		</div>
	</div>
</template>

<script setup>

const props = defineProps({
	isIntroVisible: {
		type: Boolean,
		required: true
	}
});

const emit = defineEmits(['update:isIntroVisible'])

const showHideIntro = () => {
	emit('update:isIntroVisible', !props.isIntroVisible);
};

</script>