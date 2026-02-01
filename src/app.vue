<template>
	<div class="charts-container">
		<GenreChart />
		<GenreGroupChart />
	</div>
</template>

<script setup>
	import GenreChart from './components/GenreChart.vue';
	import GenreGroupChart from './components/GenreGroupChart.vue';
</script>

<style scoped>
	.charts-container {
	display: flex;
	gap: 3rem;
	flex-wrap: wrap;
	}
</style>