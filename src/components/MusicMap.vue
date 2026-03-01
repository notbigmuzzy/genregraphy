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
    },
    year: {
        type: Number,
        required: true
    }
})

const mapContainer = ref(null)
let resizeObserver = null

const drawMap = () => {
    if (!props.genres || !mapContainer.value) return

    
    const yearData = props.genres[props.year.toString()]
    if (!yearData || !yearData.genre_group) return

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

    const allGroups = [
        "Classical & Experimental", "Electronic & Synth", "Folk & Acoustics",
        "Hip-Hop & Groove", "Jazz, Blues & Soul", "Metal & Heavy",
        "Pop & Melodies", "Reggae & Global Beats", "Rock & Overdrive"
    ]

    // 1. MACRO LAYOUT: Fiksiramo 9 glavnih grupa u nezavisne, fiksne krugove
    // koji nikada ne smeju menjati poziciju niti velicinu kroz godine!
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

    // 2. MICRO LAYOUT: Svaka grupa pakuje SVOJE zanrove ISKLJUCIVO unutar svog dodeljenog fiksnog kruga
    macroNodes.forEach(macroNode => {
        const groupName = macroNode.data.name
        
        const groupMatch = yearData.genre_group.find(g => g.name === groupName)
        const realGenres = groupMatch 
            ? Object.entries(groupMatch.genres).filter(([_, count]) => count > 0).sort((a, b) => a[0].localeCompare(b[0]))
            : []

        // Ako u potpunosti nema žanrova, ne ubacujemo ovu grupu u nodes zaVoronoi mapu UOPŠTE. 
        // Voronoi prosto nastavlja granice ostalih aktivnih preko te teritorije.
        if (realGenres.length === 0) {
            return
        }

        const diameter = Math.floor(macroNode.r * 2)
        const hierarchyData = {
            name: groupName,
            children: realGenres.map(([name, count]) => ({
                name: name, group: groupName, value: count, isDummy: false
            }))
        }

        const root = d3.hierarchy(hierarchyData)
            .sum(d => d.value)
            .sort((a, b) => (a.data.name || '').localeCompare(b.data.name || ''))

        const pack = d3.pack()
            .size([diameter, diameter])
            .padding(3)

        const packedLeaves = pack(root).leaves()

        const offsetX = macroNode.x - macroNode.r
        const offsetY = macroNode.y - macroNode.r

        packedLeaves.forEach(leaf => {
            leaf.x += offsetX
            leaf.y += offsetY
            nodes.push(leaf)
        })
    })

    // U retkom slučaju da su svi žanrovi ikada ugašeni u ovoj godini, vraćamo odmah
    if (nodes.length === 0) return

    // Obezbedjujemo konzistentan redosled zbog Voronoi algoritma
    nodes.sort((a, b) => {
        const indexA = allGroups.indexOf(a.data.group)
        const indexB = allGroups.indexOf(b.data.group)
        if (indexA !== indexB) return indexA - indexB
        return (a.data.name || '').localeCompare(b.data.name || '')
    })

    const delaunay = d3.Delaunay.from(nodes, d => d.x, d => d.y)
    const voronoi = delaunay.voronoi([0, 0, width, height])

    const colorScale = d3.scaleOrdinal()
        .domain(allGroups)
        .range(d3.schemePaired)

    const cells = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', d => {
            const groupClass = `genre-group-${d.data.group.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
            const nameClass = d.data.name ? d.data.name.toLowerCase().replace(/[^a-z0-9]+/g, '-') : 'dummy'
            return `${groupClass} genre ${nameClass}`
        })
        .attr('data-group', d => d.data.group)

    cells.append('path')
        .attr('d', (d, i) => voronoi.renderCell(i))
        .attr('fill', d => colorScale(d.data.group))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .attr('opacity', d => d.data.isDummy ? 0.1 : 0.9)
        .on('mouseenter', function(event, d) {
            if (d.data.isDummy) return
            d3.select(this)
                .attr('opacity', 1)
                .attr('stroke-width', 3)
        })
        .on('mouseleave', function(event, d) {
            if (d.data.isDummy) return
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
        .text(d => d.data.isDummy ? d.data.group : d.data.name)
        .style('opacity', d => d.data.isDummy ? 0.3 : 1)

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

// Prati promene podataka ili promene godine kako bi se Voronoi refreshovao!
watch([() => props.genres, () => props.year], drawMap, { deep: true })
</script>
