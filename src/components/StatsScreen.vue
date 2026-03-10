<template>
    <div class="stats-screen">
        <button class="close-panel" @click="$emit('showStats', false)">
            <div>
                <span>←</span><span>←</span><span>←</span>
            </div>
        </button>
        <div class="stats-area">
            <div class="highlights">
                <div class="highlight-card">
                    <h4>Peak Year (Albums)</h4>
                    <div class="value">{{ peakYearAlbums.year }}</div>
                    <div class="sub-value">{{ peakYearAlbums.albums }} albums</div>
                </div>
                <div class="highlight-card">
                    <h4>Most Diverse Year</h4>
                    <div class="value">{{ mostDiverseYear.year }}</div>
                    <div class="sub-value">{{ mostDiverseYear.genres }} genres</div>
                </div>
                <div class="highlight-card">
                    <h4>Biggest Genre Explosion</h4>
                    <div class="value">{{ biggestExplosion.year }}</div>
                    <div class="sub-value">+{{ biggestExplosion.diff }} new genres</div>
                </div>
            </div>
            <div class="chart-section top-10-section">
                <h3>All-Time Top 10 Genres</h3>
                <div class="top-10-list">
                    <div v-for="(genre, index) in top10Genres" :key="genre.name" class="top-10-item">
                        <span class="rank">{{ index + 1 }}</span>
                        <span class="name">{{ genre.name }}</span>
                        <span class="count">{{ genre.count }}</span>
                    </div>
                </div>
            </div>
            <div class="chart-section">
                <h3>Number of Genres (1950 - 2025)</h3>
                <div class="chart-wrapper">
                    <div class="y-axis">
                        <span>120</span>
                        <span>100</span>
                        <span>80</span>
                        <span>60</span>
                        <span>40</span>
                        <span>20</span>
                        <span>0</span>
                    </div>
                    <div class="chart-container">
                        <div class="chart">
                            <div v-for="stat in stats" :key="'g' + stat.year" class="chart-bar" :style="{ height: getPercentage(stat.genres, 120) + '%' }" :title="stat.year + ' - Genres: ' + stat.genres"></div>
                        </div>
                        <div class="x-axis">
                            <span v-for="year in xTicks" :key="year">{{ year }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="chart-section">
                <h3>Number of Albums (1950 - 2025)</h3>
                <div class="chart-wrapper">
                    <div class="y-axis">
                        <span>5000</span>
                        <span>4000</span>
                        <span>3000</span>
                        <span>2000</span>
                        <span>1000</span>
                        <span>0</span>
                    </div>
                    <div class="chart-container">
                        <div class="chart">
                            <div v-for="stat in stats" :key="'a' + stat.year" class="chart-bar albums-bar" :style="{ height: getPercentage(stat.albums, 5000) + '%' }" :title="stat.year + ' - Albums: ' + stat.albums"></div>
                        </div>
                        <div class="x-axis">
                            <span v-for="year in xTicks" :key="year">{{ year }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    stats: {
        type: Array,
        required: true,
        default: () => []
    },
    allData: {
        type: Object,
        required: false,
        default: () => ({})
    }
})

defineEmits(['showStats'])

const peakYearAlbums = computed(() => {
    if (!props.stats.length) return { year: '-', albums: 0 }
    return props.stats.reduce((prev, current) => (prev.albums > current.albums) ? prev : current)
})

const mostDiverseYear = computed(() => {
    if (!props.stats.length) return { year: '-', genres: 0 }
    return props.stats.reduce((prev, current) => (prev.genres > current.genres) ? prev : current)
})

const biggestExplosion = computed(() => {
    if (props.stats.length < 2) return { year: '-', diff: 0 }
    let maxDiff = 0
    let year = '-'
    for (let i = 1; i < props.stats.length; i++) {
        const diff = props.stats[i].genres - props.stats[i-1].genres
        if (diff > maxDiff) {
            maxDiff = diff
            year = props.stats[i].year
        }
    }
    return { year, diff: maxDiff }
})

const top10Genres = computed(() => {
    if (!props.allData) return []
    const counts = {}
    for (const year in props.allData) {
        const yData = props.allData[year]
        if (yData && yData.genre_group) {
            for (const group of yData.genre_group) {
                if (group.genres) {
                    for (const [genre, count] of Object.entries(group.genres)) {
                        counts[genre] = (counts[genre] || 0) + count
                    }
                }
            }
        }
    }
    return Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([name, count]) => ({ name, count }))
})

const xTicks = computed(() => {
    const ticks = []
    for (let y = 1950; y <= 2025; y += 5) {
        ticks.push(y)
    }
    return ticks
})

const getPercentage = (val, max) => {
    return max ? (val / max) * 100 : 0
}
</script>
