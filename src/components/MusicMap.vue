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
    let globalTotal = 0
    yearData.genre_group.forEach(g => { 
        if (g.total > 0) {
            globalLogTotal += (Math.log(g.total + 1) * 2) + 4
            globalTotal += g.total
        }
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
        const baseRatio = 0.05; 
        const trueRatio = globalTotal > 0 ? (groupTotal / globalTotal) : 0;
        const areaRatio = baseRatio + (trueRatio * (1 - baseRatio * 9));

        const scaleFactor = Math.sqrt(areaRatio)
        const maxDiameter = Math.min(width, height) * 0.95
        const dynamicDiameter = Math.max(40, scaleFactor * maxDiameter) 

        const hierarchyData = {
            name: groupName,
            children: realGenres.map(([name, count]) => ({
                name: name, group: groupName, value: count, isDummy: false
            }))
        }

        const root = d3.hierarchy(hierarchyData)
            .sum(d => {
                if (!d.value || d.value <= 0) return 0;
                return 25 + (Math.log10(d.value) * 5);
            }) 
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
    
    if (!cachedContinentPath || cachedMapWidth !== width || cachedMapHeight !== height) {
        cachedContinentPath = continentShape(width, height)
        cachedMapWidth = width
        cachedMapHeight = height
    }
    const continentPath = cachedContinentPath
    
    const voronoi = delaunay.voronoi([0, 0, width, height])

    const colorScale = d3.scaleOrdinal()
        .domain(allGroups)
        .range(d3.schemePaired)

    
    let defs = svg.select('defs')
    if (defs.empty()) {
        defs = svg.append('defs')
    }
    
    
    
    
    
    const clipPath = defs.selectAll('#continent-clip')
        .data([continentPath])
        .join('clipPath')
        .attr('id', 'continent-clip')
    
    clipPath.selectAll('path')
        .data([continentPath])
        .join('path')
        .attr('d', d => d)

    
    let bgGroup = svg.select('g.background-group')
    if (bgGroup.empty()) {
        bgGroup = svg.insert('g', ':first-child').attr('class', 'background-group')
    }
    
    bgGroup.selectAll('path.continent-coast')
        .data([continentPath])
        .join('path')
        .attr('class', 'continent-coast')
        .attr('d', d => d)

    let svgGroup = svg.select('g.main-group')
    if (svgGroup.empty()) {
        svgGroup = svg.append('g').attr('class', 'main-group')
    }
    
    
    svgGroup.attr('clip-path', 'url(#continent-clip)')

    const groupContainers = svgGroup.selectAll('.genre-group-container')
        .data(allGroups)
        .join(
            enter => {
                const g = enter.append('g')
                    .attr('class', d => `genre-group-container genre-group-${d.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`)
                    .attr('data-group', d => d);
                
                
                
                g.append('g').attr('class', 'layer-outline');
                
                g.append('g').attr('class', 'layer-blob');
                
                g.append('g').attr('class', 'layer-internal');

                
                g.append('g').attr('class', 'genre-texts-layer');
                    
                return g;
            },
            update => update,
            exit => exit.remove()
        )

    const initialPath = d => `M${d.x},${d.y-1}L${d.x+1},${d.y}L${d.x},${d.y+1}L${d.x-1},${d.y}Z`;

    const makeId = d => 'genre-path-' + (d.data.group + '-' + d.data.name).replace(/[^a-zA-Z0-9-]/g, '-').toLowerCase();

    let defsPathsGroup = defs.select('g.genre-paths-defs');
    if (defsPathsGroup.empty()) {
        defsPathsGroup = defs.append('g').attr('class', 'genre-paths-defs');
    }

    const defPaths = defsPathsGroup.selectAll('path.genre-def-path')
        .data(nodes, d => d.data.name)
        .join(
            enter => enter.append('path')
                .attr('class', 'genre-def-path')
                .attr('id', makeId)
                .attr('d', initialPath),
            update => update,
            exit => exit.transition().duration(500).attr('d', initialPath).remove()
        );

    defPaths.transition()
        .duration(750)
        .attrTween("d", function(d) {
            let previous = d3.select(this).attr("d");
            if (!previous || previous === '' || previous.indexOf('M0,') >= 0 || previous.includes('NaN')) {
                 previous = initialPath(d);
            }
            const index = nodes.indexOf(d);
            const current = voronoi.renderCell(index);
            return interpolatePath(previous, current || previous);
        });

    groupContainers.select('.layer-outline').selectAll('use.shape-outline')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
               .attr('class', 'shape-outline')
               .attr('href', d => `#${makeId(d)}`),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .transition().duration(750).style('opacity', 1);

    groupContainers.select('.layer-blob').selectAll('use.shape-blob')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
               .attr('class', 'shape-blob')
               .attr('href', d => `#${makeId(d)}`)
               // Dynamic fill/stroke must stay in JS because it depends on the colorScale derived from the data
               .attr('fill', d => colorScale(d.data.group))
               .attr('stroke', d => colorScale(d.data.group)),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .transition().duration(750).style('opacity', 0.9);
        
    groupContainers.select('.layer-internal').selectAll('use.shape-internal')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
               .attr('class', 'shape-internal')
               .attr('href', d => `#${makeId(d)}`)
               .on('mouseenter', function(event, d) {
                    if (d.data.isDummy) return
                    d3.select(this).classed('is-hovered', true).raise()
                })
                .on('mouseleave', function(event, d) {
                    if (d.data.isDummy) return
                    d3.select(this).classed('is-hovered', false)
                }),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .transition().duration(750).style('opacity', d => d.data.isDummy ? 0.1 : 1);

    const textsLayer = groupContainers.select('.genre-texts-layer');
    const textCells = textsLayer.selectAll('.genre-label')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => {
                const textEl = enter.append('text')
                    .attr('class', 'genre-label')
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'central')
                    .style('opacity', 0) 
                    .attr('x', d => {
                        const polygon = voronoi.cellPolygon(nodes.indexOf(d));
                        if (!polygon) return d.x;
                        const centroid = d3.polygonCentroid(polygon);
                        return centroid[0] * 0.4 + d.x * 0.6;
                    })
                    .attr('y', d => {
                        const polygon = voronoi.cellPolygon(nodes.indexOf(d));
                        if (!polygon) return d.y;
                        const centroid = d3.polygonCentroid(polygon);
                        return centroid[1] * 0.4 + d.y * 0.6;
                    })

                textEl.each(function(d) {
                    const el = d3.select(this)
                    const label = d.data.isDummy ? d.data.group : d.data.name
                    if (!label) return

                    const polygon = voronoi.cellPolygon(nodes.indexOf(d));
                    let centerX = d.x;
                    if (polygon) {
                        const centroid = d3.polygonCentroid(polygon);
                        centerX = centroid[0] * 0.4 + d.x * 0.6;
                    }

                    const words = label.split(/\s+/)
                    if (words.length > 1) {
                        const mid = Math.ceil(words.length / 2)
                        const line1 = words.slice(0, mid).join(' ')
                        const line2 = words.slice(mid).join(' ')
                        
                        el.append('tspan')
                            .text(line1)
                            .attr('x', centerX)
                            .attr('dy', '-0.5em')
                        
                        el.append('tspan')
                            .text(line2)
                            .attr('x', centerX)
                            .attr('dy', '1em')
                    } else {
                        el.append('tspan')
                            .text(words[0])
                            .attr('x', centerX)
                            .attr('dy', '0')
                    }
                })

                return textEl;
            },
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )

    const textsToUpdate = svgGroup.selectAll('.genre-label').data(nodes, d => d.data.name);
    
    textsToUpdate
        .transition()
        .duration(750)
        .attr('x', d => {
            const polygon = voronoi.cellPolygon(nodes.indexOf(d));
            if (!polygon) return d.x;
            const centroid = d3.polygonCentroid(polygon);
            return centroid[0] * 0.4 + d.x * 0.6;
        })
        .attr('y', d => {
            const polygon = voronoi.cellPolygon(nodes.indexOf(d));
            if (!polygon) return d.y;
            const centroid = d3.polygonCentroid(polygon);
            return centroid[1] * 0.4 + d.y * 0.6;
        })
        .style('opacity', d => d.data.isDummy ? 0.3 : 1)
        .on('start', function(d) {
             const polygon = voronoi.cellPolygon(nodes.indexOf(d));
             let centerX = d.x;
             if (polygon) {
                 const centroid = d3.polygonCentroid(polygon);
                 centerX = centroid[0] * 0.4 + d.x * 0.6;
             }
             d3.select(this).selectAll('tspan').attr('x', centerX)
        })
        .end().then(() => {
             textsToUpdate.each(function(d) {
                let textWidth = this.getBBox().width
                let availableWidth = d.r * 2 - 4
                if (textWidth > availableWidth && availableWidth > 0) {
                    d3.select(this).style('font-size', `${Math.max(6, availableWidth / textWidth * 10)}px`)
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
