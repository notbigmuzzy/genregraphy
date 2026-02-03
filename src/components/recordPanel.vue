<template>
	<div class="record-elements">
		<div class="the-record">
			<svg 
				ref="chartSvg"
				class="record-panel"
				viewBox="-50 -50 100 100"
				preserveAspectRatio="xMidYMid meet"
			>
				<g class="spin">
					<g class="grooves"></g>
					<g class="bars"></g>
					<circle cx="0" cy="0" r="12" fill="transparent" stroke="lightcoral" stroke-width="0.5"/>
				</g>
			</svg>
		</div>
		
		<Slider 
			v-model="yearValue"
			:min="1950"
			:max="2025"
			:step="1"
			:lazy="true"
			orientation="vertical"
		/>
	</div>
</template>

<script setup>
import Slider from '@vueform/slider'
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'
import genresData from '../api/genres.json'

const yearValue = ref(1950)
const chartSvg = ref(null)
let svg, spinGroup, bars, grooves, labels, innerRadius, outerRadius, continentColors, currentGenreData = []
let selectedBar = null
let selectedId = null
let selectedContinent = null

const spinDurationInMs = 45_000
const spinDegPerMs = 360 / spinDurationInMs
let spinAngleDeg = 0
let isSpinPaused = false
let spinTimer = null
let prevElapsedMs = 0

let pauseHover = false
let pauseYearTransition = false
let pauseSelection = false
let yearPauseTimeout = null

const updateChart = (year) => {
	const yearData = genresData[year.toString()]
	const mappedTotalForTheYear = yearData.metadata.mapped_total
	const peakGenres = yearData.metadata.peak_genres
	const genreData = []

	for (const continent of yearData.continents) {
		for (const [genre, count] of Object.entries(continent.genres)) {
			if (count > 0) {
				genreData.push({
					id: `${continent.name}::${genre}`,
					continent: continent.name,
					genre,
					count,
					total: continent.total,
					percentage: continent.total > 0 ? count / continent.total : 0,
					isPeak: peakGenres.includes(genre)
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
	
	const barGroups = bars.selectAll('g.bar-group')
		.data(genreData, d => d.id)
		.join(
			enter => {
				const g = enter.append('g')
					.attr('class', d => {
						const genreClass = d.genre.toLowerCase().replace(/[^a-z0-9]+/g, '-')
						return d.isPeak ? `bar-group peak genre-${genreClass}` : `bar-group genre-${genreClass}`
					})
					.attr('data-continent', d => d.continent)
					.attr('data-genre', d => d.genre)
					.attr('data-id', d => d.id)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
					.on('click', handleBarClick)
				
				g.append('path')
					.attr('class', 'bar-bg')
					.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
					.attr('fill', d => continentColors[d.continent] || 'lightcoral')
					.attr('opacity', 0)
					.transition()
					.duration(400)
					.attr('opacity', 0.2)
				
				g.append('path')
					.attr('class', 'bar-fg')
					.attr('d', (d, i) => {
						const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))))
						return arcGenerator.innerRadius(outerRadius - barHeight).outerRadius(outerRadius)({ data: d }, i)
					})
					.attr('fill', d => continentColors[d.continent] || 'lightcoral')
					.attr('opacity', 0)
					.transition()
					.duration(400)
					.attr('opacity', 0.8)
				
				g.append('text')
					.attr('class', 'bar-label')
					.attr('text-anchor', 'start')
					.attr('dominant-baseline', 'middle')
					.attr('opacity', 0)
					.text(d => d.genre)
					.attr('transform', (d, i) => {
						const midAngle = (angleScale(i) + angleScale(i + 1)) / 2
						const angleDeg = (midAngle * 180) / Math.PI
						const r = outerRadius - 0.8
						return `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`
					})
					.transition()
					.duration(400)
					.attr('opacity', 1)
				
				return g
			},
			update => {
				update
					.attr('class', d => {
						const genreClass = d.genre.toLowerCase().replace(/[^a-z0-9]+/g, '-')
						return d.isPeak ? `bar-group peak genre-${genreClass}` : `bar-group genre-${genreClass}`
					})
					.attr('data-continent', d => d.continent)
					.attr('data-genre', d => d.genre)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
				
				update.select('path.bar-bg')
					.transition()
					.duration(400)
					.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
					.attr('fill', d => continentColors[d.continent] || 'lightcoral')
					.attr('opacity', 0.2)
				
				update.select('path.bar-fg')
					.transition()
					.duration(400)
					.attr('d', (d, i) => {
						const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))))
						return arcGenerator.innerRadius(outerRadius - barHeight).outerRadius(outerRadius)({ data: d }, i)
					})
					.attr('fill', d => continentColors[d.continent] || 'lightcoral')
					.attr('opacity', 0.8)
				
				update.select('text.bar-label')
					.text(d => d.genre)
					.transition()
					.duration(400)
					.attr('transform', (d, i) => {
						const midAngle = (angleScale(i) + angleScale(i + 1)) / 2
						const angleDeg = (midAngle * 180) / Math.PI
						const r = outerRadius - 0.8
						return `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`
					})
					.attr('opacity', 1)
				
				return update
			},
			exit => exit
				.transition()
				.duration(300)
				.attr('opacity', 0)
				.on('end', function() {
					d3.select(this).on('click', null)
				})
				.remove()
		)

	if (selectedId) {
		bars.selectAll('g.bar-group').classed('selected', item => item?.id === selectedId)
	}
	if (selectedContinent) {
		bars.selectAll('g.bar-group').classed('same-group', item => item?.continent === selectedContinent)
	}
}

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: true
	},
	isIntroVisible: {
		type: Boolean,
		required: false,
		default: false
	}
})

