import * as d3 from 'd3'
import { interpolatePath } from 'd3-interpolate-path'
import { continentShape, continentShapeEast, continentShapeNorth, continentShapeSouth } from './defaultContinent.js'

export const drawMap = (genres, year, container, cache, allowedGroups, globalTotal) => {
    if (!genres || !container) return

    const yearData = genres[year.toString()]
    if (!yearData || !yearData.genre_group) return

    const width = container.clientWidth
    const height = container.clientHeight

    if (width === 0 || height === 0) return

    let svg = d3.select(container).select('svg')
    if (svg.empty()) {
        svg = d3.select(container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
    }

    svg.attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')

    const allGroups = allowedGroups || [
        "Classical & Experimental", "Electronic & Synth", "Folk & Acoustics",
        "Hip-Hop & Groove", "Jazz, Blues & Soul", "Metal & Heavy",
        "Pop & Melodies", "Reggae & Global Beats", "Rock & Overdrive"
    ]


    const allowedGroupsData = yearData.genre_group.filter(g => allGroups.includes(g.name) && g.total > 0)
    if (allowedGroupsData.length === 0 && !allowedGroups) return



    let computedGlobalTotal = 0
    if (allowedGroups) {
        yearData.genre_group.forEach(g => {
            if (allGroups.includes(g.name) && g.total > 0) computedGlobalTotal += g.total
        })
    } else {
        computedGlobalTotal = globalTotal || 0
        if (!globalTotal) {
            yearData.genre_group.forEach(g => {
                if (g.total > 0) computedGlobalTotal += g.total
            })
        }
    }

    const macroHierarchy = d3.hierarchy({
        name: 'root',
        children: allGroups.map(name => {
            const g = yearData.genre_group.find(g => g.name === name)

            const trueRatio = g && computedGlobalTotal > 0 ? (g.total / computedGlobalTotal) : 0
            return { name, value: Math.max(0.001, trueRatio) }
        })
    }).sum(d => d.value)
        .sort((a, b) => a.data.name.localeCompare(b.data.name))

    const macroPack = d3.pack()
        .size([width, height])

    const macroNodes = macroPack(macroHierarchy).leaves()

    let nodes = []

    macroNodes.forEach(macroNode => {
        const groupName = macroNode.data.name

        const groupMatch = yearData.genre_group.find(g => g.name === groupName)
        const realGenres = groupMatch
            ? Object.entries(groupMatch.genres).filter(([_, count]) => count > 0).sort((a, b) => a[0].localeCompare(b[0]))
            : []

        if (realGenres.length === 0) {

            nodes.push({
                x: macroNode.x,
                y: macroNode.y,
                r: 4,
                data: { name: `__placeholder__${groupName}`, group: groupName, isDummy: true, isEmpty: true }
            })
            return
        }

        const groupTotal = groupMatch ? groupMatch.total || 0 : 0
        const maxFit = 2 * Math.min(macroNode.x, width - macroNode.x, macroNode.y, height - macroNode.y)

        const hierarchyData = {
            name: groupName,
            children: realGenres.map(([name, count]) => ({
                name: name, group: groupName, value: count, isDummy: false
            }))
        }

        const root = d3.hierarchy(hierarchyData)
            .sum(d => {
                if (!d.value || d.value <= 0) return 0
                return 25 + (Math.log10(d.value) * 20)
            })
            .sort((a, b) => (a.data.name || '').localeCompare(b.data.name || ''))

        const minNodeR = 18
        const leaves = root.leaves()
        const totalSum = leaves.reduce((s, l) => s + (l.value || 0), 0)
        const minValue = Math.min(...leaves.map(l => l.value || Infinity))
        const minNeededDiameter = 2 * minNodeR * Math.sqrt(totalSum / Math.max(minValue, 1))
        const baseDiameter = Math.max(40, Math.min(macroNode.r * 2, maxFit))
        const dynamicDiameter = Math.max(baseDiameter, minNeededDiameter)

        const pack = d3.pack()
            .size([dynamicDiameter, dynamicDiameter])
            .padding(3)

        const packedLeaves = pack(root).leaves()
        const offsetX = macroNode.x - (dynamicDiameter / 2)
        const offsetY = macroNode.y - (dynamicDiameter / 2)

        if (width / height > 2) {
            const totalValue = packedLeaves.reduce((s, l) => s + (l.value || 1), 0)
            let cursor = 0
            const maxYOffset = height * 0.28
            packedLeaves.forEach((leaf, i) => {
                const share = (leaf.value || 1) / totalValue
                const cellW = width * share
                leaf.x = cursor + cellW / 2
                // stagger y with a sine wave so voronoi boundaries are diagonal
                leaf.y = height / 2 + Math.sin(i * 1.9) * maxYOffset
                leaf.r = Math.max(cellW / 2 - 4, 8)
                cursor += cellW
                nodes.push(leaf)
            })
        } else {
            packedLeaves.forEach(leaf => {
                leaf.x += offsetX
                leaf.y += offsetY
                nodes.push(leaf)
            })
        }
    })

    if (nodes.length === 0) return

    nodes.sort((a, b) => {
        const indexA = allGroups.indexOf(a.data.group)
        const indexB = allGroups.indexOf(b.data.group)
        if (indexA !== indexB) return indexA - indexB
        return (a.data.name || '').localeCompare(b.data.name || '')
    })

    const isLandscape = width / height > 2

    if (!isLandscape) {
        d3.forceSimulation(nodes)
            .force('collide', d3.forceCollide(d => Math.max(d.r, 30) + 2))
            .force('x', d3.forceX(d => d.x).strength(0.4))
            .force('y', d3.forceY(d => d.y).strength(0.4))
            .stop()
            .tick(30)
    }

    const delaunay = d3.Delaunay.from(nodes, d => d.x, d => d.y)

    const voronoi = delaunay.voronoi([0, 0, width, height])

    const EAST_GROUPS = ['Rock & Overdrive', 'Jazz, Blues & Soul', 'Folk & Acoustics', 'Classical & Experimental']
    const NORTH_GROUPS = ['Metal & Heavy']
    const SOUTH_GROUPS = ['Reggae & Global Beats']
    const isEast = allowedGroups && allowedGroups.some(g => EAST_GROUPS.includes(g))
    const isNorth = allowedGroups && allowedGroups.some(g => NORTH_GROUPS.includes(g))
    const isSouth = allowedGroups && allowedGroups.some(g => SOUTH_GROUPS.includes(g))
    const shapeFunc = isEast ? continentShapeEast : isNorth ? continentShapeNorth : isSouth ? continentShapeSouth : continentShape

    if (!cache.continentPath || cache.width !== width || cache.height !== height) {
        cache.continentPath = shapeFunc(width, height)
        cache.width = width
        cache.height = height
    }
    const continentPath = cache.continentPath

    const peakGenres = new Set((yearData.metadata && yearData.metadata.peak_genres) ? yearData.metadata.peak_genres : [])

    const colorScale = d3.scaleOrdinal()
        .domain([
            "Classical & Experimental", "Electronic & Synth", "Folk & Acoustics",
            "Hip-Hop & Groove", "Jazz, Blues & Soul", "Metal & Heavy",
            "Pop & Melodies", "Reggae & Global Beats", "Rock & Overdrive"
        ])
        .range(d3.schemePaired)

    let defs = svg.select('defs')
    if (defs.empty()) {
        defs = svg.append('defs')
    }

    const clipId = 'continent-clip-' + allGroups[0].replace(/[^a-z0-9]/gi, '-').toLowerCase()

    const clipPath = defs.selectAll(`#${clipId}`)
        .data([continentPath])
        .join('clipPath')
        .attr('id', clipId)

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

    svgGroup.attr('clip-path', `url(#${clipId})`)

    const groupContainers = svgGroup.selectAll('.genre-group-container')
        .data(allGroups)
        .join(
            enter => {
                const g = enter.append('g')
                    .attr('class', d => `genre-group-container genre-group-${d.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`)
                    .attr('data-group', d => d)

                g.append('g').attr('class', 'layer-outline')
                g.append('g').attr('class', 'layer-blob')
                g.append('g').attr('class', 'layer-internal')
                g.append('g').attr('class', 'genre-texts-layer')

                return g
            },
            update => update,
            exit => exit.remove()
        )
        .classed('empty-group', d => {
            const g = yearData.genre_group.find(g => g.name === d)
            return !g || !Object.values(g.genres || {}).some(count => count > 0)
        })

    const initialPath = d => `M${d.x},${d.y - 1}L${d.x + 1},${d.y}L${d.x},${d.y + 1}L${d.x - 1},${d.y}Z`

    const instancePrefix = allGroups[0].replace(/[^a-z0-9]/gi, '-').toLowerCase()
    const makeId = d => instancePrefix + '-genre-path-' + (d.data.group + '-' + d.data.name).replace(/[^a-zA-Z0-9-]/g, '-').toLowerCase()

    let defsPathsGroup = defs.select('g.genre-paths-defs')
    if (defsPathsGroup.empty()) {
        defsPathsGroup = defs.append('g').attr('class', 'genre-paths-defs')
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
        )

    defPaths.transition()
        .duration(750)
        .attrTween("d", function (d) {
            let previous = d3.select(this).attr("d")
            if (!previous || previous === '' || previous.indexOf('M0,') >= 0 || previous.includes('NaN')) {
                previous = initialPath(d)
            }
            const index = nodes.indexOf(d)
            const current = voronoi.renderCell(index)
            return interpolatePath(previous, current || previous)
        })

    groupContainers.select('.layer-outline').selectAll('use.shape-outline')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
                .attr('class', 'shape-outline')
                .attr('href', d => `#${makeId(d)}`),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .transition().duration(750).style('opacity', d => d.data.isEmpty ? 0 : 1)

    groupContainers.select('.layer-blob').selectAll('use.shape-blob')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
                .attr('class', 'shape-blob')
                .attr('href', d => `#${makeId(d)}`)
                .attr('fill', d => colorScale(d.data.group))
                .attr('stroke', d => colorScale(d.data.group)),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .classed('peak-genre', d => peakGenres.has(d.data.name))
        .transition().duration(750).style('opacity', d => d.data.isEmpty ? 0.08 : 0.9)

    groupContainers.select('.layer-internal').selectAll('use.shape-internal')
        .data(groupName => nodes.filter(n => n.data.group === groupName), d => d.data.name)
        .join(
            enter => enter.append('use')
                .attr('class', 'shape-internal')
                .attr('href', d => `#${makeId(d)}`)
                .on('mouseenter', function (event, d) {
                    if (d.data.isDummy) return
                    d3.select(this).classed('is-hovered', true).raise()
                })
                .on('mouseleave', function (event, d) {
                    if (d.data.isDummy) return
                    d3.select(this).classed('is-hovered', false)
                }),
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )
        .classed('peak-genre', d => peakGenres.has(d.data.name))
        .transition().duration(750).style('opacity', d => d.data.isEmpty ? 0 : (d.data.isDummy ? 0.1 : 1))

    const textsLayer = groupContainers.select('.genre-texts-layer')
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
                        const polygon = voronoi.cellPolygon(nodes.indexOf(d))
                        if (!polygon) return d.x
                        const centroid = d3.polygonCentroid(polygon)
                        return centroid[0] * 0.4 + d.x * 0.6
                    })
                    .attr('y', d => {
                        const polygon = voronoi.cellPolygon(nodes.indexOf(d))
                        if (!polygon) return d.y
                        const centroid = d3.polygonCentroid(polygon)
                        return centroid[1] * 0.4 + d.y * 0.6
                    })

                textEl.each(function (d) {
                    const el = d3.select(this)
                    const label = d.data.isDummy ? d.data.group : d.data.name
                    if (!label) return

                    const polygon = voronoi.cellPolygon(nodes.indexOf(d))
                    let centerX = d.x
                    if (polygon) {
                        const centroid = d3.polygonCentroid(polygon)
                        centerX = centroid[0] * 0.4 + d.x * 0.6
                    }

                    const words = label.split(/\s+/)
                    if (words.length > 1) {
                        const mid = Math.ceil(words.length / 2)
                        const line1 = words.slice(0, mid).join(' ')
                        const line2 = words.slice(mid).join(' ')

                        el.append('tspan').text(line1).attr('x', centerX).attr('dy', '-0.5em')
                        el.append('tspan').text(line2).attr('x', centerX).attr('dy', '1em')
                    } else {
                        el.append('tspan').text(words[0]).attr('x', centerX).attr('dy', '0')
                    }
                })

                return textEl
            },
            update => update,
            exit => exit.transition().duration(500).style('opacity', 0).remove()
        )

    svgGroup.selectAll('.genre-label').classed('peak-genre', d => peakGenres.has(d.data.name))

    const textsToUpdate = svgGroup.selectAll('.genre-label').data(nodes, d => d.data.name)

    textsToUpdate
        .transition()
        .duration(750)
        .attr('x', d => {
            const polygon = voronoi.cellPolygon(nodes.indexOf(d))
            if (!polygon) return d.x
            const centroid = d3.polygonCentroid(polygon)
            return centroid[0] * 0.4 + d.x * 0.6
        })
        .attr('y', d => {
            const polygon = voronoi.cellPolygon(nodes.indexOf(d))
            if (!polygon) return d.y
            const centroid = d3.polygonCentroid(polygon)
            return centroid[1] * 0.4 + d.y * 0.6
        })
        .style('opacity', d => d.data.isDummy ? 0.3 : 1)
        .on('start', function (d) {
            const polygon = voronoi.cellPolygon(nodes.indexOf(d))
            let centerX = d.x
            if (polygon) {
                const centroid = d3.polygonCentroid(polygon)
                centerX = centroid[0] * 0.4 + d.x * 0.6
            }
            d3.select(this).selectAll('tspan').attr('x', centerX)
        })
        .end().then(() => {
            textsToUpdate.each(function (d) {
                let textWidth = this.getBBox().width
                let availableWidth = d.r * 2 - 4
                if (textWidth > availableWidth && availableWidth > 0) {
                    d3.select(this).style('font-size', `${Math.max(6, availableWidth / textWidth * 10)}px`)
                }
            })
        }).catch(() => { })
}
