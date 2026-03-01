<template>
    <div class="music-map-wrapper">
        <div id="musicMap" class="music-map" ref="mapContainer"/>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { interpolatePath } from 'd3-interpolate-path'
import { continentShape } from '../utils/defaultContinent.js'

const props = defineProps({
    genres: {
        type: [Object, Array],
        required: true
    },
    year: {
        type: Number,
        required: true
    }
})

const mapContainer = ref(null)
let resizeObserver = null

let cachedMapWidth = 0
let cachedMapHeight = 0
let cachedContinentPath = ''

const drawMap = () => {
    if (!props.genres || !mapContainer.value) return

    
    const yearData = props.genres[props.year.toString()]
    if (!yearData || !yearData.genre_group) return

    const groupsData = yearData.genre_group.filter(g => g.total > 0)
    if (groupsData.length === 0) return

    const width = mapContainer.value.clientWidth
    const height = mapContainer.value.clientHeight

    if (width === 0 || height === 0) return

    let svg = d3.select(mapContainer.value).select('svg')
    if (svg.empty()) {
        svg = d3.select(mapContainer.value)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
    }
    
    svg.attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')

    const allGroups = [
        "Classical & Experimental", "Electronic & Synth", "Folk & Acoustics",
        "Hip-Hop & Groove", "Jazz, Blues & Soul", "Metal & Heavy",
        "Pop & Melodies", "Reggae & Global Beats", "Rock & Overdrive"
    ]


    
    const macroHierarchy = d3.hierarchy({
        name: 'root',
        children: allGroups.map(name => ({ name, value: 1 }))
    }).sum(d => d.value)
      .sort((a, b) => a.data.name.localeCompare(b.data.name))

    const macroPack = d3.pack()
        .size([width, height])
        .padding(10)

    const macroNodes = macroPack(macroHierarchy).leaves()

    let nodes = []
    let globalLogTotal = 0
    yearData.genre_group.forEach(g => { 
        if (g.total > 0) globalLogTotal += (Math.log(g.total + 1) * 2) + 4
    })

    macroNodes.forEach(macroNode => {
        const groupName = macroNode.data.name

        const groupMatch = yearData.genre_group.find(g => g.name === groupName)
        const realGenres = groupMatch 
            ? Object.entries(groupMatch.genres).filter(([_, count]) => count > 0).sort((a, b) => a[0].localeCompare(b[0]))
            : []

        
        if (realGenres.length === 0) {
            return
        }

        const groupTotal = groupMatch.total || 0
        const groupLogTotal = groupTotal > 0 ? (Math.log(groupTotal + 1) * 2) + 4 : 0
        const areaRatio = globalLogTotal > 0 ? groupLogTotal / globalLogTotal : 0.01 

        const scaleFactor = Math.sqrt(areaRatio)
        const maxDiameter = Math.min(width, height) * 0.95
        const dynamicDiameter = Math.max(20, scaleFactor * maxDiameter) 

        const hierarchyData = {
            name: groupName,
            children: realGenres.map(([name, count]) => ({
                name: name, group: groupName, value: count, isDummy: false
            }))
        }

        const root = d3.hierarchy(hierarchyData)
            .sum(d => d.value > 0 ? (Math.log(d.value + 1) * 2) + 4 : 0) 
            .sort((a, b) => (a.data.name || '').localeCompare(b.data.name || ''))

        const pack = d3.pack()
            .size([dynamicDiameter, dynamicDiameter])
            .padding(3)

        const packedLeaves = pack(root).leaves()
        const offsetX = macroNode.x - (dynamicDiameter / 2)
        const offsetY = macroNode.y - (dynamicDiameter / 2)

        packedLeaves.forEach(leaf => {
            leaf.x += offsetX
            leaf.y += offsetY
            nodes.push(leaf)
        })
    })

    if (nodes.length === 0) return

    nodes.sort((a, b) => {
        const indexA = allGroups.indexOf(a.data.group)
        const indexB = allGroups.indexOf(b.data.group)
        if (indexA !== indexB) return indexA - indexB
        return (a.data.name || '').localeCompare(b.data.name || '')
    })

    const delaunay = d3.Delaunay.from(nodes, d => d.x, d => d.y)
    
    // Define continent shape
    if (!cachedContinentPath || cachedMapWidth !== width || cachedMapHeight !== height) {
        cachedContinentPath = continentShape(width, height)
        cachedMapWidth = width
        cachedMapHeight = height
    }
    const continentPath = cachedContinentPath
    
    // Instead of rectangular box, we use the continent shape for clipping visually
    // However, Delaunay still needs a bounding box for calculation.
    // Ideally we'd use a large enough box to encompass the shape.
    const voronoi = delaunay.voronoi([0, 0, width, height])

    const colorScale = d3.scaleOrdinal()
        .domain(allGroups)
        .range(d3.schemePaired)

    // Add definitions for clip path
    let defs = svg.select('defs')
    if (defs.empty()) {
        defs = svg.append('defs')
    }

    const groupOutlineFilter = defs.selectAll('#group-outline')
        .data([1])
        .join('filter')
        .attr('id', 'group-outline')
        .attr('x', '-10%')
        .attr('y', '-10%')
        .attr('width', '120%')
        .attr('height', '120%')

    if (groupOutlineFilter.select('feMorphology').empty()) {
        groupOutlineFilter.append('feMorphology')
            .attr('in', 'SourceAlpha')
            .attr('operator', 'dilate')
            .attr('radius', '3')
            .attr('result', 'dilated')
        
        groupOutlineFilter.append('feFlood')
            .attr('flood-color', '#fff')
            .attr('flood-opacity', '1')
            .attr('result', 'flood')
            
        groupOutlineFilter.append('feComposite')
            .attr('in', 'flood')
            .attr('in2', 'dilated')
            .attr('operator', 'in')
            .attr('result', 'outline')
            
        // Knock out the inner part so it's strictly a border 
        // that doesn't affect the fill opacity of the source graphic
        groupOutlineFilter.append('feComposite')
            .attr('in', 'outline')
            .attr('in2', 'SourceAlpha')
            .attr('operator', 'out')
            .attr('result', 'borderOnly')

        const merge = groupOutlineFilter.append('feMerge')
        merge.append('feMergeNode').attr('in', 'borderOnly')
        merge.append('feMergeNode').attr('in', 'SourceGraphic')
    }
    
    const clipPath = defs.selectAll('#continent-clip')
        .data([continentPath])
        .join('clipPath')
        .attr('id', 'continent-clip')
    
    clipPath.selectAll('path')
        .data([continentPath])
        .join('path')
        .attr('d', d => d)

    // Draw background shape (coastline)
    let bgGroup = svg.select('g.background-group')
    if (bgGroup.empty()) {
        bgGroup = svg.insert('g', ':first-child').attr('class', 'background-group')
    }
    
    bgGroup.selectAll('path.continent-coast')
        .data([continentPath])
        .join('path')
        .attr('class', 'continent-coast')
        .attr('d', d => d)
        .attr('fill', '#f0f0f0') // Light background for the "land"
        .attr('stroke', '#ccc')
        .attr('stroke-width', 2)
        .attr('opacity', 0.5)

    let svgGroup = svg.select('g.main-group')
    if (svgGroup.empty()) {
        svgGroup = svg.append('g').attr('class', 'main-group')
    }
    
    // Apply clip path to the main group
    svgGroup.attr('clip-path', 'url(#continent-clip)')

    const groupContainers = svgGroup.selectAll('.genre-group-container')
        .data(allGroups)
        .join(
            enter => enter.append('g')
                .attr('class', d => `genre-group-container genre-group-${d.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`)
                .attr('data-group', d => d)
                .style('filter', 'url(#group-outline)'),
            update => update,
            exit => exit.remove()
        )

    const genreCells = groupContainers.selectAll('.genre')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name) 
        .join(
            enter => {
                const g = enter.append('g')
                    .attr('class', d => {
                        const nameClass = d.data.name ? d.data.name.toLowerCase().replace(/[^a-z0-9]+/g, '-') : 'dummy'
                        return `genre ${nameClass}`
                    })
                
                g.append('path')
                   .attr('fill', d => colorScale(d.data.group))
                   .attr('stroke', 'rgba(255, 255, 255, 0.4)')
                   .attr('stroke-width', 0.5)
                   .attr('opacity', 0) 
                   .attr('d', d => {
                        
                        
                        return `M${d.x},${d.y-1}L${d.x+1},${d.y}L${d.x},${d.y+1}L${d.x-1},${d.y}Z`
                   })
                   .on('mouseenter', function(event, d) {
                        if (d.data.isDummy) return
                        d3.select(this)
                            .attr('opacity', 1)
                            .attr('stroke', '#fff')
                            .attr('stroke-width', 2)
                    })
                    .on('mouseleave', function(event, d) {
                        if (d.data.isDummy) return
                        d3.select(this)
                            .attr('opacity', 0.9)
                            .attr('stroke', 'rgba(255, 255, 255, 0.4)')
                            .attr('stroke-width', 0.5)
                    })

                g.append('text')
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'middle')
                    .style('fill', '#000')
                    .style('pointer-events', 'none')
                    .style('font-weight', 'bold')
                    .style('font-size', '11px')
                    .text(d => d.data.isDummy ? d.data.group : d.data.name)
                    .style('opacity', 0) 
                    .attr('x', d => d.x)
                    .attr('y', d => d.y)

                return g
            },
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )

    genreCells.select('path')
        .transition()
        .duration(750)
        .attrTween("d", function(d) {
            let previous = d3.select(this).attr("d");
            
            
            if (!previous || previous.indexOf('M0,0') === 0) {
                 previous = `M${d.x},${d.y-1}L${d.x+1},${d.y}L${d.x},${d.y+1}L${d.x-1},${d.y}Z`;
            }

            const index = nodes.indexOf(d);
            const current = voronoi.renderCell(index);
            return interpolatePath(previous, current || previous);
        })
        .attr('opacity', d => d.data.isDummy ? 0.1 : 0.9)

    genreCells.select('text')
        .transition()
        .duration(750)
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .style('opacity', d => d.data.isDummy ? 0.3 : 1)
        .end().then(() => {
             
             genreCells.select('text').each(function(d) {
                let textWidth = this.getBBox().width
                let availableWidth = d.r * 2 - 4
                if (textWidth > availableWidth && availableWidth > 0) {
                    d3.select(this).style('font-size', `${Math.max(6, availableWidth / textWidth * 11)}px`)
                }
            })
        }).catch(() => {}) 
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

watch([() => props.genres, () => props.year], drawMap, { deep: true })
</script>
