export const continentShape = (width, height) => {
    const w = width;
    const h = height;

    const relativePoints = [
        [0.06, 0.26],
        [0.02, 0.16],
        [0.08, 0.08],
        [0.20, 0.02],
        [0.32, 0.04],
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
        [0.98, 0.62],
        [0.92, 0.74],
        [0.84, 0.86],
        [0.68, 0.94],
        [0.56, 0.98],
        [0.44, 0.94],
        [0.32, 0.98],
        [0.20, 0.88],
        [0.08, 0.80],
        [0.04, 0.68],
        [0.02, 0.56],
        [0.06, 0.44],
        [0.04, 0.36],
    ];


    const x = (val) => val * w;
    const y = (val) => val * h;

    const subdivide = (p1, p2, iterations, spread) => {
        if (iterations <= 0) {
            return [p2];
        }

        const midX = (p1[0] + p2[0]) / 2;
        const midY = (p1[1] + p2[1]) / 2;

        const angle = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]) + Math.PI / 2;
        const offset = (Math.random() - 0.5) * spread;

        const newX = midX + Math.cos(angle) * offset;
        const newY = midY + Math.sin(angle) * offset;

        const midPoint = [newX, newY];

        return [
            ...subdivide(p1, midPoint, iterations - 1, spread / 2),
            ...subdivide(midPoint, p2, iterations - 1, spread / 2)
        ];
    };

    let allPoints = [];
    const iterations = 3;
    const initialSpread = 0.05;

    for (let i = 0; i < relativePoints.length; i++) {
        const p1 = relativePoints[i];
        const p2 = relativePoints[(i + 1) % relativePoints.length];


        if (i === 0) allPoints.push(p1);


        const segmentPoints = subdivide(p1, p2, iterations, initialSpread);
        allPoints = allPoints.concat(segmentPoints);
    }

    if (allPoints.length === 0) return "";

    let path = `M ${x(allPoints[0][0])},${y(allPoints[0][1])}`;

    for (let i = 1; i < allPoints.length; i++) {
        path += ` L ${x(allPoints[i][0])},${y(allPoints[i][1])}`;
    }

    path += " Z";
    return path;
}
