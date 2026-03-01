<template>
    <div class="music-map-wrapper">
        <div id="musicMap" class="music-map" ref="mapContainer"/>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { drawMap } from '../utils/drawMap.js'

const props = defineProps({
    genres: {
        type: [Object, Array],
        required: true
    },
    year: {
        type: Number,
        required: true
    },
    allowedGroups: {
        type: Array,
        default: null
    }
})

const mapContainer = ref(null)
let resizeObserver = null

const cache = { width: 0, height: 0, continentPath: '' }

const getGlobalTotal = () => {
    if (!props.genres) return 0
    const yearData = props.genres[props.year.toString()]
    if (!yearData || !yearData.genre_group) return 0
    return yearData.genre_group.reduce((sum, g) => sum + (g.total || 0), 0)
}

const draw = () => {
    if (!props.genres || !mapContainer.value) return
    drawMap(props.genres, props.year, mapContainer.value, cache, props.allowedGroups, getGlobalTotal())
}

onMounted(() => {
    draw()

    resizeObserver = new ResizeObserver((entries) => {
        window.requestAnimationFrame(() => {
            if (entries.length > 0) {
                draw()
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

watch([() => props.genres, () => props.year], draw, { deep: true })
</script>
