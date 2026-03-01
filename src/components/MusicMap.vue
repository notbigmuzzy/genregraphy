<template>
    <div id="musicMap" class="music-map" ref="mapContainer">
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
    genres: {
        type: [Object, Array],
        required: true
    }
})

const mapContainer = ref(null)
let resizeObserver = null

const drawMap = () => {
    if (!props.genres || !mapContainer.value) return
    
    const yearData = props.genres['1950']
    if (!yearData) return

    const groupsData = yearData.genre_group.filter(g => g.total > 0)
    if (groupsData.length === 0) return

    const width = mapContainer.value.clientWidth
    const height = mapContainer.value.clientHeight
    
    if (width === 0 || height === 0) return

    d3.select(mapContainer.value).selectAll('*').remove()

    const svg = d3.select(mapContainer.value)
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')

    const hierarchyData = {
        name: 'root',
        children: groupsData.map(group => ({
            name: group.name,
            total: group.total,
            children: Object.entries(group.genres)
                .filter(([_, count]) => count > 0)
                .map(([name, count]) => ({
                    name: name,
                    group: group.name,
                    value: count
                }))
        }))
    }

    const root = d3.hierarchy(hierarchyData)
        .sum(d => Math.max(1, d.value || 0))
        .sort((a, b) => b.value - a.value)

    const pack = d3.pack()
        .size([width, height])
        .padding(1)

    const nodes = pack(root).leaves()

    const delaunay = d3.Delaunay.from(nodes, d => d.x, d => d.y)
    const voronoi = delaunay.voronoi([0, 0, width, height])

    const colorScale = d3.scaleOrdinal(d3.schemePaired)

    const cells = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', d => `genre-group ${d.data.group.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`)
        .attr('data-group', d => d.data.group)
        .classed('genre', true)
        .classed(d => d.data.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'), true)

    cells.append('path')
        .attr('d', (d, i) => voronoi.renderCell(i))
        .attr('fill', d => colorScale(d.data.group))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.9)
        .on('mouseenter', function() {
            d3.select(this)
                .attr('opacity', 1)
                .attr('stroke-width', 3)
        })
        .on('mouseleave', function() {
            d3.select(this)
                .attr('opacity', 0.9)
                .attr('stroke-width', 1.5)
        })

    const texts = cells.append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .style('fill', '#000')
        .style('pointer-events', 'none')
        .style('font-weight', 'bold')
        .style('font-size', '11px')
        .text(d => d.data.name)

    texts.each(function(d) {
        let textWidth = this.getBBox().width
        let availableWidth = d.r * 2 - 4
        if (textWidth > availableWidth && availableWidth > 0) {
            d3.select(this).style('font-size', `${Math.max(6, availableWidth / textWidth * 11)}px`)
        }
    })
}

onMounted(() => {
    drawMap()
    
    resizeObserver = new ResizeObserver((entries) => {
        window.requestAnimationFrame(() => {
            if (entries.length > 0) {
                drawMap()
            }
        })
    })

    if (mapContainer.value) {
        resizeObserver.observe(mapContainer.value)
    }
})

onUnmounted(() => {
    if (resizeObserver && mapContainer.value) {
        resizeObserver.unobserve(mapContainer.value)
    }
})

watch(() => props.genres, drawMap, { deep: true })
</script>
