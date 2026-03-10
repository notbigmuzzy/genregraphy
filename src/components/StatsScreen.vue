<template>
    <div class="stats-screen">
        <button class="close-panel" @click="$emit('showStats', false)">
            <div>
                <span>←</span><span>←</span><span>←</span>
            </div>
        </button>
        <div class="stats-area">
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
    }
})

defineEmits(['showStats'])

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