const emit = defineEmits(['update:isDescriptionVisible', 'bar-click'])

const recomputeSpinPaused = () => {
	isSpinPaused = pauseHover || pauseYearTransition || pauseSelection || props.isDescriptionVisible || props.isIntroVisible
}

const handleBarClick = (event, d) => {
	pauseSelection = true
	recomputeSpinPaused()
	selectedId = d.id
	selectedContinent = d.continent

	const barIndex = currentGenreData.findIndex(item => item.id === d.id)
	if (barIndex === -1) return

	if (selectedBar) {
		d3.select(selectedBar).classed('selected', false)
	}
	
	selectedBar = event.currentTarget
	if (bars) {
		bars.selectAll('g.bar-group').classed('selected', false).classed('same-group', false)
		
		bars.selectAll('g.bar-group')
			.classed('selected', item => item?.id === d.id)
			.classed('same-group', item => item?.continent === d.continent)
	} else {
		d3.select(selectedBar).classed('selected', true)
	}

	const numBars = currentGenreData.length
	const anglePerBar = (2 * Math.PI) / numBars
	const barMidAngle = (barIndex + 0.5) * anglePerBar
	const barMidDeg = (barMidAngle * 180) / Math.PI

	const targetBarDeg = 270
	const targetRotationDeg = targetBarDeg - barMidDeg
	const delta = ((targetRotationDeg - spinAngleDeg + 540) % 360) - 180
	const nextRotation = spinAngleDeg + delta

	spinGroup?.interrupt()
	spinGroup?.transition()
		.duration(600)
		.tween('rotate', () => {
			const i = d3.interpolateNumber(spinAngleDeg, nextRotation)
			return (t) => {
				spinAngleDeg = i(t)
				spinGroup.attr('transform', `rotate(${spinAngleDeg})`)
			}
		})
		.on('end', () => {
			spinAngleDeg = ((spinAngleDeg % 360) + 360) % 360
			spinGroup.attr('transform', `rotate(${spinAngleDeg})`)
		})

	emit('update:isDescriptionVisible', true);
	emit('bar-click', {
		continent: d.continent,
		genre: d.genre,
		genreName: d.genre,
		isPeak: d.isPeak,
		year: yearValue.value,
		count: d.count,
		percentage: d.percentage
	});
}

watch(yearValue, (newYear) => {
	emit('year-change', newYear);

	pauseYearTransition = true
	recomputeSpinPaused()

	updateChart(newYear);

	if (yearPauseTimeout) yearPauseTimeout.stop()
	yearPauseTimeout = d3.timeout(() => {
		pauseYearTransition = false
		recomputeSpinPaused()
	}, 250)
})

watch(() => props.isDescriptionVisible, (newValue) => {
	if (!newValue && selectedBar) {
		if (bars) {
			bars.selectAll('g.bar-group').classed('selected', false).classed('same-group', false)
		} else {
			d3.select(selectedBar).classed('selected', false)
		}
		selectedBar = null
		selectedId = null
		selectedContinent = null
		pauseSelection = false
		recomputeSpinPaused()
	}
})

watch(() => props.isIntroVisible, () => {
	recomputeSpinPaused()
})

onMounted(async () => {
	// Initialize spin state based on intro visibility
	recomputeSpinPaused()
	
	svg = d3.select(chartSvg.value)
	spinGroup = svg.select('g.spin')
	grooves = spinGroup.select('g.grooves')
	bars = spinGroup.select('g.bars')
	labels = spinGroup.select('g.labels')

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
	outerRadius = 47
	
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
	
	updateChart(yearValue.value)

	spinTimer?.stop?.()
	prevElapsedMs = 0
	spinTimer = d3.timer((elapsedMs) => {
		if (prevElapsedMs === 0) {
			prevElapsedMs = elapsedMs
			return
		}

		const dt = elapsedMs - prevElapsedMs
		prevElapsedMs = elapsedMs
		if (isSpinPaused) return

		spinAngleDeg = (spinAngleDeg + dt * spinDegPerMs) % 360
		spinGroup.attr('transform', `rotate(${spinAngleDeg})`)
	})

	svg.on('mouseenter', () => {
		pauseHover = true
		recomputeSpinPaused()
	})

	svg.on('mouseleave', () => {
		pauseHover = false
		recomputeSpinPaused()
	})
})

onBeforeUnmount(() => {
	// Stop the spin timer
	if (spinTimer) {
		spinTimer.stop()
		spinTimer = null
	}
	
	// Clear the year pause timeout
	if (yearPauseTimeout) {
		yearPauseTimeout.stop()
		yearPauseTimeout = null
	}
	
	// Remove event listeners
	if (svg) {
		svg.on('mouseenter', null)
		svg.on('mouseleave', null)
	}
	
	// Remove click handlers from bars to prevent memory leaks
	if (bars) {
		bars.selectAll('g.bar-group').on('click', null)
	}
	
	// Interrupt any ongoing transitions
	if (spinGroup) {
		spinGroup.interrupt()
	}
})

</script>