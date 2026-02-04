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

const props = defineProps({
	isDescriptionVisible: {
		type: Boolean,
		required: true
	},
	isIntroVisible: {
		type: Boolean,
		required: false,
		default: false
	},
	initialYear: {
		type: Number,
		default: 1950,
		required: false
	}
})

const yearValue = ref(props.initialYear)
const chartSvg = ref(null)
let svg, spinGroup, bars, grooves, labels, innerRadius, outerRadius, genre_groupColors, currentGenreData = []
let selectedBar = null
let selectedId = null
let selectedgenre_group = null

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

	for (const genre_group of yearData.genre_group) {
		for (const [genre, count] of Object.entries(genre_group.genres)) {
			if (count > 0) {
				genreData.push({
					id: `${genre_group.name}::${genre}`,
					genre_group: genre_group.name,
					genre,
					count,
					total: genre_group.total,
					percentage: genre_group.total > 0 ? count / genre_group.total : 0,
					isPeak: peakGenres.includes(genre)
				})
			}
		}
	}
	
	genreData.sort((a, b) => {
		if (a.genre_group !== b.genre_group) {
			return a.genre_group.localeCompare(b.genre_group)
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
					.attr('data-genre_group', d => d.genre_group)
					.attr('data-genre', d => d.genre)
					.attr('data-id', d => d.id)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
					.on('click', handleBarClick)
				
				g.append('path')
					.attr('class', 'bar-bg')
					.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
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
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
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
					.attr('data-genre_group', d => d.genre_group)
					.attr('data-genre', d => d.genre)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
				
				update.select('path.bar-bg')
					.transition()
					.duration(400)
					.attr('d', (d, i) => arcGenerator.innerRadius(innerRadius).outerRadius(outerRadius)({ data: d }, i))
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
					.attr('opacity', 0.2)
				
				update.select('path.bar-fg')
					.transition()
					.duration(400)
					.attr('d', (d, i) => {
						const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))))
						return arcGenerator.innerRadius(outerRadius - barHeight).outerRadius(outerRadius)({ data: d }, i)
					})
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
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
	if (selectedgenre_group) {
		bars.selectAll('g.bar-group').classed('same-group', item => item?.genre_group === selectedgenre_group)
	}
}

const emit = defineEmits(['update:isDescriptionVisible', 'bar-click', 'year-changed'])

const recomputeSpinPaused = () => {
	isSpinPaused = pauseHover || pauseYearTransition || pauseSelection || props.isDescriptionVisible || props.isIntroVisible
}

const handleBarClick = async (event, d) => {
	pauseSelection = true
	recomputeSpinPaused()
	selectedId = d.id
	selectedgenre_group = d.genre_group

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
			.classed('same-group', item => item?.genre_group === d.genre_group)
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

	const year = yearValue.value
	const decade = Math.floor(year / 10) * 10
	let detailedData = null
	
	try {
		const decadeData = await import(`../api/decades/${decade}.json`)
		if (decadeData.default?.[d.genre_group]?.[d.genre]) {
			detailedData = decadeData.default[d.genre_group][d.genre]
		} else {
			console.warn(`Genre data not found for ${d.genre_group} > ${d.genre} in ${decade}s`)
		}
	} catch (error) {
		console.error(`Failed to load detailed data for ${decade}:`, error)
	}

	emit('update:isDescriptionVisible', true);
	emit('bar-click', {
		genre_group: d.genre_group,
		genre: d.genre,
		genreName: d.genre,
		isPeak: d.isPeak,
		year: yearValue.value,
		decade: decade,
		count: d.count,
		percentage: d.percentage,
		detailedData: detailedData
	});
}

watch(yearValue, (newYear) => {
	pauseYearTransition = true
	emit('year-changed', newYear)
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
		selectedgenre_group = null
		pauseSelection = false
		recomputeSpinPaused()
	}
})

watch(() => props.isIntroVisible, () => {
	recomputeSpinPaused()
})

onMounted(async () => {
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
	
	genre_groupColors = {
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
	if (spinTimer) {
		spinTimer.stop()
		spinTimer = null
	}
	
	if (yearPauseTimeout) {
		yearPauseTimeout.stop()
		yearPauseTimeout = null
	}
	
	if (svg) {
		svg.on('mouseenter', null)
		svg.on('mouseleave', null)
	}
	
	if (bars) {
		bars.selectAll('g.bar-group').on('click', null)
	}
	
	if (spinGroup) {
		spinGroup.interrupt()
	}
})

</script>