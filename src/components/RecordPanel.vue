<template>
	<div class="record-elements">
		<div class="the-record">
			<svg 
				ref="chartSvg"
				class="record-panel"
				viewBox="-50 -50 100 100"
				preserveAspectRatio="xMidYMid meet"
			>
				<g class="grooves"></g>
				<g class="bars"></g>
				<circle cx="0" cy="0" r="12" fill="#242424" stroke="lightcoral" stroke-width="0.5"/>
			</svg>
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
import { ref, watch, onMounted } from 'vue'
import * as d3 from 'd3'
import genresData from '../api/genres.json'

const yearValue = ref(1950)
const chartSvg = ref(null)
const currentRotation = ref(0)
let svg, bars, grooves, innerRadius, outerRadius, continentColors, currentGenreData = []
let selectedBar = null

const updateChart = (year) => {
	if (!svg) return
	
	const yearData = genresData[year.toString()]
	if (!yearData) return
	
	const genreData = []
	for (const continent of yearData.continents) {
		for (const [genre, count] of Object.entries(continent.genres)) {
			if (count > 0) {
				genreData.push({
					continent: continent.name,
					genre,
					count,
					total: continent.total,
					percentage: continent.total > 0 ? count / continent.total : 0
				})
			}
		}
	}
	
	genreData.sort((a, b) => {
		if (a.continent !== b.continent) {
			return a.continent.localeCompare(b.continent)
		}
		return a.genre.localeCompare(b.genre)
	})
	
	currentGenreData = genreData
	
	const numBars = genreData.length
	const angleScale = d3.scaleLinear()
		.domain([0, numBars])
		.range([0, 2 * Math.PI])
	
	const heightScale = d3.scaleLog()
		.domain([0.001, 1])
		.range([0, outerRadius - innerRadius])
		.clamp(true)
	
	const arcGenerator = d3.arc()
		.startAngle((d, i) => angleScale(i))
		.endAngle((d, i) => angleScale(i + 1) - 0.005)
	
	bars.selectAll('path.bar-bg')
		.data(genreData, d => d.genre)
		.join(
			enter => enter.append('path')
				.attr('class', 'bar-bg')
				.attr('data-continent', d => d.continent)
				.attr('data-genre', d => d.genre)
				.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
				.attr('fill', d => continentColors[d.continent] || 'lightcoral')
				.attr('opacity', 0)
				.on('click', handleBarClick)
				.transition()
				.duration(400)
				.attr('opacity', 0.2),
			update => update
				.attr('data-continent', d => d.continent)
				.attr('data-genre', d => d.genre)
				.on('click', handleBarClick)
				.transition()
				.duration(400)
				.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
				.attr('fill', d => continentColors[d.continent] || 'lightcoral')
				.attr('opacity', 0.2),
			exit => exit
				.transition()
				.duration(300)
				.attr('opacity', 0)
				.remove()
		)
	
	bars.selectAll('path.bar-fg')
		.data(genreData, d => d.genre)
		.join(
			enter => enter.append('path')
				.attr('class', 'bar-fg')
				.attr('data-continent', d => d.continent)
				.attr('data-genre', d => d.genre)
				.attr('d', (d, i) => {
					const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))))
					return arcGenerator.innerRadius(outerRadius - barHeight).outerRadius(outerRadius)({ data: d }, i)
				})
				.attr('fill', d => continentColors[d.continent] || 'lightcoral')
				.attr('opacity', 0)
				.on('click', handleBarClick)
				.transition()
				.duration(400)
				.attr('opacity', 0.8),
			update => update
				.attr('data-continent', d => d.continent)
				.attr('data-genre', d => d.genre)
				.on('click', handleBarClick)
				.transition()
				.duration(400)
				.attr('d', (d, i) => {
					const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))))
					return arcGenerator.innerRadius(outerRadius - barHeight).outerRadius(outerRadius)({ data: d }, i)
				})
				.attr('fill', d => continentColors[d.continent] || 'lightcoral')
				.attr('opacity', 0.8),
			exit => exit
				.transition()
				.duration(300)
				.attr('opacity', 0)
				.remove()
		)
}

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: true
	}
})

const emit = defineEmits(['update:isDescriptionVisible', 'year-change', 'bar-click'])

const handleBarClick = (event, d) => {
	const barIndex = currentGenreData.findIndex(item => item.genre === d.genre)
	if (barIndex === -1) return

	if (selectedBar) {
		d3.select(selectedBar).classed('selected', false)
	}
	
	selectedBar = event.currentTarget
	d3.select(selectedBar).classed('selected', true)

	const numBars = currentGenreData.length
	const anglePerBar = (2 * Math.PI) / numBars
	const barMidAngle = (barIndex + 0.5) * anglePerBar
	const targetAngle = Math.PI * 1.5
	const rotationNeeded = targetAngle - barMidAngle
	const rotationDegrees = (rotationNeeded * 180) / Math.PI
	currentRotation.value = rotationDegrees
	
	grooves.transition()
		.duration(600)
		.attr('transform', `rotate(${rotationDegrees})`)
	
	bars.transition()
		.duration(600)
		.attr('transform', `rotate(${rotationDegrees})`)
	emit('update:isDescriptionVisible', !props.isDescriptionVisible);
	emit('bar-click', { continent: d.continent, genre: d.genre })
}

watch(yearValue, (newYear) => {
	emit('year-change', newYear);
	updateChart(newYear);
})

watch(() => props.isDescriptionVisible, (newValue) => {
	if (!newValue && selectedBar) {
		d3.select(selectedBar).classed('selected', false)
		selectedBar = null
	}
})

onMounted(async () => {
	svg = d3.select(chartSvg.value)
	
	grooves = svg.select('g.grooves')
	const numGrooves = 40
	const minRadius = 12
	const maxRadius = 48
	
	for (let i = 0; i < numGrooves; i++) {
		const radius = minRadius + (maxRadius - minRadius) * (i / numGrooves)
		grooves.append('circle')
			.attr('cx', 0)
			.attr('cy', 0)
			.attr('r', radius)
			.attr('fill', 'none')
			.attr('stroke', 'rgba(255, 255, 255, 0.05)')
			.attr('stroke-width', 0.3)
	}
	
	innerRadius = 12
	outerRadius = 46
	
	continentColors = {
		'The Rock Shield': '#e74c3c',
		'The Electronic Frontier': '#3498db',
		'The Hip-Hop Basin': '#9b59b6',
		'The Jazz & Blues Delta': '#f39c12',
		'The Pop Archipelago': '#e91e63',
		'The Folk & Roots Plains': '#8bc34a',
		'The Tropical Pulse': '#00bcd4',
		'The Metal Peaks': '#607d8b',
		'The Avant-Garde Isles': '#795548'
	}
	
	bars = svg.select('g.bars')
	
	updateChart(yearValue.value)
})

</script>