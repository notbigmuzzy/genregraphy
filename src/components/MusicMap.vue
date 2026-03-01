<template>
    <div id="musicMap" class="music-map" ref="mapContainer">
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { interpolatePath } from 'd3-interpolate-path'

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

// 1. MACRO LAYOUT: Fiksne proporcije (value: 1) osiguravaju da makro-krugovi UVEK stoje 
    // zakucani na idealnim apsolutnim koordinatama za svaku grupu, tako da nema zamene mesta.
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
    
    // Potreban nam je globalni total ove dekade da bismo izracunali prostor
    let globalTotal = 0
    yearData.genre_group.forEach(g => { globalTotal += g.total })

    // 2. MICRO LAYOUT: I dok su centar svake grupe fiksni, velicina kojom mikropakovanje 
    // zraci naokolo (i time pomera Voronoi zidove) zavisi isključivo od grupnjog totala.
    macroNodes.forEach(macroNode => {
        const groupName = macroNode.data.name

        const groupMatch = yearData.genre_group.find(g => g.name === groupName)
        const realGenres = groupMatch 
            ? Object.entries(groupMatch.genres).filter(([_, count]) => count > 0).sort((a, b) => a[0].localeCompare(b[0]))
            : []

        // Prazne grupe preskacemo, njihovu teritoriju upiju ostale.
        if (realGenres.length === 0) {
            return
        }

        // Velicinu racunamo na osnovu root zapremine (ukupnih vrednosti dece = genre count).
        // Voronoi ce posle to mapirati na podlogu, mada Voronoi granice najvise zavise od raseajnosti centara 
        // a ne samo od precnika. 
        const groupTotal = groupMatch.total || 0
        
        // Racunamo razmeru povrsine: procenat koji grupa zauzima u godini u odnosu na apsolutno sve
        const areaRatio = globalTotal > 0 ? groupTotal / globalTotal : 0.01 
        
        // Da bismo iz povrsine dobili dijagonalu za krug (pack radi po precnicima), 
        // primenjujemo kvadratni koren proporcije pomnozen sa raspolozivim prostorom.
        const scaleFactor = Math.sqrt(areaRatio)
        const maxDiameter = Math.min(width, height) * 0.95
        const dynamicDiameter = Math.max(20, scaleFactor * maxDiameter) // min 20 da se ne izgubi potpuno

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
            .size([dynamicDiameter, dynamicDiameter])
            .padding(3)

        const packedLeaves = pack(root).leaves()

        // Centriramo dinamicki spakovanu grupu tacno na onaj stabilni fiksni makro-centar
        const offsetX = macroNode.x - (dynamicDiameter / 2)
        const offsetY = macroNode.y - (dynamicDiameter / 2)

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

    let svgGroup = svg.select('g.main-group')
    if (svgGroup.empty()) {
        svgGroup = svg.append('g').attr('class', 'main-group')
    }

    const groupContainers = svgGroup.selectAll('.genre-group-container')
        .data(allGroups)
        .join(
            enter => enter.append('g')
                .attr('class', d => `genre-group-container genre-group-${d.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`)
                .attr('data-group', d => d),
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
                   .attr('stroke', '#fff')
                   .attr('stroke-width', 1.5)
                   .attr('opacity', 0) // start invisible
                   .attr('d', d => {
                        // Initial small shape at target position - using a polygon (rhombus) 
                        // instead of circle arc to make interpolation to Voronoi polygon smoother
                        return `M${d.x},${d.y-1}L${d.x+1},${d.y}L${d.x},${d.y+1}L${d.x-1},${d.y}Z`
                   })
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

                g.append('text')
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'middle')
                    .style('fill', '#000')
                    .style('pointer-events', 'none')
                    .style('font-weight', 'bold')
                    .style('font-size', '11px')
                    .text(d => d.data.isDummy ? d.data.group : d.data.name)
                    .style('opacity', 0) // start invisible
                    .attr('x', d => d.x)
                    .attr('y', d => d.y)

                return g
            },
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )

    // Update paths with smooth interpolation
    genreCells.select('path')
        .transition()
        .duration(750)
        .attrTween("d", function(d) {
            let previous = d3.select(this).attr("d");
            
            // Fallback if previous is missing or weird, ensure we start from the node center
            if (!previous || previous.indexOf('M0,0') === 0) {
                 previous = `M${d.x},${d.y-1}L${d.x+1},${d.y}L${d.x},${d.y+1}L${d.x-1},${d.y}Z`;
            }

            const index = nodes.indexOf(d);
            const current = voronoi.renderCell(index);
            return interpolatePath(previous, current || previous);
        })
        .attr('opacity', d => d.data.isDummy ? 0.1 : 0.9)

    // Update texts
    genreCells.select('text')
        .transition()
        .duration(750)
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .style('opacity', d => d.data.isDummy ? 0.3 : 1)
        .end().then(() => {
             // Font size adjustment
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

// Prati promene podataka ili promene godine kako bi se Voronoi refreshovao!
watch([() => props.genres, () => props.year], drawMap, { deep: true })
</script>
