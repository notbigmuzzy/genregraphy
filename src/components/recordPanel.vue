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
					<g class="center-button" @click="handleCenterClick" style="cursor: pointer;">
						<circle cx="0" cy="0" r="12" fill="transparent" stroke="lightcoral" stroke-width="0.5"/>
						<text class="year-center" x="0" y="1" text-anchor="middle" dominant-baseline="middle">
							{{ yearValue }}
							<!-- {{ hoveredPercentage !== null ? hoveredPercentage : (viewMode === 'groups' ? yearValue : 'Back') }} -->
						</text>
					</g>
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
const viewMode = ref('groups')
const activeGroup = ref(null)
const hoveredPercentage = ref(null)
const chartSvg = ref(null)
let svg, spinGroup, bars, grooves, labels, innerRadius, outerRadius, genre_groupColors, currentGenreData = []
let selectedBar = null
let selectedId = null
let selectedgenre_group = null
let lastClickedGroupAngle = { start: 0, end: 0 }

const spinDurationInMs = 45_000
const spinDegPerMs = 360 / spinDurationInMs
let spinAngleDeg = 0
let isSpinPaused = false
let spinTimer = null
let prevElapsedMs = 0
let momentumVelocity = 0

let pauseHover = false
let pauseYearTransition = false
let pauseSelection = false
let yearPauseTimeout = null

