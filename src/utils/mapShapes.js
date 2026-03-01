// Defines the path data for the continent shape
// We return a function that generates the path string based on width and height
export const getContinentPath = (width, height) => {
    const w = width;
    const h = height;

    // A more complex, "jagged" set of points to simulate a coastline.
    // Coordinates are percentages of [0, 1].
    // Using many points + straight lines (L) instead of curves (Q/C) for a rugged look.
    const relativePoints = [
        [0.20, 0.30], // Start 
        [0.18, 0.25],
        [0.22, 0.18], // Northwest bay
        [0.25, 0.15],
        [0.32, 0.12], // North coast
        [0.38, 0.08],
        [0.45, 0.10], // Northern peak
        [0.55, 0.05],
        [0.65, 0.12],
        [0.75, 0.10], // Northeast
        [0.85, 0.15],
        [0.92, 0.22], // East tip
        [0.88, 0.30],
        [0.94, 0.40], // East bay area
        [0.90, 0.50],
        [0.92, 0.60],
        [0.85, 0.70], // Southeast
        [0.78, 0.80],
        [0.65, 0.88], // South coast
        [0.55, 0.92], // South tip
        [0.45, 0.88],
        [0.35, 0.90],
        [0.25, 0.82], // Southwest
        [0.15, 0.75],
        [0.12, 0.65], // West coast
        [0.08, 0.55],
        [0.12, 0.45],
        [0.10, 0.38],
    ];

    // Scaling helper
    const x = (val) => val * w;
    const y = (val) => val * h;

    // Function to add fractal noise (midpoint displacement)
    const subdivide = (p1, p2, iterations, spread) => {
        if (iterations <= 0) {
            return [p2];
        }

        const midX = (p1[0] + p2[0]) / 2;
        const midY = (p1[1] + p2[1]) / 2;

        // Random offset based on spread
        // We use a deterministic-ish randomness or just pure random. 
        // For a stable map (if desired), we'd need a seeded random. 
        // For now, pure random gives a "living" map feel on reload.
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
    const iterations = 3; // How crinkly the coast is
    const initialSpread = 0.05; // Size of the jitter relative to width/height

    // Generate full point list with noise
    for (let i = 0; i < relativePoints.length; i++) {
        const p1 = relativePoints[i];
        const p2 = relativePoints[(i + 1) % relativePoints.length];

        // Add the start point
        if (i === 0) allPoints.push(p1);

        // Add the subdivided points between p1 and p2
        const segmentPoints = subdivide(p1, p2, iterations, initialSpread);
        allPoints = allPoints.concat(segmentPoints);
    }

    // Convert to SVG Path
    if (allPoints.length === 0) return "";

    let path = `M ${x(allPoints[0][0])},${y(allPoints[0][1])}`;

    for (let i = 1; i < allPoints.length; i++) {
        path += ` L ${x(allPoints[i][0])},${y(allPoints[i][1])}`;
    }

    path += " Z"; // Close the path
    return path;
}
