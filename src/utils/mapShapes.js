export const getContinentPath = (width, height) => {
    const w = width;
    const h = height;

    const relativePoints = [
        [0.12, 0.30],
        [0.08, 0.22],
        [0.15, 0.15],
        [0.25, 0.10],
        [0.35, 0.12],
        [0.45, 0.05],
        [0.55, 0.10],
        [0.62, 0.08],
        [0.68, 0.12],
        [0.75, 0.15],
        [0.78, 0.18],
        [0.82, 0.25],
        [0.80, 0.30],
        [0.94, 0.40],
        [0.90, 0.50],
        [0.92, 0.60],
        [0.85, 0.70],
        [0.78, 0.80],
        [0.65, 0.88],
        [0.55, 0.92],
        [0.45, 0.88],
        [0.35, 0.90],
        [0.25, 0.82],
        [0.15, 0.75],
        [0.12, 0.65],
        [0.08, 0.55],
        [0.12, 0.45],
        [0.10, 0.38],
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
