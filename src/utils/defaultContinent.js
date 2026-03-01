
const seededRand = (seed) => {
    const s = Math.sin(seed * 127.1 + 311.7) * 43758.5453
    return s - Math.floor(s)
}

const subdivide = (p1, p2, iterations, spread, seedOffset) => {
    if (iterations <= 0) return [p2]

    const midX = (p1[0] + p2[0]) / 2
    const midY = (p1[1] + p2[1]) / 2
    const angle = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]) + Math.PI / 2
    const offset = (seededRand(seedOffset) - 0.5) * spread

    const midPoint = [midX + Math.cos(angle) * offset, midY + Math.sin(angle) * offset]

    return [
        ...subdivide(p1, midPoint, iterations - 1, spread / 2, seedOffset * 1.3 + 1),
        ...subdivide(midPoint, p2, iterations - 1, spread / 2, seedOffset * 1.7 + 2),
    ]
}

const buildPath = (relativePoints, w, h, iterations, spread) => {
    const x = (val) => val * w
    const y = (val) => val * h

    let allPoints = []
    for (let i = 0; i < relativePoints.length; i++) {
        const p1 = relativePoints[i]
        const p2 = relativePoints[(i + 1) % relativePoints.length]
        if (i === 0) allPoints.push(p1)
        allPoints = allPoints.concat(subdivide(p1, p2, iterations, spread, i * 13.7 + 1))
    }

    let path = `M ${x(allPoints[0][0])},${y(allPoints[0][1])}`
    for (let i = 1; i < allPoints.length; i++) {
        path += ` L ${x(allPoints[i][0])},${y(allPoints[i][1])}`
    }
    return path + ' Z'
}


export const continentShape = (width, height) => buildPath([
    [0.06, 0.26],
    [0.02, 0.16],
    [0.08, 0.08],
    [0.20, 0.02],
    [0.32, 0.04],
    [0.38, 0.08],
    [0.36, 0.13],
    [0.42, 0.10],
    [0.44, 0.02],
    [0.56, 0.02],
    [0.64, 0.02],
    [0.72, 0.04],
    [0.80, 0.08],
    [0.84, 0.12],
    [0.88, 0.20],
    [0.86, 0.26],
    [0.98, 0.38],
    [0.98, 0.50],
    [0.94, 0.56],
    [0.90, 0.54],
    [0.92, 0.60],
    [0.98, 0.62],
    [0.92, 0.74],
    [0.84, 0.86],
    [0.68, 0.94],
    [0.60, 0.90],
    [0.56, 0.94],
    [0.52, 0.90],
    [0.44, 0.94],
    [0.40, 0.99],
    [0.36, 0.96],
    [0.32, 0.98],
    [0.20, 0.88],
    [0.08, 0.80],
    [0.04, 0.68],
    [0.02, 0.56],
    [0.12, 0.53],
    [0.20, 0.50],
    [0.14, 0.47],
    [0.06, 0.44],
    [0.12, 0.40],
    [0.10, 0.35],
    [0.06, 0.38],
    [0.04, 0.36],
], width, height, 3, 0.04)


export const continentShapeEast = (width, height) => buildPath([
    [0.18, 0.02],
    [0.34, 0.01],
    [0.52, 0.04],
    [0.60, 0.08],
    [0.58, 0.14],
    [0.66, 0.10],
    [0.68, 0.02],
    [0.82, 0.06],
    [0.94, 0.12],
    [0.98, 0.24],
    [0.96, 0.36],
    [0.90, 0.40],
    [0.88, 0.46],
    [0.94, 0.50],
    [0.98, 0.46],
    [0.94, 0.56],
    [0.98, 0.66],
    [0.96, 0.76],
    [0.90, 0.86],
    [0.78, 0.94],
    [0.72, 0.88],
    [0.68, 0.92],
    [0.70, 0.97],
    [0.64, 0.98],
    [0.50, 0.96],
    [0.36, 0.98],
    [0.28, 0.92],
    [0.24, 0.98],
    [0.22, 0.94],
    [0.10, 0.86],
    [0.04, 0.74],
    [0.02, 0.62],
    [0.06, 0.50],
    [0.18, 0.54],
    [0.28, 0.52],
    [0.20, 0.46],
    [0.08, 0.44],
    [0.02, 0.40],
    [0.04, 0.28],
    [0.08, 0.16],
], width, height, 3, 0.04)


export const continentShapeNorth = (width, height) => buildPath([
    // top — flat
    [0.01, 0.02],
    [0.99, 0.02],
    // right side — small bumps only
    [0.99, 0.20],
    [0.97, 0.38],
    [0.99, 0.55],
    [0.97, 0.68],
    [0.95, 0.76],
    // bottom — organic bays via subdivide
    [0.84, 0.80],
    [0.76, 0.76],
    [0.68, 0.82],
    [0.60, 0.78],
    [0.52, 0.81],
    [0.44, 0.76],
    [0.36, 0.82],
    [0.28, 0.78],
    [0.20, 0.80],
    [0.12, 0.76],
    // left side — small bumps only
    [0.05, 0.74],
    [0.03, 0.62],
    [0.05, 0.48],
    [0.02, 0.32],
    [0.01, 0.16],
], width, height, 4, 0.11)


// South continent — Reggae, Jamaica-shaped but taller
export const continentShapeSouth = (width, height) => buildPath([
    [0.38, 0.02],   // top left of peak
    [0.52, 0.01],   // top center
    [0.66, 0.04],   // top right shoulder
    [0.78, 0.10],   // NE slope
    [0.88, 0.18],   // eastern upper coast
    [0.96, 0.28],   // east coast upper
    [0.98, 0.40],   // east coast mid
    [0.96, 0.52],   // east coast lower — slight bay
    [0.92, 0.58],   // bay indent east
    [0.96, 0.65],   // exit bay
    [0.94, 0.76],   // SE coast
    [0.86, 0.88],   // south-east corner
    [0.72, 0.96],   // south coast right
    [0.58, 0.98],   // south bottom
    [0.44, 0.96],   // south coast left
    [0.30, 0.90],   // SW coast — small bump out
    [0.24, 0.96],   // SW peninsula tip
    [0.16, 0.88],   // back from SW
    [0.08, 0.78],   // west coast lower
    [0.04, 0.66],   // west bay indent
    [0.10, 0.54],   // west bay depth  — big bay
    [0.22, 0.50],   // west bay far wall
    [0.14, 0.44],   // exit bay
    [0.04, 0.40],   // west coast upper
    [0.06, 0.28],   // NW slope
    [0.14, 0.16],   // north-west shoulder
    [0.26, 0.06],   // top-left approach
], width, height, 3, 0.035)