const updateChart = (year) => {
	const yearData = genresData[year.toString()]
	const mappedTotalForTheYear = yearData.metadata.mapped_total
	const peakGenres = yearData.metadata.peak_genres
	const chartData = []

	if (viewMode.value === 'groups') {
		for (const genre_group of yearData.genre_group) {
			if (genre_group.total > 0) {
				chartData.push({
					id: `group::${genre_group.name}`,
					type: 'group',
					name: genre_group.name,
					genre_group: genre_group.name,
					total: genre_group.total,
					percentage: genre_group.total / mappedTotalForTheYear,
					isPeak: false
				})
			}
		}
		chartData.sort((a, b) => a.name.localeCompare(b.name))
	} else {
		const activeGroupData = yearData.genre_group.find(g => g.name === activeGroup.value)
		if (activeGroupData) {
			for (const [genre, count] of Object.entries(activeGroupData.genres)) {
				if (count > 0) {
					chartData.push({
						id: `${activeGroupData.name}::${genre}`,
						type: 'genre',
						genre_group: activeGroupData.name,
						genre,
						name: genre,
						count,
						total: activeGroupData.total,
						percentage: activeGroupData.total > 0 ? count / activeGroupData.total : 0,
						isPeak: peakGenres.includes(genre)
					})
				}
			}
			chartData.sort((a, b) => a.genre.localeCompare(b.genre))
		}
	}
	
	currentGenreData = chartData
	
	const numBars = chartData.length
	
	// Ako nema podataka (npr. prazna grupa u određenoj godini), izlazimo ranije
	if (numBars === 0) {
		bars.selectAll('g.bar-group')
			.data([])
			.exit()
			.transition()
			.duration(400)
			.attr('opacity', 0)
			.remove()
		return
	}

	const angleScale = d3.scaleLinear()
		.domain([0, numBars])
		.range([0, 2 * Math.PI])
	
	const heightScale = d3.scalePow()
		.exponent(0.5)
		.domain([0, 1])
		.range([0, outerRadius - innerRadius])
		.clamp(true)
	
	const arcGenerator = d3.arc()
		.innerRadius(d => d.innerRadius)
		.outerRadius(d => d.outerRadius)
		.startAngle(d => d.startAngle)
		.endAngle(d => d.endAngle)

	const layoutData = chartData.map((d, i) => {
		const startAngle = angleScale(i);
		const endAngle = numBars === 1 ? angleScale(i + 1) - 0.001 : Math.max(angleScale(i) + 0.001, angleScale(i + 1) - 0.005);
		const barHeight = Math.max(1, Math.floor(heightScale(Math.max(d.percentage, 0.001))));
		
		return {
			...d,
			startAngle,
			endAngle,
			bgInnerRadius: innerRadius,
			bgOuterRadius: outerRadius,
			fgInnerRadius: outerRadius - barHeight,
			fgOuterRadius: outerRadius,
			midAngle: (startAngle + endAngle) / 2
		};
	});
	
	const barGroups = bars.selectAll('g.bar-group')
		.data(layoutData, d => d.id)
		.join(
			enter => {
				const g = enter.append('g')
					.attr('class', d => {
						const nameClass = d.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')
						return d.isPeak ? `bar-group peak ${d.type}-${nameClass}` : `bar-group ${d.type}-${nameClass}`
					})
					.attr('data-type', d => d.type)
					.attr('data-genre_group', d => d.genre_group)
					.attr('data-name', d => d.name)
					.attr('data-id', d => d.id)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
					.on('click', handleBarClick)
					.on('mouseenter', (event, d) => {
						hoveredPercentage.value = `${(d.percentage * 100).toFixed(1)}%`
					})
					.on('mouseleave', () => {
						hoveredPercentage.value = null
					})
				
				g.append('path')
					.attr('class', 'bar-bg')
					.each(function(d) { 
						let initialStart = d.startAngle;
						let initialEnd = d.endAngle;
						if (viewMode.value === 'genres' && lastClickedGroupAngle.start !== lastClickedGroupAngle.end) {
							const groupSpan = lastClickedGroupAngle.end - lastClickedGroupAngle.start;
							initialStart = lastClickedGroupAngle.start + (d.startAngle / (2 * Math.PI)) * groupSpan;
							initialEnd = lastClickedGroupAngle.start + (d.endAngle / (2 * Math.PI)) * groupSpan;
						}
						this._current = { ...d, innerRadius: d.bgInnerRadius, outerRadius: d.bgOuterRadius, startAngle: initialStart, endAngle: initialEnd }; 
					})
					.attr('d', function(d) { return arcGenerator(this._current); })
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
					.attr('opacity', 0)
					.transition()
					.duration(800)
					.ease(d3.easeCubicOut)
					.attr('opacity', 0.2)
					.attrTween('d', function(d) {
						const target = { ...d, innerRadius: d.bgInnerRadius, outerRadius: d.bgOuterRadius };
						const i = d3.interpolate(this._current, target);
						this._current = target;
						return t => arcGenerator(i(t));
					})
				
				g.append('path')
					.attr('class', 'bar-fg')
					.each(function(d) { 
						let initialStart = d.startAngle;
						let initialEnd = d.endAngle;
						if (viewMode.value === 'genres' && lastClickedGroupAngle.start !== lastClickedGroupAngle.end) {
							const groupSpan = lastClickedGroupAngle.end - lastClickedGroupAngle.start;
							initialStart = lastClickedGroupAngle.start + (d.startAngle / (2 * Math.PI)) * groupSpan;
							initialEnd = lastClickedGroupAngle.start + (d.endAngle / (2 * Math.PI)) * groupSpan;
						}
						this._current = { ...d, innerRadius: d.fgInnerRadius, outerRadius: d.fgOuterRadius, startAngle: initialStart, endAngle: initialEnd }; 
					})
					.attr('d', function(d) { return arcGenerator(this._current); })
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
					.attr('opacity', 0)
					.transition()
					.duration(800)
					.ease(d3.easeCubicOut)
					.attr('opacity', 0.8)
					.attrTween('d', function(d) {
						const target = { ...d, innerRadius: d.fgInnerRadius, outerRadius: d.fgOuterRadius };
						const i = d3.interpolate(this._current, target);
						this._current = target;
						return t => arcGenerator(i(t));
					})
				
				g.append('text')
					.attr('class', 'bar-label')
					.attr('text-anchor', 'start')
					.attr('dominant-baseline', 'middle')
					.attr('opacity', 0)
					.text(d => d.name)
					.each(function(d) {
						let initialMid = d.midAngle;
						if (viewMode.value === 'genres' && lastClickedGroupAngle.start !== lastClickedGroupAngle.end) {
							const groupSpan = lastClickedGroupAngle.end - lastClickedGroupAngle.start;
							initialMid = lastClickedGroupAngle.start + (d.midAngle / (2 * Math.PI)) * groupSpan;
						}
						this._currentAngle = initialMid;
					})
					.attr('transform', function(d) {
						const angleDeg = (this._currentAngle * 180) / Math.PI;
						const r = outerRadius - 0.8;
						return `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`;
					})
					.transition()
					.duration(800)
					.ease(d3.easeCubicOut)
					.attrTween('transform', function(d) {
						const targetAngle = d.midAngle;
						const i = d3.interpolate(this._currentAngle, targetAngle);
						this._currentAngle = targetAngle;
						return t => {
							const angleDeg = (i(t) * 180) / Math.PI;
							const r = outerRadius - 0.8;
							return `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`;
						};
					})
					.attr('opacity', 1)
				
				return g
			},
			update => {
				update
					.attr('class', d => {
						const nameClass = d.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')
						return d.isPeak ? `bar-group peak ${d.type}-${nameClass}` : `bar-group ${d.type}-${nameClass}`
					})
					.attr('data-type', d => d.type)
					.attr('data-genre_group', d => d.genre_group)
					.attr('data-name', d => d.name)
					.attr('data-is-peak', d => d.isPeak ? 'true' : 'false')
					.on('mouseenter', (event, d) => {
						hoveredPercentage.value = `${(d.percentage * 100).toFixed(1)}%`
					})
					.on('mouseleave', () => {
						hoveredPercentage.value = null
					})
				
				update.select('path.bar-bg')
					.transition()
					.duration(600)
					.ease(d3.easeCubicOut)
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
					.attr('opacity', 0.2)
					.attrTween('d', function(d) {
						const target = { ...d, innerRadius: d.bgInnerRadius, outerRadius: d.bgOuterRadius };
						const i = d3.interpolate(this._current || target, target);
						this._current = target;
						return t => arcGenerator(i(t));
					})
				
				update.select('path.bar-fg')
					.transition()
					.duration(600)
					.ease(d3.easeCubicOut)
					.attr('fill', d => genre_groupColors[d.genre_group] || 'lightcoral')
					.attr('opacity', 0.8)
					.attrTween('d', function(d) {
						const target = { ...d, innerRadius: d.fgInnerRadius, outerRadius: d.fgOuterRadius };
						const i = d3.interpolate(this._current || target, target);
						this._current = target;
						return t => arcGenerator(i(t));
					})
				
				update.select('text.bar-label')
					.text(d => d.name)
					.transition()
					.duration(600)
					.ease(d3.easeCubicOut)
					.attrTween('transform', function(d) {
						const targetAngle = d.midAngle;
						const currentAngle = this._currentAngle !== undefined ? this._currentAngle : targetAngle;
						const i = d3.interpolate(currentAngle, targetAngle);
						this._currentAngle = targetAngle;
						return t => {
							const angleDeg = (i(t) * 180) / Math.PI;
							const r = outerRadius - 0.8;
							return `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`;
						};
					})
					.attr('opacity', 1)
				
				return update
			},
			exit => exit
				.transition()
				.duration(600)
				.ease(d3.easeCubicIn)
				.attr('opacity', 0)
				.tween('collapse', function(d) {
					if (viewMode.value === 'groups' && lastClickedGroupAngle.start !== lastClickedGroupAngle.end) {
						const groupSpan = lastClickedGroupAngle.end - lastClickedGroupAngle.start;
						const targetStart = lastClickedGroupAngle.start + (d.startAngle / (2 * Math.PI)) * groupSpan;
						const targetEnd = lastClickedGroupAngle.start + (d.endAngle / (2 * Math.PI)) * groupSpan;
						
						const bgPath = d3.select(this).select('path.bar-bg').node();
						const fgPath = d3.select(this).select('path.bar-fg').node();
						const textNode = d3.select(this).select('text.bar-label').node();
						
						const iStart = d3.interpolate(d.startAngle, targetStart);
						const iEnd = d3.interpolate(d.endAngle, targetEnd);
						const iMid = d3.interpolate(d.midAngle, (targetStart + targetEnd) / 2);
						
						return t => {
							const s = iStart(t);
							const e = iEnd(t);
							if (bgPath && bgPath._current) {
								bgPath._current.startAngle = s;
								bgPath._current.endAngle = e;
								d3.select(bgPath).attr('d', arcGenerator(bgPath._current));
							}
							if (fgPath && fgPath._current) {
								fgPath._current.startAngle = s;
								fgPath._current.endAngle = e;
								d3.select(fgPath).attr('d', arcGenerator(fgPath._current));
							}
							if (textNode) {
								const angleDeg = (iMid(t) * 180) / Math.PI;
								const r = outerRadius - 0.8;
								d3.select(textNode).attr('transform', `rotate(${angleDeg}) translate(0, -${r}) rotate(90)`);
							}
						};
					}
				})
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

const handleCenterClick = () => {
	if (viewMode.value === 'genres') {
		viewMode.value = 'groups'
		activeGroup.value = null
		emit('update:isDescriptionVisible', false)
		updateChart(yearValue.value)
	}
}

const handleBarClick = async (event, d) => {
	if (d.type === 'group') {
		const barIndex = currentGenreData.findIndex(item => item.id === d.id)
		const numBars = currentGenreData.length
		const anglePerBar = (2 * Math.PI) / numBars
		lastClickedGroupAngle = {
			start: barIndex * anglePerBar,
			end: (barIndex + 1) * anglePerBar - 0.005
		}

		activeGroup.value = d.name
		viewMode.value = 'genres'
		updateChart(yearValue.value)
		return
	}

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

		if (momentumVelocity !== 0) {
			momentumVelocity *= Math.pow(0.95, dt / 10)
			if (Math.abs(momentumVelocity) < 0.001) momentumVelocity = 0
		}

		if (pauseYearTransition || pauseSelection || props.isDescriptionVisible || props.isIntroVisible) {
			momentumVelocity = 0
			return
		}

		let velocity = momentumVelocity
		if (!pauseHover) {
			velocity += spinDegPerMs
		}

		if (velocity !== 0) {
			spinAngleDeg = (spinAngleDeg + velocity * dt) % 360
			spinGroup.attr('transform', `rotate(${spinAngleDeg})`)
		}
	})

	svg.on('mouseenter', () => {
		pauseHover = true
		recomputeSpinPaused()
	})

	svg.on('wheel', (event) => {
		event.preventDefault()
		const delta = event.deltaY
		momentumVelocity += delta * 0.0003
	}, { passive: false })

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
		svg.on('wheel', null)
	}
	
	if (bars) {
		bars.selectAll('g.bar-group').on('click', null)
	}
	
	if (spinGroup) {
		spinGroup.interrupt()
	}
})

</script>